from enum import Enum
# ─────────────────────────── Cardinal Directions ──────────────────────────── #
class Direction(Enum):
    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

# ─────────────────────── Map representing the dungeon ─────────────────────── #
class DungeonMap(object):
    """ Dungeon Map represented by a grid of n * m cells """
    # ------------ different types of cells found in the dungeon ------------- #

    empty           = ' '
    start           = '◦'
    wall            = '■'
    enemy           = 'E'
    trap            = 'R'
    cracks          = 'C'
    treasure        = 'T'
    magic_sword     = 'S'
    golden_key      = 'K'
    magic_portal    = 'P'
    moving_platform = '-'

    def __init__(self, n : int, m : int):
        """
        The dungeon is a grid of size n * m, initialized
        with only a starting position (bottom right corner) and
        a treasure (bottom top corner).
        """
        self.n, self.m = n, m
        self.__grid = [self.empty for i in range(self.n * self.m)]
        self[0, 0] = DungeonMap.treasure
        self[n - 1, m - 1] = DungeonMap.start

        self.init_map = self.generate_map()
        self.reset()

    def is_valid(self, g=None):
        """
        Test the validity of the map:
            - 1 (& only 1) start
            - 1 (& only &) treasure
            - 1+ golden key
            - 1+ magic sword
        """
        g = self.__grid if g is None else g
        return g.count(DungeonMap.start) == 1 and \
                g.count(DungeonMap.treasure) == 1 and \
                g.count(DungeonMap.golden_key) >= 1 and \
                g.count(DungeonMap.magic_sword) >= 1

    # ────────────────────── generate a random dungeon ─────────────────────── #
    def generate_map(self):
        """ @TODO: finish the random generation """
        self[0, 1] = DungeonMap.golden_key
        self[1, 0] = DungeonMap.magic_sword
        assert self.is_valid()
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
        formated_lines = ['│ ' + ' │ '.join(line) + ' │' for line in dungeon_lines]
        return top + "\n" + ("\n" + sep + "\n").join(formated_lines) + "\n" + bot + "\n"

    def __repr__(self):
        return "DungeonMap({}, {})".format(self.n, self.m)
