# ───────────────────────────────── imports ────────────────────────────────── #
from enum import Enum
from random import choice as rchoice, randint
from numpy.random import choice as npchoice

# ─────────────────────────── Cardinal Directions ──────────────────────────── #
class Direction(Enum):
    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

# ─────────────────────────────── Cells Types ──────────────────────────────── #
class Cell(Enum):
    pretty_cells = True
    empty           = '  '[pretty_cells]
    start           = '◦◦'[pretty_cells]
    wall            = '■■'[pretty_cells]
    enemy           = 'Eﲅ'[pretty_cells]
    trap            = 'R☠'[pretty_cells]
    crack           = 'Cﲯ'[pretty_cells]
    treasure        = 'Tﰤ'[pretty_cells]
    magic_sword     = 'SS'[pretty_cells]
    golden_key      = 'K'[pretty_cells]
    magic_portal    = 'P'[pretty_cells]
    moving_platform = '--'[pretty_cells]

# ─────────────────────── Map representing the dungeon ─────────────────────── #
class DungeonMap(object):
    """ Dungeon Map represented by a grid of n * m cells """
    # ------------ different types of cells found in the dungeon ------------- #

    def __init__(self, n : int, m : int):
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

    # ──────────────────── tests of validity for the map ───────────────────── #
    def winnable(self):
        """ Is there a non-lethal path from start to treasure, and back ? """
        # @TODO: code this
        pass

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

    # ────────────────────── find random non-wall cells ────────────────────── #
    def random_cell_dist(self, start: (int, int)= (0, 0), dist: int= -1):
        """
        Finds a random valid cell within a 'dist' manhattan distance of the start
        if 'dist' = -1, finds a random valid cell in the whole map
        """
        candidates = list()
        a, b = start
        for h in range(self.n * self.m):
            pos = (h // self.m, h % self.m)
            if (dist < 0 or 0 < self.distance(start, pos) <= dist) and self[pos] != Cell.wall:
                candidates.append(pos)
        assert len(candidates) > 0, "empty candidates for a random cell"
        return rchoice(candidates)

    # ────────────────────────── manhattan distance ────────────────────────── #
    @staticmethod
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
        return (i,j) if self[ni, nj] == Cell.wall else (ni, nj)

    # ────────────────────── generate a random dungeon ─────────────────────── #
    def generate_map(self):
        """ @TODO: finish the random generation """
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
        cells = [cell for (cell,_) in cell_p]
        distrib = [p for (_,p) in cell_p]
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
        """ Loads a snapshot of a dungeon of same size """
        assert len(snapshot) == self.n * self.m
        self.__grid = snapshot

    def reset(self):
        """ Resets the dungeon to its initial layout (stored in init_map) """
        self.load(self.init_map)

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
        top = "┌───" + "┬───" * (self.m - 1) + "┐"
        sep = "├───" + "┼───" * (self.m - 1) + "┤"
        bot = "└───" + "┴───" * (self.m - 1) + "┘"
        m = self.m
        dungeon_lines = [self[row * m : (row + 1) * m] for row in range(self.n)]
        formated_lines = ['│ ' + ' │ '.join([cell.value for cell in line]) + ' │'
                for line in dungeon_lines]
        return top + "\n" + ("\n" + sep + "\n").join(formated_lines) + "\n" + bot + "\n"

    def __repr__(self):
        return "DungeonMap({}, {})".format(self.n, self.m)

# ────────────────────────── A Star implementation ─────────────────────────── #
class AStar(object):
    """ Special AStar algorithm adapted to this specific labyrinth """

    dist = DungeonMap.dist # we reuse the Manhattan distance

    def __init__(self, unreachable: list= (Cell.wall, Cell.crack)):
        """
        Creates an instance of the AStar algorithm
            - unreachable: list of cells forbidden (not accessible)
        """
        self.unreachable = unreachable
        self.objective = (-1, -1)
        self.grid = None
        self.map = None

    # ─────────────── loads a map for the next shortest paths ──────────────── #
    def load_map(self, d_map: DungeonMap):
        """
        Loads a dungeon map that will be used for every pathfinding

        @return None
        """
        self.map = d_map
        n, m = d_map.n, d_map.m
        self.grid = [Cell(h // m, h % m, self.reachable(d_map[h])) for h in range(n * m)]

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
        return self.objective != (-1, -1)

    # ──────────────────── test if a cell can be reached ───────────────────── #
    def reachable(self, cell: Cell):
        """
        returns a boolean if the cell is accessible

        @param cell: type of a cell (Cell enumeration)
        @return bool: is that cell accessible ?
        """
        return cell not in self.unreachable and self.map is not None

    def heuristic(self, pos: (int, int)):
        """
        Computes the heuristic value H for a cell: distance betweenthis cell
        and the objective cell, multiplied by 10

        @param pos: tuple of 2 ints (coordinates)
        @returns heuristic value H
        """
        assert self.ready
        return 10 * self.dist(pos, self.objective)

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

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __getitem__(self, index):
        """
        Easier way to access the cells of the currently loaded map
        ex:
            self[4, 7] instead of self.map[4, 7]

        @return Cell: the cell present at (index), or an IndexError
        """
        return self.grid[index]

# ────────────────────────── Cell object for AStar ─────────────────────────── #
class Cell(object):
    """ Cell object to compute the AStar shortest path in a labyrinth """
    def __init__(self, i, j, reachable):
        """
        Initializes a new cell
        """
        self.reachable = reachable
        self.parent = None
        self.pos = (i, j)
        self.g, self.h, self.f = 0, 0, 0
