# Paper detector impact audit

Start with [the audit report](report/paper-impact-audit.md), then the
[exact Setup corrections](report/setup-corrections.md) and
[replay wording correction](report/replay-wording-correction.md).

This folder preserves the references consulted for the audit. The original
Zenodo release has not been edited. `release.zip` matches the published Zenodo
checksum recorded in `zenodo-record.json`; `release/` is its unchanged extracted
content. The ZIP and checkpoints remain available locally but are omitted from
the new repository's Git history. The included release manifest identifies them.

`run-source/` contains historical per-run source snapshots verified against the
paper's recorded Git commits. `dependencies/` contains the consulted MiniGrid
and Gymnasium source and package metadata. `paper-tables/` preserves the original
replay table used for the arithmetic check. `audit-protocol/` contains the locked
retrospective protocol and its publication receipt.

`report/` holds the generated tables, checks and report; matching deliverables
are in this project's artifacts directory. `audit-scripts/` preserves the scripts
used, whose executable project-root versions are in `audits/` on the audit
branch. They read existing files only and do not train or run policies.

Unknown historical event counts are explicitly marked unknown. Initial-cache
exposures count episodes, not realized missed transitions. Proposed paper text
is a draft and has not been applied. Stage 1 is paused pending review.
