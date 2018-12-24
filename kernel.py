# ───────────────────────────────── imports ────────────────────────────────── #
from characters import Adventurer
from dungeon_map import DungeonMap
# ──────────────────────────────────────────────────────────────────────────── #

# ────────────── Kernel classes for the MADI project (01/2019) ─────────────── #
class Dungeon(object):
    """ Dungeon object containing all the game logic """

    def __init__(self, n: int, m: int, nb_players: int = 1):
        self.map = DungeonMap(n, m)
        self.adventurers = [Adventurer(n - 1, m - 1)]

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __str__(self):
        return str(self.map)

    def __repr__(self):
        return "Dungeon({} x {}, {} players)".format(self.n, self.m, len(self.adventurers))

# ──────────────────────────────── executable ──────────────────────────────── #
if __name__ == '__main__':
    d = Dungeon(8, 8)
    print(d)
