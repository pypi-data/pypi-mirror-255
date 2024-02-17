import pytest
import torch as pt
import matplotlib.pyplot as plt

from quadmoments.torch.quadmoments import moments
from quadmoments.torch.baseline import baseline_nth_moment

@pytest.mark.parametrize("n, d", [(10, 10), (2, 100), (30, 2)])
def test_samples(n, d, m=1000):
    print("\n### Gradients wrt the stdev:")
    print("############################\n")
    s = pt.ones(d).cuda() * 1e-2
    s.requires_grad = True
    dist = pt.distributions.MultivariateNormal(loc=pt.zeros(d).to(s), scale_tril=(s.sqrt()).diag())
    X = dist.rsample(pt.Size((m, )))
    emp_moment = pt.mean(pt.pow(X.mm(X.T).diag().unsqueeze(0), pt.arange(n+1).unsqueeze(-1).to(X)), dim=1)
    emp_moment[-1].backward()
    assert s.grad is not None
    print("Empirical:\n", s.grad.cpu().tolist())
    s.grad = None
    t_moment = moments(n, s)
    t_moment[-1].backward()
    assert s.grad is not None
    print("\nOur estimate:\n", s.grad.cpu().tolist())
    b_moment = baseline_nth_moment(n, s)
    print(f"\n### Estimates of {n} moments:")
    print("###########################")
    print(f"\nEmpirical from {m} random realisations of RV:")
    print(list(emp_moment.flatten().cpu().tolist()))
    print(f"\nOur algorithm:")
    print(list(t_moment.flatten().cpu().tolist()))
    print(f"\nBaseline from textbook:")
    print(b_moment)

if __name__ == '__main__':
    N = 6
    d = 5
    test_samples(N, d)
    plt.show()
