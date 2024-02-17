from math import comb
import torch as pt


def baseline_nth_moment(n: int, diag: pt.Tensor):
    moments = [1.] + ([0.]*n)
    for r in range(1, n+1):
        def g(k):
            trace = diag.pow(k+1).sum()
            return trace * comb(r-1, k) * 2**k
        moments[r] = sum(g(r-1-r_) * moments[r_] for r_ in range(r)).item()
    return moments
