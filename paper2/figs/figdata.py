"""Shared loaders, colours and labels for the paper-2 figures. Data: paper2/data (snapshots and extracted series)."""
import csv
from collections import defaultdict
from pathlib import Path

FIGS = Path(__file__).resolve().parent
DATA = FIGS.parent / "data"
SRC = DATA / "sources"
# Okabe-Ito colours as in the registered Stage 3 figure; T is the grey baseline and "E, tamper on" is black, a
# colour no arm in the held-out panel uses.
COLORS = {"E": "#0072B2", "R": "#009E73", "T": "#7F7F7F", "N": "#E69F00", "S": "#CC79A7",
          "tamper_off": "#0072B2", "tamper_on": "#000000", "cma": "#0072B2", "random": "#009E73"}
LABELS = {"E": "E (CMA-ES-selected)", "R": "R (random-search-selected)", "T": "T (task-only)",
          "N": "N (episodic novelty)", "S": r"S (satiation)$^\dagger$",
          "tamper_off": "E, tamper off", "tamper_on": "E, tamper on"}
SHORT = {"E": "E", "R": "R", "T": "T", "N": "N", "S": "S", "tamper_off": "off", "tamper_on": "on"}


def rows(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def series(path, key, xcol, ycol, seedcol="seed"):
    """-> {key value: (x list, {seed: y list})} for long-format CSVs."""
    out = defaultdict(lambda: defaultdict(list))
    xs = defaultdict(list)
    for r in rows(path):
        out[r[key]][r[seedcol]].append((float(r[xcol]), float(r[ycol])))
    res = {}
    for k, seeds in out.items():
        curves = [sorted(v) for v in seeds.values()]
        grid = [x for x, _ in curves[0]]
        assert all([x for x, _ in c] == grid for c in curves), k
        res[k] = (grid, [[y for _, y in c] for c in curves])
    return res
