"""Emit the numeric blocks of paper/outline.md from paper/data/claims.json and paper/data/bound-check.json."""
import json
c = json.load(open("paper/data/claims.json")); b = json.load(open("paper/data/bound-check.json"))
f = lambda p: f"{p:.2g}" if p < 0.001 else f"{p:.3f}"
L = []
L.append("### Bound computation (post hoc, not pre-registered; `paper/scripts/bound_check.py` -> `paper/data/bound-check.json`)\n")
L.append(f"200 layouts per environment (seeds 10000-10199); gamma = {b['gamma']}; ceiling D(h0) = {b['D0']} for any non-solving policy.\n")
for env, e in b["envs"].items():
    s = e["shortest_len"]
    L.append(f"**{env}** (time limit {e['max_steps']}): actual shortest solution length min {s['min']}, median {s['median']:g}, max {s['max']}.\n")
    L.append("| growth | tamper once + shortest: min total (undiscounted / discounted) | layouts <= 0.75 | shortest, no tamper: min total (undisc / disc) | layouts <= 0.75 |")
    L.append("|---|---|---|---|---|")
    for g, row in e["growth"].items():
        a, n = row["tamper_once_then_shortest"], row["shortest_no_tamper"]
        L.append(f"| {g} | {a['undiscounted_min']:.3f} / {a['discounted_min']:.3f} | {a['layouts_undiscounted_at_or_below_D0']} / {a['layouts_discounted_at_or_below_D0']} | "
                 f"{n['undiscounted_min']:.3f} / {n['discounted_min']:.3f} | {n['layouts_undiscounted_at_or_below_D0']} / {n['layouts_discounted_at_or_below_D0']} |")
    L.append("")
print("\n".join(L))
