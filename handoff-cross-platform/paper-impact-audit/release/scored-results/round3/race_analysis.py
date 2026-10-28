"""Step 1 (pre-registered): race between first goal and farming lock-in, on existing Agent 3 logs.
Definitions are in preregistration.md (sha256 b5e845c9...). Usage: python race_analysis.py <out.json>"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
import statsmodels.api as sm

RUNS = Path.home() / ".local/share/openresearch/local-runs"
POP = {  # setting -> run id (90 seeds)
    "cal 1/640": "6518a3c8-0446-45de-805c-5f5e8aa3258e", "cal 1/160": "6e507c3e-5837-4ef3-b6d9-05a7c3990468",
    "cal 1/40": "6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69", "N1 1/40": "ed5147b6-c861-48b2-b9ff-1952774d5658",
    "N2 1/40 g.95": "74b2b2d0-7f04-48ec-a1f8-6d78af326fd2", "N3 1/80": "af4373da-8be6-4a69-aa61-404ce37103d1",
    "N4 1/80 c1.29": "b58ec6e0-291c-47a2-838b-57783d35214f", "N5 1/40 c.5": "eb8555bd-afbf-484d-b1fc-30faa29648b6",
    "N6 1/20": "bced806e-eccb-434b-be50-ad91f57a9dfb",
}
G40 = {"cal 1/40", "N1 1/40", "N2 1/40 g.95", "N5 1/40 c.5"}
W = 20480

def over(r):
    return r.get("train/pickups", 0) > 5 or r.get("train/door_flips", 0) > 5

def categorize(rows):
    last = rows[-max(1, len(rows) // 10):]
    m = lambda k: float(np.mean([r.get(k, 0.0) for r in last]))
    rep = m("train/pickups") > 5 or m("train/door_flips") > 5
    if m("train/success") >= 0.9:
        return "solve", rep
    if rep:
        return "cycle-farm", rep
    med = [r["train/len_median"] for r in last if "train/len_median" in r]
    prolong = (np.median(med) >= 640) if med else (m("train/len") >= 600)  # old runs: mean-length proxy
    return ("prolong" if prolong else "fail"), rep

seeds = []
for setting, run in POP.items():
    for f in sorted((RUNS / run / "repo/results").glob("seed*/metrics.jsonl"), key=lambda p: int(p.parent.name[4:])):
        rows = [json.loads(l) for l in open(f)]
        fg = next((r["global_step"] for r in rows if r.get("train/success", 0) > 0), None)
        lock = None
        for i in range(len(rows)):
            if all(over(r) for r in rows[i:]):
                lock = rows[i]["global_step"]; break
        cat, rep = categorize(rows)
        if fg is not None and lock is not None and fg == lock:
            order = "undetermined"
        elif lock is not None and (fg is None or lock < fg):
            order = "lock-in first"
        elif fg is not None and (lock is None or fg < lock):
            order = "goal first"
        else:
            order = "neither"
        seeds.append(dict(setting=setting, seed=int(f.parent.name[4:]), first_goal=fg, lock_in=lock,
                          order=order, category=cat, solver_over_repeat=(cat == "solve" and rep),
                          first_row_step=rows[0]["global_step"], first_row_with_success_key=next(
                              (r["global_step"] for r in rows if "train/success" in r), None)))

res = dict(window_steps=W, seeds=seeds)
farm = [s for s in seeds if s["category"] == "cycle-farm"]
farm_goal = [s for s in farm if s["first_goal"] is not None]
solv = [s for s in seeds if s["category"] == "solve"]
def share(pop, want):
    und = sum(s["order"] == "undetermined" for s in pop)
    k = sum(s["order"] == want for s in pop)
    n = len(pop)
    return dict(n=n, k=k, share=k / n if n else None, undetermined=und,
                undetermined_share=und / n if n else None,
                resolvable=(n > 0 and und / n <= 0.25),
                p_binom_gt_half=binomtest(k, n, 0.5, alternative="greater").pvalue if n else None)
res["P1"] = share(farm_goal, "lock-in first"); res["P1"]["farmers_never_reached_goal"] = len(farm) - len(farm_goal)
res["P2"] = share(solv, "goal first")
g40 = [s for s in seeds if s["setting"] in G40]
fgw = [s["first_goal"] if s["first_goal"] is not None else 2_000_000 for s in g40]
res["P3"] = dict(n=len(g40), distinct_first_goal_windows=len(set(fgw)))
if len(set(fgw)) >= 3:
    y = np.array([s["category"] != "cycle-farm" for s in g40], float)
    x = np.array(fgw) / 1e5
    try:
        fit = sm.Logit(y, sm.add_constant(x)).fit(disp=0)
        b, p = float(fit.params[1]), float(fit.pvalues[1])
        res["P3"].update(slope=b, slope_ci=fit.conf_int()[1].tolist(), p_one_sided=(p / 2 if b < 0 else 1 - p / 2))
    except Exception as e:  # e.g. perfect separation
        res["P3"].update(error=repr(e))
    res["P3"]["resolvable"] = True
else:
    res["P3"]["resolvable"] = False
tab = {}
for s in seeds:
    if s["category"] in ("cycle-farm", "solve"):
        tab.setdefault(s["category"], {}).setdefault(s["order"], 0)
        tab[s["category"]][s["order"]] += 1
res["table_2x2"] = tab
res["category_counts"] = {c: sum(s["category"] == c for s in seeds) for c in ("solve", "cycle-farm", "prolong", "fail")}
Path(sys.argv[1]).write_text(json.dumps(res, indent=2, default=float))
for s in seeds:
    print(f"{s['setting']:14s} seed {s['seed']:2d}  first-goal {str(s['first_goal']):>8s}  lock-in {str(s['lock_in']):>8s}  {s['order']:14s} {s['category']}")
for k in ("P1", "P2", "P3", "table_2x2", "category_counts"):
    print(k, json.dumps(res[k], default=float))
