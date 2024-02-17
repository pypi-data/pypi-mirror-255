import pytest
import torch as pt
from quadmoments.torch.quadmoments import quadmoments
from quadmoments.torch.baseline import baseline_nth_moment

EPS = 1e-4

@pytest.mark.parametrize("n, d", [(10, 10), (30, 2), (2, 100)])
def test_interface(n, d, test_samples=10000000):
    qform = pt.randn((d, d))
    qform = qform.T @ qform
    sigma = pt.randn((d, d))
    sigma = pt.tril(sigma) * 1e-6 + 1e-2 * pt.eye(d)
    sigma.requires_grad = True
    qform.requires_grad = True
    m = quadmoments(n, qform, ltrcovariance=sigma, flag="sym").flatten().tolist()
    m_b = baseline_nth_moment(n, pt.linalg.eigvals(qform @ sigma.T @ sigma).real)
    X = (sigma @ pt.randn((d, test_samples))).T
    m_emp = pt.matmul(X.unsqueeze(1), qform.unsqueeze(0)).matmul(X.unsqueeze(-1)).pow(pt.arange(n+1).unsqueeze(-1)).mean(dim=0).flatten().tolist()
    print(m)
    print(m_b)
    print(m_emp)
    assert all((abs(a-b) < EPS for a, b in zip(m, m_b)))
    assert all((abs(a-b) < EPS for a, b in zip(m, m_emp)))
    assert all((abs(a-b) < EPS for a, b in zip(m_emp, m_b)))

if __name__ == '__main__':
    test_interface(6, 100)
