# Paper 2: sources and number pipeline

`paper.tex` (repository root) is the draft of "Found by Search, Broken by a Shortcut: Transfer and Tampering of
Searched Intrinsic Rewards". Every number in it is a `\val{key}` macro; nothing is typed by hand.

| Step | Command (repo root) | Output |
|---|---|---|
| Snapshot the saved result files (local paths replaced by placeholders) | `EIR_ARTIFACTS=<artifacts dir> python3 paper2/scripts/snapshot_sources.py` | `paper2/data/sources/` with `SHA256SUMS`, `SOURCES.json` |
| Independent extraction from the raw Stage 3 run logs | `EIR_ARTIFACTS=<artifacts dir> uv run --isolated --no-project --with numpy python paper2/scripts/extract_claims.py` | `paper2/data/claims.json` |
| Per-seed tamper series for Figure 6 | `EIR_ARTIFACTS=<artifacts dir> python3 paper2/scripts/extract_series.py` | `paper2/data/tamper-series.csv` |
| Number macros | `python3 paper2/scripts/make_numbers.py` | `paper2/numbers.tex`, `paper2/data/numbers.json` |
| Tables | `python3 paper2/scripts/make_tables.py` | `paper2/tables/*.tex` |
| Figures | `cd paper2/figs && uv run --isolated --no-project --with matplotlib --with numpy python fig2_search.py` (and fig3-fig7) | `paper2/figs/*.pdf`, `*.svg` |
| Build | `latexmk -pdf paper.tex` | `paper.pdf` |
| Check | `uv run --isolated --no-project --with numpy python paper2/scripts/check_numbers.py` | must print `PASS` |

The first three steps need the project's artifacts directory (the full Stage 3 run archive); everything after them
runs from the repository alone. `paper2/data/worded-counts.json` records the evidence for every count written as a
word, and `paper2/data/github-push-events.json` the public GitHub push feed used in Appendix B.
