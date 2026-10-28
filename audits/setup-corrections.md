# Draft Setup corrections for the existing paper

**Draft for review; the paper and archived training code have not been edited.**
This text describes the implementation that produced the archived results. It is
not a claim that a corrected implementation would produce the same outcomes.
The audit protocol was locked in commit
`26c14faf193a4bd21388b0f4673ace0d712aee71` before the audit's numerical checks.
This document contains source-level corrections; insert numerical audit findings
only from the separate checked audit report. No new training was performed to
write these paragraphs.

## Proposed replacement after equation (1) in Setup

The explore event is an exact 7×7 egocentric symbolic view not previously seen
after an action in the current episode. The reset observation is not inserted
into the seen-view set. On terminating and truncating steps, novelty is computed
from the final observation, before clearing that set. In DoorKey, the grasp
event is a transition from carrying nothing to carrying an object, and the open
event is a change in a cached door's open or locked state, including closing a
door. These physical events are detected only on nonterminating, nontruncating
steps. In KeyCorridor, the `locked_door_key` mode instead restricts grasp to
picking up a key and open to a closed-to-open transition of a door that was
locked at episode start; reopening that door counts again. Picking up the target
ball ends the task and is deliberately outside this key-only reward definition.
The registered DoorKey and KeyCorridor tasks contain no boxes. Although the
generic detector's documentation mentioned boxes, its implementation compares
only door-specific open/locked attributes and does not detect opening or
removing a box.

The training code attaches the event detector before the first seeded reset.
MiniGrid's constructor grid is empty, so each parallel environment's door cache
remains empty during its initial training episode. The first termination or
truncation triggers an autoreset and refreshes that cache from the next episode's
grid. Novelty and pickup detection operate during the initial episode; this
initialization issue concerns door detection. Evaluation resets environments
before attaching the detector and therefore does not have that initial blind
period. On every terminating or truncating transition, the detector skips
physical grasp/open events because the vector environment has already reset;
this can omit an otherwise eligible key pickup or door event at the time limit.
The code comment that terminal pickups cannot occur was too broad: pickup-goal
environments can terminate on a pickup, even though the KeyCorridor target-ball
pickup is intentionally excluded by its reward definition.

## Proposed addition to the tamper paragraph

Tamper handling is applied after the ordinary need update and still sets all
needs to zero when the done action is pressed, including on a terminal or
truncated step. Intrinsic reward is calculated before resetting needs to their
initial value for the next episode. A nonnegative per-press cost, when enabled,
is deducted from the training extrinsic reward without multiplying it by the
intrinsic coefficient; task-success metrics retain the raw environment reward.
The skipped physical-event detection described above does not disable this
tamper mechanism.

## Proposed limitation or correction-list entry

The reported results describe the archived implementation, including its
initial-episode door cache and its omission of terminal physical events. A
source audit establishes those differences from a fully transition-based event
definition, but does not establish how training with repaired detectors would
change the learning curves, solve counts, or behavioral comparisons. In
particular, the initial blind period is limited to the first episode of each
parallel training environment; that limit is not evidence that its learning
effect is negligible. The box-detection discrepancy does not identify a missing
box event on the registered DoorKey or KeyCorridor tasks, because their
generators do not place boxes. UnlockPickup was a planned calibration candidate,
rather than a completed run in this release. It contains a box, but its planned
key/locked-door mode excluded target-box pickup and box toggling from the
registered reward definition. Corrected-implementation outcomes must be
reported separately from observations made with the archived implementation.
The potential-difference ceiling remains mathematically valid for any event
sequence because needs remain bounded and tampering is a valid transition to
zero needs; this fact alone does not validate the detector semantics or quantify
their experimental effects.

## Source mapping

All references below resolve to files retained under the project's
`handoff-cross-platform` directory. Line numbers refer to unchanged source
snapshots. The Markdown links are relative to this draft.

