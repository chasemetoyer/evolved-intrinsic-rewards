"""Figure 3: tamper-cost sweep at growth 1/160, normalization on. (a) solve rate, Clopper-Pearson 95%;
(b) tamper presses per step over the final 10% of training (per seed; median and interquartile range; descriptive)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import numpy as np
import orx_figstyle as st
from figdata import J, cp, solves, FIGS, TEXTW
st.use_style()
r5, s0, rs = J("round5-scores.json"), J("step0-tamper-cost.json"), J("run-series.json", src=False)
costs = [("r4-B1", "B1", 0.0), ("B9", "B9", 0.01), ("B10", "B10", 0.1), ("B11", "B11", 1.0)]
thr = s0["1/160"]["largest_c_still_tampers"]
fig, (a, b) = st.figure_grid(1, 2, width=TEXTW, ratio=0.42)
for ax in (a, b):
    ax.set_xscale("symlog", linthresh=0.005, linscale=0.6); ax.set_xlim(-0.002, 2.0)
    ax.set_xticks([0, 0.01, 0.1, 1.0], ["0", "0.01", "0.1", "1"]); ax.set_xlabel("tamper cost per press")
    ax.axvline(thr, color=st.BASELINE, ls=":", lw=0.9)
for key, _, c in costs:
    k, n = solves(r5, key); lo, hi = cp(k, n)
    a.errorbar(c, k / n, yerr=[[k / n - lo], [hi - k / n]], fmt="o", color=st.PALETTE["orange"], ms=4, capsize=2, elinewidth=0.8)
    a.text(c * 0.8 if c > 0 else c, hi + 0.04, f"{k}/{n}", ha="center", fontsize=6)
k, n = solves(r5, "r4-A1b")
a.axhline(k / n, color=st.PALETTE["blue"], ls="--", lw=0.8)
a.text(0.0025, k / n - 0.08, f"no tamper action ({k}/{n})", color=st.PALETTE["blue"], fontsize=6)
a.text(thr * 1.1, 0.62, "small-grid optimum\n(explore need omitted)", fontsize=5.6, color="#555555", backgroundcolor="white")
a.set_ylabel("solve rate (fraction of 20 seeds)"); a.set_ylim(-0.03, 1.18)
rng = np.random.default_rng(0)
for _, key, c in costs:
    v = np.array([s["presses_per_step"] for s in rs["presses"][key].values()])
    jit = c * (1 + rng.uniform(-0.12, 0.12, len(v))) if c > 0 else rng.uniform(-0.0012, 0.0012, len(v))
    b.scatter(jit, v, s=5, color=st.PALETTE["orange"], alpha=0.45, linewidths=0)
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    b.errorbar(c, med, yerr=[[med - q1], [q3 - med]], fmt="_", color="#222222", ms=9, capsize=2, elinewidth=0.9)
b.axhline(1 / 7, color=st.BASELINE, ls="--", lw=0.8); b.text(0.0025, 1 / 7 + 0.004, "uniform random policy (1/7)", fontsize=6, color="#555555")
b.text(thr * 1.1, 0.10, "small-grid optimum\n(explore need omitted)", fontsize=5.6, color="#555555", backgroundcolor="white")
b.set_ylabel("tamper presses per step"); b.set_ylim(-0.005, 0.16)
st.panel_labels([a, b])
st.save(fig, str(FIGS / "fig3_cost_sweep"))
