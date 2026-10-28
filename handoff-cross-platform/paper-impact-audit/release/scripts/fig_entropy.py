"""Figure 2: policy entropy over training, tamper on vs matched tamper off (round 4). Mean and 95% t-interval across 20 seeds."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import numpy as np
import orx_figstyle as st
from figdata import J, FIGS, TEXTW
st.use_style()
rs = J("run-series.json", src=False)["entropy"]
pairs = [("B1", "A1b", "growth 1/160, norm on"), ("B2", "B7", "growth 1/160, norm off"), ("B3", "B5", "growth 1/40, norm on"), ("B4", "B6", "growth 1/40, norm off")]
fig, axes = st.figure_grid(2, 2, width=TEXTW, ratio=0.62, sharey=True, sharex=True)
axes = axes.ravel()
for ax, (on, off, title) in zip(axes, pairs):
    for key, col, lab in ((off, st.PALETTE["blue"], "satiation (no tamper)"), (on, st.PALETTE["orange"], "satiation + tamper")):
        seeds = list(rs[key].values()); steps = np.array(seeds[0]["step"]) / 1e6
        assert all(s["step"] == seeds[0]["step"] for s in seeds)
        runs = np.array([s["entropy"] for s in seeds])
        m, lo, hi = st.mean_ci(runs)
        ax.plot(steps, m, color=col, lw=1.0, label=lab); ax.fill_between(steps, lo, hi, color=col, alpha=0.25, linewidth=0)
    ax.axhline(np.log(7), color=st.BASELINE, ls="--", lw=0.7)
    ax.text(0.98, 0.04, title, transform=ax.transAxes, ha="right", fontsize=6.2)
    ax.set_xlim(0, 2.0); ax.set_ylim(0, 2.05)
for ax in axes[2:]: ax.set_xlabel("environment steps (millions)")
for ax in axes[::2]: ax.set_ylabel("policy entropy (nats)")
axes[0].text(0.05, np.log(7) + 0.03, "uniform (ln 7)", fontsize=5.8, color="#555555")
axes[0].legend(loc="center right", bbox_to_anchor=(1.0, 0.45), fontsize=5.8, frameon=True, framealpha=0.95, edgecolor="none")
st.panel_labels(axes)
st.save(fig, str(FIGS / "fig2_entropy"))
