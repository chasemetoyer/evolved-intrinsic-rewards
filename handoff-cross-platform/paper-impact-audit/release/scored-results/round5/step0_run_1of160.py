"""Step 0, growth 1/160: grid c in {0, 0.01, 0.1, 1.0} (the Part B costs) and bisection to 0.002 for the largest c at which
the optimal policy still tampers. Uses the certified early stop (validated against full convergence on all 21 growth-1/40
cases, step0-1of40-full-convergence.json). Merges the full-convergence 1/40 results into step0-tamper-cost.json."""
import json, sys, time
from fractions import Fraction
from pathlib import Path
here = Path(__file__).parent
sys.path.insert(0, str(here)); import value_iteration_tamper_cost as vc

gamma, model = 0.99, vc.build(Fraction(1, 160)); L = model[0]
b0 = vc.v3.bidx[(vc.v3.START, 0, vc.v3.KEY0, vc.v3.LOCKED)]
def one(c):
    t0 = time.time(); V, its, d = vc.solve(model, gamma, c, certify=True)
    r = vc.rollout(model, V, gamma, c, margin=2 * gamma * gamma / (1 - gamma) * d)
    r.pop("actions", None); r.pop("loop", None)
    r.update(c=c, iterations=its, final_delta=d, V_start=float(V[b0, (L - 1) // 2, (L - 1) // 2]), seconds=round(time.time() - t0, 1))
    print("1/160", json.dumps(r), flush=True); return r
grid = [one(c) for c in (0.0, 0.01, 0.1, 1.0)]
lo = max((r["c"] for r in grid if r["tampers"] > 0), default=None)
hi = min((r["c"] for r in grid if r["tampers"] == 0 and (lo is None or r["c"] > lo)), default=None)
bis = []
if lo is not None and hi is not None:
    while hi - lo > 2e-3:
        mid = (lo + hi) / 2; r = one(mid); bis.append(r)
        if r["tampers"] > 0: lo = mid
        else: hi = mid
full40 = json.loads((here / "step0-1of40-full-convergence.json").read_text())
tam = [r["tampers"] > 0 for r in grid]
full40["1/160"] = dict(gamma=gamma, grid=grid, bisection=bis, bisection_precision=2e-3, method="certified early stop",
                       monotone_on_grid=all(not (not a and b) for a, b in zip(tam, tam[1:])),
                       largest_c_still_tampers=lo, smallest_c_no_tamper=hi,
                       reaches_goal_at_every_c=all(r["outcome"] == "reaches goal" for r in grid + bis),
                       all_certified=all(r.get("certified") or r["final_delta"] < 1e-7 for r in grid + bis))
full40["1/40"]["method"] = "full convergence (max |dV| < 1e-7)"
(here / "step0-tamper-cost.json").write_text(json.dumps(full40, indent=1))
for k, v in full40.items():
    print(k, "largest c still tampering:", v["largest_c_still_tampers"], "| smallest c without:", v["smallest_c_no_tamper"],
          "| reaches goal at every c:", v["reaches_goal_at_every_c"], "|", v["method"])
