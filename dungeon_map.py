# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from enum import Enum
from random import choice as rchoice, randint
from numpy.random import choice as npchoice
import utils
# ─────────────────────────── Cardinal Directions ──────────────────────────── #
class Direction(Enum):
    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

    @property
    def reverse(self):
        return list(Direction)[(self.to_int + 2) % 4]

    @property
    def to_int(self):
        return list(Direction).index(self)

    @staticmethod
    def from_int(value: int):
        return list(Direction)[int(value)]

# ─────────────────────────────── Cells Types ──────────────────────────────── #
class Cell(Enum):
    pretty_cells = True
    empty = '  '[pretty_cells]
    start = '◉◉'[pretty_cells]
    wall = '■■'[pretty_cells]
    enemy = 'Eﲅ'[pretty_cells]
    trap = 'R☠'[pretty_cells]
    crack = 'Cﲯ'[pretty_cells]
    treasure = 'Tﰤ'[pretty_cells]
    magic_sword = 'SS'[pretty_cells]
    golden_key = 'K'[pretty_cells]
    magic_portal = 'P'[pretty_cells]
    moving_platform = '--'[pretty_cells]

    def to_save(self):
        switch = {
            self.empty: "a",
            self.start: "b",
            self.wall: "c",
            self.enemy: "d",
            self.trap: "e",
            self.crack: "f",
            self.treasure: "g",
            self.magic_sword: "h",
            self.golden_key: "i",
            self.magic_portal: "j",
            self.moving_platform: "k",
        }
        return switch[self]

    def to_load(c: str):
        switch = {
            'a': Cell.empty,
            'b': Cell.start,
            'c': Cell.wall,
            'd': Cell.enemy,
            'e': Cell.trap,
            'f': Cell.crack,
            'g': Cell.treasure,
            'h': Cell.magic_sword,
            'i': Cell.golden_key,
            'j': Cell.magic_portal,
            'k': Cell.moving_platform,
        }
        return switch[c]


