# evolved-intrinsic-rewards (working repository)

**The paper's artifact has moved to
[github.com/chasemetoyer/found-by-search](https://github.com/chasemetoyer/found-by-search) (tag `v1.0`).** Use that
repository to read the paper, check its numbers, or rebuild its tables and figures. It holds the paper, the
committed data and results, the scripts, and a copy of the training code and pre-registration.

This repository is the project's working history. It stays public as independent evidence of when each part of the
pre-registered study was locked and pushed:

| What | Where |
|---|---|
| Stage 1 protocol and lock | branch `orx/stage-1-infrastructure-and-calibration` |
| Stage 2 protocol and lock, which also registered every Stage 3 test (lock commit `f757692`, pushed before any search result) | branch `orx/stage-2-cma-es-vs-equal-budget-random-search-2m` |
| Stage 3 code, amendments, pre-launch receipts and frozen rewards (commit `7acab8c`, the source of `found-by-search/research/`) | branch `orx/stage-3-modal-launch-path-and-frozen-evaluation` |
| Pre-lock determinism check and a read-only Linux diagnosis | branches `orx/stage-2-pre-check-cpu-isa-pinning-determinism`, `orx/read-only-mac-linux-input-specification-diagnosi` |

The push times of these commits on GitHub are the public record that the protocols came before the data. The
paper's Appendix B lists each amendment with its commit and its first public push.

**Superseded on this branch.** An earlier copy of the paper artifact on `main` (commit `62dba42`, tag `v1.0-paper2`)
is incomplete: two input folders under `data/raw/repo/` were left out by a `.gitignore` rule, so `make all` fails on a
fresh clone. The data in it are the same as in `found-by-search`; that repository has the complete, checked version.

The working files on the research branches include records written by the AI agents that ran the project, with
absolute paths from the machine they ran on. They are kept unchanged so that the hashes in the locked registration
files still verify.

License: code MIT, data and paper CC BY 4.0, as in `found-by-search`.