| Correction | Source and exact location |
|---|---|
| Event definitions, cached objects, terminal skip | [Final archived intrinsic module](../handoff-cross-platform/code/final-round5/intrinsic.py), lines 47–116; `_start` at 74–83, `_state` at 85–86, terminal skip at 97–99, key/locked-door mode at 109–115. |
| Same defects already present in the exact A1b snapshot | [A1b intrinsic module](../handoff-cross-platform/code/a1b-run-commit-1533734/intrinsic.py), lines 47–97. |
| Training attach before reset; evaluation reset before attach | [Final PPO](../handoff-cross-platform/code/final-round5/ppo.py), lines 223–227 and 281–303; [A1b PPO](../handoff-cross-platform/code/a1b-run-commit-1533734/ppo.py), lines 211–214 and 271–286. |
| Empty constructor cache, rather than a prior populated layout | [MiniGrid constructor](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/minigrid_env.py), lines 109–111; [empty Grid](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/core/grid.py), lines 28–35; [vector constructor](../handoff-cross-platform/paper-impact-audit/dependencies/gymnasium/vector/sync_vector_env.py), lines 111–181; [RoomGrid constructor](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/core/roomgrid.py), lines 72–102. |
| Seeded reset generates the populated grid | [MiniGrid reset](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/minigrid_env.py), lines 119–157. |
| Physical terminal state is replaced before detector call | [SAME_STEP autoreset](../handoff-cross-platform/paper-impact-audit/dependencies/gymnasium/vector/sync_vector_env.py), lines 318–334; [PPO final-observation restoration](../handoff-cross-platform/code/final-round5/ppo.py), lines 337–350 and 241–246. |
| Time limits can coincide with otherwise valid pickup/toggle | [MiniGrid step](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/minigrid_env.py), lines 560–588: action effects precede the truncation check. |
| Box opening is invisible to door-only attributes | [Box class and toggle](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/core/world_object.py), lines 272–293; compare archived intrinsic `_state`, lines 85–86. |
| DoorKey contains key and door, with goal termination | [DoorKey generator](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/envs/doorkey.py), lines 74–99; [goal termination](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/minigrid_env.py), lines 550–556. |
| Registered KeyCorridor uses ball target, no box | [KeyCorridor default and generator](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/envs/keycorridor.py), lines 74–78 and 103–125; [registrations](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/__init__.py), lines 255–264; [object constructor](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/core/roomgrid.py), lines 209–228. |
| Successful ball pickup terminates KeyCorridor | [KeyCorridor step](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/envs/keycorridor.py), lines 128–136. |
| UnlockPickup contains a target box and terminates on pickup | [UnlockPickup](../handoff-cross-platform/paper-impact-audit/dependencies/minigrid/envs/unlockpickup.py), lines 82–105; [registered calibration semantics](../handoff-cross-platform/preregistration-template/preregistration.md), Part C operational details. |
| Tamper and episode-need-reset order | [Final archived intrinsic module](../handoff-cross-platform/code/final-round5/intrinsic.py), lines 161–172. |
| Extrinsic tamper cost and raw task metrics | [Final PPO](../handoff-cross-platform/code/final-round5/ppo.py), lines 311 and 337–353. |
| Existing reward equation and ceiling | [Supplied paper](../handoff-cross-platform/preprintpaper.pdf), Setup equation (1) and Proposition 1. |

## Dependency provenance and version limitation

The source snapshots were copied byte-for-byte from the session's installed
MiniGrid 3.2.0 and Gymnasium 1.4.0 packages. Their distribution metadata is
retained beside the source, and [versions.json](../handoff-cross-platform/paper-impact-audit/dependencies/versions.json)
records original paths and SHA-256 hashes. The independent file list is
[SHA256SUMS](../handoff-cross-platform/paper-impact-audit/dependencies/SHA256SUMS).
These are selected source files for this audit, not a complete historical
runtime environment.

The [original A1b run log](../handoff-cross-platform/paper-impact-audit/release/run-records/3629f9a7-8038-452a-bbef-53d5685e0a85/log)
declares CPython 3.12.12 on its first line. The
[archived requirements](../handoff-cross-platform/paper-impact-audit/release/code/requirements.txt)
select NumPy 2.4.6 for Python below 3.12 and NumPy 2.5.4 for Python 3.12 or later
(lines 82 and 88). Thus the handoff README's unqualified NumPy 2.4.6 statement
does not by itself identify the original run environment. Selection of NumPy
2.5.4 for that logged Python version follows from the archived lock markers;
it is an inference, not an imported-version measurement from the original run.
The release [README](../handoff-cross-platform/paper-impact-audit/release/README.md)
states that per-run Python environments were excluded. This source audit does
not claim bit-identical learning between that original runtime and the current
Python 3.11 audit environment.
