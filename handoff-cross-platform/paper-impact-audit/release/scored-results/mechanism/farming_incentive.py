"""Farming incentive of the homeostatic reward, derived from the reward equation alone (no training).

r_t = D(h_t) - D(h_{t+1}),  D(h) = sum_k h_k^2.  Summing with discount gives, for an episode of T steps,
    G = D(h_0) - (1-gamma) * sum_{t=1}^{T-1} gamma^(t-1) D(h_t) - gamma^(T-1) D(h_T)
so the agent is paid for keeping a discounted *average* of its drive low. For one farmable need
(grasp: drop/pick-up; open: close/open door) with per-step growth g and full relief per event, compare:
    once:    relieve once at step 1 (what solving seeds do with the key), then the need climbs g per
             step and saturates at 1
    farm:    relieve every `period` steps (2 for drop -> pick-up), so h cycles 0, g, 0, g, ...
F(g, gamma) = discounted drive saved by farming instead of relieving once = the incentive to farm instead of exploring for the goal.
NOTE: this 'relieve once' baseline replaced a first 'never relieve' baseline after seeing the three
growth runs at gamma=0.99, so those runs are not evidence for F. Prediction (pre-registered for new runs): the fraction of seeds that farm rises with F, whatever (g, gamma) produced it.
"""
import json, sys
import numpy as np

def disc_drive(h, gamma):
    t = np.arange(1, len(h) - 1)  # h holds h_0..h_T
    return (1 - gamma) * np.sum(gamma ** (t - 1) * h[1:-1] ** 2) + gamma ** (len(h) - 2) * h[-1] ** 2

def need_path(g, T, h0, period=None):
    h, out = h0, [h0]
    for t in range(1, T + 1):
        h = min(1.0, h + g)
        if t == 1 or (period and t % period == 0):
            h = max(0.0, h - 1.0)
        out.append(h)
    return np.array(out)

def incentive(g, gamma, T=640, h0=0.5, period=2):
    return disc_drive(need_path(g, T, h0), gamma) - disc_drive(need_path(g, T, h0, period), gamma)

def g_for(F_target, gamma, lo=1e-4, hi=0.5):
    for _ in range(80):  # bisection; F increases with g
        mid = (lo * hi) ** 0.5
        lo, hi = (mid, hi) if incentive(mid, gamma) < F_target else (lo, mid)
    return (lo * hi) ** 0.5

def effective(g, gamma, coef=1.0):
    """Intrinsic return scales linearly with coef, so the temptation is coef * F."""
    return coef * incentive(g, gamma)


if __name__ == "__main__":
    rows = []
    for gamma in (0.95, 0.99, 0.995):
        for d in (640, 320, 160, 80, 60, 40, 20, 10):
            rows.append(dict(gamma=gamma, growth=f"1/{d}", g=1 / d, F=round(incentive(1 / d, gamma), 4)))
    for r in rows:
        print(f"gamma {r['gamma']:<6} growth {r['growth']:>6}  F = {r['F']:.4f}")
    if len(sys.argv) > 1:
        json.dump(rows, open(sys.argv[1], "w"), indent=2)
