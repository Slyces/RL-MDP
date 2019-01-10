#!/usr/bin/env python3
# enconding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from characters import State, Adventurer
from kernel import Dungeon
from interface import TextInterface, LearningInterface
from dungeon_map import Direction
import numpy as np
# ──────────────────────────────────────────────────────────────────────────── #

class MDP(Adventurer):
    def __init__(self, i: int, j: int, n: int, m: int, name: str= 'MDP',
            T: np.array= None, R: np.array= None):
        super().__init__(i, j, n, m, name)
        assert T is not None and R is not None
        n_states = State.max_id + 1
        self.T, self.R = T, R
        self.P = np.zeros(n_states) - 1
        self.gamma = 0.9
        self.epsilon = 10e-5

    # ───────────────────────── configure the agent ────────────────────────── #
    def setup(self):
        self.V, self.P = self.value_iteration()

    # ────────────────── test of the validity of that agent ────────────────── #
    @property
    def ready(self):
        return np.amin(self.P) >= 0

    # ──────────────────── play (decide the next action) ───────────────────── #
    def play(self, state: State):
        assert self.ready
        return Direction.from_int(self.P[state.id])

    # ────────────────────── value iteration algorithm ─────────────────────── #
    def value_iteration(self):
        """
        @return V, P: two arrays of N x 1
                    - V: containing the estimated reward for each state
                    - P: containing the policy associated
        """
        # ────────────────────────── variables init ────────────────────────── #
        n_states = State.max_id + 1

        # ────────────────────────── matrices init ─────────────────────────── #
        # Q = np.zeros((n_states, 4), np.float32)
        lV = np.ones(n_states, np.float32)
        V = np.zeros(n_states, np.float32)

        # ──────────────────────────── main loop ───────────────────────────── #
        i = 0
        while not (np.abs(V - lV) < self.epsilon).all() and i < 1000:
            lV = V # lV is last V
            Q = R + self.gamma * np.matmul(T, V)
            V = np.amax(Q, axis=1)
            i += 1
        P = np.argmax(Q, axis=1)
        return V, P

if __name__ == '__main__':
    np.set_printoptions(precision=2, linewidth=200)
    n, m = 2, 4
    d = Dungeon(n, m)
    # N = State.max_id + 1
    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [MDP(n - 1, m - 1, n, m, T=T, R=R)]

    # V, P = agent.value_iteration()
    # print(V.reshape(N, 1))
    # print(P.reshape(N, 1))
    # print(np.concatenate((P.reshape(N, 1), V.reshape(N, 1)), axis=1))

    agent.setup()

    I = LearningInterface(d)
    I.play_game()
