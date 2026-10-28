"""Pre-registered farming test: farm fraction vs predicted temptation E, and vs growth rate.
Data: prediction-results.json (from test_predictions.py). 10 seeds per node."""
import json
from pathlib import Path
from orx_chart import render_chart

here = Path(__file__).parent
res = json.loads((here / "prediction-results.json").read_text())
meta = {  # node -> (growth g, group)
    "calibration growth 1/640": (1/640, "Calibration (seen before F was defined)"),
    "calibration growth 1/160": (1/160, "Calibration (seen before F was defined)"),
    "calibration growth 1/40": (1/40, "Calibration (seen before F was defined)"),
    "N1": (1/40, "Pre-registered, gamma 0.99, coef 1"), "N3": (1/80, "Pre-registered, gamma 0.99, coef 1"),
    "N6": (1/20, "Pre-registered, gamma 0.99, coef 1"),
    "N4": (1/80, "Pre-registered, coef changed"), "N5": (1/40, "Pre-registered, coef changed"),
    "N2": (1/40, "Pre-registered, gamma 0.95"),
}
groups = {}
for k, (g, grp) in meta.items():
    r = res[k]
    groups.setdefault(grp, []).append(dict(E=r["E"], g=g, frac=r["farmers"] / r["n"]))
def series(x, key):
    return [dict(name=grp, points=sorted([dict(step=p[x], **{key: p["frac"]}) for p in pts], key=lambda d: d["step"]))
            for grp, pts in groups.items()]
render_chart(
    here / "farming-test.html",
    title="The temptation formula's coef and discount predictions failed; farming tracked growth rate in these runs (post hoc)",
    subtitle="Agent 3 (homeostatic satiation), DoorKey-8x8, 2M steps, 10 seeds per point. Farmer = >5 pick-ups or door flips per episode.",
    metrics=[
        dict(key="frac_E", label="vs predicted temptation E", type="scatter", unit="fraction of seeds",
             xLabel="Predicted temptation E = coef x F(g, gamma)", yLabel="Fraction of seeds that farm",
             series=series("E", "frac_E")),
        dict(key="frac_g", label="vs growth rate (post hoc)", type="scatter", unit="fraction of seeds", xScale="log",
             xLabel="Need growth per step (log)", yLabel="Fraction of seeds that farm",
             series=series("g", "frac_g")),
    ],
    x_label="",
)
