from typing import Optional
import torch as pt
from quadmoments.error import QuadMomentsError
from quadmoments.torch.quadform import QuadForm

def decompose(
        qform: QuadForm,
        scalarcovariance: Optional[pt.Tensor],
        covariance: Optional[pt.Tensor],
        diagcovariance: Optional[pt.Tensor],
        ltrcovariance: Optional[pt.Tensor],
        precision_matrix: Optional[pt.Tensor],
        ) -> pt.Tensor:
    if scalarcovariance is not None:
        if diagcovariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a scalar covariance, but the diagonal of a covariance matrix has been provided as well.\n   sigma:\n{scalarcovariance}\n    Diagonal:\n{diagcovariance}\nYou may need to chose between both.")
        elif ltrcovariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a scalar covariance, but the cholesky factor of a covariance matrix has been provided as well.\n   sigma:\n{scalarcovariance}\n   Lower-triangular:\n{ltrcovariance}\nYou may need to chose between both.")
        elif covariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a scalar covariance, but the full covariance matrix has been provided as well.\n   sigma:\n{scalarcovariance}\n   Full:\n{covariance}\nYou may need to chose between both.")
        elif precision_matrix is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a scalar covariance, but the full precision matrix has been provided as well.\n   sigma:\n{scalarcovariance}\n   Precision matrix:\n{precision_matrix}\nYou may need to chose between both.")
        else:
            # We have the right format
            return handle_scalar(qform, scalarcovariance)

    elif diagcovariance is not None:
        if ltrcovariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the cholesky factor of this matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Lower-triangular:\n{ltrcovariance}\nYou may need to chose between both.")
        elif covariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the full covariance matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Full:\n{covariance}\nYou may need to chose between both.")
        elif precision_matrix is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a diagonal covariance, but the full precision matrix has been provided as well.\n   Diagonal:\n{diagcovariance}\n   Precision matrix:\n{precision_matrix}\nYou may need to chose between both.")
        else:
            # We have the right format
            return handle_diagonal(qform, diagcovariance)

    elif ltrcovariance is not None:
        if covariance is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a lower-triangular covariance (Cholesky factor), but the full covariance matrix has been provided as well.\n   Lower-triangular:\n{ltrcovariance}\n   Full:\n{covariance}\nYou may need to chose between both.")
        elif precision_matrix is not None:
            raise QuadMomentsError(f"The covariance for the moments has been defined as a lower-triangular covariance (Cholesky factor), but the full precision matrix has been provided as well.\n   Lower-triangular:\n{ltrcovariance}\n   Precision matrix:\n{precision_matrix}\nYou may need to chose between both.")
        else:
            # We have the right format
            return handle_ltr(qform, ltrcovariance)
    elif covariance is not None:
        L, _ = pt.linalg.cholesky_ex(covariance)
        return handle_ltr(qform, L)
    elif precision_matrix is not None:
        L = pt.distributions.multivariate_normal._precision_to_scale_tril(precision_matrix)
        return handle_ltr(qform, L)
    else:
        raise QuadMomentsError("Please provide to the decomposition a matrix.")

def handle_scalar(qform: QuadForm, sigma: pt.Tensor) -> pt.Tensor:
    if sigma.dim() != 0 and (sigma.dim() != 1 or len(sigma) != 1):
        raise QuadMomentsError(f"You have provided a scalar covariance, but it dot not have the tensor dimension of a scalar:\nShape: {sigma.shape}")
    else:
        return sigma * qform.get_eigv()

def handle_diagonal(qform: QuadForm, diagcovariance: pt.Tensor) -> pt.Tensor:
    if diagcovariance.dim() != 1:
        raise QuadMomentsError(f"You have provided a diagonal covariance, but it does not have the tensor-dimension of a vector:\nDim diag(Sigma): {diagcovariance.dim()}")
    else:
        return qform.get_eigv_from_sqrt(diagcovariance.diag().sqrt())

def handle_ltr(qform: QuadForm, ltrcovariance: pt.Tensor) -> pt.Tensor:
    if ltrcovariance.dim() == 1:
        L = pt.zeros([qform.shape[0], qform.shape[1]])
        L[*pt.tril_indices(row=qform.shape[0], col=qform.shape[1], offset=0)] = ltrcovariance
        return qform.get_eigv_from_sqrt(L)
    elif ltrcovariance.dim() == 2:
        return qform.get_eigv_from_sqrt(ltrcovariance)
    else:
        raise QuadMomentsError(f"You have provided a lower-triangular covariance (Cholesky factor), but it does not have a compatible tensor-dimension:\nDim L: {ltrcovariance.dim()}")
