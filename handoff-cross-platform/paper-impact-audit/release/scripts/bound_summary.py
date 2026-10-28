"""POST HOC: combine check (a) (richer solving family) and check (b) (learned 1/20 farming policies) on the same layouts.
Usage: python paper/scripts/bound_summary.py -> paper/data/bound-summary.json"""
import json
import numpy as np
b = json.load(open("paper/data/bound-check.json")); f = json.load(open("paper/data/farming-policy-returns.json"))
dk = b["envs"]["MiniGrid-DoorKey-8x8-v0"]["growth"]["1/20"]
best = np.array(dk["rich_no_tamper_family"]["per_layout_best_discounted"])
farmers = [s for s, v in f["policies"].items() if v["success_rate"] < 0.5]       # the learned farming policies
solver = [s for s, v in f["policies"].items() if v["success_rate"] >= 0.5]
F = np.array([f["policies"][s]["discounted"] for s in farmers])                   # (policies, layouts)
out = dict(note="POST HOC, not pre-registered", growth="1/20", layouts=len(best), D0=b["D0"],
           best_solving_discounted=dict(min=float(best.min()), median=float(np.median(best)), max=float(best.max())),
           learned_policies={s: dict(success_rate=f["policies"][s]["success_rate"], mean_discounted=f["policies"][s]["mean_discounted"],
                                     max_discounted=max(f["policies"][s]["discounted"])) for s in f["policies"]},
           farming_policy_seeds=farmers, solver_seeds=solver,
           farmers_mean_discounted=float(F.mean()), farmers_max_discounted_any_layout=float(F.max()),
           layouts_where_any_farmer_beats_best_solving=int((F >= best[None, :]).any(axis=0).sum()),
           layouts_where_any_farmer_reaches_D0=int((F >= b["D0"]).any(axis=0).sum()))
# empirical check of the bound itself: every NON-solving episode of every learned policy must have discounted return <= D0
ns = [d for s in f["policies"] for d, ok in zip(f["policies"][s]["discounted"], f["policies"][s]["success"]) if not ok]
nsu = [d for s in f["policies"] for d, ok in zip(f["policies"][s]["undiscounted"], f["policies"][s]["success"]) if not ok]
out.update(non_solving_episodes=len(ns), max_discounted_non_solving=float(max(ns)), max_undiscounted_non_solving=float(max(nsu)),
           bound_holds_on_all_non_solving_episodes=bool(max(ns) <= b["D0"] and max(nsu) <= b["D0"]),
           solving_episodes_by_farming_seeds=int(sum(ok for s in farmers for ok in f["policies"][s]["success"])))
json.dump(out, open("paper/data/bound-summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "learned_policies"}, indent=1))
for s, v in out["learned_policies"].items(): print(s, v)
