# ───────────────────────────────── imports ────────────────────────────────── #
from character import State, Adventurer
from kernel import Dungeon
# ──────────────────────────────────────────────────────────────────────────── #

class MDP(Adventurer):
    def __init__(self, i: int, j: int, n: int, m: int, name: str= 'MDP',
            T: np.array= None, R: np.array= None):
        super().__init__(i, j, n, m, name)
        assert T is not None and R is not None
