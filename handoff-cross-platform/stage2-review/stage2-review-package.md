# Stage 2 review package — approved choices, pre-lock verification pending

**Status:** nothing is locked, no lock has been pushed, and the Stage 2 search has
not been launched.

Updated for approval entry 24 (2026-10-28). The earlier pre-lock checks are
retained below as historical evidence:

- the pinned determinism test;
- a secret scan of the repository history;
- smoke-mode tests of the new controller, CMA-ES and random search.

**New required gate: pending.** The exact registered `search` mode, its validator
branch and its plan wiring must now pass a tiny-budget test with seeds at or
above 5000. The earlier smoke-mode result does not satisfy that gate. Report the
new result as pass/fail only, with no learning-performance values. The lock must
freeze code that has already run.

The user approved the decisions in section 7, including a **$35 Stage 2 cap**
covering pre-lock checks and a **separate $10 Stage 3 cap**. After receiving this
updated draft and the exact-path smoke result, the user makes the repository
public. No lock, lock push or registered search launch occurs before that step.

Historical spending snapshot from the preceding review, all in the shared
Stage 2 ledger; refresh after the new smoke test before final delivery:

- **Guard:** $0.910, including the $0.50 allowance, for 120 calls.
- **Measured compute:** $0.13.
- **Modal-billed (complete hours only):** $0.059.

Files in this folder:

- [stage2-preregistration-draft.md](stage2-preregistration-draft.md)
- [pinned-determinism-summary.json](pinned-determinism-summary.json)
- [stage2-cost-projection.json](stage2-cost-projection.json)
- [smoke-test-result.json](smoke-test-result.json)
- [secret-scan-report.md](secret-scan-report.md)

## 1. Determinism result and the CPU-handling rule it implies

Run `ba62845c` (commit `613ef15`). The protocol (`stage2/determinism-protocol.md`)
was committed before the run. It used Stage 1's exact seed-910 spec with
`ATEN_CPU_CAPABILITY=avx2`, `MKL_CBWR=AVX2` and `ONEDNN_MAX_CPU_ISA=AVX2`. The stop
rule (at least 2 replicates each on Zen 3, Zen 4 and Intel) was met after two
waves.

| CPU class | Replicates | Fingerprint |
|---|---|---|
| AMD Zen 3 (family 19h, model 1) | 46 | A (`5e3565d7…`) |
| AMD Zen 4 (family 19h, model 17) | 5 | A (`5e3565d7…`) |
| Intel (model 85 × 11, model 106 × 2) | 13 | B (`04ecd790…`) |

**Reading, as the committed protocol prescribes.** The MKL pin was **not applied**
in the 51 AMD containers (51 of 64). So this test never ran with all three pins in
effect on AMD. By the protocol, the result reads as "pins not applied there", not
"pins insufficient".

- **Outcome:** with the settings you specified, seed 910 is **not bit-identical
  across Zen 3, Zen 4 and Intel**, so your rule applies.
- Whether all three pins *in effect* would give identity remains untested. The
  user has now explicitly declined the MKL COMPATIBLE follow-up.

The probe in every container shows which pins took effect:

- **ATen:** read AVX2 in 64 of 64 containers.
- **oneDNN:** reported AVX2 in 64 of 64, with `jit:avx2` convolutions.
- **MKL:** reported `CNR:AVX2` only on the 13 Intel containers. On AMD it reported
  `CNR:AUTO` and its generic code path. Intel documents that on non-Intel CPUs only
  the AUTO and COMPATIBLE modes are supported.

What the fingerprints show:

- **Within each class:** every replicate is identical.
- **Zen 3 vs Zen 4:** now identical. This is the pair that differed in Stage 1.
- **AMD vs Intel:** MKL is the only recorded difference between the two groups.
- **Stage 1 comparison:** neither pinned fingerprint equals a Stage 1 unpinned
  replicate.
- **Pinned vs unpinned Zen 3:** on Zen 3 the ATen and oneDNN caps match the
  defaults, so a mismatch is not obviously expected. It is *consistent with*
  Intel's note that an unsupported `MKL_CBWR` value on non-Intel CPUs switches MKL
  to the AUTO branch, "which may cause results to differ". This was not tested
  directly.

