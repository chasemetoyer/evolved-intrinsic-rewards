"""Step 2 (pre-registered): exact optimal policy of the Agent 3 reward on a small DoorKey-style grid.

Layout 7x5 incl. walls: left room x in {1,2}, wall x=3 with locked door at (3,2), right room x in {4,5}, y in 1..3.
Agent starts (1,1) facing east; key at (2,3); goal at (5,3). Actions: left, right, forward, pickup, drop, toggle.
Needs (grasp, open) on a lattice of spacing g/m (m=1: bin = g; m=2: halved). Explore need omitted.
r = 1[goal] + D(h_t) - D(h_{t+1}),  D = h_grasp^2 + h_open^2,  h <- clip(h + g - 1*event, 0, 1), coef 1.
Infinite horizon, discounted; goal is terminal. Value iteration to max|dV| < 1e-7.
Usage: python value_iteration.py <out.json> [quick]
"""
import json, sys, time
from fractions import Fraction
import numpy as np

W, H = 7, 5
DOOR, GOAL, START, KEY0 = (3, 2), (5, 3), (1, 1), (2, 3)
FLOOR = [(x, y) for x in (1, 2, 4, 5) for y in (1, 2, 3) if (x, y) != GOAL]  # 11 cells
POS = FLOOR + [DOOR]
KEYPOS = FLOOR + ["carried"]
DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # east, south, west, north
ACTIONS = ["left", "right", "forward", "pickup", "drop", "toggle"]
LOCKED, CLOSED, OPEN = 0, 1, 2

base = [(p, d, k, ds) for p in POS for d in range(4) for k in KEYPOS for ds in (LOCKED, CLOSED, OPEN)
        if k != p and not (p == DOOR and ds != OPEN)]
bidx = {s: i for i, s in enumerate(base)}
B, A = len(base), len(ACTIONS)

def step(s, a):
    """-> (next base state or None if goal, grasp_event, open_event)"""
    p, d, k, ds = s
    f = (p[0] + DIRS[d][0], p[1] + DIRS[d][1])
    if a == 0: return (p, (d - 1) % 4, k, ds), 0, 0
    if a == 1: return (p, (d + 1) % 4, k, ds), 0, 0
    if a == 2:
        if f == GOAL: return None, 0, 0
        if f == DOOR: return ((f, d, k, ds) if ds == OPEN else s), 0, 0
        if f in FLOOR and k != f: return (f, d, k, ds), 0, 0
        return s, 0, 0
    if a == 3:
        if k == f: return (p, d, "carried", ds), 1, 0
        return s, 0, 0
    if a == 4:
        if k == "carried" and f in FLOOR: return (p, d, f, ds), 0, 0
        return s, 0, 0
    if a == 5:
        if f == DOOR:
            if ds == LOCKED and k == "carried": return (p, d, k, OPEN), 0, 1
            if ds == CLOSED: return (p, d, k, OPEN), 0, 1
            if ds == OPEN: return (p, d, k, CLOSED), 0, 1
        return s, 0, 0

NB = np.zeros((B, A), np.int64); EG = np.zeros((B, A), np.int64); EO = np.zeros((B, A), np.int64); GL = np.zeros((B, A), bool)
for i, s in enumerate(base):
    for a in range(A):
        nb, eg, eo = step(s, a)
        GL[i, a] = nb is None; NB[i, a] = 0 if nb is None else bidx[nb]; EG[i, a] = eg; EO[i, a] = eo

