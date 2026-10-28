"""B0 (pre-registered): round-3 exact solver extended with the tamper action.

Reuses round3/value_iteration.py (layout, actions, rewards, lattice) unchanged and adds a 7th action, "done" as tamper:
the world is unchanged, both modeled needs (grasp, open) are set to 0 with no growth that step, and the reward is
D(h_t) - D(0) = D(h_t). Explore need omitted, as in round 3. Growth 1/160 and 1/40, gamma 0.99, bin = g;
halved-bin check at 1/40. Usage: python value_iteration_tamper.py <out.json>"""
import json, sys, time
from fractions import Fraction
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "round3"))
import value_iteration as v3  # noqa: E402

ACTIONS = v3.ACTIONS + ["tamper"]
B, A = v3.B, len(ACTIONS)

def solve(g, gamma, m=1, tol=1e-7, max_iter=200000):
    spacing = Fraction(g) / m
    L = int(Fraction(1) / spacing) + 1
    assert Fraction(1, 2) / spacing == int(Fraction(1, 2) / spacing)
    lv = np.arange(L) * float(spacing)
    k = np.arange(L)
    shift = {e: np.clip(k + m - e * (L - 1), 0, L - 1) for e in (0, 1)}
    Dg = lv ** 2
    Dfull = Dg[:, None] + Dg[None, :]
    R = {(eg, eo): Dfull - (Dg[shift[eg]][:, None] + Dg[shift[eo]][None, :]) for eg in (0, 1) for eo in (0, 1)}
    V = np.zeros((B, L, L)); t0 = time.time()
    for it in range(max_iter):
        S = {(eg, eo): V[:, shift[eg]][:, :, shift[eo]] for eg in (0, 1) for eo in (0, 1)}
        best = np.full((B, L, L), -np.inf)
        for a in range(len(v3.ACTIONS)):
            Q = np.empty((B, L, L))
            for eg in (0, 1):
                for eo in (0, 1):
                    rows = np.where((v3.EG[:, a] == eg) & (v3.EO[:, a] == eo))[0]
                    if len(rows) == 0: continue
                    cont = np.where(v3.GL[rows, a], 0.0, gamma)[:, None, None]
                    Q[rows] = R[(eg, eo)][None] + v3.GL[rows, a][:, None, None] * 1.0 + cont * S[(eg, eo)][v3.NB[rows, a]]
            np.maximum(best, Q, out=best)
        Qt = Dfull[None] + gamma * V[:, 0, 0][:, None, None]   # tamper: same base state, needs -> (0, 0)
        np.maximum(best, Qt, out=best)
        delta = np.abs(best - V).max(); V = best
        if delta < tol: break
    return V, shift, R, Dfull, L, it + 1, float(delta), time.time() - t0

def q_values(V, shift, R, Dfull, gamma, b, kg, ko):
    q = list(v3.q_values(V, shift, R, gamma, b, kg, ko))
    q.append(Dfull[kg, ko] + gamma * V[b, 0, 0])
    return np.array(q)

def rollout(V, shift, R, Dfull, L, gamma, max_steps=10000):
    b, kg, ko = v3.bidx[(v3.START, 0, v3.KEY0, v3.LOCKED)], (L - 1) // 2, (L - 1) // 2
    seen, acts, tamper_steps, pk, dc = {}, [], [], 0, 0
    for t in range(max_steps):
        key = (b, kg, ko)
        if key in seen:
            loop = acts[seen[key]:]
            return dict(outcome="cycles", steps_before_loop=seen[key], loop=loop[:40], tampers=len(tamper_steps),
                        tamper_steps=tamper_steps[:40], tampers_in_loop=loop.count("tamper"))
        seen[key] = t
        q = q_values(V, shift, R, Dfull, gamma, b, kg, ko)
        a = int(np.argmax(q)); acts.append(ACTIONS[a])
        if a == len(v3.ACTIONS):  # tamper
            tamper_steps.append(t); kg, ko = 0, 0; continue
        pk += int(v3.EG[b, a]); dc += int(v3.EO[b, a])
        if v3.GL[b, a]:
            return dict(outcome="reaches goal", steps=t + 1, actions=acts, tampers=len(tamper_steps),
                        tamper_steps=tamper_steps, pickups=pk, door_changes=dc)
        kg, ko, b = shift[v3.EG[b, a]][kg], shift[v3.EO[b, a]][ko], v3.NB[b, a]
    return dict(outcome="no goal within limit", tampers=len(tamper_steps))

if __name__ == "__main__":
    res = []
    for g, m in [(Fraction(1, 160), 1), (Fraction(1, 40), 1), (Fraction(1, 40), 2)]:
        V, shift, R, Dfull, L, its, delta, secs = solve(g, 0.99, m)
        b0 = v3.bidx[(v3.START, 0, v3.KEY0, v3.LOCKED)]
        r = dict(growth=f"1/{g.denominator}", gamma=0.99, bin=("g" if m == 1 else "g/2"), levels=L, iterations=its,
                 final_delta=delta, seconds=round(secs, 1), V_start=float(V[b0, (L - 1) // 2, (L - 1) // 2]),
                 **rollout(V, shift, R, Dfull, L, 0.99))
        print(json.dumps({k: v for k, v in r.items() if k != "actions"}), flush=True)
        res.append(r)
        json.dump(res, open(sys.argv[1], "w"), indent=1)
