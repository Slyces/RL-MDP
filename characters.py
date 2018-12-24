# ───────────────────────────────── imports ────────────────────────────────── #
from dungeon_map import Direction
from utils import vprint
# ──────────────────────────────────────────────────────────────────────────── #

class Adventurer(object):
    """ Adventurer for the MDP game. """

    def __init__(self, i: int, j: int):
        """
        Initializes an adventurer at position (i, j)
            - where i in the row and j the column
            - where (0, 0) is the top left of the dungeon
        """
        self.i, self.j = i, j
        self.__items = []

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