**Approved rule:** skip the MKL COMPATIBLE test, run unpinned, record the CPU type
for every run and treat same-seed results as unpaired. Exact cross-machine
reproducibility is an explicit limitation; integer seed matching does not remove
CPU-dependent numerical variation.

- The search runs unpinned. Pinning did not give full identity, and the pinned
  runs took 85.2 s on average against 71.8 s for the four unpinned Stage 1 runs of
  the same spec (×1.19; the CPU mix differs, so this is indicative only).
- Every container's CPU class is logged (`stage2-container-cpu-log.jsonl` in the
  handoff).

**Empirical concurrency check:** 32 containers were running at once (peak 32), all
writing to the Modal Volumes v2 volume.

## 2. Secret scan of the repository history

Covered: 8 refs, 19 commits and 2,567 blobs, including all Stage 2 commits up to
`ca8ce97`. **No credentials were found.**

| Check | Result |
|---|---|
| Your 8 live credential values (Modal token ID and secret from the environment and `~/.modal.toml`, GitHub token, `HF_TOKEN`, `RUNPOD_API_KEY`, Claude Code messaging token) | Absent from every blob and commit message |
| Token-format patterns (Modal, GitHub, AWS, PEM, Hugging Face, `sk-` keys) | No matches |
| Sensitive filenames ever committed | None |
| gitleaks 8.30.0 | 7 generic-api-key hits, all false positives (see below) |

The 7 gitleaks hits are:

- Modal's own public analytics key, in two saved copies of Modal web pages;
- experiment-name-to-UUID maps;
- a file-hash map.

Not secrets, but visible once the repository is public:

- your commit email (`cmetoyerbusiness@gmail.com`);
- your Northeastern email, in the extracted text of your own preprint;
- 592 absolute `/Users/chasemetoyer` paths;
- your preprint (`handoff-cross-platform/preprintpaper.pdf` and its extracted text), tracked on the research
  branches;
- the unpublished paper-correction drafts (`audits/setup-corrections.md`, `audits/replay-wording-correction.md`,
  `paper-tables/replay.tex` and their copies under `paper-impact-audit/report/`), also tracked on the research
  branches.

GitHub's live refs (`git ls-remote`) were checked: all five point to commits that were scanned.

## 3. Earlier smoke-mode tests and the new exact-path gate

Run `120ba00c` (commit `45f80a3`): 56 tiny calls at 8,192 steps, with seeds ≥ 5000
and optimizer RNG seeds different from the registered draft.

| Check | Result |
|---|---|
| Controller: 56/56 calls complete, 0 uncertain, no stop; every result hash-verified | **Pass** |
| Concurrency: 32 calls in flight (all 32 submitted before the first completion). The 30-s container sample peaked at 16 because smoke calls last about 30 s; sustained 32 running was shown in the determinism run | **Pass** |
| CMA-ES: 2 generations of ask/tell; replaying from recorded fitness reproduces the candidates exactly | **Pass** |
| Random search: 12 candidates, the same latent box and decoding (equal budget) | **Pass** |
| Every decoded genome within bounds; zero-growth atoms present | **Pass** |
| Finalist selection and a winner chosen for each method | **Pass** |
| CPU logged for all 56 containers; ISA probe in every attempt | **Pass** |
| First end-to-end training with the generic four-need reward (this path was only unit-tested in Stage 1) | **Pass** |

Locally, 15 orchestration tests pass, including an interrupted-resume test: recorded
calls are reattached, nothing recorded is resubmitted, and the same key set results.

The preceding evidence covers shared smoke-mode code, not the registered
`search` mode, its validator branch or its plan wiring. Those paths must be added
**before** the lock and exercised with tiny budgets and seeds >=5000. A new
pass/fail result must identify the tested source commit and confirm that path.
The lock commit must only freeze code already exercised. **New exact-path
result: pending**, not inferred from the earlier pass.

## 4. Draft pre-registration (summary; full text in the draft file)

