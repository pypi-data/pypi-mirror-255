import numbers
from typing import Optional
import numpy as np
from scipy.linalg import solve_triangular, circulant
from quadmoments.numpy.decompose import decompose
from quadmoments.coefs import beta_coefs


def quadmoment(
        n: numbers.Number,
        quadform: np.ndarray,
        *,
        covariance: Optional[np.ndarray]=None,
        diagcovariance: Optional[np.ndarray]=None,
        ltrcovariance: Optional[np.ndarray]=None,
        precision_matrix: Optional[np.ndarray]=None
        ):
    if isinstance(n, int):
        if n == 0:
            return 1.
        elif n == 1:
            decompose(quadform, covariance, diagcovariance, ltrcovariance, precision_matrix).sum()
        else:
            diag = decompose(quadform, covariance, diagcovariance, ltrcovariance, precision_matrix)
            return moments(n, diag)[-1]
    else:
        raise

def alphas(n: int, diag: np.ndarray):
    betas = beta_coefs(n)
    return circulant(
            np.vander(diag, N=n, increasing=True)
                [:, 1:]
                .sum(0)
        ) * betas

def moments(n: int, diag: np.ndarray):
    a_coefs = alphas(n + 1, diag)
    system_matrix = np.block([[np.zeros([n+1, 1]).T], [a_coefs, np.zeros([1, n]).T]]) - np.eye(n+1)
    rhs = np.zeros([n+1, 1])
    rhs[0, 0] = -1.
    moments = solve_triangular(system_matrix, rhs, lower=True)
    return moments
