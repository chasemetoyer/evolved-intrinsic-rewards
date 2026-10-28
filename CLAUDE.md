# evolved-intrinsic-rewards — start here

This project is handed between AI agents (Claude, ChatGPT and others) through a
shared, model-independent handoff on this Mac. Claude Code loads it through
these imports:

@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/CONTINUE-HERE.md
@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/SESSION-RULES.md
@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/DECISIONS.md

If those imports did not load, read the three files directly before doing
anything else. The folder is untracked on `main`; milestone copies are
committed on `orx/stage-1-infrastructure-and-calibration`. The user's latest
instructions take precedence over every file here.

## Session rules (summary; SESSION-RULES.md is authoritative)

Start of session
- Read the files above, then `approvals-log.jsonl`, `session-state.json`,
  `runtime-state.json`, `run-registry.json`, `budget.json` and the last
  entries of `session-log.jsonl` in the same folder.
- Check the lock in `agent-owner.json`. If another agent owns it, only read.
  Take over only with the user's authorization, by claiming the lease from
  the recorded research worktree with `scripts/checkpoint.py --claim`.
- Check live processes and `orx runs`. Never start a second controller.
- Reconcile the ledger with Modal using read-only queries (never `.get()` an
  in-flight call) and spending with `budget.json`.

During the session
- Detached launches only: `orx exp run`, or `nohup` helpers with their PID
  recorded in the handoff folder.
- Write before wait: every run is recorded with key, status, Modal call ID
  and cost before anyone waits on it; refresh `run-registry.json` first.
- Never relaunch a recorded run; reconnect through its call ID.
- Never stop or replace the controller or its Modal app without approval.
- Checkpoint after every step with `scripts/checkpoint.py` (note and exact
  next action). Append every user approval to `approvals-log.jsonl`.
- Locked registration files are immutable; use timestamped amendments.

End of session
- Final checkpoint: what passed, what remains, active run and process IDs,
  spending evidence and the exact next action. Keep the lease while your
  watcher runs; release it only when handing off. Stop at stage boundaries.
