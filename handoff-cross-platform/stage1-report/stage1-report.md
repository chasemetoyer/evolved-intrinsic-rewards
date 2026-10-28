# Stage 1 report

Status: complete. Stage 2 has not started.

All empirical numbers below are generated from retained outputs. `stage1-numbers.json` contains the full precision values and provenance. The independent number-check result is required for final handoff.

## Carryover verification

| Item | Location | Verification / disposition |
| --- | --- | --- |
| A1 PPO / CNN | handoff-cross-platform/code/*/ppo.py; stage1/corrected_ppo.py | Archived source retained; corrected adapter keeps learner/CNN and Table 10 settings. |
| A2 wrappers / modes | generic_reward.py; stage1/corrected_ppo.py; archived intrinsic.py | Corrected reset/terminal capture; legacy locked_door_key remains available; validation records below. |
| A3 satiation / tamper | generic_reward.py; archived intrinsic.py | Need reset and extrinsic press cost covered by validation. |
| A4 statistical procedures | stage1/statistics.py; tests/test_scoring.py | Archived procedures reused; known statistical examples checked in validation. |
| A5 quota evaluation | archived ppo.py:evaluate | Per-environment episode quota preserved. |
| A6 number checking | scripts/report_stage1.py; scripts/check_numbers.py | Generated JSON and report; independent cross-check required. |
| B1 generic events | generic_reward.py | Four generic events; successful terminal target pickup excluded under the approved correction. |
| B2 refill / farming / tamper | generic_reward.py; stage1/manifest.json | Growth bounds enforced; repeated paid events retained; tamper experiment deferred. |
| B3 advantage normalization | stage1/manifest.json | Enabled in every Stage 1 arm. |
| B4 easy-task calibration | stage1/score.py | Fixed room-to-improve rule applied without tuning. |
| B5 primary metrics | stage1/score.py | Curve area and solve count primary; behavior labels descriptive. |
| C1 immutable lock | preregistration/stage1-lock.json; scripts/verify_lock.py | Input hashes checked before runs; later changes need timestamped amendments. |
| C2 corroborated lock | preregistration/stage1-github-receipt.json | Committed lock and GitHub receipt checked before launch. |
| C3 seed roles | stage1/manifest.json | Calibration roles separated; paper seeds restricted to descriptive reproduction. |
| C4 same platform / pins | stage1/modal_app.py; pyproject.toml; uv.lock | All new evidence uses Modal; per-attempt complete installed package inventory retained. |
| C5 fixed scoring | stage1/score.py; preregistration | No formulas fitted to outcomes; failures and unavailable cells retained. |
| C6 credentials | .gitignore; environment / Modal configuration | Credential ignore rules established before source publication. |
| C7 stage boundary | this report and draft outline | Stop for approval before Stage 2. |

## Corrected detector definitions

The new project uses corrected detection throughout. The archived-detector Modal reproduction is the explicitly authorized exception. Physical events are captured before SAME_STEP autoreset, and new_view uses the true final observation on a final step.

| Event | Exact Stage 1 definition |
| --- | --- |
| new_view | Exact bytes of the symbolic 7x7 post-action observation not yet seen in this episode. The reset view is not preinserted; clear seen views after processing a terminal/truncated transition. |
| pickup | Carrying changes from nothing to any object, except a pickup that itself terminates the task with positive raw task reward. Excluded successful target pickups are recorded separately. A timeout alone does not exclude a pickup. |
| drop | An executed drop action changes carrying from an object to nothing. Blocked attempts do not count. |
| toggle | A door changes open/locked state, including closing/reopening, or a toggle action removes/replaces a box with its contents. Blocked attempts do not count. |

| Choice | Fixed Stage 1 behavior | Stage 2 pre-registration |
| --- | --- | --- |
| Final-step events | Count, subject to the successful target-pickup exception | OPEN decision |
| Box openings | Count as toggle | OPEN decision |
| Successful target pickup | Excluded from paid pickup event; separately diagnosed | OPEN decision |
| Detector attachment | Only after the initial seeded reset | OPEN decision |

The corrected descriptive satiation control maps new_view/pickup/toggle to the original three needs and observed state; it adds no drop need. The four-event module retains all four needs, including zero-weight channels.

## Validation and signed ceiling

Validation `validation-detector-and-reward`: complete=yes; passed cases=30, passed subtests=23; XML aggregate tests=53, testcase nodes=30, failures=0, errors=0, skipped=0; passed=yes. The XML aggregate includes subtests and is not the number of standalone test cases.
Numerical bound checks: 240 episode/prefix records; 0 tolerance violations; tolerance=2e-05.

Both detectors on the same recorded trajectories:

| Seed | Steps | new_view disagreements | pickup disagreements | drop disagreements | toggle disagreements | Reward mismatches |
| --- | --- | --- | --- | --- | --- | --- |
| 905 | 1000 | 0 | 0 | 8 | 0 | 0 |
| 906 | 1000 | 0 | 0 | 4 | 0 | 0 |
| 907 | 1000 | 0 | 0 | 9 | 0 | 0 |
| 908 | 1000 | 0 | 0 | 12 | 0 | 0 |
| 909 | 1000 | 0 | 0 | 12 | 0 | 0 |

Drop is an added channel absent from the archived detector and has zero weight in the reduction configuration; its disagreement counts are not detector defects. Per-step disagreement details and indices are retained in the JSON. The reduction criterion concerns arithmetic on recorded paper events; the detector comparison is separate.

Corrected event totals in the recorded corpus:

| Event | Count |
| --- | --- |
| new_view | 539 |
| pickup | 48 |
| drop | 45 |
| toggle | 0 |
Coverage limitation: this random DoorKey corpus contains no toggle events. Its detector agreement cannot validate door or box fixes; targeted fixtures cover those cases.

`reduction-summary.json`:

| Seed | Scalar steps | Bit identical |
| --- | --- | --- |
| 905 | 1000 | yes |
| 906 | 1000 | yes |
| 907 | 1000 | yes |
| 908 | 1000 | yes |
| 909 | 1000 | yes |

| Targeted coverage | Test | Passed |
| --- | --- | --- |
| Initial empty/stale door cache | test_initial_door_cache_is_populated_after_reset | yes |
| Box opening and timeout events | test_box_and_timeout_events_compare_both_detectors_on_same_transition | yes |
| Terminal pickup, target exclusion and physical events | test_any_object_pickup_drop_toggle_and_terminal_capture | yes |

Evidence limits: targeted fixture pass status and source are retained, but detailed fixture trajectories were not saved. The recorded corpus retains observations/actions/done/events/rewards; it does not retain raw object states, raw task rewards, separate termination/truncation flags or need histories. Need histories can be reconstructed from the saved events. The separate bound-rollout helper did not retain its own raw arrays. Independent verification against the saved reduction corpus reproduces the bound returns, but does not establish direct provenance of those unretained helper arrays.

Let $V(h)=\sum_k w_k h_k^2$, $L=\sum_k\min(w_k,0)$, and $U=\sum_k\max(w_k,0)$. The archived dynamics apply one clip after growth minus event relief: $h_{t+1}=\operatorname{clip}(h_t+g-s e_t,0,1)$, followed by an optional tamper reset. For one episode or finite prefix with $0<\gamma\le1$:

$$G_T=V(h_0)-(1-\gamma)\sum_{t=1}^{T-1}\gamma^{t-1}V(h_t)-\gamma^{T-1}V(h_T).$$

The coefficients on future potentials are nonnegative and sum to one. Consequently $V(h_0)-U\le G_T\le V(h_0)-L$. At fixed $h_0=.5$, the upper bound is $\frac14\sum_{w_k\ge0}w_k+\frac34\sum_{w_k<0}|w_k|\le3$. For nonnegative unit weights on the three legacy needs this reduces to $.75$. Episode resets are not paid transitions; adding returns over repeated episodes does not inherit a single-episode constant ceiling. Floating-point checks use an explicit numerical tolerance.

## Modal, reproducibility and spending

Declared environment:

```json
{
  "python": "3.12.12",
  "dependencies": [
    "gymnasium==1.4.0",
    "minigrid==3.2.0",
    "modal==1.6.3",
    "numpy==2.5.4",
    "pytest==9.2.0",
    "scipy==1.17.1",
    "tomli-w==1.2.0",
    "torch==2.14.1",
    "trackio==0.43.0"
  ]
}
```

One function input represents one configuration/task/seed/budget. Outputs and complete package inventories are stored on the Modal volume and synchronized with hashes. Raw timing and serializer metadata are excluded from numerical bit-identity checks.

Python 3.12.12 and NumPy 2.5.4 follow the archived Mac runtime log and conditional dependency markers. This choice was registered before new results; the earlier unconditional NumPy 2.4.6 statement was incomplete. The container base digest and each attempt's actual installed package inventory are retained in environment/provenance files. The full transitive package lock is uv.lock.

| Task / method | Seed | Budget | Completed repeats | Numerically bit identical |
| --- | --- | --- | --- | --- |
| DoorKey-8x8 / episodic_count | 910 | 131072 | 2 | no |
| DoorKey-8x8 / episodic_count | 911 | 131072 | 2 | yes |

### Determinism outcome and container CPU types

| Seed | Replicate | Attempt | CPU type | AVX-512 | Inferred ATen tier | Pair bit identical |
| --- | --- | --- | --- | --- | --- | --- |
| 910 | 0 | 30f0df23 | AMD Zen 3 (Milan range) | no | AVX2 | no |
| 910 | 1 | f8db40e3 | AMD Zen 4 (Genoa range) | yes | AVX512 | no |
| 911 | 0 | c99c1ddb | AMD Zen 3 (Milan range) | no | AVX2 | yes |
| 911 | 1 | dd58f416 | AMD Zen 3 (Milan range) | no | AVX2 | yes |

Seed 910: both calls used the same source commit; installed package inventories identical: yes; the specifications differ only in id, replicate. The logged metrics first differ at row 0 (step 20480), in approx_kl, v_loss only (relative differences approx_kl 1.8e-05, v_loss 2.3e-07); every rollout statistic in that row is identical. Episode statistics first differ at row 5 (step 122880). 7 of 7 logged rows differ. At the last row (step 131072), training success is 0.12 versus 0.15 and mean training return 0.0519 versus 0.0570.

Interpretation (consistent with the records, not a controlled test): every mismatched pair ran on two different CPU types and every matching pair ran on one CPU type. A difference that starts in the last bits of optimizer statistics while episodes are still identical is the signature of floating-point rounding, not of a seeding or logic difference. The matching pair also shows that the replicate label does not enter the computation. The pattern is consistent with PyTorch and its math libraries choosing CPU-specific vector kernels: different kernels sum float32 values in a different order, and PPO's sampled actions then amplify the last-bit differences into different trajectories. The evidence is 2 planned pairs, and no execution setting was changed in response. Modal assigns containers from a mixed CPU pool (next section), so separate calls with the same seed are not guaranteed to be bit identical. The open Stage 2 decision on CPU instruction-set pinning addresses this.

## Modal containers and CPU types

Every worker attempt saved /proc/cpuinfo. Modal's gVisor sandbox reports the model name as unknown, so the CPU type is identified from vendor, family, model and instruction-set flags, using range-based CPUID labels. The ATen tier is inferred from the flags with PyTorch's dispatch rule (AVX512 requires avx512vl, avx512bw, avx512dq and FMA3); the workers did not record PyTorch's own capability string. Attempts superseded by a provider preemption exist only on the Modal volume; their metadata was copied with hashes into the shared handoff folder.

| CPU type | AVX-512 | Inferred ATen tier | Final attempts | Superseded attempts | Unfinished |
| --- | --- | --- | --- | --- | --- |
| AMD Zen 3 (Milan range) | no | AVX2 | 110 | 1 | 0 |
| AMD Zen 4 (Genoa range) | yes | AVX512 | 11 | 0 | 0 |
| Intel 6/55h (Skylake-SP family) | yes | AVX512 | 1 | 0 | 0 |
| Intel 6/55h, Cascade Lake class | yes | AVX512 | 29 | 0 | 0 |
| unmapped (AuthenticAMD family 23 model 49) | no | AVX2 | 3 | 0 | 0 |
| unmapped (GenuineIntel family 6 model 143) | yes | AVX512 | 1 | 0 | 0 |

Superseded attempts. Modal restarted the same input under the same call ID, and the controller charged the whole call, including the lost attempt:

| Run | Superseded attempt | CPU type | Wall seconds before stop | Recorded error |
| --- | --- | --- | --- | --- |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed41-r0 | 547b824b | AMD Zen 3 (Milan range) | 440.1 | KeyboardInterrupt:  |

The per-container list is in the appendix.

Spending record (guard estimates and provider-reported completed intervals are distinct from an invoice):

```json
{
  "completed_training_calls": 154,
  "guard_total_usd": "2.8835326375965309242140",
  "provider_invoice_cost_usd": null,
  "provider_reported_complete_intervals_cost_usd": "1.52017854",
  "limit_usd": "15",
  "overhead_allowance_usd": "0.50",
  "setup_failures": [
    {
      "reason": "ImageBuildError: Image build for im-l05pUtZrKBR79SHh6TH0yS failed.\nView the build logs:\n  modal image logs im-l05pUtZrKBR79SHh6TH0yS",
      "utc": "2026-10-28T03:13:39.723246+00:00"
    },
    {
      "reason": "ImageBuildError: Image build for im-VnCm75YY9OuotFjAaroUJ5 failed.\nView the build logs:\n  modal image logs im-VnCm75YY9OuotFjAaroUJ5",
      "utc": "2026-10-28T03:21:28.338465+00:00"
    }
  ],
  "setup_attempt_guard_usd": "0.25",
  "setup_guard_basis": "Protective reservation per failed or in-flight build, not invoice cost",
  "limitations": "Estimates include a protective overhead allowance. Provider accounting is delayed; this is not a guaranteed invoice cap.",
  "ledger_call_count": 155
}
```

## Descriptive Mac reference

The two Modal groups are compared with the same original Mac reference using counts and curve areas only. No inferential tests or cross-platform conclusions are drawn, and no configuration is adjusted from this comparison.

| Seed | Mac solve / area | Archived Modal solve / area | Corrected Modal solve / area |
| --- | --- | --- | --- |
| 40 | 1 / 0.886626 | 1 / 0.813312 | 1 / 0.910162 |
| 41 | 1 / 0.923900 | 1 / 0.937822 | 1 / 0.927251 |
| 42 | 1 / 0.840422 | 1 / 0.915478 | 1 / 0.928759 |
| 43 | 1 / 0.826787 | 1 / 0.862162 | 1 / 0.864688 |
| 44 | 1 / 0.925675 | 1 / 0.915594 | 1 / 0.918247 |

| Group | Completed | Solve count | Mean curve area |
| --- | --- | --- | --- |
| mac | 5 | 5 | 0.880682 |
| archived_modal | 5 | 5 | 0.888873 |
| corrected_modal | 5 | 5 | 0.909821 |

## Calibration

AUC is the arithmetic mean of logged rolling training success. Solve requires mean success at least .9 over the final floor(10%) of log rows. First-solved medians include unsolved seeds right-censored at the nominal budget. Actual training stops at the last complete PPO batch. Cost columns are function-compute estimates, with invoices retained separately. Partial cells are descriptive and cannot select a task.

| Task | Method | Budget | Completed | Solves | Mean AUC | Median first solve | Censored | Mean wall seconds | Mean estimated USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DoorKey-8x8 | none | 1000000 | 5/5 | 0 | 0.087066 | 1000000 | 5 | 403.0 | 0.007068 |
| DoorKey-8x8 | none | 2000000 | 5/5 | 3 | 0.367180 | 1320976 | 2 | 756.3 | 0.013266 |
| DoorKey-8x8 | episodic_count | 1000000 | 5/5 | 1 | 0.195111 | 1000000 | 4 | 416.4 | 0.007303 |
| DoorKey-8x8 | episodic_count | 2000000 | 5/5 | 3 | 0.514341 | 701872 | 2 | 769.5 | 0.013498 |
| KeyCorridorS3R1 | none | 1000000 | 5/5 | 4 | 0.660076 | 290912 | 1 | 385.8 | 0.006768 |
| KeyCorridorS3R1 | none | 2000000 | 5/5 | 5 | 0.867794 | 247072 | 0 | 791.7 | 0.013886 |
| KeyCorridorS3R1 | episodic_count | 1000000 | 5/5 | 5 | 0.855368 | 189632 | 0 | 419.1 | 0.007351 |
| KeyCorridorS3R1 | episodic_count | 2000000 | 5/5 | 5 | 0.920398 | 200784 | 0 | 753.1 | 0.013209 |
| UnlockPickup | none | 1000000 | 5/5 | 0 | 0.004204 | 1000000 | 5 | 371.8 | 0.006521 |
| UnlockPickup | none | 2000000 | 5/5 | 0 | 0.003082 | 2000000 | 5 | 637.4 | 0.011180 |
| UnlockPickup | episodic_count | 1000000 | 5/5 | 0 | 0.005510 | 1000000 | 5 | 405.1 | 0.007105 |
| UnlockPickup | episodic_count | 2000000 | 5/5 | 0 | 0.006612 | 2000000 | 5 | 818.6 | 0.014358 |
| KeyCorridorS3R2 | none | 1000000 | 5/5 | 0 | 0.009043 | 1000000 | 5 | 379.0 | 0.006648 |
| KeyCorridorS3R2 | none | 2000000 | 5/5 | 0 | 0.004746 | 2000000 | 5 | 763.7 | 0.013395 |
| KeyCorridorS3R2 | episodic_count | 1000000 | 5/5 | 0 | 0.016268 | 1000000 | 5 | 399.9 | 0.007014 |
| KeyCorridorS3R2 | episodic_count | 2000000 | 5/5 | 0 | 0.053379 | 2000000 | 5 | 768.2 | 0.013474 |
| BlockedUnlockPickup | none | 1000000 | 5/5 | 0 | 0.001469 | 1000000 | 5 | 397.0 | 0.006964 |
| BlockedUnlockPickup | none | 2000000 | 5/5 | 0 | 0.001980 | 2000000 | 5 | 836.0 | 0.014663 |
| BlockedUnlockPickup | episodic_count | 1000000 | 5/5 | 0 | 0.005809 | 1000000 | 5 | 402.6 | 0.007062 |
| BlockedUnlockPickup | episodic_count | 2000000 | 5/5 | 0 | 0.008219 | 2000000 | 5 | 824.8 | 0.014467 |
| DoorKey-16x16 | none | 1000000 | 5/5 | 0 | 0.017126 | 1000000 | 5 | 477.5 | 0.008375 |
| DoorKey-16x16 | none | 2000000 | 5/5 | 0 | 0.045234 | 2000000 | 5 | 867.4 | 0.015215 |
| DoorKey-16x16 | episodic_count | 1000000 | 5/5 | 0 | 0.035647 | 1000000 | 5 | 482.8 | 0.008468 |
| DoorKey-16x16 | episodic_count | 2000000 | 5/5 | 0 | 0.033276 | 2000000 | 5 | 902.4 | 0.015827 |
| MultiRoom-N2-S4 | none | 1000000 | 5/5 | 5 | 0.918449 | 149616 | 0 | 466.2 | 0.008177 |
| MultiRoom-N2-S4 | none | 2000000 | 5/5 | 5 | 0.959837 | 150096 | 0 | 902.2 | 0.015825 |
| MultiRoom-N2-S4 | episodic_count | 1000000 | 5/5 | 5 | 0.919714 | 142368 | 0 | 492.9 | 0.008646 |
| MultiRoom-N2-S4 | episodic_count | 2000000 | 5/5 | 5 | 0.961469 | 137584 | 0 | 894.3 | 0.015686 |

| Task | Role | Selection | Best mean AUC | Reason |
| --- | --- | --- | --- | --- |
| DoorKey-8x8 | training | kept | 0.195111 | Fixed rule passed |
| KeyCorridorS3R1 | training | rejected | 0.855368 | Best baseline mean curve area exceeds 0.85 |
| UnlockPickup | training | kept | 0.005510 | Fixed rule passed |
| KeyCorridorS3R2 | held_out | kept | 0.053379 | Fixed rule passed |
| BlockedUnlockPickup | held_out | rejected | 0.008219 | Best baseline mean curve area is below 0.05 |
| DoorKey-16x16 | held_out | rejected | 0.045234 | Best baseline mean curve area is below 0.05 |
| MultiRoom-N2-S4 | held_out | rejected | 0.961469 | Best baseline mean curve area exceeds 0.85 |

Training-task baseline separation at the fitness budget uses two-sided MWU (exact without ties, permutation with ties), Holm-adjusted across the three planned tasks. A missing or non-significant result does not establish equal performance; the fitness budget remains a user decision.

| Task | Novelty − task-only mean AUC | p | Holm p | Detected separation |
| --- | --- | --- | --- | --- |
| DoorKey-8x8 | 0.108044 | 0.690476 | 1.000000 | no |
| KeyCorridorS3R1 | 0.195291 | 0.055556 | 0.166667 | no |
| UnlockPickup | 0.001306 | 0.690476 | 1.000000 | no |

## Cost projection

Stage 2 requires 240 candidates across both search methods, three training seeds per task: 720 training runs per kept training task, before finalist re-evaluation. Candidate runtime is not yet measured; the baseline mean is a planning proxy. No projection selects tasks from incomplete cells.

| Stage 2 fitness budget scenario | Training runs | Estimated USD |
| --- | --- | --- |
| 1000000 | 1440 | 10.0790 |
| 2000000 | 1440 | 18.8287 |

Stage 3 baseline-roster scenarios (not commitments):

| Methods | Training runs | Estimated USD |
| --- | --- | --- |
| 3 | 180 | 2.3751 |
| 4 | 240 | 3.1668 |
| 5 | 300 | 3.9585 |

Additional tamper training scenarios, if the no-tamper Stage 3 runs serve as controls:

| Methods | Extra tamper conditions | Additional runs | Additional estimated USD |
| --- | --- | --- | --- |
| 3 | 1 | 180 | 2.3751 |
| 3 | 2 | 360 | 4.7502 |
| 4 | 1 | 240 | 3.1668 |
| 4 | 2 | 480 | 6.3336 |
| 5 | 1 | 300 | 3.9585 |
| 5 | 2 | 600 | 7.9171 |

Excluded from these projections: Candidate re-evaluation, storage/egress, image builds, failed calls, and billing changes need additional allowance.

## Stage 2 draft and decisions

DRAFT, NOT LOCKED

No evolutionary or random-search evaluation has been run. Every proposal below
needs approval at the Stage 1 boundary before it becomes a Stage 2 commitment.

- Genome: four events, each with weight in [-1,1], relief in [0,1], and growth either zero or log-scaled in [1/640,1/20]; h0=.5 fixed. Preserve the corrected generic event definitions approved for Stage 1, including exclusion of success-terminal target pickup. Twelve physical parameters. A proposed latent representation uses direct bounded weight/relief coordinates and a growth coordinate with a zero atom plus a positive logarithmic interval. OPEN: zero-atom probability/threshold, transformation, clipping/reflection at CMA boundaries, initialization and sigma.
- Event semantics — four separate OPEN decisions for the Stage 2 lock: retain final-step event inclusion; retain box-opening inclusion; retain successful target-pickup exclusion; retain attachment only after the initial seeded reset. These are fixed for the present Stage 1 batch and must not be silently treated as locked Stage 2 choices. Also confirm exact-view byte novelty, no preinserted reset view, and state-change rather than attempted-action events.
- Fitness proposal: equal-weight mean training-success curve area over the kept training tasks and three seeds per candidate at the chosen fitness budget. No task-specific fitted formula and no held-out-task feedback. OPEN: confirm the budget, aggregation, treatment of failed/time-limited evaluations, and safeguards for repeated positively paid events.
- CMA-ES: population ten, twelve generations. OPEN: optimizer/library version, seed and initial mean/covariance/sigma; stopping behavior under numerical failure; number of finalists and independent re-evaluation seeds/budget; winner tie-break and whether to reserve candidate evaluations for re-evaluation.
- Random-search control: the same number of candidate evaluations, task set, training budgets and seed counts. OPEN: prior over mixed zero/log growth, matched handling of boundary atoms, winner re-evaluation, and whether random-search winner joins final evaluation. No search starts in Stage 1.
- Seeds: calibration 900–999, evolution 1000–1999, random search 3000–3999, final evaluation 2000–2999. OPEN: exact within-role allocation, common versus fresh candidate seed panels, independent finalist panel, and layout seed mapping. Never reuse seeds across roles.
- Cross-CPU numerical reproducibility — OPEN decision for the Stage 2 lock: test whether forcing ATEN_CPU_CAPABILITY=avx2 and MKL_CBWR=AVX2 makes seed 910 bit-identical across Zen 3 and Zen 4 containers. If it does, use these settings in Stage 2. If it does not, record the CPU type for every run and treat same-seed results as unpaired. This test was not run in Stage 1. Note for the test design: PyTorch normally runs batched float32 CPU convolutions through oneDNN, whose kernel instruction set is controlled separately (ONEDNN_MAX_CPU_ISA) and is not set by these two variables.
- Final evaluation: best evolved reward and approved baselines, twenty fresh seeds per kept task, nominal two-million-step training, fixed per-environment evaluation quota. OPEN: baseline roster (task-only, episodic novelty, random-search winner, fixed satiation); whether task aggregation or individual tasks are primary; independent versus paired seed comparisons; minimum worthwhile effect; multiplicity family. Proposed tests retain exact Fisher for solves and exact MWU without ties/permutation MWU with ties for area, Clopper–Pearson intervals, and Holm adjustment. A superiority hit should require the registered direction and adjusted p<.05; numerical level predictions need prewritten intervals. Non-significance does not establish equivalence.
- Tamper test: introduce the done-action need reset only after search. OPEN: freeze policy versus retrain/fine-tune a learner under the selected reward; matched no-tamper condition; free versus paid presses and costs; tasks/methods; budget/seeds; performance noninferiority margin and test; whether press frequency is a separate endpoint. Keep presses and repeated paid events descriptive unless explicit hit rules are locked. Resistance requires a defined performance criterion; bounded return alone is insufficient.
- Budget: approve measured cost projection, re-evaluation overhead, and a hard spending limit. Make the repository public before the Stage 2 lock, commit and push every lock file, and record timestamped amendments. No Stage 3 lock is implied by this draft.


Stage boundary: no evolution or random search starts from this report. User approval and resolution of the listed open decisions are required.

## Appendix: CPU type of every Modal container

| Run | Attempt | Role | CPU type | Vendor / family / model | AVX-512 | Inferred ATen tier | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validation-detector-and-reward | 6e0212d1 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| determinism-DoorKey-8x8-episodic_count-131072-seed910-r0 | 30f0df23 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| determinism-DoorKey-8x8-episodic_count-131072-seed910-r1 | f8db40e3 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| determinism-DoorKey-8x8-episodic_count-131072-seed911-r0 | c99c1ddb | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| determinism-DoorKey-8x8-episodic_count-131072-seed911-r1 | dd58f416 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform-DoorKey-8x8-homeostatic-2000000-seed40-r0 | b1922224 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed40-r0 | a3bae323 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform-DoorKey-8x8-homeostatic-2000000-seed41-r0 | fd1d0f2d | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed41-r0 | 547b824b | superseded | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | modal-volume-copy |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed41-r0 | 5f223620 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| cross_platform-DoorKey-8x8-homeostatic-2000000-seed42-r0 | 9010dc09 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed42-r0 | 61eb92c5 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform-DoorKey-8x8-homeostatic-2000000-seed43-r0 | 10b91c9d | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed43-r0 | edc98396 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform-DoorKey-8x8-homeostatic-2000000-seed44-r0 | a40c6ae7 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| cross_platform_corrected-DoorKey-8x8-homeostatic-2000000-seed44-r0 | f9c24da9 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-1000000-seed900-r0 | 9dfbbde5 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-DoorKey-8x8-episodic_count-1000000-seed900-r0 | 32b8cd17 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-1000000-seed900-r0 | 11808a8e | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-1000000-seed900-r0 | 0a945893 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-none-1000000-seed900-r0 | 40652b3f | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-episodic_count-1000000-seed900-r0 | 60629bab | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-none-1000000-seed900-r0 | 596b3cae | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-1000000-seed900-r0 | 75313630 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-1000000-seed900-r0 | 4f5db775 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-1000000-seed900-r0 | bf5f5f1a | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-1000000-seed900-r0 | fa334f0e | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-1000000-seed900-r0 | 914a5176 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-none-1000000-seed900-r0 | d3bf8db3 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-1000000-seed900-r0 | dbdb800b | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-1000000-seed901-r0 | cadacf02 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-1000000-seed901-r0 | 8c5b7534 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-1000000-seed901-r0 | b86e38a2 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R1-none-1000000-seed901-r0 | 83125dbe | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-episodic_count-1000000-seed901-r0 | 89fec4dd | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-1000000-seed901-r0 | 8fac6029 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-1000000-seed901-r0 | 6ed4eec3 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-1000000-seed901-r0 | 28efd197 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-1000000-seed901-r0 | 0f2be257 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-1000000-seed901-r0 | 496cadec | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-DoorKey-16x16-episodic_count-1000000-seed901-r0 | de45c3d6 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-1000000-seed901-r0 | 2d2233a8 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-1000000-seed901-r0 | ae5082e3 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-none-1000000-seed901-r0 | e30784fd | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-1000000-seed902-r0 | cc23316c | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-1000000-seed902-r0 | 0b5fdddc | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-1000000-seed902-r0 | 0c7b9175 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-1000000-seed902-r0 | ebd26c93 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-none-1000000-seed902-r0 | af9d7587 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-1000000-seed902-r0 | f9469993 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-1000000-seed902-r0 | 1e38ef86 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-1000000-seed902-r0 | c13a72b5 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-1000000-seed902-r0 | b2ffa8a7 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-1000000-seed902-r0 | 1bd4f641 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-1000000-seed902-r0 | ceaa6e27 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-1000000-seed902-r0 | d2aea3e2 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-none-1000000-seed902-r0 | f44a2462 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-1000000-seed902-r0 | 6dc22f8e | final | unmapped (AuthenticAMD family 23 model 49) | AuthenticAMD / 23 / 49 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-1000000-seed903-r0 | b2d99bac | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-1000000-seed903-r0 | be8697b5 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-1000000-seed903-r0 | 61200237 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-1000000-seed903-r0 | 2d244693 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-1000000-seed903-r0 | 98c1de46 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-1000000-seed903-r0 | 3ce0417f | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-1000000-seed903-r0 | f03320c7 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-1000000-seed903-r0 | 1f6abf72 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-1000000-seed903-r0 | 4125259b | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-1000000-seed903-r0 | c75b7369 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-1000000-seed903-r0 | b4e61b39 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-1000000-seed903-r0 | bb36c06b | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-1000000-seed903-r0 | be7c3112 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-none-1000000-seed903-r0 | 94cab164 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-1000000-seed904-r0 | 806788e6 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-1000000-seed904-r0 | dbb0b4ab | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-1000000-seed904-r0 | 171eb1ba | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-1000000-seed904-r0 | 9253a912 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-none-1000000-seed904-r0 | 7a2ff556 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-episodic_count-1000000-seed904-r0 | 13536f14 | final | Intel 6/55h (Skylake-SP family) | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-none-1000000-seed904-r0 | 30161ccb | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-1000000-seed904-r0 | 2264c8ff | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-1000000-seed904-r0 | 7d46d630 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-1000000-seed904-r0 | d6a8978e | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-1000000-seed904-r0 | d8a8041b | final | unmapped (GenuineIntel family 6 model 143) | GenuineIntel / 6 / 143 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-none-1000000-seed904-r0 | 7534dd55 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-1000000-seed904-r0 | 46c56600 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-1000000-seed904-r0 | fa3d1916 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-2000000-seed900-r0 | 7b99353f | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-2000000-seed900-r0 | 08e82543 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-2000000-seed900-r0 | 379f4dbb | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-2000000-seed900-r0 | b00bce27 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-UnlockPickup-none-2000000-seed900-r0 | d59386a6 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-2000000-seed900-r0 | f4d32612 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-none-2000000-seed900-r0 | 6a78bc0c | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-2000000-seed900-r0 | e0e25f3c | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-2000000-seed900-r0 | ccdae848 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-2000000-seed900-r0 | 634f11eb | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-2000000-seed900-r0 | 2ec0211c | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-2000000-seed900-r0 | 0d56449c | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-none-2000000-seed900-r0 | e7bd8cdd | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-2000000-seed900-r0 | f10a7d11 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-2000000-seed901-r0 | dc0497a7 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-2000000-seed901-r0 | 3554967a | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-2000000-seed901-r0 | 7ec9d117 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-2000000-seed901-r0 | 3846927e | final | unmapped (AuthenticAMD family 23 model 49) | AuthenticAMD / 23 / 49 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-2000000-seed901-r0 | df7eba70 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-2000000-seed901-r0 | 7b16d7b5 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-2000000-seed901-r0 | ce66870d | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-2000000-seed901-r0 | 3c878a35 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-2000000-seed901-r0 | 93ee3fad | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-2000000-seed901-r0 | fc55a07e | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-2000000-seed901-r0 | 0012a4f7 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-DoorKey-16x16-none-2000000-seed901-r0 | bab661b9 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-2000000-seed901-r0 | c0050fd0 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-none-2000000-seed901-r0 | 22c8b215 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-2000000-seed902-r0 | f51d3336 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-2000000-seed902-r0 | 545fcf08 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-2000000-seed902-r0 | 024f20e3 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-2000000-seed902-r0 | 97137297 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-2000000-seed902-r0 | 11ee5899 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-2000000-seed902-r0 | 7ae5fb87 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-none-2000000-seed902-r0 | 5536319c | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-2000000-seed902-r0 | 13f6b3fe | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-2000000-seed902-r0 | 0cb34c6f | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-2000000-seed902-r0 | 62ffa318 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-2000000-seed902-r0 | 661c787b | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-2000000-seed902-r0 | 155c0b16 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-none-2000000-seed902-r0 | 641c60d7 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-2000000-seed902-r0 | 5d761a50 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-DoorKey-8x8-episodic_count-2000000-seed903-r0 | 9f6104e4 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-2000000-seed903-r0 | 8f165ab6 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-2000000-seed903-r0 | 4d30488a | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R1-none-2000000-seed903-r0 | e119219a | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-2000000-seed903-r0 | 81112bf2 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-2000000-seed903-r0 | a93fa992 | final | AMD Zen 4 (Genoa range) | AuthenticAMD / 25 / 17 | yes | AVX512 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-2000000-seed903-r0 | a059ba67 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-2000000-seed903-r0 | 473167a2 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-2000000-seed903-r0 | 05266cf2 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-2000000-seed903-r0 | 4665d204 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-2000000-seed903-r0 | 51f44a1a | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-2000000-seed903-r0 | 16aea733 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-2000000-seed903-r0 | 0d72828e | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-none-2000000-seed903-r0 | 59a3c21d | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-none-2000000-seed904-r0 | b8215786 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-8x8-episodic_count-2000000-seed904-r0 | 92f0ca03 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-none-2000000-seed904-r0 | 7cdf93d5 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R1-episodic_count-2000000-seed904-r0 | 0cb25a88 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-none-2000000-seed904-r0 | 25ba3ebd | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-UnlockPickup-episodic_count-2000000-seed904-r0 | 92af84cf | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-none-2000000-seed904-r0 | 9020d793 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-KeyCorridorS3R2-episodic_count-2000000-seed904-r0 | 13968484 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-BlockedUnlockPickup-none-2000000-seed904-r0 | 0804bc43 | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-BlockedUnlockPickup-episodic_count-2000000-seed904-r0 | bcbdc4e5 | final | unmapped (AuthenticAMD family 23 model 49) | AuthenticAMD / 23 / 49 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-none-2000000-seed904-r0 | e7799e0f | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-DoorKey-16x16-episodic_count-2000000-seed904-r0 | 169e6a52 | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
| calibration-MultiRoom-N2-S4-none-2000000-seed904-r0 | db567a4c | final | Intel 6/55h, Cascade Lake class | GenuineIntel / 6 / 85 | yes | AVX512 | synced-results |
| calibration-MultiRoom-N2-S4-episodic_count-2000000-seed904-r0 | ee4e40cb | final | AMD Zen 3 (Milan range) | AuthenticAMD / 25 / 1 | no | AVX2 | synced-results |