# ─────────────────────── Map representing the dungeon ─────────────────────── #
class DungeonMap(object):
    """ Dungeon Map represented by a grid of n * m cells """

    # ------------ different types of cells found in the dungeon ------------- #
    def __init__(self, n: int, m: int):
        """
        The dungeon is a grid of size n * m, initialized
        with only a starting position (bottom right corner) and
        a treasure (bottom top corner).
        """
        self.n, self.m = n, m
        self.__grid = [Cell.empty for i in range(self.n * self.m)]
        self[0, 0] = Cell.treasure
        self[n - 1, m - 1] = Cell.start

        self.init_map = self.generate_map()
        self.reset()

    # ────────────────────── is that dungeon winnable ? ────────────────────── #
    def __is_winnable(self, portals: bool = False):
        """
        Tests if the dungeon is winnable,
        i.e: there exists a path from the start to the golden key, from the
        golden key to the treasure and from the treasure to the start

        @param portals: [bool] authorizes the use of random portals in the path
        @return cool: True if the path exists under the given conditions
        """
        astar = AStar(unreachable=(Cell.wall, Cell.crack)) if portals else \
            AStar(unreachable=(Cell.wall, Cell.crack, Cell.magic_portal))
        astar.load_map(self)
        key, treasure, start = None, (0, 0), (self.n - 1, self.m - 1)
        for h in range(self.m * self.n):
            if self[h] == Cell.golden_key:
                key = (h // self.m, h % self.m)
        path_to_key = astar.process_shortest_path(start, key)
        path_to_treasure = astar.process_shortest_path(key, treasure)
        path_back = astar.process_shortest_path(treasure, start)

        # for path_str in ('path_to_key', 'path_to_treasure', 'path_back'):
        # path = locals()[path_str]
        # if path:
        # print((' * ' + path_str + ' * ').center(4 * self.m + 1, '-'))
        # astar.display_path(path)
        return bool(path_to_key) and bool(path_to_treasure) and bool(path_back)

    def valid(self, g=None):
        """
        Test the validity of the map:
            - 1 (& only 1) start
            - 1 (& only &) treasure
            - 1+ golden key
            - 1+ magic sword
        """
        g = self.__grid if g is None else g
        return g.count(Cell.start) == 1 and \
               g.count(Cell.treasure) == 1 and \
               g.count(Cell.golden_key) >= 1 and \
               g.count(Cell.magic_sword) >= 1

    # ──────────── find all non-wall cells at a certain distance ───────────── #
    def all_cell_dist(self, start: (int, int) = (0, 0), dist: int = -1):
        """
        Finds all valid cells within a 'dist' manhattan distance of the start
        if 'dist' = -1, finds all valid cells in the whole map
        """
        candidates = list()
        for h in range(self.n * self.m):
            pos = (h // self.m, h % self.m)
            if (dist < 0 or 0 < self.distance(start, pos) <= dist) and self[pos] != Cell.wall:
                candidates.append(pos)
        assert len(candidates) > 0, "empty candidates for a random cell"
        return candidates

    # ────────────────────── find random non-wall cells ────────────────────── #
    def random_cell_dist(self, start: (int, int) = (0, 0), dist: int = -1):
        """
        Finds a random valid cell within a 'dist' manhattan distance of the start
        if 'dist' = -1, finds a random valid cell in the whole map
        """
        return rchoice(self.all_cell_dist(start, dist))

    # ───────── find the neighbors of a cell (with their direction) ────────── #
    def neighbors(self, i: int, j: int):
        """
        @param i: int= row of the target cell
        @param j: int= col of the target cell

        @return generator (pos, direction) for each neighbor of (i, j)
        """
        for direction in Direction:
            ni, nj = self.move((i, j), direction)
            if (ni, nj) != (i, j):
                yield ((ni, nj), direction)

    # ────────────────────────── manhattan distance ────────────────────────── #
    def distance(self, A: (int, int), B: (int, int)):
        """ Returns the Manhattan distance between A and B """
        (ax, ay), (bx, by) = A, B
        return abs(ax - bx) + abs(ay - by)

    # ─────────────────────────── simulates a move ─────────────────────────── #
    def move(self, pos: (int, int), direction: Direction):
        """ Returns the position after a move """
        i, j = pos
        di, dj = direction.value
        ni, nj = min(max(i + di, 0), self.n - 1), min(max(j + dj, 0), self.m - 1)
        return (ni, nj)

    # ────────────────────── generate a random dungeon ─────────────────────── #
    def generate_map(self):
        """
        Generates a list of cells to be loaded as a layout

        @return a grid of Cell enums randomly generated
        """
        n, m = self.n, self.m
        grid = ['' for i in range(n * m)]
        # ------------------- treasure and start are fixed ------------------- #
        grid[0] = Cell.treasure
        grid[n * m - 1] = Cell.start
        required = [Cell.golden_key, Cell.magic_sword]
        while len(required) > 0:
            h = randint(1, n * m - 2)
            if grid[h] == '': grid[h] = required.pop()

        cell_p = [
            (Cell.empty, 0.5),
            (Cell.wall, 0.2),
            (Cell.magic_portal, 0.05),
            (Cell.crack, 0.05),
            (Cell.moving_platform, 0.05),
            (Cell.trap, 0.05),
            (Cell.enemy, 0.1)
        ]
        cells = [cell for (cell, _) in cell_p]
        distrib = [p for (_, p) in cell_p]
        for h in range(n * m):
            cell = npchoice(cells, p=distrib)
            if grid[h] == '': grid[h] = cell

        assert self.valid(grid)
        return grid

    # ──────────────────── take a snapshot, reload, reset ──────────────────── #
    def snapshot(self):
        """ Returns a snapshot (save) of the dungeon at this point of time """
        return self.__grid.copy()

    def load(self, snapshot):
        """ Loads a snapshot (list of cells) of a dungeon of same size """
        assert len(snapshot) == self.n * self.m
        self.__grid = snapshot
        self.winnable = self.__is_winnable(portals=False)

    def reset(self):
        """ Resets the dungeon to its initial layout (stored in init_map) """
        self.load(self.init_map)

    def load_map(self, save_path: str):
        try:
            with open(save_path, 'r') as file:
                line = file.readline()
                self.n, self.m = [int(x) for x in line.split(',')]
                line = file.readline()
                self.__grid = [Cell.to_load(c) for c in line]
        except FileNotFoundError:
            print("File to load don't exist !")
        self.init_map = self.__grid
        self.reset()

    def save_map(self, save_path: str):
        with open(save_path, 'w',  newline='') as file:
            file.write(str(self.n) + ',' + str(self.m) + '\n' + ''.join([c.to_save() for c in self.__grid]))

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __getitem__(self, indexes):
        if isinstance(indexes, (list, tuple)) and len(indexes) == 2:
            return self.__grid[indexes[0] * self.m + indexes[1]]
        if isinstance(indexes, (int, slice)):
            return self.__grid[indexes]
        raise IndexError

    def __setitem__(self, indexes, value):
        if isinstance(indexes, (list, tuple)) and len(indexes) == 2:
            self.__grid[indexes[0] * self.m + indexes[1]] = value
        elif isinstance(indexes, (int, slice)):
            self.__grid[indexes] = value
        else:
            raise IndexError

    def __iter__(self):
        return iter(self.__grid)

    # ---------------------------- representation ---------------------------- #
    def __str__(self):
        """
        String representation of the dungeon. Ex:
        ┌───┬───┬───┬───┬───┬───┐
        │ T │   │   │   │   │   │
        ├───┼───┼───┼───┼───┼───┤
        │   │   │   │   │   │   │
        ├───┼───┼───┼───┼───┼───┤
        │   │   │   │   │   │ ◦ │
        └───┴───┴───┴───┴───┴───┘
        """
        # return utils.grid([cell.value for cell in self.__grid], (self.n, self.m))
        top = "┌───" + "┬───" * (self.m - 1) + "┐"
        sep = "├───" + "┼───" * (self.m - 1) + "┤"
        bot = "└───" + "┴───" * (self.m - 1) + "┘"
        m = self.m
        dungeon_lines = [self[row * m: (row + 1) * m] for row in range(self.n)]
        formated_lines = ['│ ' + ' │ '.join([cell.value for cell in line]) + ' │'
                          for line in dungeon_lines]
        return top + "\n" + ("\n" + sep + "\n").join(formated_lines) + "\n" + bot + "\n"

    def __repr__(self):
        return "DungeonMap({}, {})".format(self.n, self.m)

# ────────────────────────── A Star implementation ─────────────────────────── #
class AStar(object):
    """ Special AStar algorithm adapted to this specific labyrinth """

    dist = DungeonMap.distance  # we reuse the Manhattan distance

    def __init__(self, unreachable: list = (Cell.wall, Cell.crack)):
        """
        Creates an instance of the AStar algorithm
            - unreachable: list of cells forbidden (not accessible)
        """
        self.unreachable = unreachable
        self.objective = (-1, -1)
        self.map, self.grid = None, None

    # ─────────────── loads a map for the next shortest paths ──────────────── #
    def load_map(self, d_map: DungeonMap):
        """
        Loads a dungeon map that will be used for every pathfinding

        @return None
        """
        self.map = d_map
        n, m = d_map.n, d_map.m
        self.grid = [{'parent': None, 'f': 0, 'g': 0, 'h': 0} for h in range(n * m)]

    def unload_map(self):
        """
        Unloads a dungeon map

        @return None
        """
        self.map, self.grid = None, None

    # ────────────── method to check if the algorithm is ready ─────────────── #
    @property
    def ready(self):
        """
        The algorithm needs to be configured before finding a shortest path

        @return bool: True if ready to find a shortest path
        """
        return self.objective != (-1, -1) and self.grid is not None and self.map is not None

    # ──────────────────── test if a cell can be reached ───────────────────── #
    def reachable(self, pos: (int, int)):
        """
        returns a boolean if the pos is accessible

        @param pos: position of a cell
        @return bool: is that cell accessible ?
        """
        return self.map is not None and self.map[pos] not in self.unreachable

    def heuristic(self, pos: (int, int)):
        """
        Computes the heuristic value H for a cell: distance betweenthis cell
        and the objective cell, multiplied by 10

        @param pos: tuple of 2 ints (coordinates)
        @returns heuristic value H
        """
        assert self.ready
        return 10 * self.dist(pos, self.objective)

    # ──────────────────────────── display a path ──────────────────────────── #
    def get_path(self):
        """ Returns the last path found by the AStar object """
        path = [self.objective]
        while self[path[-1]]['parent'] != self.start:
            path += [self[path[-1]]['parent']]
        return path + [self.start]

    def display_path(self, path: list = None):
        """ Shows the path found by the algorithm """
        path = self.get_path() if path is None else path
        print('path : ' + ' → '.join([str(x) for x in path[::-1]]))

    # ──────────────────────────── adjacent cells ──────────────────────────── #
    def adjacent_cells(self, pos: (int, int)):
        """
        Returns a generator of the positions adjacent to the given position
        Counter-clockwise, starting from the top and finishing to the right

        @param pos: a valid position (coordinates) in the map
        @return generator of the neighboring positions of 'pos'
        """
        i, j = pos
        assert 0 <= i < self.map.n and 0 <= j < self.map.m
        if i < self.map.n - 1: yield (i + 1, j)
        if 0 < i: yield (i - 1, j)
        if j < self.map.m - 1: yield (i, j + 1)
        if 0 < j: yield (i, j - 1)

    # ──────────────────────────── update a cell ───────────────────────────── #
    def update_cell(self, adj, cell):
        """
        Update adjacent cell

        @param adj adjacent cell to the current cell
        @param cell current cell being processed
        """
        self[adj]['g'] = self[cell]['g'] + 10
        self[adj]['h'] = self.heuristic(adj)
        self[adj]['f'] = self[adj]['h'] + self[adj]['g']
        self[adj]['parent'] = cell

    # ─────────── main part of the algorithm : find shortest path ──────────── #
    def process_shortest_path(self, start, objective):
        self.start, self.objective = start, objective
        # add starting cell to open heap queue
        opened, closed = [], []
        opened.append((self[start]['f'], start))
        while len(opened):
            # pop cell from heap queue
            f, cell = opened.pop(0)
            # add cell to closed list so we don't process it twice
            closed.append(cell)
            # if ending cell, display found path
            if cell == objective:
                return self.get_path()
            # get adjacent cells for cell
            for adj_cell in self.adjacent_cells(cell):
                if self.reachable(adj_cell) and adj_cell not in closed:
                    if (self[adj_cell]['f'], adj_cell) in opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if self[adj_cell]['g'] > self[cell]['g'] + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        opened.append((self[adj_cell]['f'], adj_cell))

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __getitem__(self, index):
        """
        Easier way to access the cells of the currently loaded map
        ex:
            self[4, 7] instead of self.map[4, 7]

        @return Cell: the cell present at (index), or an IndexError
        """
        return self.grid[index] if isinstance(index, int) else self.grid[index[0] * self.map.m + index[1]]
