import torch as pt
from dataclasses import dataclass

@dataclass
class QuadForm:
    data: pt.Tensor
    flag: str

    def get_eigv(self) -> pt.Tensor:
        if self.flag == 'sym':
            return pt.linalg.eigvalsh(self.data)
        elif self.flag == 'diag':
            return self.data
        else:
            return pt.linalg.eigvals(self.data)

    def get_eigv_from_sqrt(self, cb: pt.Tensor) -> pt.Tensor:
        if self.flag == 'sym':
            return pt.linalg.eigvalsh(cb.T @ self.data @ cb)
        elif self.flag == 'diag':
            return pt.linalg.eigvalsh(cb.T @ (self.data.unsqueeze(-1) * cb))
        else:
            return pt.linalg.eigvals(self.data @ cb.T @ cb)

    def get_eigv_from_full(self, factor: pt.Tensor) -> pt.Tensor:
        if self.flag == 'diag':
            return pt.linalg.eigvals(self.data.unsqueeze(-1) @ factor)
        else:
            return pt.linalg.eigvals(self.data @ factor)

    @property
    def shape(self):
        if self.flag == 'diag':
            return self.data.shape[0], self.data.shape[0]
        else:
            return self.data.shape[0], self.data.shape[1]

