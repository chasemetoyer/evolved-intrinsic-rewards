"""Round 5, Part D (pre-registered; run only after preregistration.md is locked): analyses of round-4 logs.

Tamper-on runs B1-B4 and their matched tamper-off runs (B1:A1b, B2:B7, B3:B5, B4:B6), seeds 40-59.
D1: exact first-goal step (summary.json), classification (never found / found then lost / kept solving) and a
    'declined' flag: peak rolling success (max train/success over rows from the first-goal row on) >= 0.10 and
    final-10% mean success <= 0.5 x peak.
D2: policy entropy (logged per row): final-10% mean per seed; tamper-on vs matched tamper-off, one-sided MWU (H1: on > off).
D3: done fraction per row = train/tampers / train/len (both are means over the same last 100 episodes, so the ratio is
    the exact share of those episodes' steps spent on 'done'). Rise row = first row with done fraction >= 1/7 + 0.05.
    Decline row = first row after the peak-success row with success <= 0.5 x peak (peak >= 0.10). Order: rise first if
    rise row + 3 <= decline row; decline first if decline row + 3 <= rise row; otherwise undetermined (the 100-episode
    rolling window spans about 3 rows). Prediction scored only if resolvable (see preregistration.md).
Usage: python part_d_analysis.py <out.json>"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest, mannwhitneyu, permutation_test

RUNS = Path.home() / ".local/share/openresearch/local-runs"
ON = {"B1": "bb00e7e5-65d0-4411-a236-2dacc19f0e63", "B2": "a8f5efc4-63e7-4a55-8020-08f7e7cff7bb",
      "B3": "78c44406-6e63-466f-b309-8dfb82bfe663", "B4": "f0a40d20-3702-4087-803c-8db52fefaf1e"}
OFF = {"A1b": "3629f9a7-8038-452a-bbef-53d5685e0a85", "B7": "115c6566-d1b2-4ea2-9c6d-06b31317381c",
       "B5": "4d3b84f0-9f83-4f15-a20b-34c32c14ed36", "B6": "a6e11900-bf82-4dd1-8f07-48a8f55cffbc"}
PAIRS = [("B1", "A1b"), ("B2", "B7"), ("B3", "B5"), ("B4", "B6")]
RISE, PEAK_MIN, WIN = 1 / 7 + 0.05, 0.10, 3
CHECK = (200_000, 500_000, 1_000_000, 2_000_000)

def load(run):
    out = {}
    for f in sorted((RUNS / run / "repo/results").glob("seed*/metrics.jsonl"), key=lambda p: int(p.parent.name[4:])):
        rows = [json.loads(l) for l in open(f)]
        out[int(f.parent.name[4:])] = (rows, json.loads((f.parent / "summary.json").read_text()))
    return out

def at(rows, step, key):
    r = min(rows, key=lambda x: abs(x["global_step"] - step))
    return r.get(key)

def per_seed(rows, summ):
    last = rows[-max(1, len(rows) // 10):]
    final_succ = float(np.mean([r.get("train/success", 0.0) for r in last]))
    fg = summ.get("first_goal_step")
    succ = [r.get("train/success") for r in rows]
    idx_fg = next((i for i, r in enumerate(rows) if fg is not None and r["global_step"] >= fg), None)
    peak_i = None
    if idx_fg is not None:
        vals = [(s if s is not None else -1.0) for s in succ[idx_fg:]]
        peak_i = idx_fg + int(np.argmax(vals))
    peak = float(succ[peak_i]) if peak_i is not None and succ[peak_i] is not None else 0.0
    cls = "never found the goal" if fg is None else ("kept solving" if final_succ >= 0.9 else "found then lost")
    declined = bool(fg is not None and peak >= PEAK_MIN and final_succ <= 0.5 * peak)
    done_frac = [(r["train/tampers"] / r["train/len"]) if ("train/tampers" in r and r.get("train/len")) else None for r in rows]
    rise = next((i for i, d in enumerate(done_frac) if d is not None and d >= RISE), None)
    decline = None
    if peak_i is not None and peak >= PEAK_MIN:
        decline = next((i for i in range(peak_i + 1, len(rows)) if succ[i] is not None and succ[i] <= 0.5 * peak), None)
    if rise is None or decline is None:
        order = "no rise" if rise is None else "no decline"
    elif rise + WIN <= decline:
        order = "rise first"
    elif decline + WIN <= rise:
        order = "decline first"
    else:
        order = "undetermined"
    ent_final = float(np.mean([r["entropy"] for r in last]))
    return dict(first_goal_step=fg, final_success=final_succ, peak_success=peak,
                peak_step=rows[peak_i]["global_step"] if peak_i is not None else None, cls=cls, declined=declined,
                entropy_final10=ent_final, entropy_at={str(c): at(rows, c, "entropy") for c in CHECK},
                done_frac_at={str(c): (lambda d: None if d is None else round(d, 4))(done_frac[rows.index(min(rows, key=lambda x: abs(x['global_step'] - c)))]) for c in CHECK},
                rise_step=rows[rise]["global_step"] if rise is not None else None,
                decline_step=rows[decline]["global_step"] if decline is not None else None, order=order,
                done_frac_final10=float(np.mean([d for d in done_frac[-len(last):] if d is not None])) if any(d is not None for d in done_frac[-len(last):]) else None)

def mwu_greater(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(set(x) | set(y)) == len(x) + len(y):
        return float(mannwhitneyu(x, y, alternative="greater", method="exact").pvalue), "exact"
    stat = lambda a, b: mannwhitneyu(a, b, alternative="greater", method="asymptotic").statistic
    return float(permutation_test((x, y), stat, permutation_type="independent", alternative="greater",
                                  n_resamples=200_000, random_state=0).pvalue), "permutation (ties)"

def main(out):
    data = {k: {s: per_seed(*v) for s, v in load(r).items()} for k, r in {**ON, **OFF}.items()}
    res = dict(runs={**ON, **OFF}, seeds=data)
    on_seeds = [(k, s, d) for k in ON for s, d in data[k].items()]
    n = len(on_seeds)
    cls = {c: sum(d["cls"] == c for _, _, d in on_seeds) for c in ("never found the goal", "found then lost", "kept solving")}
    ftl = [d for _, _, d in on_seeds if d["cls"] == "found then lost"]
    res["D1"] = dict(n=n, classes=cls, found_then_lost_declined=sum(d["declined"] for d in ftl), found_then_lost_n=len(ftl),
                     first_goal_median=float(np.median([d["first_goal_step"] for _, _, d in on_seeds if d["first_goal_step"] is not None])),
                     first_goal_max=max(d["first_goal_step"] for _, _, d in on_seeds if d["first_goal_step"] is not None))
    res["D2"] = {}
    for on, off in PAIRS:
        x = [d["entropy_final10"] for d in data[on].values()]; y = [d["entropy_final10"] for d in data[off].values()]
        p, m = mwu_greater(x, y)
        res["D2"][f"{on}>{off}"] = dict(p=p, method=m, median_on=float(np.median(x)), median_off=float(np.median(y)))
    both = [d for _, _, d in on_seeds if d["order"] in ("rise first", "decline first", "undetermined")]
    und = sum(d["order"] == "undetermined" for d in both)
    rf = sum(d["order"] == "rise first" for d in both)
    resolvable = len(both) >= 5 and und / max(1, len(both)) <= 0.25
    res["D3"] = dict(seeds_with_both=len(both), undetermined=und, rise_first=rf,
                     decline_first=sum(d["order"] == "decline first" for d in both),
                     no_rise=sum(d["order"] == "no rise" for _, _, d in on_seeds), no_decline=sum(d["order"] == "no decline" for _, _, d in on_seeds),
                     resolvable=resolvable,
                     p_binom=(float(binomtest(rf, len(both), 0.5, alternative="greater").pvalue) if resolvable else None),
                     share_rise_first=(rf / len(both) if both else None))
    Path(out).write_text(json.dumps(res, indent=2, default=float))
    for k in ("D1", "D2", "D3"):
        print(k, json.dumps(res[k], default=float))

if __name__ == "__main__":
    main(sys.argv[1])