def solve(g, gamma, m=1, tol=1e-7, max_iter=200000):
    spacing = Fraction(g) / m
    L = int(Fraction(1) / spacing) + 1
    assert Fraction(1, 2) / spacing == int(Fraction(1, 2) / spacing), "0.5 must be on the lattice"
    s = float(spacing); lv = np.arange(L) * s
    def nxt(k, ev):  # lattice index after growth and relief
        return np.clip(k + m - ev * (L - 1), 0, L - 1)
    k = np.arange(L)
    shift = {e: nxt(k, e) for e in (0, 1)}
    Dg = lv ** 2
    # need reward for each (eg, eo): R[kg, ko] = D(h) - D(h')
    R = {(eg, eo): (Dg[:, None] + Dg[None, :]) - (Dg[shift[eg]][:, None] + Dg[shift[eo]][None, :])
         for eg in (0, 1) for eo in (0, 1)}
    V = np.zeros((B, L, L))
    t0 = time.time()
    for it in range(max_iter):
        S = {(eg, eo): V[:, shift[eg]][:, :, shift[eo]] for eg in (0, 1) for eo in (0, 1)}
        best = np.full((B, L, L), -np.inf)
        for a in range(A):
            Q = np.empty((B, L, L))
            for eg in (0, 1):
                for eo in (0, 1):
                    rows = np.where((EG[:, a] == eg) & (EO[:, a] == eo))[0]
                    if len(rows) == 0: continue
                    cont = np.where(GL[rows, a], 0.0, gamma)[:, None, None]
                    Q[rows] = R[(eg, eo)][None] + GL[rows, a][:, None, None] * 1.0 + cont * S[(eg, eo)][NB[rows, a]]
            np.maximum(best, Q, out=best)
        delta = np.abs(best - V).max(); V = best
        if delta < tol: break
    return V, shift, R, L, it + 1, delta, time.time() - t0

def q_values(V, shift, R, gamma, b, kg, ko):
    q = []
    for a in range(A):
        eg, eo = EG[b, a], EO[b, a]
        r = R[(eg, eo)][kg, ko] + (1.0 if GL[b, a] else 0.0)
        q.append(r if GL[b, a] else r + gamma * V[NB[b, a], shift[eg][kg], shift[eo][ko]])
    return np.array(q)

def rollout(V, shift, R, L, gamma, max_steps=10000):
    b, kg, ko = bidx[(START, 0, KEY0, LOCKED)], (L - 1) // 2, (L - 1) // 2
    seen, trace, events = {}, [], dict(pickups=0, door_changes=0)
    for t in range(max_steps):
        key = (b, kg, ko)
        if key in seen:  # deterministic loop
            loop = trace[seen[key]:]
            return dict(outcome="cycles", steps_before_loop=seen[key], loop_len=len(loop),
                        loop_pickups=sum(x[1] == "pickup" and x[2] for x in loop),
                        loop_door_changes=sum(x[1] == "toggle" and x[2] for x in loop),
                        loop_actions=[x[1] for x in loop][:40], **events)
        seen[key] = t
        q = q_values(V, shift, R, gamma, b, kg, ko)
        a = int(np.argmax(q))  # ties -> first action in ACTIONS order
        ev = bool(EG[b, a] or EO[b, a])
        trace.append((key, ACTIONS[a], ev))
        events["pickups"] += int(EG[b, a]); events["door_changes"] += int(EO[b, a])
        if GL[b, a]:
            return dict(outcome="reaches goal", steps=t + 1, actions=[x[1] for x in trace], **events)
        kg, ko, b = shift[EG[b, a]][kg], shift[EO[b, a]][ko], NB[b, a]
    return dict(outcome="no goal within limit", **events)

if __name__ == "__main__":
    out, quick = sys.argv[1], len(sys.argv) > 2
    main = [Fraction(1, 80), Fraction(1, 40), Fraction(1, 20)]
    sweep = [Fraction(1, d) for d in (160, 80, 60, 40, 30, 20, 10, 6, 4, 2)]
    jobs = [(g, gm, m) for g in main for gm in (0.99, 0.95) for m in (1, 2)]
    jobs += [(g, gm, 1) for g in sweep for gm in (0.99, 0.95) if g not in main]
    if quick: jobs = [(Fraction(1, 20), 0.95, 1)]
    res = []
    for g, gm, m in jobs:
        V, shift, R, L, its, delta, secs = solve(g, gm, m)
        r = dict(growth=f"1/{g.denominator}", gamma=gm, bin=("g" if m == 1 else "g/2"), levels=L,
                 iterations=its, final_delta=float(delta), seconds=round(secs, 1),
                 V_start=float(V[bidx[(START, 0, KEY0, LOCKED)], (L - 1) // 2, (L - 1) // 2]),
                 **rollout(V, shift, R, L, gm))
        print(json.dumps({k: v for k, v in r.items() if k != "actions"}), flush=True)
        res.append(r)
        json.dump(res, open(out, "w"), indent=1)
