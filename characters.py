# ───────────────────────────────── imports ────────────────────────────────── #
from dungeon_map import Direction, Cell
from utils import vprint


# ──────────────────────────────────────────────────────────────────────────── #

# ───────────────────── state object for a n x m dungeon ───────────────────── #
class State(object):
    """ State of the MDP as designed in the dungeon """

    # ────────────────────────── static attributes ─────────────────────────── #
    n, m, max_id = 0, 0, 0
    swords = 2
    treasures = 3

    def configure(n: int, m: int):
        """ Configures the static parameters of the class """
        State.n, State.m, State.max_id = n, m, n * m * State.swords * State.treasures

    # ───────────────────────────── constructor ────────────────────────────── #
    def __init__(self, sword: int = None, treasure: int = None, position: int = None,
                 s_id: int = None):
        """
        Creates a state object. Two way to initialze:
            - Using the 3 separate values composing a state:

                State(sword=0, treasure=1, position=4) <=> State(0, 1, 4)

            - Using the state id:

                State(s_id=14) # must use the keyword
        """
        assert (sword is not None and treasure is not None and position is not None) or \
               s_id is not None
        if s_id is not None:
            self.s_id = s_id
            self.word, self.treasures, self.position = State.id_to_state(s_id)
        else:
            self.sword, self.treasure, self.position = sword, treasure, position
            self.s_id = State.state_to_id(sword, treasure, position)

    # ──────────────── static conversions : state <--> values ──────────────── #
    @staticmethod
    def id_to_state(s_id: int):
        position = s_id % (State.n * State.m)
        treasure = (s_id // (State.n * State.m)) % State.treasures
        sword = (s_id // (State.n * State.m * State.treasures)) % State.swords
        return sword, treasure, position

    @staticmethod
    def state_to_id(sword: int, treasure: int, position: int):
        n, m = State.n, State.m
        return sword * State.treasures * n * m + treasure * n * m + position

    # ───────────────────────── some usefull getters ───────────────────────── #
    @property
    def i(self):
        return self.position // State.m

    @property
    def j(self):
        return self.position % State.m

    @i.setter
    def i(self, v: int):
        self.position = v * State.m + self.j

    @j.setter
    def j(self, v: int):
        self.position = self.i + v

# ────────────────────── state factory to create states ────────────────────── #
def state_factory(n, m):
    """ Creates a State class configured with the right size (n & m) """
    pass


# ──────────────────────────────── adventurer ──────────────────────────────── #
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

    # ───────────────────────── getter for the state ───────────────────────── #
    @property
    def state(self):
        treasure = 0
        if self.has_item(Cell.golden_key): treasure = 1
        if self.has_item(Cell.treasure): treasure = 2
        return State(self.has_item(Cell.magic_sword), treasure, self.cell_id)

    # ────────────────────────── getter for cell id ────────────────────────── #
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
        return Direction.NORTH



    # ──────────────────────────── magic methods ───────────────────────────── #
    def __repr__(self):
        return self.name

    # ───────────────────────────── string infos ───────────────────────────── #
    @property
    def infos(self):
        return '{} items {} [{}]'.format(self.name,
                                         set([item.value for item in self.__items]), 'ALIVE' if self.alive else 'DEAD')


class AdventurerLearning(Adventurer):

    def __init__(self, i: int, j: int, n: int, m: int, name='Remi'):
        super().__init__(i, j, n, m, name)




    def process_reward(self, state, action: Direction, reward: float):
        """ The agent processes the reward obtained while performing an action """

        pass
