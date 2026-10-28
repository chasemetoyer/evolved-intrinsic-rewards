"""Figure 1: solve rate with and without the tamper action, both environments (Clopper-Pearson 95%)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import numpy as np, matplotlib.pyplot as plt
import orx_figstyle as st
from figdata import J, cp, solves, FIGS, TEXTW
st.use_style()
r4, r5 = J("round4-scores.json"), J("round5-scores.json")
groups = [  # (label, [(bar label, scores, key)])
    ("DoorKey\ngrowth 1/160, norm on", [("task-only", r5, "A1"), ("satiation", r4, "A1b"), ("satiation + tamper", r4, "B1")]),
    ("DoorKey\ngrowth 1/160, norm off", [("task-only", r5, "A2"), ("satiation", r4, "B7"), ("satiation + tamper", r4, "B2")]),
    ("DoorKey\ngrowth 1/40, norm on", [("satiation", r4, "B5"), ("satiation + tamper", r4, "B3")]),
    ("DoorKey\ngrowth 1/40, norm off", [("satiation", r4, "B6"), ("satiation + tamper", r4, "B4")]),
    ("KeyCorridorS3R1\ngrowth 1/160, norm on", [("task-only", r5, "C6"), ("satiation", r5, "C1"), ("satiation + tamper", r5, "C5")]),
]
color = {"task-only": st.BASELINE, "satiation": st.PALETTE["blue"], "satiation + tamper": st.PALETTE["orange"]}
fig, ax = st.figure(width=TEXTW, ratio=0.42)
w, x0, ticks, seen = 0.26, 0.0, [], set()
for gl, bars in groups:
    xs = x0 + (np.arange(len(bars)) - (len(bars) - 1) / 2) * w
    for x, (bl, sc, key) in zip(xs, bars):
        k, n = solves(sc, key); lo, hi = cp(k, n)
        ax.bar(x, k / n, w * 0.92, color=color[bl], label=bl if bl not in seen else None); seen.add(bl)
        ax.errorbar(x, k / n, yerr=[[k / n - lo], [hi - k / n]], fmt="none", ecolor="#333333", elinewidth=0.6, capsize=1.5)
        ax.text(x, hi + 0.03, f"{k}/{n}", ha="center", va="bottom", fontsize=5.5)
    ticks.append((x0, gl)); x0 += 1.0
ax.set_xticks([t for t, _ in ticks], [l for _, l in ticks], fontsize=5.8)
ax.set_ylabel("solve rate (fraction of 20 seeds)")
ax.set_ylim(0, 1.18); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.13), frameon=False)
st.save(fig, str(FIGS / "fig1_solve_tamper"))
