from time import time
import torch as pt
import numpy as np
import matplotlib.pyplot as plt

from quadmoments.torch.quadmoments import moments
from quadmoments.numpy.quadmoments import moments as npmoments
from quadmoments.torch.baseline import baseline_nth_moment

def test_curves(it=100, n_max=10, d=3):
    moments(4, pt.zeros(2))#warmup
    our, nours, their = [], [], []
    snp = np.ones(d) * 1e-6
    s = pt.from_numpy(snp).cuda()
    ns = range(2, n_max)
    diffs1, diffs2 = [], []
    for n in ns:
        t0 = time()
        t_moment = moments(n, s)
        t = time() - t0
        our.append(t)
        t0 = time()
        n_moment = npmoments(n, snp)
        t = time() - t0
        nours.append(t)
        t0 = time()
        b_moment = baseline_nth_moment(n, s)
        t = time() - t0
        their.append(t)
        diffs1.append(np.max(np.abs(t_moment.cpu().numpy() - b_moment)))
        diffs2.append(np.max(np.abs(t_moment.cpu().numpy() - n_moment)))
    _, axes = plt.subplots(3, 1)
    axes[0].plot(ns, our, label="our")
    axes[0].plot(ns, their, label="their")
    axes[0].plot(ns, nours, label="numpy")
    axes[1].plot(list(map(lambda d: abs(d[1]-d[0]) / d[0], zip(our, their))))
    axes[2].plot(diffs1, label="torch vs theirs")
    axes[2].plot(diffs2, label="torch vs numpy")
    axes[0].legend()
    axes[2].legend()
    axes[0].set_yscale("log")
    # axes[2].set_yscale("log")

if __name__ == '__main__':
    iters = 100
    N = 50
    d = 5
    test_curves(iters, N, d)
    plt.show()
