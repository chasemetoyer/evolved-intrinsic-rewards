"""Round-5 report tables from round5-scores.json, part-d-results.json, step0-tamper-cost.json (no new analysis).
Usage: python make_tables_r5.py > round5-tables.md"""
import json
from pathlib import Path
H = Path(__file__).parent
r = json.loads((H / "round5-scores.json").read_text()); D = r["runs"]
fp = lambda p: "–" if p is None else (f"{p:.2g}" if p < 0.001 else f"{p:.3f}")
ci = lambda c: f"[{c[0]:.2f}, {c[1]:.2f}]"
def cis(x):
    c = x.get("ci")
    if not c: return "–"
    return ci(c) if isinstance(c[0], float) else " vs ".join(ci(y) for y in c)
res = lambda x: "**n/a (unresolvable)**" if x["hit"] is None else ("**hit**" if x["hit"] else "**miss**")
print("## Table 1. Every prediction\n")
print("| ID | Prediction | Expected | Observed | 95% CI (Clopper-Pearson) | Result | Test | raw p | Holm p |")
print("|---|---|---|---|---|---|---|---|---|")
for x in r["predictions"]:
    print(f"| {x['id']} | {x['prediction']} | {x['expected']} | {x['observed']} | {cis(x)} | {res(x)} | {x['test']} | {fp(x['p'])} | {fp(x.get('p_holm'))} |")
print(f"\nHolm set size: {r['holm_m_abc']} tests.\n")
print("## Table 2. Every run (solve count and success-curve area)\n")
print("| Run | Env, budget | solve | cycle-farm | prolong | fail | cycle-farm label | success-curve area mean | presses/ep. median | tamperers | pick-ups median |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
order = ["A1", "A2", "B9", "B10", "B11", "C1", "C2", "C3", "C4", "C5", "C6", "r4-B1", "r4-B2", "r4-B3", "r4-A1b"]
for k in [k for k in order if k in D]:
    d = D[k]; c = d["categories"]
    print(f"| {k} | {d['env'].removeprefix('MiniGrid-').removesuffix('-v0')}, {d['budget']/1e6:g}M | {c['solve']} {ci(d['ci']['solve'])} | {c['cycle-farm']} | {c['prolong']} | {c['fail']} | {d['cycle_farm_label']} | {d['auc_mean']:.3f} | {d['presses_median']:.2f} | {d['tamperers']} | {d['pickups_median']:.2f} |")
print("\n## Table 3. Part B per seed: tamper presses per episode (final 10% of steps) and category\n")
cols = [k for k in ("r4-B1", "B9", "B10", "B11", "r4-A1b") if k in D]
ab = {"solve": "S", "cycle-farm": "C", "prolong": "P", "fail": "F"}
print("| seed | " + " | ".join({"r4-B1": "B1 (c=0)", "B9": "B9 (c=0.01)", "B10": "B10 (c=0.1)", "B11": "B11 (c=1.0)", "r4-A1b": "A1b (tamper off)"}[k] for k in cols) + " |")
print("|---|" + "---|" * len(cols))
for i in range(20):
    print(f"| {D[cols[0]]['seeds'][i]['seed']} | " + " | ".join(f"{D[k]['seeds'][i]['presses']:.2f} {ab[D[k]['seeds'][i]['category']]}" for k in cols) + " |")
pd = json.loads((H / "part-d-results.json").read_text())
print("\n## Table 4. Part D per seed (round-4 tamper-on runs)\n")
print("| run | seed | first-goal step | class | peak success (step) | final-10% success | declined | entropy final-10% | done share final-10% | rise step | decline step | order |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for run in ("B1", "B2", "B3", "B4"):
    for s, d in sorted(pd["seeds"][run].items(), key=lambda kv: int(kv[0])):
        fg = "never" if d["first_goal_step"] is None else f"{d['first_goal_step']:,}"
        pk = f"{d['peak_success']:.2f} ({d['peak_step']:,})" if d["peak_step"] else f"{d['peak_success']:.2f}"
        print(f"| {run} | {s} | {fg} | {d['cls']} | {pk} | {d['final_success']:.3f} | {'yes' if d['declined'] else 'no'} | {d['entropy_final10']:.3f} | "
              f"{d['done_frac_final10']:.3f} | {d['rise_step'] if d['rise_step'] is None else format(d['rise_step'], ',')} | {d['decline_step'] if d['decline_step'] is None else format(d['decline_step'], ',')} | {d['order']} |")
print("\nMatched tamper-off runs, final-10% entropy medians: " + ", ".join(f"{k} {sorted(v['entropy_final10'] for v in pd['seeds'][k].values())[10]:.3f}" for k in ("A1b", "B7", "B5", "B6")))
s0 = json.loads((H / "step0-tamper-cost.json").read_text())
print("\n## Table 5. Step 0: optimal policy with a per-press tamper cost (gamma 0.99)\n")
print("| growth | c | outcome | steps | tamper presses (at step) | V(start) | method |")
print("|---|---|---|---|---|---|---|")
for g in ("1/160", "1/40"):
    for x in sorted(s0[g]["grid"] + s0[g]["bisection"], key=lambda x: x["c"]):
        print(f"| {g} | {x['c']:.6g} | {x['outcome']} | {x.get('steps', '–')} | {x['tampers']} ({x.get('tamper_steps')}) | {(format(x['V_start'], '.6f') if 'V_start' in x else '–')} | {s0[g].get('method', '')} |")
    print(f"| {g} | **largest c still tampering: {s0[g]['largest_c_still_tampers']:.4g}; smallest c with no tamper: {s0[g]['smallest_c_no_tamper']:.4g}; reaches goal at every c: {s0[g]['reaches_goal_at_every_c']}** | | | | | |")
