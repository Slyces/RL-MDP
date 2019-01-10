# ───────────────────────────────── imports ────────────────────────────────── #
from characters import State, Adventurer
from kernel import Dungeon
import numpy as np
# ──────────────────────────────────────────────────────────────────────────── #

class MDP(Adventurer):
    def __init__(self, i: int, j: int, n: int, m: int, name: str= 'MDP',
            T: np.array= None, R: np.array= None):
        super().__init__(i, j, n, m, name)
        assert T is not None and R is not None
        self.T, self.R = T, R

    def value_iteration(self):
        """
        @return V: array of N x 1, containing the estimated reward for each
        state
        """
        # ────────────────────────── variables init ────────────────────────── #
        n_states = State.max_id + 1
        epsilon = 10e-5
        gamma = 0.9
        delta = 1

        # ────────────────────────── matrices init ─────────────────────────── #
        Q = np.zeros((n_states, 4), np.float32)
        lV = np.ones(n_states, np.float32)
        V = np.zeros(n_states, np.float32)

        # ──────────────────────────── main loop ───────────────────────────── #
        i = 0
        while not (np.abs(V - lV) < epsilon).all() and i < 1000:
            lV = V # lV is last V
            Q = R + gamma * np.matmul(T, V)
            V = np.amax(Q, axis=1)
            i += 1
        P = np.argmax(Q, axis=1)
        return V, P

if __name__ == '__main__':
    np.set_printoptions(precision=2, linewidth=200)
    d = Dungeon(2, 2)
    N = State.max_id + 1
    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [MDP(1, 1, 2, 2, T=T, R=R)]

    V, P = agent.value_iteration()
    # print(V.reshape(N, 1))
    # print(P.reshape(N, 1))
    print(np.concatenate((P.reshape(N, 1), V.reshape(N, 1)), axis=1))