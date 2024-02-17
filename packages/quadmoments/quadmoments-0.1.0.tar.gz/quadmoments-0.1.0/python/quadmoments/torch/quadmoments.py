import numbers
from typing import Optional
import torch as pt
import numpy as np
from quadmoments.torch.decompose import decompose
from quadmoments.coefs import beta_coefs #.coefs import beta_coefs

from quadmoments.torch.quadform import QuadForm

def quadmoment(*args, **kwargs):
    return quadmoments(*args, **kwargs)[-1]

def quadmoments(
        n: numbers.Number,
        quadform: pt.Tensor,
        *,
        flag: str="",
        scalarcovariance: Optional[pt.Tensor]=None,
        covariance: Optional[pt.Tensor]=None,
        diagcovariance: Optional[pt.Tensor]=None,
        ltrcovariance: Optional[pt.Tensor]=None,
        precision_matrix: Optional[pt.Tensor]=None
        ):
    qform = QuadForm(quadform, flag)
    if isinstance(n, int):
        if n == 0:
            return pt.tensor([1.])
        elif n == 1:
            return decompose(qform, scalarcovariance, covariance, diagcovariance, ltrcovariance, precision_matrix)
        else:
            diag = decompose(qform, scalarcovariance, covariance, diagcovariance, ltrcovariance, precision_matrix)
            return moments(n, diag)
    else:
        raise NotImplementedError("Non-integer moments of gaussians are are not implemented.")

def lowtr_circulant(diag: pt.Tensor, dim: int=-1):
    r"""
    From a vector ``diag``, computes its flipped circular embedding with zeros
    above the diagonal.
    Can be batched in left dimension(s).
    
    ::math
        \lambda \to \begin{matrix}
            \lambda_1 &        &           & \\
            \lambda_2 & \ddots & 0         & \\
            \vdots    & \cdot  & \ddots    & \\
            \lambda_n & \dots  & \lambda_2 & \lambda_1 \\
        \end{matrix}
    """
    d = diag.shape[dim] # Dimension of the vector
    zero_padds = pt.zeros(d - 1).to(diag)
    return pt.cat([zero_padds, diag]).unfold(dim, d, 1).flip((-1,))

def alphas(n: int, diag: pt.Tensor):
    betas = beta_coefs(n).astype(np.float32)
    betas = pt.from_numpy(betas).to(diag)
    return lowtr_circulant(
            diag
                .unsqueeze(-1)
                .pow(
                    pt.arange(start=1, end=n, step=1)
                        .unsqueeze(0)
                        .to(diag)
                )
                .sum(0)
        ) * betas

def moments(n: int, diag: pt.Tensor):
    a_coefs = alphas(n+1, diag)
    d = a_coefs.device
    t = a_coefs.dtype
    system_matrix = pt.cat([pt.cat([pt.zeros(1, n, device=d, dtype=t), a_coefs], dim=0), pt.zeros(n+1, 1, device=d, dtype=t)], dim=1) - pt.eye(n+1, device=d, dtype=t)
    rhs = pt.zeros(n+1, 1, device=d, dtype=t)
    rhs[0, 0] = -1.
    moments = pt.linalg.solve_triangular(system_matrix, rhs, upper=False)
    return moments