| Item | Draft |
|---|---|
| Genome bounds | 4 events × (weight in [−1, 1], relief in [0, 1], growth 0 or in [1/640, 1/20]); h0 = 0.5. Shared latent [0, 1]^12; growth = 0 if u < 0, else (1/640)·32^u. Approved 50% zero-growth prior; intrinsic coefficient fixed at 1.0 |
| Fitness | Raw equal-weight mean training curve area over DoorKey-8x8 and UnlockPickup × 3 seeds, at nominal 2M steps; no task normalization or baseline subtraction |
| Training tasks | DoorKey-8x8 and UnlockPickup (Stage 1 fixed rule); KeyCorridorS3R2 held out |
| CMA-ES | pycma 4.5.0; population 10, 12 generations; mean z = 0.5; σ0 = 0.25; bounds [0, 1]^12; RNG seed 424242; generation barrier; resume by replay |
| Random search | 120 i.i.d. uniform candidates on the same box (`default_rng(535353)`), fixed at the lock |
| Finalists | Top 3 per method, re-evaluated on 10 fresh seeds per training task at 2M; winner = best re-evaluated mean |
| Seeds | CMA-ES 1000–1035; random search 3000–3035; finalists 1900–1909 and 3900–3909; final evaluation 2000–2019; tamper 2020–2039 |
| Final evaluation (Stage 3) | E, R, T and N, plus fixed satiation descriptive only; 20 seeds per kept task. Primary: E vs T, N and R on held-out area, one-sided MWU, Holm m = 3. A meaningful improvement requires adjusted p < .05 and observed mean E-minus-comparator area >= .05. Primary transfer claim rests on one held-out task. Secondary: training tasks, Holm m = 6. All tests unpaired |
| Tamper test (Stage 3) | Retrain E from scratch on DoorKey-8x8, free tamper vs disabled, 20 seeds each. Before any tamper run compute P0 = .25 sum(w) from the frozen winner. P0 > 0: predict lower area with tamper, one-sided MWU off > on. P0 <= 0: predict location-shift noninferiority, lower one-sided 95% Hodges–Lehmann shift bound > −.05. No paid variants |
| Failure handling | Candidate numerical failure: run area 0. Infrastructure failure: retry same input/call, retain all attempts and costs; maximum three retries. Stop new submissions if candidate failures / terminal logical runs > 5%, drain in-flight calls, then halt; no warm-up denominator |

## 5. Cost projection and the approved $35 / $10 caps

Source: [stage2-cost-projection.json](stage2-cost-projection.json) and
`scripts/stage2_projection.py`. The figures below are the **prior projection
snapshot**, produced when the cap was $30, before the newly required exact-path
smoke. They are not a refreshed spending statement. The approved caps are now
$35 for Stage 2 (including all pre-lock checks) and $10 for Stage 3. Regenerate
the machine-readable projection and current ledger snapshot after the new smoke;
do not treat the prior JSON's cap field as the current authorization.

Assumptions:

- **Run cost:** Stage 1 measured per-run 2M costs on the two training tasks
  (DoorKey-8x8 $0.01338, UnlockPickup $0.01277) stand in for candidate runs.
- **Overhead ratios:** Stage 1's billed/measured ratio (1.032) and guard/measured
  ratio (1.146).
- **Peak reservations:** 32 in-flight calls reserve $2.05.
- **Volume:** 1,560 runs (1,440 search + 120 finalist).

| Scenario | Measured compute | Expected billed | Guard at end | **Guard peak** | Duration at 32 |
|---|---|---|---|---|---|
| **Unpinned** (the rule above) | $20.40 | $21.04 | $24.29 | **$26.34** | ~10.5 h |
| Pinned (×1.19, historical reference; not selected) | $24.21 | $24.98 | $28.66 | **$30.71** | ~12.4 h |

- The unpinned scenario remains the selected plan. Keep the 3,600-second deadline
  and ten finalist seeds. Current headroom must be recomputed from the $35 cap
  and updated pre-lock ledger; candidate runtime is still a baseline-cost proxy.
- **Stage 3 is separately capped at $10.** The preceding estimate was roughly
  $4.49 measured and $5.15 on the guard basis: 300 final-evaluation runs
  (5 methods × 3 tasks × 20 seeds, $3.96) plus 40 tamper runs ($0.54). These are
  planning estimates, not measured Stage 3 spending or a billing guarantee.

## 6. Concurrency plan

- **Limits:**
  - controller: at most 32 calls in flight;
  - Modal Function: `max_containers = 32` (the per-function cap);
  - workspace: Modal's documented limit is 100 containers on Starter and 5,000 on
    Team, and the workspace had no other running containers.
