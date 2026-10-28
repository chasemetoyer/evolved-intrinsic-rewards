# Paper detector impact audit

**Stage 1 is paused. This report audits existing paper records; no new training or policy replays were run. The Zenodo release and manuscript were not modified.**

The audit covers every actual round 2–5 run: 43 runs and 775 seed-runs, including the selected round-5 calibration. The records establish the scope of the defects, but do not retain enough transition information to count every historically missed event. Unknown counts below are not zero. [Machine-readable per-run evidence](per-run.json) · [CSV](per-run.csv) · [Independent number checks](number-check.json).

## What changes, and what remains unknown

| Question | Audit finding |
|---|---|
| Missed box openings | Structurally zero opportunities in the completed DoorKey and default KeyCorridor tasks: neither places boxes. The documented generic detector nevertheless failed to detect box opening/removal. The Setup must say that open covered doors only. |
| Terminal pickups | The detector skips physical events on every terminating or truncating transition. Whole-training counts of omitted eligible pickups are not recoverable. Successful KeyCorridor target-ball pickups can be counted in the retained final window, but were deliberately ineligible under the registered key-only reward. |
| Door references after reset | More precisely, an empty pre-reset door cache. It exposes 11,120 initial training episodes across 39 runs; the open reward/state channel is active in 10,480 of those episodes. These are exposed episodes, **not counts of missed openings**. Actual missed transitions are unknown. The cache refreshes after the first episode of each environment. |
| Existing solve counts and curve areas | All 25 applicable round-4/round-5 solve-count comparisons and 500 per-seed curve-area comparisons match the raw logs. No correction to these archived numbers is demonstrated by the audit. This is not an exhaustive regeneration of every number or p-value in the paper. |
| An additional reported quantity | The farming replay’s reported “pickups per episode” counted **pickup-action attempts made while carrying nothing**, not successful pickups. Its numeral is reproducible, but its description needs correction; the successful-pickup count is unavailable. |
| Conclusions after repairing the implementation | Not established. The paper’s empirical comparisons remain descriptions of the implementation actually run. The audit cannot certify that retraining with corrected detectors would preserve solve counts, learning speed, statistical significance, or the wireheading/farming conclusions. The mathematical bounded-return proof remains valid for the archived reward. |

The definite corrections are to the methods and interpretation of the replay counter. There is no evidence here for replacing measured learning results with hypothetical corrected-agent results. Equally, the absence of historical event traces does not establish that the defects were harmless.

## Every round 2–5 run

DK = DoorKey-8x8; KC = KeyCorridorS3R1. U = not identifiable from retained records. N/A = the intrinsic event detector or the relevant event definition does not apply. “Blind episodes” counts the initial episode of each parallel environment, not omitted door transitions. All tasks in this table have zero box opportunities; “0” in the box column is a structural result. “Off” marks the explore-only mask, where the missing door/pickup events cannot change those reward/state coordinates.

