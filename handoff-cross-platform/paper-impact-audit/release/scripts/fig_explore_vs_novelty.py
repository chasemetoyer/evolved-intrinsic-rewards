"""Figure 4: explore-only satiation vs episodic novelty (round 4, A2): evaluation-curve area per seed (dots) with mean
and bootstrap 95% interval (10,000 resamples, seed 0), on the training grid (8x8) and a larger grid (16x16)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import numpy as np
import orx_figstyle as st
from figdata import J, FIGS, TEXTW
st.use_style()
r4 = J("round4-scores.json")["runs"]
arms = [("A2a", "explore-only\nsatiation 1/640", st.PALETTE["blue"]), ("A2b", "explore-only\nsatiation 1/160", st.PALETTE["cyan"]),
        ("A2c", "episodic\nnovelty", st.PALETTE["green"])]
fig, axes = st.figure_grid(1, 2, width=TEXTW, ratio=0.40, sharey=True)
rng = np.random.default_rng(0)
for ax, grid in zip(axes, ("DoorKey-8x8", "DoorKey-16x16")):
    for i, (key, lab, col) in enumerate(arms):
        v = np.array([s["curve"][grid] for s in r4[key]["seeds"]])
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=6, color=col, alpha=0.55, linewidths=0)
        boots = rng.choice(v, (10_000, len(v))).mean(axis=1); lo, hi = np.percentile(boots, [2.5, 97.5])
        ax.errorbar(i + 0.25, v.mean(), yerr=[[v.mean() - lo], [hi - v.mean()]], fmt="o", ms=3.5, color="#222222", capsize=2, elinewidth=0.8)
    ax.set_xticks(range(3), [l for _, l, _ in arms], fontsize=6.5); ax.set_xlim(-0.5, 2.6)
    ax.text(0.02, 0.97, f"evaluated on {grid}", transform=ax.transAxes, fontsize=6.2, va="top")
axes[0].set_ylabel("evaluation-curve area (mean success)"); axes[0].set_ylim(-0.03, 1.05)
st.panel_labels(axes)
st.save(fig, str(FIGS / "fig4_explore_vs_novelty"))
