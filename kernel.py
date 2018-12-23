# ───────────────────────────────── imports ────────────────────────────────── #

class 

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
        self.__grid[0][0]

    def __getitem__(self, indexes):
        if isinstance(indexes, (list, tuple)) and len(indexes) == 2:
            return self.__grid[indexes[0]][indexes[1]]
        if isinstance(indexes, int):
            return self.__grid[indexes]
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
        top = "┌" + "┬───" * self.m + "┐"
        sep = "├" + "┼───" * self.m + "┤"
        bot = "└" + "┴───" * self.m + "┘"
        dungeon_lines = [
            '│ ' + ' │ '.join([cells_repr[cell] for cell in row])
            for row in self.__grid
        ]
        return top + "\n" + (sep + "\n").join(dungeon_lines) + bot + "\n"
