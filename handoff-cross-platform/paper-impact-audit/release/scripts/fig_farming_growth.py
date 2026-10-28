"""Figure 5: farming against need growth rate. (a) DoorKey-8x8: fraction of seeds in the cycle-farm category
(Clopper-Pearson 95%), normalization on and off; filled = pre-registered scoring, open = round-2 runs re-scored under
the round-3 categories (exploratory). (b) KeyCorridorS3R1: peak over training of rolling key pick-ups per episode
(median and interquartile range across 20 seeds; descriptive); every seed ended with 0 farmers."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import numpy as np
import orx_figstyle as st
from figdata import J, cp, FIGS, TEXTW
st.use_style()
r3, r4, r5 = J("round3-scores.json"), J("round4-scores.json"), J("round5-scores.json")
rs = J("run-series.json", src=False)["keycorridor_pickups"]
ex = r3["exploratory_rescore"]
def cf(d): return d["counts"]["cycle-farm"] if "counts" in d else d["categories"]["cycle-farm"]
pre_on = [(1/640, r4["runs"]["A1a"]), (1/160, r4["runs"]["A1b"]), (1/60, r3["round3"]["R1"]), (1/40, r3["round3"]["R4"]),
          (1/40, r4["runs"]["B5"]), (1/30, r3["round3"]["R2"])]
exp_on = [(1/640, ex["Agent 3: homeostatic satiation, growth 1/640"]), (1/160, ex["Agent 3: homeostatic satiation, growth 1/160"]),
          (1/80, ex["N3: growth 1/80"]), (1/40, ex["Agent 3: homeostatic satiation, growth 1/40"]),
          (1/40, ex["N1: anchor replicate, growth 1/40, seeds 10-19"]), (1/20, ex["N6: growth 1/20"])]
pre_off = [(1/160, r4["runs"]["B7"]), (1/40, r3["round3"]["R7"]), (1/40, r4["runs"]["B6"])]
fig, (a, b) = st.figure_grid(1, 2, width=TEXTW, ratio=0.44)
def plot(ax, pts, color, filled, dx, label):
    seen = {}
    for g, d in pts:
        k, n = cf(d), d["n"]; lo, hi = cp(k, n)
        j = seen.get(g, 0); seen[g] = j + 1; x = g * (1 + dx + 0.07 * j)
        ax.errorbar(x, k / n, yerr=[[k / n - lo], [hi - k / n]], fmt="o", ms=3.5, color=color, mfc=color if filled else "white",
                    capsize=1.5, elinewidth=0.7, label=label if label and j == 0 and g == pts[0][0] else None)
plot(a, pre_on, st.PALETTE["orange"], True, 0.0, "norm on, pre-registered scoring")
plot(a, exp_on, st.PALETTE["orange"], False, -0.10, "norm on, re-scored (exploratory)")
plot(a, pre_off, st.PALETTE["blue"], True, 0.05, "norm off, pre-registered scoring")
a.set_xscale("log"); a.set_xticks([1/640, 1/160, 1/80, 1/40, 1/20], ["1/640", "1/160", "1/80", "1/40", "1/20"]); a.minorticks_off()
a.set_xlabel("need growth per step"); a.set_ylabel("cycle-farm fraction of seeds"); a.set_ylim(-0.03, 1.05)
a.legend(loc="upper left", fontsize=5.8)
g_of = {"C1": 1/160, "C2": 1/40, "C3": 1/20, "C4": 1/20}
for key, col in (("C1", st.PALETTE["orange"]), ("C2", st.PALETTE["orange"]), ("C3", st.PALETTE["orange"]), ("C4", st.PALETTE["blue"])):
    v = np.array([s["peak_key_pickups"] for s in rs[key].values()]); q1, m, q3 = np.percentile(v, [25, 50, 75])
    x = g_of[key] * (1.07 if key == "C4" else 1.0)
    b.errorbar(x, m, yerr=[[m - q1], [q3 - m]], fmt="o", ms=3.5, color=col, capsize=1.5, elinewidth=0.7,
               label={"C1": "norm on", "C4": "norm off"}.get(key))
    nf = sum(s['category'] == 'cycle-farm' for s in rs[key].values())
    if key == "C4": b.text(x * 1.08, m, f"{nf}/20 farm\nat end", fontsize=5.3, ha="left", va="center")
    else: b.text(x, q3 + 1.2, f"{nf}/20\nfarm at end", fontsize=5.3, ha="center", va="bottom")
c6 = np.median([s["peak_key_pickups"] for s in rs["C6"].values()])
b.axhline(c6, color=st.BASELINE, ls="--", lw=0.8); b.text(1/195, c6 + 1.0, "task-only, median peak", fontsize=5.6, color="#555555")
b.axhline(5, color=st.BASELINE, ls=":", lw=0.7); b.text(1/195, 5 - 3.4, "cycle-farm threshold (5)", fontsize=5.6, color="#555555")
b.set_xscale("log"); b.set_xticks([1/160, 1/40, 1/20], ["1/160", "1/40", "1/20"]); b.minorticks_off(); b.set_xlim(1/200, 1/9)
b.set_xlabel("need growth per step"); b.set_ylabel("peak key pick-ups per episode"); b.set_ylim(0, 48)
b.legend(loc="upper left", fontsize=5.8)
st.panel_labels([a, b])
st.save(fig, str(FIGS / "fig5_farming_growth"))
