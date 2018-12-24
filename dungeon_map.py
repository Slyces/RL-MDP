# ───────────────────────────────── imports ────────────────────────────────── #
from enum import Enum
from random import choice as rchoice

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
    def random_cell(self, start: (int, int)= (0, 0), dist: int= -1):
        """
        Finds a random valid cell within a 'dist' manhattan distance of the start
        if 'dist' = -1, finds a random valid cell in the whole map
        """
        candidates = set()
        a, b = start
        for h in range(self.n * self.m):
            pos = (h // self.m, h % self.m)
            if dist < 0 or self.distance(start, pos) <= dist and self[pos] != Cell.wall:
                candidates.add(pos)
        assert len(candidates) > 0, "empty candidates for a random cell"
        return rchoice(candidates)

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
        return (i,j) if self[ni, nj] == Cell.wall else (ni, nj)

    # ────────────────────── generate a random dungeon ─────────────────────── #
    def generate_map(self):
        """ @TODO: finish the random generation """
        self[0, 1] = Cell.golden_key
        self[1, 0] = Cell.magic_sword
        assert self.valid()
        return self.snapshot()

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
