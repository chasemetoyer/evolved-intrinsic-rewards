# Shared research state

Before doing work, read `handoff-cross-platform/CONTINUE-HERE.md` and the
canonical Mac project copy of `handoff-cross-platform/session-state.json` named
there. These files are the shared memory across chats and models. The latest
user instructions take precedence over these notes.

Use `scripts/checkpoint.py` to claim ownership when the user switches agents,
and checkpoint at meaningful steps. Only one lead chat may own edits or launches
at once; its explicitly assigned helpers may edit their assigned files.
Readers and already-running compute can continue. Do not start a second
controller or rerun completed inputs when taking over. Check the run registry,
Modal call handles and budget ledger first. A source checkpoint is not proof
that a result passed; inspect persisted logs and outputs.

Stage 1 only. No evolution or random search. The user approved the paper audit
and resumed Stage 1 with archived-detector and corrected-detector descriptive
checks. Preserve all protected registration files and use timestamped amendments
for later implementation repairs. Stop at the Stage 1 report or the $15 guard.

Keep credentials out of checkpoint files, Git and chat. Usage snapshots may be
incomplete: never claim account quota is known when it is not exposed. Save
source and an exact next action before ending a turn or handing off.

Also read `handoff-cross-platform/SESSION-RULES.md` (start, during and end
rules) and `handoff-cross-platform/approvals-log.jsonl` in the canonical Mac
folder before acting.

Stage 2 update (2026-10-28): Stage 1 is complete and Stage 2 is in pre-lock
review. The Stage 2 entries in `handoff-cross-platform/DECISIONS.md` and
`approvals-log.jsonl` supersede the "Stage 1 only" rule above. No Stage 2 lock,
lock push or search launch happens without the user's recorded approval.


## Current stage supersedes the earlier Stage 1-only restriction

User approval24 authorized Stage2. Stage1 is complete; the exact search path
passed its smoke test, the user made the repository public, and the registration
was locked, pushed and verified. Registered search run55d43a42 is now active
under the35USD cap. Follow the canonical handoff; do not duplicate it. Stop
after its checked Stage2 report for approval before Stage3.
