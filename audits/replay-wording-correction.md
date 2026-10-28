# Draft correction to the replay description

This is proposed replacement wording only. The original manuscript and release were not edited.

## Original passage

> “The DoorKey farming is genuine. Replays of the 1/20 farmers show 137–184 pick-ups per 640-step episode, with pick-up and drop taking 48–63% of their actions.”

Location: supplied preprint, Section 5.5, DoorKey/normalization-on bullet, PDF page 12. The original sentence is supported by the N6 replay fields and generated number keys listed in the companion audit.

## Proposed replacement

> **Repeated pickup/drop attempts in the recorded replays.** For the policies classified as 1/20 farmers, the archived replay summaries record per-policy means of 137–184 pickup attempts while not carrying per episode, with a mean episode length of 640 steps. Pickup and drop actions together account for 48–63% of actions. These counters measure attempted actions and do not establish how many pickups succeeded or how many drop–pickup cycles completed.

## Companion qualification

> The older replay script attached its event detector before the first explicit environment reset, exposing each policy’s first replay episode to stale initial door references. Its saved summaries contain no action or state trajectories. The effect on the recorded need and return averages cannot be quantified from those summaries. These summaries describe the implementation actually replayed, rather than a corrected replay or corrected training run.

The following return/need bullet may retain its archived numerical values only with this qualification; no corrected numerical replacement is identified by the retained records.

## Counter semantics

The writer increments `pickups` for action 3 while not carrying, `drops` for action 4 while carrying, and `toggles` for action 5. It does not verify state transitions. It then averages these counts across replay episodes. Its `success` field is also an episode-average fraction, not a literal success count or a whole-training solve label. Fractional success values cannot determine the missing episode denominator uniquely. Action frequencies are rounded to three decimal places before saving.

Table 2 was independently reconstructed from retained per-layout arrays: all 44 displayed numerical values match, and all 560 per-policy means agree within the numerical-check tolerance of 1e-12. This checks arithmetic for the retained replay, not corrected-detector counterfactuals.

Sources: `handoff-cross-platform/preprintpaper.pdf`; `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay_checkpoints.py:45-70`; `handoff-cross-platform/paper-impact-audit/release/scripts/make_numbers.py:324-341`; `handoff-cross-platform/paper-impact-audit/paper-tables/replay.tex`. Reproduction script: `audits/audit_replays.py`.
