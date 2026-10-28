"""Extract per-row / per-seed series from the run logs for Figures 2-4 (descriptive only; no tests).
Every extracted value that also appears in a scored file is recomputed with the identical formula and must match
EXACTLY; any mismatch aborts (exit 1) and is reported.
Usage: python paper/scripts/extract_run_series.py <artifacts three-agents dir> paper/data/run-series.json"""
import json, sys
from pathlib import Path
import numpy as np
A, out = Path(sys.argv[1]), Path(sys.argv[2])
RUNS = Path.home() / ".local/share/openresearch/local-runs"
ROUND4 = {"B1": "bb00e7e5-65d0-4411-a236-2dacc19f0e63", "B2": "a8f5efc4-63e7-4a55-8020-08f7e7cff7bb", "B3": "78c44406-6e63-466f-b309-8dfb82bfe663",
          "B4": "f0a40d20-3702-4087-803c-8db52fefaf1e", "A1b": "3629f9a7-8038-452a-bbef-53d5685e0a85", "B7": "115c6566-d1b2-4ea2-9c6d-06b31317381c",
          "B5": "4d3b84f0-9f83-4f15-a20b-34c32c14ed36", "B6": "a6e11900-bf82-4dd1-8f07-48a8f55cffbc"}
ROUND5 = {"B9": "b971c18d-0fd7-4c68-b627-eb098b0b3569", "B10": "a25b7c99-84bb-4cbb-a742-5594444b7fc1", "B11": "896b2863-59b7-44c0-addc-4091b9bab73c",
          "C1": "c14516de-0174-4001-b8b2-5125e8aa49d3", "C2": "ad87a02f-7353-4a64-8c32-e981408dd774", "C3": "aa29d1c3-78f8-4c3d-b58f-ee45102255cf",
          "C4": "2153e884-0de7-4f7c-b942-27507be467ef", "C5": "35c840cd-2776-4817-9ac0-1f21f93c5e4d", "C6": "6571bce6-65f1-4227-aade-a4b2a6ac357e"}
pd = json.loads((A / "round5/part-d-results.json").read_text())
r5 = json.loads((A / "round5/round5-scores.json").read_text())["runs"]
mismatches = []
def check(what, got, want):
    if got != want: mismatches.append(f"{what}: extracted {got!r} != scored {want!r}")
def seeds_of(run):
    for f in sorted((RUNS / run / "repo/results").glob("seed*/metrics.jsonl"), key=lambda p: int(p.parent.name[4:])):
        yield int(f.parent.name[4:]), [json.loads(l) for l in open(f)], json.loads((f.parent / "summary.json").read_text())
def done_share(rows):
    return [(r["train/tampers"] / r["train/len"]) if ("train/tampers" in r and r.get("train/len")) else None for r in rows]
res = dict(note="Descriptive series extracted from run logs; overlaps with scored files checked for exact equality.", runs={**ROUND4, **ROUND5})
# Figure 3: entropy per row (round-4 tamper-on and matched tamper-off runs)
res["entropy"] = {}
for k, run in ROUND4.items():
    per = {}
    for s, rows, summ in seeds_of(run):
        last = rows[-max(1, len(rows) // 10):]
        ef = float(np.mean([r["entropy"] for r in last]))
        check(f"{k} seed {s} entropy_final10", ef, pd["seeds"][k][str(s)]["entropy_final10"])
        for c in (200_000, 500_000, 1_000_000, 2_000_000):
            v = min(rows, key=lambda x: abs(x["global_step"] - c))["entropy"]
            check(f"{k} seed {s} entropy_at {c}", v, pd["seeds"][k][str(s)]["entropy_at"][str(c)])
        per[s] = dict(step=[r["global_step"] for r in rows], entropy=[r["entropy"] for r in rows], entropy_final10=ef)
    res["entropy"][k] = per
# Figure 2: presses per step (done share) over the final 10% of rows, plus presses per episode, for B1 (round 4) and B9-B11
res["presses"] = {}
for k, run in {"B1": ROUND4["B1"], "B9": ROUND5["B9"], "B10": ROUND5["B10"], "B11": ROUND5["B11"], "A1b": ROUND4["A1b"]}.items():
    per = {}
    for s, rows, summ in seeds_of(run):
        last = rows[-max(1, len(rows) // 10):]
        ds = done_share(rows)
        pps = float(np.mean([d for d in ds[-len(last):] if d is not None]))
        ppe = summ["final10_exact"]["tampers_per_episode"]
        if k in ("B1",):
            check(f"{k} seed {s} done_frac_final10", pps, pd["seeds"][k][str(s)]["done_frac_final10"])
        sk = {"B1": "r4-B1", "A1b": "r4-A1b"}.get(k, k)
        sc = next(x for x in r5[sk]["seeds"] if x["seed"] == s)
        check(f"{k} seed {s} presses_per_episode", ppe, sc["presses"])
        per[s] = dict(presses_per_step=pps, presses_per_episode=ppe, category=sc["category"],
                      mean_len_final10=float(np.mean([r["train/len"] for r in last])))
    res["presses"][k] = per
# Figure 4: KeyCorridor transient key pick-ups (max over training of the rolling 100-episode mean) and final categories
res["keycorridor_pickups"] = {}
for k in ("C1", "C2", "C3", "C4", "C5", "C6"):
    per = {}
    for s, rows, summ in seeds_of(ROUND5[k]):
        last = rows[-max(1, len(rows) // 10):]
        sc = next(x for x in r5[k]["seeds"] if x["seed"] == s)
        fk = float(np.mean([r.get("train/key_pickups", 0.0) for r in last]))
        check(f"{k} seed {s} final key pick-ups", fk, sc["pickups"])
        per[s] = dict(peak_key_pickups=max(r.get("train/key_pickups", 0.0) for r in rows), final_key_pickups=fk, category=sc["category"])
    res["keycorridor_pickups"][k] = per
if mismatches:
    print("MISMATCHES (stopping):"); [print("  " + m) for m in mismatches]; sys.exit(1)
out.write_text(json.dumps(res, indent=1)); print("all overlapping values match exactly; written", out)
for k, per in res["keycorridor_pickups"].items():
    print(k, "median peak key pick-ups", round(float(np.median([v["peak_key_pickups"] for v in per.values()])), 2))
for k, per in res["presses"].items():
    v = sorted(x["presses_per_step"] for x in per.values()); print(k, "presses/step median", round(float(np.median(v)), 4), "range", round(v[0], 4), round(v[-1], 4))