- **Measured:** 32 containers running at once in the determinism run.
- **Storage:** all outputs go to the Modal Volumes v2 volume
  `evolved-intrinsic-rewards-stage2`. v1, which Stage 1 used, recommends at most
  five writers.
- **Scheduling:**
  - CMA-ES generations take the critical path (60 runs per generation, two waves);
  - random-search runs fill the free slots;
  - finalist re-evaluation follows once both searches are complete.
- **Budget and resume:** each call reserves its 3,600-s deadline plus a 60-s
  termination allowance before submission. If the controller dies, a relaunch
  reattaches the recorded call IDs and never resubmits a recorded key.

## 7. Decisions now approved

1. Skip the MKL COMPATIBLE test. Run unpinned, log every container's CPU, use
   unpaired tests and disclose the exact cross-machine reproducibility limitation.
2. Stage 2 cap $35 including pre-lock checks; retain 3,600-second deadlines and
   ten finalist seeds. Stage 3 has a separate $10 cap.
3. Intrinsic coefficient 1.0; 50% zero-growth prior; initial latent mean 0.5 and
   sigma0 0.25; raw equal fitness weighting.
4. Candidate-caused numerical training failures contribute area 0, infrastructure
   failures retry, and more than 5% failed runs stops the search. Three finalists
   per method are re-evaluated on ten fresh seeds per training task.
5. Keep E/R/T/N plus fixed satiation descriptive. The primary Holm family is the
   three E-versus-comparator tests on held-out area. Calling an effect meaningful
   requires both adjusted p < .05 and observed mean-area gain >= .05. The primary
   transfer claim rests on one held-out task, not a demonstrated task population.
6. Tamper testing retrains from scratch on DoorKey-8x8 with free presses only.
   Before any tamper run, freeze the selected winner and record
   P0 = .25 sum(w). If positive, predict collapse via the one-sided off > on area
   test; otherwise predict noninferiority with delta .05. Do not switch branches
   after seeing results, and do not run paid variants.
7. The user makes the repository public as is, after receiving the updated draft
   and the passing exact search-mode smoke result.

**Operational failure rule to review against the tested code.** For each plan,
the denominator is terminal logical runs: successes plus candidate numerical
failures. If candidate failures / that denominator > .05, stop new submissions,
drain already-running calls and halt. There is no grace period; a first early
failure can trigger the guard. Historical smoke runs and infrastructure attempts
are outside this denominator. Infrastructure retries are limited to three within
the same Modal input/call, retained and costed individually; exhaustion stops for
reconciliation regardless of the candidate-failure fraction. Unknown source,
import or programming errors are not assigned area 0. There are no replacement
candidates or seeds.

**Tamper estimands.** The positive-payoff branch uses a directional rank test; a
pass does not independently establish zero task success. The nonpositive branch
uses a one-sided 95% lower bound for the Hodges–Lehmann on-minus-off location
shift, requiring it to exceed -.05. It is a rank-based location-shift criterion
under a common-shape shift model, not mean-area noninferiority under arbitrary
distributions. Mean areas and their difference are reported separately. Only
the branch fixed from the frozen winner is tested.

## 8. Remaining gates and exact next steps

1. Implement the registered search mode, validator branch and plan wiring now;
   verify failure/retry accounting and run that exact path with tiny budgets and
   seeds >=5000. Report pass/fail only; preserve the tested commit and output
   hashes. The earlier smoke-mode pass is not a substitute.
2. Refresh this package's smoke result, current spending and cost projection;
   deliver it with the updated unlocked draft. All earlier numerical evidence
   remains identifiable as earlier evidence.
3. Wait for the user to make the repository public as approved. Do not create or
   push a lock before this gate.
4. Freeze the already-tested code, search configuration, candidate list and
   protocol; commit and push the lock, then verify it against GitHub.
5. Launch the registered Stage 2 search through the tracked experiment runner.
   Keep the shared ledger and call registry; no recorded input is duplicated.
6. Stop at the Stage 2 report for the separate Stage 3 execution approval.

The scientific choices above are resolved. The exact-path smoke and public
repository gate remain pending; this package is not itself a lock or a launch.
