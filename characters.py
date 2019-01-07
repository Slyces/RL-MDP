# ───────────────────────────────── imports ────────────────────────────────── #
from dungeon_map import Direction
from utils import vprint
# ──────────────────────────────────────────────────────────────────────────── #

class Adventurer(object):
    """ Adventurer for the MDP game. """

    def __init__(self, i: int, j: int, n: int, m: int, name='Remi'):
        """
        Initializes an adventurer at position (i, j)
            - where i in the row and j the column
            - where (0, 0) is the top left of the dungeon
        """
        self.name = name
        self.alive = True
        self.i, self.j = i, j
        self.n, self.m = n, m
        self.__items = []

    # ──────────────── get the id number of the current state ──────────────── #
    @property
    def state_id(self):
        """
        Returns a number between 0 and 2 * 3 * n * m (inclusive)
            where n & m are the size of the current dungeon

        (s, t, c):
            - s : 1 if I have a sword, else 0
            - t : 2 if I have the treasure (and the key)
                  1 if I have the key
                  0 else
            - c : id of the current position
        """
        swords = 2 # number of states considering the sword only
        treasure = 3 # number of states considering treasure and key only
        cells = self.n * self.m # number of states considering the position

        treasure_value = 0
        if self.has_item(Cell.golden_key): treasure_value = 1
        elif self.has_item(Cell.treasure): treasure_value = 2

        return self.has_item(Cell.magic_sword) * treasure * cells + \
                treasure_value * cells + self.cell_id

    @property
    def cell_id(self):
        return self.i * self.m + self.j

    # ─────────────────────── death of the adventurer ──────────────────────── #
    def kill(self):
        """ kills the adventurer """
        self.alive = False

    # ─────────────────────── position getter / setter ─────────────────────── #
    @property
    def pos(self):
        return (self.i, self.j)

    @pos.setter
    def pos(self, new_pos: (int, int)):
        self.i, self.j = new_pos

    # ─────────────── methods changing the state of the agent ──────────────── #
    def acquire_item(self, item):
        if item in self.__items:
            vprint("Player {} can't acquire {}, he already has one".format(
                self, item))
        else:
            self.__items.append(item)

    def has_item(self, item):
        return item in self.__items

    # ─────────────────────── decision making methods ──────────────────────── #
    def play(self, state):
        """
        Main method of the Adventurer agent.
        He will choose the actions to perform during his turn, (moving).
        Returns the direction chosen (North, East, South, West)
        """
        return Directions.NORTH

    def process_reward(self, state, action: Direction, reward: float):
        """ The agent processes the reward obtained while performing an action """
        pass

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __repr__(self):
        return self.name

    # ───────────────────────────── string infos ───────────────────────────── #
    @property
    def infos(self):
        return '{} items {} [{}]'.format(self.name,
                set([item.value for item in self.__items]),'ALIVE' if self.alive else 'DEAD')
