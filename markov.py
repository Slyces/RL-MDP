# ───────────────────────────────── imports ────────────────────────────────── #
import numpy as np
from numpy.linalg import matrix_power
# ──────────────────────────────────────────────────────────────────────────── #

class MarkovChain(np.ndarray):

    def __new__(cls, a):
        obj = np.asarray(a).view(cls)
        return obj

    def __init__(self, matrix: np.array):
        super().__init__()
        self.chain_size = self.shape[0]
        assert all(np.sum(self, 1) == 1)

    def iterate(self, mu: np.array, n: int= 1):
        """
        mu: probability distribution over the states of the markov chain

        returns the distribution in n steps
        """
        return np.matmul(mu, matrix_power(self, n))

    def convergence_iteration(self, mu: np.array, epsilon: float= 10e-9):
        mu_next = self.iterate(mu)
        while (mu_next != mu).any():
            mu = mu_next
            mu_next = self.iterate(mu)
        return mu_next
