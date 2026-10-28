"""Round 5, Step 0 (no training): round-4 tamper solver extended with a per-press tamper cost c.

Same small 7x5 DoorKey-style MDP, rewards and lattice as round3/value_iteration.py and round4/value_iteration_tamper.py.
The tamper action ("done") sets both modeled needs (grasp, open) to 0 with no growth that step and pays
D(h_t) - c: the cost is subtracted from the step's extrinsic reward and is not scaled by the intrinsic coefficient
(coef = 1 here). Explore need omitted, as in rounds 3-4. Growth 1/160 and 1/40, gamma 0.99, bin = g.
For each growth rate: a grid of c values, then bisection for the largest c at which the greedy optimal rollout from
the start state still tampers at least once. Usage: python value_iteration_tamper_cost.py <out.json>"""
import json, sys, time
from fractions import Fraction
from pathlib import Path
import numpy as np
import torch

torch.set_num_threads(12)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "round3"))
import value_iteration as v3  # noqa: E402

ACTIONS = v3.ACTIONS + ["tamper"]
B = v3.B

def build(g, m=1):
    spacing = Fraction(g) / m
    L = int(Fraction(1) / spacing) + 1
    lv = np.arange(L) * float(spacing); k = np.arange(L)
    shift = {e: np.clip(k + m - e * (L - 1), 0, L - 1) for e in (0, 1)}
    Dg = lv ** 2; Dfull = Dg[:, None] + Dg[None, :]
    R = {(eg, eo): Dfull - (Dg[shift[eg]][:, None] + Dg[shift[eo]][None, :]) for eg in (0, 1) for eo in (0, 1)}
    rows = {(a, eg, eo): np.where((v3.EG[:, a] == eg) & (v3.EO[:, a] == eo))[0]
            for a in range(len(v3.ACTIONS)) for eg in (0, 1) for eo in (0, 1)}
    return L, shift, Dfull, R, rows

def solve(model, gamma, c, tol=1e-7, max_iter=200000, V0=None, certify=False):
    """Value iteration in float64 torch (multi-threaded; same arithmetic as the numpy round-3/4 solvers).

    certify=True: stop early once the greedy rollout from the start state is provably the optimal one. With
    eps = gamma/(1-gamma) * max|V_k - V_{k-1}| bounding max|V_k - V*|, every Q-value is within gamma*eps of Q*;
    if at every step of the rollout the chosen action beats every alternative by more than 2*gamma*eps, the optimal
    policy takes exactly the same actions, so the rollout (outcome, steps, tamper count and timing) is exact."""
    L, shift, Dfull, R, rows = model
    T = lambda x: torch.as_tensor(x)
    sh = {e: T(shift[e]).long() for e in (0, 1)}
    R4 = torch.stack([T(R[(eg, eo)]) for eg in (0, 1) for eo in (0, 1)])            # (4, L, L)
    Df = T(Dfull)
    EG, EO, GL, NB = (T(v3.EG).long(), T(v3.EO).long(), T(v3.GL), T(v3.NB).long())
    V = torch.zeros((B, L, L), dtype=torch.float64)
    for it in range(max_iter):
        S4 = torch.stack([V.index_select(1, sh[eg]).index_select(2, sh[eo]) for eg in (0, 1) for eo in (0, 1)])
        best = Df[None] - c + gamma * V[:, 0, 0][:, None, None]                     # tamper
        for a in range(len(v3.ACTIONS)):
            e = EG[:, a] * 2 + EO[:, a]
            goal = GL[:, a].to(torch.float64)[:, None, None]
            Q = R4[e] + goal * 1.0 + (1.0 - goal) * gamma * S4[e, NB[:, a]]
            best = torch.maximum(best, Q)
        delta = float((best - V).abs().max()); V = best
        if delta < tol: break
        if certify and delta < 1e-3 and it % 20 == 0:
            eps = gamma / (1 - gamma) * delta
            if rollout(model, V.numpy(), gamma, c, margin=2 * gamma * eps).get("certified"):
                return V.numpy(), it + 1, delta
    return V.numpy(), it + 1, delta

