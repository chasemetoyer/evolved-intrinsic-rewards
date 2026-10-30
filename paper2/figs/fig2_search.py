"""Figure 2: search fitness of every Stage 2 candidate by generation (CMA-ES) or batch (random search).

Regenerate: python3 paper2/figs/fig2_search.py (data: paper2/data/sources/s2x-candidates.csv)."""
import numpy as np
from figdata import COLORS, SRC, rows
from orx_figstyle import TEXT, figure_grid, panel_labels, save, use_style

COLS = [("area/combined", "Combined fitness"), ("area/DoorKey-8x8", "DoorKey-8x8 area"), ("area/UnlockPickup", "UnlockPickup area")]


def main():
    use_style()
    cand = rows(SRC / "s2x-candidates.csv")
    fig, axes = figure_grid(1, 3, width=TEXT, ratio=0.33, sharey=True)
    rng = np.random.default_rng(0)  # horizontal jitter only
    handles = {}
    for ax, (col, ylabel) in zip(axes, COLS):
        for m, off, name, marker, ls in (("cma", -0.17, "CMA-ES candidates", "o", "-"),
                                         ("random", 0.17, "random-search candidates", "^", "--")):
            sel = [r for r in cand if r["method"] == m]
            g = np.array([int(r["group"]) for r in sel])
            y = np.array([float(r[col]) for r in sel])
            ax.scatter(g + off + rng.uniform(-0.07, 0.07, len(g)), y, s=7, marker=marker, color=COLORS[m], alpha=0.6,
                       linewidths=0, label=name)
            groups = sorted(set(g))
            best = np.maximum.accumulate([y[g == k].max() for k in groups])
            (line,) = ax.step(groups, best, where="post", color=COLORS[m], lw=1.1, ls=ls, label=f"{name.split()[0]} best so far")
            handles[name] = ax.collections[-1]
            handles[line.get_label()] = line
        ax.set_xlabel("Generation or batch index")
        ax.set_xticks(range(0, 12, 3))
        ax.set_ylim(0, 1)
        ax.set_ylabel(ylabel) if ax is axes[0] else None
        ax.grid(axis="y", color="#eeeeee", lw=0.5)
    axes[1].set_ylabel("DoorKey-8x8 area")
    axes[2].set_ylabel("UnlockPickup area")
    panel_labels(axes)
    fig.legend(handles=list(handles.values()), labels=list(handles), loc="outside lower center", ncol=4, frameon=False, fontsize=6)
    save(fig, str(SRC.parents[1] / "figs" / "fig2_search"))


if __name__ == "__main__":
    main()
