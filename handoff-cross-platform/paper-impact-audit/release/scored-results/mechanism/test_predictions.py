"""Score the pre-registered farming predictions (written before the runs launched).

FARMER = final-10% train/pickups > 5 OR train/door_flips > 5 (door_flips logged on new nodes only).
Tests: logistic regression of farmer status on E = coef * F(g, gamma) over N1-N6 (slope > 0 predicted);
one-sided Fisher exact tests N2 < N1, N5 < N4, N6 > N3.
Usage: python test_predictions.py <out.json>
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import fisher_exact
import statsmodels.api as sm

RUNS = Path.home() / ".local/share/openresearch/local-runs"
NODES = {  # title prefix -> (E, predicted farmers [lo, hi])
    "N1": (0.764, (2, 8)), "N2": (0.281, (0, 2)), "N3": (0.593, (1, 4)),
    "N4": (0.764, (2, 8)), "N5": (0.382, (0, 1)), "N6": (0.870, (6, 10)),
    "Control: pay each event once": (None, (0, 0)),
}
CALIBRATION = {"6518a3c8-0446-45de-805c-5f5e8aa3258e": ("growth 1/640", 0.048),
               "6e507c3e-5837-4ef3-b6d9-05a7c3990468": ("growth 1/160", 0.368),
               "6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69": ("growth 1/40", 0.764)}

def seeds_of(run):
    out = []
    for f in sorted((RUNS / run / "repo/results").glob("seed*/metrics.jsonl")):
        rows = [json.loads(l) for l in open(f)]
        last = rows[-max(1, len(rows) // 10):]
        m = lambda k: float(np.mean([r.get(k, 0.0) for r in last]))
        s = json.loads((f.parent / "summary.json").read_text())
        out.append(dict(seed=int(f.parent.name[4:]), pickups=m("train/pickups"), door_flips=m("train/door_flips"),
                        success=m("train/success"), farmer=bool(m("train/pickups") > 5 or m("train/door_flips") > 5),
                        solved=s["first_solved_step"] is not None))
    return out

def main(runs_by_node, out_path):
    res, X, y = {}, [], []
    for name, run in runs_by_node.items():
        E, (lo, hi) = NODES[name]
        ss = seeds_of(run); k = sum(s["farmer"] for s in ss)
        res[name] = dict(run=run, E=E, predicted=[lo, hi], farmers=k, n=len(ss), within=lo <= k <= hi,
                         solved=sum(s["solved"] for s in ss), seeds=ss)
        if E is not None:
            X += [E] * len(ss); y += [s["farmer"] for s in ss]
    for run, (lab, E) in CALIBRATION.items():
        ss = seeds_of(run)
        res["calibration " + lab] = dict(run=run, E=E, farmers=sum(s["farmer"] for s in ss), n=len(ss), seeds=ss)
    fit = sm.Logit(np.array(y, float), sm.add_constant(np.array(X))).fit(disp=0)
    res["logistic"] = dict(slope=float(fit.params[1]), slope_ci=fit.conf_int()[1].tolist(),
                           p_one_sided=float(fit.pvalues[1] / 2 if fit.params[1] > 0 else 1 - fit.pvalues[1] / 2))
    def fisher(a, b, alt):  # is farm rate of a (alt) than b?
        A, B = res[a], res[b]
        t = [[A["farmers"], A["n"] - A["farmers"]], [B["farmers"], B["n"] - B["farmers"]]]
        return dict(table=t, p=float(fisher_exact(t, alternative=alt)[1]))
    res["fisher"] = {"N2 < N1": fisher("N2", "N1", "less"), "N5 < N4": fisher("N5", "N4", "less"),
                     "N6 > N3": fisher("N6", "N3", "greater")}
    Path(out_path).write_text(json.dumps(res, indent=2))
    for k, v in res.items():
        if "farmers" in v:
            pr = f"pred {v['predicted']} {'HIT' if v.get('within') else 'MISS'}" if "predicted" in v else "(calibration)"
            print(f"{k:34s} E={v['E']}  farmers {v['farmers']}/{v['n']}  {pr}  solved {v.get('solved','-')}")
    print("logistic slope", res["logistic"]); print("fisher", json.dumps(res["fisher"]))

if __name__ == "__main__":
    import subprocess, re
    txt = subprocess.run(["orx", "runs", "1afd0818-4752-445e-80b2-5e37e0cc6797"], capture_output=True, text=True).stdout
    runs = {}
    for line in txt.splitlines():
        m = re.match(r"^([0-9a-f-]{36})\s+done\s+(.*?)\s+[0-9a-f]{7}\s", line)
        if m:
            for name in NODES:
                if m[2].startswith(name) and name not in runs:
                    runs[name] = m[1]
    main(runs, sys.argv[1])
