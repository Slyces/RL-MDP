# ───────────────────────────────── imports ────────────────────────────────── #

# ──────────────────────────────────────────────────────────────────────────── #

# ────────────── Kernel classes for the MADI project (01/2019) ─────────────── #
class Dungeon(object):
    """ Dungeon represented by a grid of n * m cells """
    # ------------ different types of cells found in the dungeon ------------- #
    empty = 0
    start = 1
    wall = 2
    enemy = 3
    trap = 4
    cracks = 5
    treasure = 6
    magic_sword = 7
    golden_key = 8
    magic_portal = 9
    moving_platform = 10

    def __init__(self, n : int, m : int):
        """ Inits an empty dungeon of n rows and m cols """
        self.n, self.m = n, m
        self.__grid = [[Dungeon.empty for i in range(m)] for j in range(n)]
        self[0, 0] = self.treasure
        self[self.n - 1, self.m - 1] = self.start

        self.init_map = self.generate_map()

    # ---------------------- generate a random dungeon ----------------------- #
    def generate_map(self):
        """ @TODO: finish the random generation """
        return self.snapshot()

    # -------------------- take a snapshot, reload, reset -------------------- #
    def snapshot(self):
        """ Returns a snapshot (save) of the dungeon at this point of time """
        return self.__grid.copy()

    def load(self, snapshot):
        """ Loads a snapshot of a dungeon of same size """
        assert len(snapshot) == self.n and len(snapshot[0]) == self.m
        self.__grid = snapshot

    # ---------------------------- magic methods ----------------------------- #
    def __getitem__(self, indexes):
        if isinstance(indexes, (list, tuple)) and len(indexes) == 2:
            return self.__grid[indexes[0]][indexes[1]]
        if isinstance(indexes, int):
            return self.__grid[indexes]
        raise IndexError

    def __setitem__(self, indexes, value):
        if isinstance(indexes, (list, tuple)) and len(indexes) == 2:
            self.__grid[indexes[0]][indexes[1]] = value
        elif isinstance(indexes, int):
            self.__grid[indexes] = value
        else:
            raise IndexError


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
        cells_repr  = {
                Dungeon.empty           : ' ',
                Dungeon.start           : '◦',
                Dungeon.wall            : '■',
                Dungeon.enemy           : 'E',
                Dungeon.trap            : 'R',
                Dungeon.cracks          : 'C',
                Dungeon.treasure        : 'T',
                Dungeon.magic_sword     : 'S',
                Dungeon.golden_key      : 'K',
                Dungeon.magic_portal    : 'P',
                Dungeon.moving_platform : '-',
        }
        top = "┌───" + "┬───" * (self.m - 1) + "┐"
        sep = "├───" + "┼───" * (self.m - 1) + "┤"
        bot = "└───" + "┴───" * (self.m - 1) + "┘"
        dungeon_lines = [
            '│ ' + ' │ '.join([cells_repr[cell] for cell in row]) + ' │'
            for row in self.__grid
        ]
        return top + "\n" + ("\n" + sep + "\n").join(dungeon_lines) + "\n" + bot + "\n"

    def __repr__(self):
        return "Dungeon({}, {})".format(self.n, self.m)

if __name__ == '__main__':
    d = Dungeon(8, 8)
    print(d)
