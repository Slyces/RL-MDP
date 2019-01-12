# ───────────────────────────────── imports ────────────────────────────────── #
import csv

from dungeon_map import Direction, Cell
from utils import vprint
from states import State
import numpy as np, random
# ──────────────────────────────────────────────────────────────────────────── #
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

    def process_reward(self, oldState: State, newState: State, action: Direction,
            reward: float):
        """ The agent processes the reward obtained while performing an action """
        pass

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __repr__(self):
        return self.name

    # ───────────────────────────── string infos ───────────────────────────── #
    @property
    def infos(self):
        return '{} items {} [{}]'.format(
                self.name,
                '{ ' + ' , '.join([item.value for item in self.__items]) + ' }',
                'ALIVE' if self.alive else 'DEAD')

# ───────────────────────────── q-learning agent ───────────────────────────── #
class AdventurerLearning(Adventurer):

    def __init__(self, i: int, j: int, n: int, m: int, name='Remi'):
        super().__init__(i, j, n, m, name)
        self.Q = np.zeros((State.max_id, 4))

    def play(self, state: State):
        return Qlearning.policy(self.Q, state)

    def policy(self):
        return Qlearning.policy(self.Q, self.state)

    def process_reward(self, old_state: State, new_state: State, action: Direction, reward: float):
        """ The agent processes the reward obtained while performing an action """
        self.Q = Qlearning.update(self.Q, old_state, new_state, action, reward)
        pass

    def load_Qtable(self, tab: float):
        self.Q = tab

    def load_Qtable_from_file(self, path: str):
        try:
            with open(path, "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                self.Q = np.zeros((1, 4))
                for row in csv_reader:
                    row = [float(i) for i in row]
                    self.Q = np.vstack([self.Q, row])
            self.Q = np.delete(self.Q, (0), axis=0)
            assert State.max_id == len(self.Q), "Q_table size don't fit with map"
        except FileNotFoundError:
            print("File to load don't exist !")
        # except AssertionError:
        #     print("load a normal empty Qtable..")
        #     self.Q = np.zeros((State.max_id, 4))
        #     print("Done")


    def save_Qtable(self, path):
        with open(path, 'w',  newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(self.Q)

# ───────────────────────────── q-learning class ───────────────────────────── #
class Qlearning(object):
    beta = 8
    learning_rate = 0.1
    gamma = 0.9

    def policy(q_table: float, state: State):
        row = q_table[state.id]
        softmax_distribution = Qlearning.softmax(row)
        result = Qlearning.random_index(softmax_distribution)
        return Direction.from_int(result)

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

        action_index = action.to_int
        delta = reward + Qlearning.gamma * currentRow[len(currentRow) - 1] - q_table[old_state.id][action_index]

        q_table[old_state.id][action_index] += Qlearning.learning_rate * delta
        q_table[old_state.id][action_index] = round(q_table[old_state.id][action_index], 5)

        return q_table

