"""Shared loaders for the figure scripts. Everything comes from paper/data (scored-file snapshots in paper/data/sources,
plus run-series.json from extract_run_series.py, which was cross-checked against the scored files)."""
import json
from pathlib import Path
from scipy.stats import beta
ROOT = Path(__file__).resolve().parents[1]
SRC, DATA, FIGS = ROOT / "data" / "sources", ROOT / "data", ROOT / "figs"
TEXTW = 5.5          # figures are built at 5.5in and included at exactly 5.5in (scale 1.0) in the 6.5in text block
def J(name, src=True):
    return json.loads(((SRC if src else DATA) / name).read_text())
def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi
def solves(scores, key):
    d = scores["runs"][key]; return d["categories"]["solve"], d["n"]
