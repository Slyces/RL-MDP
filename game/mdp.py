#!/usr/bin/env python3
# enconding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from .characters import State, Adventurer
from .kernel import Dungeon
from .dungeon_map import Direction, Cell
from .utils import rand_argmax
import numpy as np
# ──────────────────────────────────────────────────────────────────────────── #

class MDP(Adventurer):
    def __init__(self, dungeon: Dungeon, name: str= 'MDP'):
        super().__init__(dungeon, name)
        n_states = State.max_id + 1
        self.P = np.zeros(n_states) - 1
        self.gamma = 0.9
        self.epsilon = 10e-5
        self.reset()

    # ───────────────────────── configure the agent ────────────────────────── #
    def reset(self):
        super().reset()
        self.T = self.dungeon.make_transition_matrix()
        self.R = self.dungeon.make_reward_matrix(self.T)
        self.V, self.P = self.value_iteration()
        # self.V, self.P = self.policy_iteration()

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
        R, T = self.R, self.T
        # Q = np.zeros((n_states, 4), np.float32)
        lV = np.ones(n_states, np.float32)
        V = np.zeros(n_states, np.float32)

        # ──────────────────────────── main loop ───────────────────────────── #
        i = 0
        while not (np.abs(V - lV) < self.epsilon).all() and i < 10000:
            lV = V # lV is last V
            Q = R + self.gamma * np.matmul(T, V)
            V = np.amax(Q, axis=1)
            i += 1
        P = np.argmax(Q, axis=1)
        return V, P

    # ────────────────────── policy iteration algorithm ────────────────────── #
    def policy_iteration(self):
        """
        @return V, P: two arrays of N x 1
                    - V: containing the estimated reward for each state
                    - P: containing the policy associated
        """
        # ────────────────────────── variables init ────────────────────────── #
        n_states = State.max_id + 1

        # ────────────────────────── matrices init ─────────────────────────── #
        R, T = self.R, self.T
        I = np.identity(n_states)
        lP = np.zeros(n_states, np.int8) - 1 # last policy
        P = np.random.randint(4, dtype=np.int8, size=n_states) # random
        
        V = np.zeros(n_states, np.float32)
        Q = np.ones((n_states, 4), np.float32)
        lQ = np.zeros((n_states, 4), np.float32)

        # ──────────────────────────── main loop ───────────────────────────── #
        i = 0
        while not (lP == P).all() and (np.amax(Q, 1) > np.amax(lQ, 1)).any() \
                and i < 10000:
            lP, lQ = P, Q
            Ts = T[np.arange(n_states), P, :] # Transitions of current Policy
            Rs = R[np.arange(n_states), P]
            V = np.linalg.solve(self.gamma * Ts - I, -Rs)
            Q = R + self.gamma * np.matmul(T, V)
            P = rand_argmax(Q, 1)
            i += 1
        return V, P

class ValueMDP(MDP):
    """ MDP using the value iteration for its policy """
    def setup(self):
        self.V, self.P = self.value_iteration()

class PolicyMDP(MDP):
    """ MDP using the policy iteration for its policy """
    def setup(self):
        self.V, self.P = self.policy_iteration()


# if __name__ == '__main__':
    # np.set_printoptions(precision=2, linewidth=300)
    # n, m = 8, 16
    # d = Dungeon(n, m)

    # T = d.make_transition_matrix()
    # R = d.make_reward_matrix(T)
    # agent, = d.agents = [MDP(n - 1, m - 1, n, m, T=T, R=R)]

    # agent.setup()

    # I = LearningInterface(d)
    # I.play_game(1)