def rollout(model, V, gamma, c, max_steps=10000, margin=None):
    """Greedy rollout from the start state. With `margin`, also reports whether every chosen action beat every
    alternative by more than `margin` (min_gap), i.e. whether the rollout is certified optimal."""
    L, shift, Dfull, R, rows = model
    b, kg, ko = v3.bidx[(v3.START, 0, v3.KEY0, v3.LOCKED)], (L - 1) // 2, (L - 1) // 2
    seen, acts, tsteps, min_gap = {}, [], [], np.inf
    for t in range(max_steps):
        key = (b, kg, ko)
        if key in seen:
            return dict(outcome="cycles", tampers=len(tsteps), tamper_steps=tsteps[:20], loop=acts[seen[key]:][:20],
                        min_gap=min_gap, certified=(margin is not None and min_gap > margin))
        seen[key] = t
        q = np.array(list(v3.q_values(V, shift, R, gamma, b, kg, ko)) + [Dfull[kg, ko] - c + gamma * V[b, 0, 0]])
        a = int(np.argmax(q)); acts.append(ACTIONS[a])
        min_gap = min(min_gap, float(q[a] - np.max(np.delete(q, a))))
        if a == len(v3.ACTIONS):
            tsteps.append(t); kg, ko = 0, 0; continue
        if v3.GL[b, a]:
            return dict(outcome="reaches goal", steps=t + 1, tampers=len(tsteps), tamper_steps=tsteps, actions=acts,
                        min_gap=min_gap, certified=(margin is not None and min_gap > margin))
        kg, ko, b = shift[v3.EG[b, a]][kg], shift[v3.EO[b, a]][ko], v3.NB[b, a]
    return dict(outcome="no goal within limit", tampers=len(tsteps))

if __name__ == "__main__":
    gamma, out = 0.99, {}
    plan = {Fraction(1, 40): ([0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0], 1e-4),
            Fraction(1, 160): ([0.0, 0.01, 0.1, 1.0], 2e-3)}   # 1/160 solves take ~10 min each when c > 0
    for g, (grid, prec) in plan.items():
        name = f"1/{g.denominator}"; model = build(g); res = []; t0 = time.time()
        for c in grid:
            V, its, d = solve(model, gamma, c)
            L = model[0]
            r = dict(c=c, iterations=its, final_delta=d,
                     V_start=float(V[v3.bidx[(v3.START, 0, v3.KEY0, v3.LOCKED)], (L - 1) // 2, (L - 1) // 2]),
                     **rollout(model, V, gamma, c)); r.pop("actions", None); res.append(r)
            print(name, json.dumps(r), flush=True)
        tam = [r["tampers"] > 0 for r in res]
        monotone = all(not (not a and b) for a, b in zip(tam, tam[1:]))  # once it stops tampering it never restarts
        lo = max((r["c"] for r in res if r["tampers"] > 0), default=None)
        hi = min((r["c"] for r in res if r["tampers"] == 0 and (lo is None or r["c"] > lo)), default=None)
        bis = []
        if lo is not None and hi is not None:
            a, b = lo, hi
            while b - a > prec:
                mid = (a + b) / 2
                V, its, d = solve(model, gamma, mid)
                r = rollout(model, V, gamma, mid); r.pop("actions", None); bis.append(dict(c=mid, iterations=its, **r))
                print(name, "bisect", json.dumps(dict(c=mid, outcome=r["outcome"], tampers=r["tampers"], iterations=its)), flush=True)
                if r["tampers"] > 0: a = mid
                else: b = mid
            lo, hi = a, b
        out[name] = dict(gamma=gamma, grid=res, bisection=bis, bisection_precision=prec, monotone_on_grid=monotone,
                         largest_c_still_tampers=lo, smallest_c_no_tamper=hi,
                         reaches_goal_at_every_c=all(r["outcome"] == "reaches goal" for r in res + bis),
                         seconds=round(time.time() - t0, 1))
        json.dump(out, open(sys.argv[1], "w"), indent=1)
    for k, v in out.items():
        print(k, "largest c with tamper:", v["largest_c_still_tampers"], "| smallest c without:", v["smallest_c_no_tamper"],
              "| reaches goal at every c:", v["reaches_goal_at_every_c"], "| monotone on grid:", v["monotone_on_grid"])
