from typing import Optional
import numpy as np
from scipy.linalg import solve_triangular
from quadmoments.error import QuadMomentsError

def __precision_to_scale_tril(P):
    """
    Private function from https://pytorch.org/docs/stable/_modules/torch/distributions/multivariate_normal.html#MultivariateNormal
    Please do not use, it is uggly copy paste code.
    """
    # Ref: https://nbviewer.jupyter.org/gist/fehiepsi/5ef8e09e61604f10607380467eb82006#Precision-to-scale_tril
    Lf = np.linalg.cholesky(P[::-1, ::-1])
    L_inv = Lf[::-1, ::-1]
    Id = np.eye(P.shape[-1])
    L = solve_triangular(L_inv, Id, lower=True, trans=1)
    return L

def decompose(
        quadform: np.ndarray,
        covariance: Optional[np.ndarray],
        diagcovariance: Optional[np.ndarray],
        ltrcovariance: Optional[np.ndarray],
        precision_matrix: Optional[np.ndarray],
        ) -> np.ndarray:
    if diagcovariance is not None:
        if ltrcovariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the cholesky factor of this matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Lower-triangular:\n{ltrcovariance}\nYou may need to chose between both.")
        elif covariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the full covariance matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Full:\n{covariance}\nYou may need to chose between both.")
        elif precision_matrix is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the full precision matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Precision matrix:\n{precision_matrix}\nYou may need to chose between both.")
        else:
            # We have the right format
            return handle_diagonal(quadform, diagcovariance)

    elif ltrcovariance is not None:
        if covariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a lower-triangular covariance (Cholesky factor), but the full covariance matrix has been provided as well.\n   Lower-triangular:\n{ltrcovariance}\n   Full:\n{covariance}\nYou may need to chose between both.")
        elif precision_matrix is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a lower-triangular covariance (Cholesky factor), but the full precision matrix has been provided as well.\n   Lower-triangular:\n{ltrcovariance}\n   Precision matrix:\n{precision_matrix}\nYou may need to chose between both.")
        else:
            # We have the right format
            return handle_ltr(quadform, ltrcovariance)
    elif covariance is not None:
        L = np.linalg.cholesky(covariance)
        return handle_ltr(quadform, L)
    elif precision_matrix is not None:
        L = __precision_to_scale_tril(precision_matrix)
        return handle_diagonal(quadform, L)
    else:
        raise QuadMomentsError("Please provide to the decomposition a matrix.")

def handle_diagonal(quadform: np.ndarray, diagcovariance: np.ndarray) -> np.ndarray:
    if diagcovariance.ndim != 1:
        raise QuadMomentsError(f"You have provided a diagonal covariance, but it does not have the tensor-dimension of a vector:\nDim diag(Sigma): {diagcovariance.ndim}")
    else:
        return np.diagonal(quadform) * diagcovariance

def handle_ltr(quadform: np.ndarray, ltrcovariance: np.ndarray) -> np.ndarray:
    if ltrcovariance.ndim == 1:
        L = np.zeros_like(quadform)
        L[*np.tril_indices(quadform.shape[0])] = ltrcovariance
        return np.linalg.eigvals(quadform @ L)
    elif ltrcovariance.ndim == 2:
        return np.linalg.eigvals(quadform @ ltrcovariance)
    else:
        raise QuadMomentsError(f"You have provided a lower-triangular covariance (Cholesky factor), but it does not have a compatible tensor-dimension:\nDim L: {ltrcovariance.ndim}")