| Round / arm | Run | Task | Seeds | Box omissions | Eligible terminal pickups omitted | Blind episodes | Open channel |
|---|---|---|---:|---|---|---:|---|
| 2 / N1 | [ed5147b6](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/ed5147b6-c861-48b2-b9ff-1952774d5658/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / N2 | [74b2b2d0](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/74b2b2d0-7f04-48ec-a1f8-6d78af326fd2/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / N3 | [af4373da](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/af4373da-8be6-4a69-aa61-404ce37103d1/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / N4 | [b58ec6e0](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/b58ec6e0-291c-47a2-838b-57783d35214f/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / N5 | [eb8555bd](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/eb8555bd-afbf-484d-b1fc-30faa29648b6/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / N6 | [bced806e](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/bced806e-eccb-434b-be50-ad91f57a9dfb/config.toml) | DK | 10 | 0 | U | 160 | On |
| 2 / pay-once | [5b13189d](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/5b13189d-614e-48c4-96b7-431838a41e1c/config.toml) | DK | 10 | 0 | U | 160 | On |
| 3 / R1 | [4cac9e0a](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/4cac9e0a-5ab1-442f-9d25-62d625570ee0/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R2 | [eea13605](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/eea13605-38d3-4e23-adf3-a10cfc5bcbae/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R3 | [3d03a914](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/3d03a914-1a1d-4422-9d29-7ea01b422f2f/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R4 | [fff9fd5b](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/fff9fd5b-1dd3-4c51-b95c-0ead1e089fd0/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R5 | [c3d67c09](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/c3d67c09-a955-4220-a44e-bfbb68308bce/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R6 | [89d8e34c](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/89d8e34c-dcbb-45d7-8aab-d20e928f2825/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R7 | [135d1475](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/135d1475-e4cf-4a4f-8ca2-be0d84c1d409/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R8 | [1205f6d0](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/1205f6d0-b06c-4061-8621-ccfb17787fb8/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R9 | [a7cb164e](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/a7cb164e-db25-4428-aa9f-165f0c285814/config.toml) | DK | 20 | 0 | U | 320 | On |
| 3 / R10 | [07653362](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/07653362-50c4-4b7a-9506-2c0428496fba/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / A1a | [a97113a1](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/a97113a1-8de5-4940-a548-26275a829e4f/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / A1b | [3629f9a7](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/3629f9a7-8038-452a-bbef-53d5685e0a85/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / A1c | [1d549b2f](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/1d549b2f-663c-4931-b8d5-6ce42c0a523c/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / A2a | [224a7d96](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/224a7d96-a57b-451d-b33e-1e156bf74fbe/config.toml) | DK | 20 | 0 | U | 320 | Off |
| 4 / A2b | [7a364fed](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/7a364fed-a875-4d3d-a366-21a162be994d/config.toml) | DK | 20 | 0 | U | 320 | Off |
| 4 / A2c | [2d94fc36](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/2d94fc36-66b9-40db-b192-13b54b12bb6c/config.toml) | DK | 20 | N/A; no boxes | N/A | N/A | N/A |
| 4 / B1 | [bb00e7e5](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/bb00e7e5-65d0-4411-a236-2dacc19f0e63/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B2 | [a8f5efc4](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/a8f5efc4-63e7-4a55-8020-08f7e7cff7bb/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B3 | [78c44406](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/78c44406-6e63-466f-b309-8dfb82bfe663/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B4 | [f0a40d20](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/f0a40d20-3702-4087-803c-8db52fefaf1e/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B5 | [4d3b84f0](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/4d3b84f0-9f83-4f15-a20b-34c32c14ed36/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B6 | [a6e11900](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/a6e11900-bf82-4dd1-8f07-48a8f55cffbc/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B7 | [115c6566](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/115c6566-d1b2-4ea2-9c6d-06b31317381c/config.toml) | DK | 20 | 0 | U | 320 | On |
| 4 / B8 | [fb860207](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/fb860207-8246-4393-b352-0f74a9e88da2/config.toml) | DK | 20 | 0 | U | 320 | On |
| 5 / A1 | [022a3e90](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/022a3e90-09c1-43dc-8c4e-3a266d1ee5d0/config.toml) | DK | 20 | N/A; no boxes | N/A | N/A | N/A |
| 5 / A2 | [1c7b2eda](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/1c7b2eda-0224-4a90-9755-26051f89f3f0/config.toml) | DK | 20 | N/A; no boxes | N/A | N/A | N/A |
| 5 / B10 | [a25b7c99](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/a25b7c99-84bb-4cbb-a742-5594444b7fc1/config.toml) | DK | 20 | 0 | U | 320 | On |
| 5 / B11 | [896b2863](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/896b2863-59b7-44c0-addc-4091b9bab73c/config.toml) | DK | 20 | 0 | U | 320 | On |
| 5 / B9 | [b971c18d](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/b971c18d-0fd7-4c68-b627-eb098b0b3569/config.toml) | DK | 20 | 0 | U | 320 | On |
| 5 / C1 | [c14516de](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/c14516de-0174-4001-b8b2-5125e8aa49d3/config.toml) | KC | 20 | N/A; no boxes | U | 320 | On |
| 5 / C2 | [ad87a02f](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/ad87a02f-7353-4a64-8c32-e981408dd774/config.toml) | KC | 20 | N/A; no boxes | U | 320 | On |
| 5 / C3 | [aa29d1c3](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/aa29d1c3-78f8-4c3d-b58f-ee45102255cf/config.toml) | KC | 20 | N/A; no boxes | U | 320 | On |
| 5 / C4 | [2153e884](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/2153e884-0de7-4f7c-b942-27507be467ef/config.toml) | KC | 20 | N/A; no boxes | U | 320 | On |
| 5 / C5 | [35c840cd](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/35c840cd-2776-4817-9ac0-1f21f93c5e4d/config.toml) | KC | 20 | N/A; no boxes | U | 320 | On |
| 5 / C6 | [6571bce6](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/6571bce6-65f1-4227-aade-a4b2a6ac357e/config.toml) | KC | 20 | N/A; no boxes | N/A | N/A | N/A |
| 5 / calibration | [bd005cb8](/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/paper-impact-audit/release/run-records/bd005cb8-bad4-4321-a593-e4d3fc1a39fd/config.toml) | KC | 5 | N/A; no boxes | U | 80 | On |

For every enabled detector, the actual number of door transitions missed during the initial blind period is U. Eligible terminal door events are likewise U. The saved rolling means cannot locate actions at the first episode or at timeout, and overlapping means cannot be summed into event totals. The physical episode tracker starts after reset, so its door counter does not automatically share the detector’s initial blind period; it does also skip terminal physical events.

The run index follows the scored round maps. Earlier exploratory runs reused as reference comparators are not relabeled as round-2 runs. The older growth-1/40 replay is covered separately below. UnlockPickup was a planned calibration candidate, but no completed UnlockPickup run appears in this release’s round-5 calibration.

## What can be counted at terminal pickups

The following are exact counts of successful target-ball pickups among episodes completing in the last training window, aggregated over the configured seeds. The window begins after 90% of actual training steps. These ball pickups are deliberately excluded by `locked_door_key`; they are **not counts of erroneously omitted rewarded key pickups**. A successful target pickup also explains why the original comment “terminal-step pickups can’t happen” was incorrect. Additional pickup events on timeout are not identifiable.

| Round-5 arm | Target-ball pickups | Completed episodes in window | Intrinsic detector skipped these target events? |
|---|---:|---:|---|
| C1 | 257,255 | 257,255 | Yes; intentionally ineligible |
| C2 | 247,484 | 247,487 | Yes; intentionally ineligible |
| C3 | 231,234 | 231,240 | Yes; intentionally ineligible |
| C4 | 229,895 | 229,901 | Yes; intentionally ineligible |
| C5 | 20 | 14,785 | Yes; intentionally ineligible |
| C6 | 252,614 | 252,631 | N/A; task-only control |
| calibration | 62,140 | 62,141 | Yes; intentionally ineligible |

In DoorKey, successful termination is entering the goal, not picking up an object. Nevertheless, a pickup or door toggle can occur on the time-limit step, so “no terminal pickups” cannot be inferred for all DoorKey transitions.

## Archived replay coverage

| Replay family | Policies | Retained episode count | Initial cache exposures | Open channel active on exposures |
|---|---:|---|---:|---:|
| replay-growth-1-40 | 10 | Not recorded as a total | 10 | 10 |
| replay-n1 | 10 | Not recorded as a total | 10 | 10 |
| replay-n6 | 10 | Not recorded as a total | 10 | 10 |
| replay-payonce | 10 | Not recorded as a total | 10 | 10 |
| exploratory-replay-A2b | 20 | 60 | 20 | 0 |
| farming-policy-returns | 10 | 2000 | 0 | 0 |
| tamper-policy-returns | 80 | 16000 | 0 | 0 |
| bound-check | Path families | Not recorded as a total | 0 | 0 |

The older mechanism replays expose 60 initial episodes, of which 40 have an active open channel. Their stored summaries contain action-attempt frequencies and averaged needs, not ordered trajectories. The later learned-policy replay families retain 18,000 per-layout episode summaries and initialize after reset. They still omit the action/state/event sequences needed to reconstruct corrected terminal rewards.

The older replay writer’s default episode count is overridable and is not evidence of its historical invocation. Its action sampler also lacks an explicitly seeded Torch generator. A fresh replay of a final checkpoint would be a new diagnostic, not reconstruction of the historical training trajectory. [Detailed replay evidence](replay-audit.md) · [Structured replay inventory](replay-audit.json).

## Exact proposed paper corrections

The complete replacement text for Setup, the tamper paragraph, and a limitations/corrections entry is in [Setup corrections — draft](setup-corrections.md). The core changes are: open covered doors only; physical events were skipped at termination and truncation; training began with an empty door cache until the first episode ended; evaluation initialized after reset; and KeyCorridor’s target-ball pickup was intentionally outside the key-only reward.

The replay wording correction is in [Replay wording — draft](replay-wording-correction.md). Both documents describe the implementation that generated the archived results. Neither has been applied to the paper or archive.

The paper’s potential-difference ceiling does not require correct event detection. Each need remains in its prescribed bounded interval, and tampering remains a valid zero-need transition. This algebraic validity does not determine the effect of detector fixes on learning or empirical conclusions.

## Provenance and checks

The local release ZIP matches the size and checksum returned by Zenodo for DOI `10.5281/zenodo.23708846`. All 3,139 entries in its SHA256 manifest passed; the extracted files also match the ZIP. SHA256 of the unchanged ZIP: `2af41b79e648e1bef653754b7e98e5e05499e40715bd1c2e8abdfef4e470419b`. [Integrity record](archive-integrity.json).

The exact historical learner, intrinsic module, configuration and seed runner were recovered for every audited run. All 172 files match the recorded Git commits byte for byte. The effective configuration printed in each released log matches its saved configuration, and every configured seed has a complete metric sequence and summary. [Source verification](source-verification.json).

The audit protocol was hash-locked and committed before these numerical calculations, then pushed to the private project repository. The saved GitHub ref and server `pushed_at` corroborate publication; the author timestamp alone is not used as proof. This remains a retrospective audit: the bug hypotheses, existing paper results, source code and selected records were already known when the audit protocol was locked.

An additional runtime-provenance discrepancy needs resolution before any future cross-platform claim: the A1b log identifies Python 3.12.12, while the archived requirements select NumPy 2.5.4 on that Python branch. The unqualified NumPy 2.4.6 statement in the handoff/paper does not identify that runtime. This selection follows from log plus dependency markers; the release does not retain a per-run installed-package inventory. It is not a measured import-version result. The preserved MiniGrid/Gymnasium source versions support the detector control-flow audit.

All new tables are generated from the archived records by the audit scripts, and the independent checker recomputes their counts from raw inputs. Numerical score checks use the paper’s arithmetic mean of logged training success and its final-log-window solve threshold; the standardized audit values do not replace the original round-2 farming classifications. See [number-check.json](number-check.json) for the precise checks and their limits.

**Stop point:** no Stage 1 validation rollouts, determinism runs, cross-platform runs, calibration, evolution, or random search were launched. Stage 1 will remain on hold pending review of this audit.
