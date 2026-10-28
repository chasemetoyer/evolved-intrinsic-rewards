"""Round-2 comparison: success AUC (95% bootstrap CI over 10 seeds) and pick-ups per episode.
Data: ../data/round2-node-summary.json (built by ../data/compare_runs.py from each run's per-seed metrics.jsonl)."""
import json
from pathlib import Path
from orx_chart import render_chart

here = Path(__file__).parent
rows = [r for r in json.loads((here / "../data/round2-node-summary.json").read_text()) if r["n"] == 10]
short = {
    "Agent 1 @ 10 seeds (powered baseline)": "Agent 1: PPO (task only)",
    "Agent 2b: episodic novelty, coef 3e-4": "Novelty, ep. count 3e-4",
    "Agent 2b: episodic novelty, coef 1e-3": "Novelty, ep. count 1e-3",
    "Agent 2b: episodic novelty, coef 3e-3": "Novelty, ep. count 3e-3",
    "LP curiosity (fixed lag), coef 0.1": "LP curiosity 0.1",
    "LP curiosity (fixed lag), coef 0.3": "LP curiosity 0.3",
    "LP curiosity (fixed lag), coef 1.0": "LP curiosity 1.0",
    "Agent 3: homeostatic satiation, growth 1/640": "Agent 3: satiation, growth 1/640",
    "Agent 3: homeostatic satiation, growth 1/160": "Agent 3: satiation, growth 1/160",
    "Agent 3: homeostatic satiation, growth 1/40": "Agent 3: satiation, growth 1/40",
    "Control: constant event bonus (no satiation)": "Control: same events, no satiation",
}
rows = [r for r in rows if r["title"] in short]
rows.sort(key=lambda r: list(short).index(r["title"]))
auc = [dict(step=i, label=short[r["title"]], auc=round(r["auc"], 4), lower=round(r["auc_lo"], 4), upper=round(r["auc_hi"], 4))
       for i, r in enumerate(rows)]
pick = [dict(step=i, label=short[r["title"]], pickups=round(r["pickups"], 2))
        for i, r in enumerate([r for r in rows if r["pickups"] is not None])]
render_chart(
    here / "round2-comparison.html",
    title="Constant event rewards are farmed; slow-rebuilding satiation is not; fast-rebuilding satiation is farmed in half the seeds",
    subtitle="MiniGrid DoorKey-8x8 · PPO · 2M steps · 10 seeds per node · whiskers = 95% bootstrap CI",
    metrics=[
        dict(key="auc", label="Success AUC", type="dot", unit="fraction", xLabel="Mean training success (area under curve)",
             series=[dict(name="Success AUC", points=auc)]),
        dict(key="pickups", label="Pick-ups per episode (reward hack)", type="bar", unit="pick-ups/episode",
             yLabel="Pick-ups per episode, final 10% of training (1 = just the key)",
             series=[dict(name="Pick-ups", points=pick)]),
    ],
    x_label="",
)
