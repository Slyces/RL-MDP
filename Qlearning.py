

from characters import State
import numpy as np
import random
from dungeon_map import Direction


class Qlearning(object):
    action_max = 4
    beta = 8

    def __init__(self):

        self.Q = [State.max_id][Qlearning.action_max]

        for state in range(State.max_id):
            for action in range(Qlearning.action_max):
                self.Q[state][action] = 0

    def policy(self, state: State):

        row = self.Q[state.s_id]
        softmax_distribution = self.softmax(row)
        result = self.randomIndex(softmax_distribution)

        if result == 0:
            return Direction.NORTH
        elif result == 1:
            return  Direction.EAST
        elif result == 2:
            return Direction.SOUTH
        else:
            return Direction.WEST


    def softmax(self, array: np.array()):
        values = len(array)
        sum_array = 0
        for value in array:
            sum_array += np.exp(value * Qlearning.beta)
        for i in range(len(values)):
            values[i] = np.exp(array[i] * Qlearning.beta) / sum_array
        return values

    def randomIndex(self, array: np.array()):
        p = random.random()
        sum = 0.0
        i = 0
        while sum < p:
            sum += array[i]
            i += 1
        return i - 1
