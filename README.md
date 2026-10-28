# Evolved intrinsic rewards — Stage 1

Can an evolutionary search over generic intrinsic-reward parameters help PPO
learn faster on unseen tasks, and resist a tamper action introduced afterward?
This repository currently implements infrastructure and baseline calibration
only. Evolution and random search are not authorized in Stage 1.

This project follows *Satisfied, Not Solving: Wireheading of Bounded Homeostatic
Rewards in Reinforcement Learning*, DOI 10.5281/zenodo.23708846. Source materials
are retained in [handoff-cross-platform](handoff-cross-platform/README.md).
The repository is private; the user will make it public before Stage 2 locks.

## Source and carryover map

| Item | Original source | New location / treatment |
|---|---|---|
| A1 PPO and CNN | `handoff-cross-platform/code/final-round5/ppo.py`; exact A1b snapshot in `code/a1b-run-commit-1533734` | Archived files unchanged. `stage1/corrected_ppo.py` adapts reset/attachment, event capture and diagnostics; optimization, encoder and evaluation code retain archived bodies. |
| A2 MiniGrid wrappers and event detection | Archived PPO wrappers and `intrinsic.py::EventDetector`, including `locked_door_key` | Wrappers reused; `generic_reward.py` supplies corrected pre-autoreset capture. The archived-detector platform check directly executes the exact A1b snapshot. |
| A3 satiation and tamper | Archived `intrinsic.py::Homeostatic` and PPO extrinsic press-cost handling | Three-need arithmetic retained for the descriptive control; new signed four-need module in `generic_reward.py`. Tamper action remains 6. |
| A4 statistical tools | `handoff-cross-platform/scripts/score_round4.py` and `score_round5.py` | `stage1/statistics.py`: exact Fisher, Clopper–Pearson, exact/permutation MWU, permutation JT, Holm. Two-sided MWU support is explicit for calibration. |
| A5 unbiased evaluation quota | Archived PPO `evaluate`, round 4 onward | Same per-environment quota and 64 episodes per environment type. |
| A6 checked numbers | `handoff-cross-platform/scripts/check_numbers.py` and companion generators | Audit checker in `audits/`; Stage 1 score/report scripts regenerate numbers and cross-check raw outputs. |
| B1 hand-wired subgoal caveat | Paper and approved impact audit | New reward uses generic events; no key/door subgoal reward. Current successful-target-pickup exclusion is explicit and flagged for Stage 2 review. |
| B2 bounded rewards remain exploitable | Paper and approved impact audit | Growth bounded; tamper reset/cost retained; corrected realized event counters retained for repeated-event diagnostics. |
| B3 advantage normalization | Archived PPO setting | On in every Stage 1 training configuration. |
| B4 easy KeyCorridor candidate | Paper | Fixed task-selection rule in `preregistration/stage1.md` and `stage1/score.py`; no tuning to force inclusion. |
| B5 behavior labels descriptive | Paper corrections | Success-curve area and solve counts remain primary. |
| C1 immutable pre-registration | Original templates in handoff | `preregistration/stage1.md`, lock, source-input hashes; later changes only through timestamped amendments. |
| C2 corroborated lock publication | User's process correction | Commit and GitHub ref/server publication receipt before evidence. |
| C3 disjoint seed roles | User's Stage 1 instruction | Calibration 900–904; validation 905–909; determinism 910–911. Historical 40–44 only in explicitly authorized descriptive runs. Future roles reserved in the protocol. |
| C4 one comparison platform | User's Stage 1 instruction | Every scientific worker runs on the same pinned Modal image; local orchestration only. |
| C5 fixed scoring and balanced reporting | User's Stage 1 instruction | Mechanical selection, complete-cell requirements, failures and incomplete cells retained. |
| C6 secrets | User's Stage 1 instruction | `.gitignore` precedes research commits; Modal credentials come from external environment/settings. |
| C7 stage boundary | User's Stage 1 instruction | Stop after the Stage 1 report. Stage 2 outline is a draft only. |

The [approved paper impact audit](handoff-cross-platform/paper-impact-audit/report/paper-impact-audit.md)
documents the inherited detector limitations, unknown historical counts, and
exact correction drafts. The Zenodo deposit and its local release copy remain
unchanged.

## Current corrected event definitions

- `new_view`: previously unseen exact post-action 7x7 symbolic view in this
  episode, including the true final view; reset view is not preinserted.
- `pickup`: actual None-to-object carrying transition, including final steps,
  except a successful target pickup that itself terminates the task with
  positive raw task reward. Excluded targets are recorded separately.
- `drop`: successful object-to-None carrying transition caused by drop.
- `toggle`: a door's open/locked state changes, or a toggled box is removed or
  replaced by its contents. Final-step changes count.

Capture occurs before SAME_STEP autoreset, and detector attachment occurs only
after reset. Final-step inclusion, box inclusion, target-pickup exclusion, and
after-reset attachment are fixed for Stage 1 and listed as open Stage 2 decisions.

## Reproducible execution

Use Python 3.12.12 and `uv sync --locked`. The Python/NumPy branch follows the
archived Mac runtime log and dependency markers, as disclosed in the audit and
Stage 1 protocol. The container base digest, all dependency versions and runtime
inventories are recorded. Do not copy virtual environments between worktrees.

The fixed run command is `bash scripts/run_stage1.sh`, invoked by the project's
tracked experiment runner after the registration lock and GitHub receipt are
committed. Its local controller submits separate Modal Function calls for each
configuration/task/seed; training and validation occur only on Modal. Do not
invoke a learner directly. The first validation worker must pass before training
starts. The manifest contains only validation, determinism, descriptive checks,
and calibration. Budget reservations include in-flight calls and failed work;
the total Stage 1 limit is $15.

Outputs are persisted on the Modal volume and retrieved to `results/`. The
Stage 1 report and supporting data are durable project artifacts, with a copy of
the report in the repository. Dollar estimates and provider billing evidence
are labeled separately. Large checkpoints and credentials are excluded from Git.
