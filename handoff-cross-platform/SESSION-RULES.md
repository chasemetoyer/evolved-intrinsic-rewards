# Session rules for every agent

Added 2026-10-28 by `claude_opus_5_5_chat_864bae6d` at the user's request.
These rules complement `CONTINUE-HERE.md` (takeover steps), `DECISIONS.md`
(approved scope) and `approvals-log.jsonl` (append-only approvals). The user's
latest instructions take precedence over every file here.

## Shared files

| File | Role | Written by |
|---|---|---|
| `CONTINUE-HERE.md` | Takeover entry point | agents, by hand |
| `SESSION-RULES.md` | These rules | agents, by hand |
| `DECISIONS.md` | Curated summary of approved scope and constraints | agents, by hand |
| `approvals-log.jsonl` | Append-only user approvals, exact quotes when available | agents, one line per approval |
| `agent-owner.json` | Lock: the single agent allowed to edit, commit or launch | `scripts/checkpoint.py --claim/--release` |
| `session-log.jsonl` | Append-only checkpoints with note and exact next action | `scripts/checkpoint.py` (manual runs) |
| `session-state.json` | Latest full state, refreshed every 30 s | checkpoint watcher |
| `runtime-state.json` | Live controller state on every ledger change | the controller |
| `run-registry.json` | Every manifest run: key, status, Modal call ID, cost, containers and CPU type | `scripts/run_registry.py` |
| `budget.json` | Spending per stage against its cap | `scripts/run_registry.py` |
| `container-cpu-log.jsonl` | Append-only CPU type of every Modal container (attempt) | `scripts/run_registry.py` |
| `stage1-container-cpu/volume-attempts/` | Metadata copies of attempts never synced, e.g. preempted ones | `scripts/run_registry.py` |
| `.checkpoint-watcher.pid`, `.run-registry-watcher.pid` | PIDs of the detached helpers | the agent that started them |

## Start of session

1. Read in order: `CLAUDE.md` or `AGENTS.md`, `CONTINUE-HERE.md`, this file,
   `DECISIONS.md`, `approvals-log.jsonl`, then `session-state.json`,
   `runtime-state.json`, `run-registry.json`, `budget.json` and the last
   entries of `session-log.jsonl`.
2. Check the lock in `agent-owner.json`. If another agent owns it, do not
   edit, commit or launch; reading is fine. Take over only when the user
   authorizes it, by claiming from the recorded research worktree:
   `uv run --locked python scripts/checkpoint.py --claim --owner <name> --note '<why>' --next-action '<next>'`.
   The previous owner's watcher exits on its next tick by design. Restart the
   watcher under your name, detached, and record its PID. Never stop a running
   controller in order to take over.
3. Check live processes: the controller (`scripts/run_stage1.sh`,
   `python -m stage1.modal_app`), both watchers, and `orx runs`. A controller
   can outlive any chat. Never start a second controller.
4. Reconcile before acting. Compare ledger calls with Modal using read-only
   queries (call-graph status, app list, volume listing). Never call `.get()`
   on an in-flight call; result collection belongs to the controller. Compare
   spending with `budget.json`.
5. Checkpoint the start with a note and the exact next action.

## During the session

1. **Detached launches only.** Compute starts only through `orx exp run`
   (supervised by the OpenResearch app) or, for helper processes, through
   `nohup … &` with the PID written into this folder. Never run training or a
   controller as a foreground process of a chat.
2. **Write before wait.** Every run is recorded with its key, status, Modal
   call ID and cost reservation before anyone waits on it. The controller
   ledger does this for each Modal call: reserve, persist, submit, record the
   call ID, persist. Refresh `run-registry.json`
   (`uv run --locked python scripts/run_registry.py`) before every wait or wake.
3. **Never relaunch a recorded run.** A key already in the ledger or registry
   (complete, running, reserved or uncertain) is reconnected through its call
   ID and never resubmitted. A Modal preemption restart (same call ID, new
   attempt folder) is not a relaunch; it is logged. An uncertain call blocks
   new launches until its state and charges are reconciled. A frozen
   experiment node is never re-run.
4. Do not stop, cancel or replace the controller or its Modal app without the
   user's explicit approval. Keep the OpenResearch app open and the Mac online
   while it runs: the controller is the app's child process and holds an
   ephemeral Modal app.
5. **Checkpoint after every step:**
   `uv run --locked python scripts/checkpoint.py --owner <name> --note '<what happened>' --next-action '<exact next action>'`.
6. Record each user approval the moment it is given: append one line to
   `approvals-log.jsonl` with the exact quote. Never edit or delete earlier
   lines; supersede them with a new line.
7. Locked registration files are immutable. A change to a registered
   implementation file needs a timestamped amendment with replacement hashes,
   committed and pushed before use. New helper files are listed in the
   amendment's `added_unregistered_files`, never in `implementation_sha256`.
8. Budget: stop before the next reservation could cross the stage cap. Report
   the guard, measured compute and Modal-billed amounts as separate numbers.
9. The CPU type of every Modal container is logged in
   `container-cpu-log.jsonl`. Same-seed runs on different CPU types are not
   expected to be bit-identical.

## End of session

1. Final checkpoint: what passed, what remains untested, active process and
   run IDs, spending evidence, and the exact next action.
2. Refresh `run-registry.json` and `budget.json`; commit milestone copies of
   the handoff files on the research branch and push.
3. Keep the lock while your watcher runs. Release it (`--release`) only when
   handing off.
4. Stop at stage boundaries for the user's approval.
