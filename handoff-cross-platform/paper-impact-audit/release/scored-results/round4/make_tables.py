"""Build the round-4 report tables from round4-scores.json (no new analysis). Usage: python make_tables.py > tables.md"""
import json
from pathlib import Path
r = json.loads((Path(__file__).parent / "round4-scores.json").read_text())
S, P = r["runs"], r["predictions"]
f = lambda x: "–" if x is None else (f"{x:.2g}" if x < 0.001 else f"{x:.3f}")
ci = lambda c: f"[{c[0]:.2f}, {c[1]:.2f}]"
def cis(row):
    c = row.get("ci")
    if not c: return "–"
    return ci(c) if isinstance(c[0], float) else " vs ".join(ci(x) for x in c)
print("| ID | Prediction | Expected (range) | Observed | 95% CI (Clopper-Pearson) | Result | Test (method) | raw p | Holm p |")
print("|---|---|---|---|---|---|---|---|---|")
exp = {"A1-P1": "A1b < A1c (medians 230k vs 300k)", "A1-P2": "A1b < A1c (20.5 vs 22.0)", "A1-P3": "A1b < A1a < A1c (A1a 260k)",
       "A1-P4": "A1b < A1a < A1c (A1a 21.2)", "A2-P1": "A2a 0.30 (0.08-0.55) < A2c 0.60 (0.40-0.80)", "A2-P2": "A2b 0.40 (0.12-0.65) < A2c 0.60",
       "A2-P3": "A2a 0.15 (0.02-0.40) < A2c 0.40 (0.20-0.65)", "A2-P4": "A2b 0.22 (0.04-0.45) < A2c 0.40",
       "A2-P5": "A2a 6/20 (2-11) < A2c 17/20 (13-20)", "A2-P6": "A2b 9/20 (4-14) < A2c 17/20", "A2-P7": "A2a 2/20 (0-6) < A2c 9/20 (4-14)",
       "A2-P8": "A2b 3/20 (0-8) < A2c 9/20", "B0-P": "tampers 1-3x, reaches goal in 12-16 steps, both growth rates",
       "PB2-B1": "B1 8/20 (3-14) < A1b 19/20 (15-20)", "PB2-B2": "B2 15/20 (9-19) < B7 20/20 (16-20)", "PB2-B3": "B3 5/20 (1-10) < B5 10/20 (5-15)",
       "PB2-B4": "B4 14/20 (8-19) < B6 20/20 (16-20)", "PB3-B3": "B3 14/20 (8-19) > B4 5/20 (1-10)", "PB3-B1": "B1 9/20 (4-15) > B2 3/20 (0-8)",
       "PB4": "B5 9/20 (4-14) > B6 0/20 (0-2)", "PB5": "B8 15/20 (11-20); hit iff >= 11"}
for x in P:
    e = exp.get(x["id"], x["expected"])
    test = x["test"] + (f" ({x['method']})" if x["method"] and x["method"] not in ("exact", "value iteration") else "")
    if x["id"].startswith(("A1-P3", "A1-P4")):
        test = "median ordering; " + x["method"]
    print(f"| {x['id']} | {x['prediction']} | {e} | {x['observed']} | {cis(x)} | {'**hit**' if x['hit'] else '**miss**'} | {test} | {f(x['p'])} | {f(x.get('p_holm'))} |")
print()
print("| Run | Change | solve | cycle-farm | prolong | fail | first-solved median | solved-ep. length median | train AUC median | final eval 8x8 / 16x16 (median) | 16x16 solve (>= 0.9) |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
lab = {"A1a": "growth 1/640", "A1b": "growth 1/160", "A1c": "growth 0", "A2a": "explore only, 1/640, coef 1.226", "A2b": "explore only, 1/160, coef 7.355",
       "A2c": "episodic novelty 1e-3", "B1": "tamper on, 1/160, norm on", "B2": "tamper on, 1/160, norm off", "B3": "tamper on, 1/40, norm on",
       "B4": "tamper on, 1/40, norm off", "B5": "tamper off, 1/40, norm on", "B6": "tamper off, 1/40, norm off", "B7": "tamper off, 1/160, norm off",
       "B8": "constant event bonus, norm off"}
for k in ("A1a", "A1b", "A1c", "A2a", "A2b", "A2c", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"):
    s = S[k]; c = s["categories"]; m = s["medians"]
    fs = "censored (2M)" if m["first_solved"] >= 2_000_000 else f"{m['first_solved']:,.0f}"
    print(f"| {k} | {lab[k]} | {c['solve']} | {c['cycle-farm']} | {c['prolong']} | {c['fail']} | {fs} | {m['solved_len']:.1f} | {m['train_auc']:.3f} | {m['eval8']:.2f} / {m['eval16']:.2f} | {s['solve16']} |")
print()
print("| Run | 8x8 eval-curve area mean (median) | 16x16 eval-curve area mean (median) |")
print("|---|---|---|")
for k in ("A2a", "A2b", "A2c"):
    s = S[k]; print(f"| {k} | {s['mean curve DoorKey-8x8']:.3f} ({s['medians']['curve DoorKey-8x8']:.3f}) | {s['mean curve DoorKey-16x16']:.3f} ({s['medians']['curve DoorKey-16x16']:.3f}) |")
print()
cols = ["B1", "A1b", "B2", "B7", "B3", "B5", "B4", "B6"]
ab = {"solve": "S", "cycle-farm": "C", "prolong": "P", "fail": "F"}
print("| seed | " + " | ".join(f"{c}{' (off)' if c in ('A1b', 'B7', 'B5', 'B6') else ''}" for c in cols) + " |")
print("|---|" + "---|" * len(cols))
for i in range(20):
    print(f"| {S['B1']['seeds'][i]['seed']} | " + " | ".join(f"{S[c]['seeds'][i]['done_per_episode']:.2f} {ab[S[c]['seeds'][i]['category']]}" for c in cols) + " |")
print("| median | " + " | ".join(f"{S[c]['done_rate_median']:.2f}" for c in cols) + " |")
print("| tamperers / loopers | " + " | ".join((f"{S[c]['tamperer']}/{S[c]['looper']}" if c in ('B1', 'B2', 'B3', 'B4') else "n/a (no-op)") for c in cols) + " |")
