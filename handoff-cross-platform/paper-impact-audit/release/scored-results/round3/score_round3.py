"""Step 3/4 scoring, exactly as pre-registered (preregistration.md, sha256 b5e845c9...).
Categories per seed on the final 10% of training: solve > cycle-farm > prolong > fail.
Also re-scores all earlier runs under the same categories (EXPLORATORY; old runs use the mean-length proxy
for prolong and pick-ups only where door_flips was not logged). Usage: python score_round3.py <out.json>"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.stats import beta, fisher_exact
import statsmodels.api as sm

P = "1afd0818-4752-445e-80b2-5e37e0cc6797"
RUNS = Path.home() / ".local/share/openresearch/local-runs"

def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return [float(lo), float(hi)]

def categorize(f):
    rows = [json.loads(l) for l in open(f)]
    last = rows[-max(1, len(rows) // 10):]
    m = lambda k: float(np.mean([r.get(k, 0.0) for r in last]))
    rep = m("train/pickups") > 5 or m("train/door_flips") > 5
    if m("train/success") >= 0.9:
        return "solve", rep, "median"
    if rep:
        return "cycle-farm", rep, "median"
    med = [r["train/len_median"] for r in last if "train/len_median" in r]
    if med:
        return ("prolong" if np.median(med) >= 640 else "fail"), rep, "median"
    return ("prolong" if m("train/len") >= 600 else "fail"), rep, "mean-proxy"

def run_table():
    txt = subprocess.run(["orx", "runs", P], capture_output=True, text=True).stdout
    out = []
    for line in txt.splitlines():
        mm = re.match(r"^([0-9a-f-]{36})\s+done\s+(.*?)\s+[0-9a-f]{7}\s", line)
        if mm:
            out.append((mm[1], mm[2]))
    return out[::-1]

def score(run):
    cats = [categorize(f) for f in sorted((RUNS / run / "repo/results").glob("seed*/metrics.jsonl"))]
    n = len(cats)
    c = {k: sum(x[0] == k for x in cats) for k in ("solve", "cycle-farm", "prolong", "fail")}
    return dict(n=n, counts=c, ci={k: cp(v, n) for k, v in c.items()},
                solvers_over_repeat=sum(x[0] == "solve" and x[1] for x in cats),
                prolong_basis=sorted({x[2] for x in cats}), per_seed=[x[0] for x in cats])

def main(out):
    runs = run_table()
    byt = {t: r for r, t in runs}
    R = {}
    for t, r in byt.items():
        mm = re.match(r"^(R\d+):", t)
        if mm:
            R[mm[1]] = dict(title=t, run=r, **score(r))
    res = dict(round3=R)
    pred = {"R1": (6, 1, 10), "R2": (16, 12, 20), "R3": (8, 3, 13), "R4": (11, 6, 16), "R5": (13, 8, 18),
            "R6": (4, 0, 9), "R7": (10, 5, 15), "R8": (16, 11, 20), "R9": (2, 0, 4), "R10": (0, 0, 1)}
    rows = []
    def farm(k): return R[k]["counts"]["cycle-farm"]
    def fisher(a, b, alt):
        t = [[farm(a), R[a]["n"] - farm(a)], [farm(b), R[b]["n"] - farm(b)]]
        return float(fisher_exact(t, alternative=alt)[1])
    for k, (e, lo, hi) in pred.items():
        if k not in R: continue
        rows.append(dict(prediction=f"{k} cycle-farm", expected=e, range=[lo, hi], observed=farm(k), n=R[k]["n"],
                         ci=R[k]["ci"]["cycle-farm"], hit=lo <= farm(k) <= hi))
    tests = {}
    if {"R1", "R4"} <= R.keys(): tests["R1 < R4 (Fisher, one-sided)"] = fisher("R1", "R4", "less")
    if {"R2", "R4"} <= R.keys(): tests["R2 > R4 (Fisher, one-sided)"] = fisher("R2", "R4", "greater")
    if {"R8", "R6"} <= R.keys(): tests["R8 > R6 (Fisher, one-sided)"] = fisher("R8", "R6", "greater")
    if {"R9", "R4"} <= R.keys(): tests["R9 < R4 (Fisher, one-sided)"] = fisher("R9", "R4", "less")
    grid = {"R3": (0.5, 1), "R4": (1, 1), "R5": (2, 1), "R6": (0.5, 0), "R7": (1, 0), "R8": (2, 0)}
    if grid.keys() <= R.keys():
        X, y = [], []
        for k, (coef, norm) in grid.items():
            lc = np.log2(coef)
            for c in R[k]["per_seed"]:
                X.append([lc, norm, lc * norm]); y.append(c == "cycle-farm")
        try:
            fit = sm.Logit(np.array(y, float), sm.add_constant(np.array(X))).fit(disp=0)
            b, p = fit.params, fit.pvalues
            tests["logistic b1 (log2 coef) > 0"] = dict(b=float(b[1]), ci=fit.conf_int()[1].tolist(),
                                                       p_one_sided=float(p[1] / 2 if b[1] > 0 else 1 - p[1] / 2))
            tests["logistic b3 (log2 coef x norm_on) < 0"] = dict(b=float(b[3]), ci=fit.conf_int()[3].tolist(),
                                                                p_one_sided=float(p[3] / 2 if b[3] < 0 else 1 - p[3] / 2))
            tests["logistic b2 (norm_on)"] = dict(b=float(b[2]), ci=fit.conf_int()[2].tolist())
        except Exception as e:
            tests["logistic"] = dict(error=repr(e))
    if "R10" in R:
        c = R["R10"]["counts"]
        rows += [dict(prediction="R10 prolong", expected=0, range=[0, 1], observed=c["prolong"], n=R["R10"]["n"],
                      ci=R["R10"]["ci"]["prolong"], hit=c["prolong"] <= 1),
                 dict(prediction="R10 solve", expected=17, range=[12, 20], observed=c["solve"], n=R["R10"]["n"],
                      ci=R["R10"]["ci"]["solve"], hit=12 <= c["solve"] <= 20)]
    res["prediction_rows"], res["tests"] = rows, tests
    res["exploratory_rescore"] = {t: score(r) for r, t in runs if not re.match(r"^R\d+:", t)}
    Path(out).write_text(json.dumps(res, indent=2, default=float))
    for r in rows:
        print(f"{r['prediction']:18s} exp {r['expected']:>2} {r['range']}  obs {r['observed']}/{r['n']}  CI {np.round(r['ci'],2).tolist()}  {'HIT' if r['hit'] else 'MISS'}")
    print(json.dumps(tests, indent=1, default=float))

if __name__ == "__main__":
    main(sys.argv[1])
