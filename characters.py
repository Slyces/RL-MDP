# ───────────────────────────────── imports ────────────────────────────────── #
from dungeon_map import Direction, Cell
from utils import vprint
import numpy as np
import random


# ──────────────────────────────────────────────────────────────────────────── #
class State(object):
    """ State of the MDP as designed in the dungeon """

    # ────────────────────────── static attributes ─────────────────────────── #
    n, m, max_id = 0, 0, 0
    swords = 2
    treasures = 3

    def configure(n: int, m: int):
        """ Configures the static parameters of the class """
        State.n, State.m = n, m
        State.max_id = n * m * State.swords * State.treasures # account for death

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
        self.__sword, self.__treasure, self.__position, self.__id = -1, -1, -1, -1
        if s_id is not None:
            self.id = s_id
            # self.sword, self.treasure, self.position = State.id_to_state(s_id)
        else:
            # self.sword, self.treasure, self.position = sword, treasure, position
            self.id = State.state_to_id(sword, treasure, position)

    # ─────────────────── use getters for the same reason ──────────────────── #
    @property
    def sword(self): return self.__sword

    @property
    def treasure(self): return self.__treasure

    @property
    def position(self): return self.__position

    @property
    def id(self): return self.__id

    # ──────────────── use setters to garanty value coherency ──────────────── #
    @sword.setter
    def sword(self, value: int):
        self.__sword = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @treasure.setter
    def treasure(self, value: int):
        self.__treasure = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @position.setter
    def position(self, value: int):
        self.__position = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @id.setter
    def id(self, value: int):
        self.__id = value
        self.__sword, self.treasure, self.position = State.id_to_state(value)

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

    def __str__(self):
        return "<S:{},T:{},p:({},{})>".format(self.sword, self.treasure, self.i, self.j)


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
        self.init_pos = i, j
        self.i, self.j = i, j
        self.n, self.m = n, m
        self.__items = []

    def reset(self):
        self.__items = []
        self.alive = True
        self.pos = self.init_pos

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

    def process_reward(self, oldState: State, newState: State, action: Direction, reward: float):
        """ The agent processes the reward obtained while performing an action """
        pass

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
        self.Q = np.zeros((State.max_id, 4))

    def policy(self):
        return Qlearning.policy(self.Q, self.state)

    def process_reward(self, old_state: State, new_state: State, action: Direction, reward: float):
        """ The agent processes the reward obtained while performing an action """
        self.Q = Qlearning.update(self.Q, old_state, new_state, action, reward)
        pass

    def load_Qtable(self, tab):
        self.Q = tab


class Qlearning(object):
    beta = 8
    learning_rate = 0.4
    gamma = 0.9

    def policy(q_table: float, state: State):
        row = q_table[state.id]
        softmax_distribution = Qlearning.softmax(row)
        result = Qlearning.random_index(softmax_distribution)
        return Qlearning.int_to_direction(result)

    def softmax(array):
        values = np.zeros(len(array))
        sum_array = 0.0
        for value in array:
            sum_array += np.exp(value * Qlearning.beta)
        for i in range(len(values)):
            values[i] = np.exp(array[i] * Qlearning.beta) / sum_array
        return values

    def random_index(array):
        p = random.random()
        sum = 0.0
        i = 0
        while sum < p:
            sum += array[i]
            i += 1
        return i - 1

    def update(q_table: float, old_state: State, new_state: State, action: Direction, reward: float):
        currentRow = np.sort(q_table[new_state.id].copy())

        action_index = Qlearning.direction_to_int(action)
        delta = reward + Qlearning.gamma * currentRow[len(currentRow) - 1] - q_table[old_state.id][action_index]

        old = q_table[old_state.id][action_index]
        q_table[old_state.id][action_index] += Qlearning.learning_rate * delta
        q_table[old_state.id][action_index] = round(q_table[old_state.id][action_index], 5)
        new = q_table[old_state.id][action_index]

        return q_table

    # ------------------------- Usefull def --------------------------#

    def direction_to_int(direction: Direction):
        if direction == Direction.NORTH:
            return 0
        elif direction == Direction.EAST:
            return 1
        elif direction == Direction.SOUTH:
            return 2
        else:
            return 3

    def int_to_direction(number: int):
        if number == 0:
            return Direction.NORTH
        elif number == 1:
            return Direction.EAST
        elif number == 2:
            return Direction.SOUTH
        else:
            return Direction.WEST
