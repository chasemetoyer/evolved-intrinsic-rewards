# Stage 2 pre-registration — DRAFT, NOT LOCKED

This draft is for the user's review. It locks nothing, and no Stage 2 search
evidence exists. It becomes binding only after the user approves it. The lock
will hash this file, the search configuration and the implementation, and will
be committed and pushed after the user has made the repository public. Text
marked **OPEN** needs a user decision before the lock.

## Scope and prior knowledge

- **Stage 2:** CMA-ES and an equal-budget random search over a 12-parameter
  intrinsic reward, followed by finalist re-evaluation.
- **Stage 3:** the final evaluation and the tamper test. Both are specified here,
  so that their tests are registered before any search result exists. They run only
  after a separate Stage 3 approval (**OPEN:** whether Stage 3 has its own cap).
- **Already known:** all Stage 1 results (calibration, task selection,
  determinism) and the pre-lock Stage 2 checks.
- **Pre-lock checks:**
  - the pinned determinism test (`stage2/determinism-protocol.md`, committed
    before its evidence);
  - smoke tests of the controller, CMA-ES and random search on tiny budgets, with
    seeds ≥ 5000 and optimizer RNG seeds different from those registered here.
    Smoke results are reported as pass or fail only.

## Fixed inputs carried from Stage 1

- **Learner:** the archived PPO and CNN with Table 10 settings and
  per-minibatch advantage normalization, through the unchanged corrected trainer
  (`stage1/corrected_ppo.py`). The evaluation quota is 64 episodes per environment
  type.
- **Events:** the corrected detector definitions, all four kept (user decision,
  2026-10-28):
  - final-step events count;
  - box openings count as toggles;
  - a successful target pickup is excluded from the paid pickup event;
  - the detector attaches only after the initial reset.
- **Reward dynamics:** generic reward with four needs starting at h0 = 0.5, a
  single clip after growth minus relief, and the signed reward V(h) − V(h′). Tamper
  is off throughout the search.
- **Tasks (Stage 1 fixed rule):**
  - training: DoorKey-8x8 and UnlockPickup;
  - held out: KeyCorridorS3R2;
  - rejected: KeyCorridorS3R1 and MultiRoom-N2-S4 (too easy), BlockedUnlockPickup
    and DoorKey-16x16 (too hard).

## Genome and encoding

- **Twelve parameters.** For each event (new_view, pickup, drop, toggle): weight
  w ∈ [−1, 1], relief s ∈ [0, 1], and growth g ∈ {0} ∪ [1/640, 1/20]. h0 is fixed at
  0.5.
- **Shared latent box.** Both methods search z ∈ [0, 1]^12 and decode it
  identically: w = 2z − 1; s = z; u = 2z − 1, with g = 0 if u < 0 and otherwise
  g = (1/640)·32^u (log scale).
  - Floating-point excursions of at most 1e-12 are clipped; anything beyond that
    is rejected.
  - The worker re-checks every bound.
- **Intrinsic coefficient:** fixed at 1.0, as in the paper's satiation reward.
  **OPEN:** whether to fix 1.0 or search it.
- **Zero-growth atom:** prior mass 1/2 under random search. The CMA-ES initial
  mean sits exactly at the zero/log boundary (u = 0). **OPEN:** whether a 50%
  zero-growth prior is wanted.

## Fitness

- **Budget:** nominal 2,000,000 steps (1,998,848 actual), per the user's decision.
- **Definition:** fitness is the equal-weight mean training curve area (Stage 1's
  definition: the arithmetic mean of logged training success) over the two
  training tasks × 3 seeds. Each run trains separately; no 1M prefix is reused.
- **UnlockPickup:** baseline areas are 0.003–0.007, so this task contributes
  little fitness variance and the fitness is driven mainly by DoorKey-8x8.
  **OPEN:** keep equal weighting or change it. No task-specific fitted formula is
  proposed.
- **Failed evaluations:** any failed call stops the search for reconciliation,
  as in Stage 1. **OPEN:** whether candidate-caused training failures should
  instead count as area 0.

## CMA-ES (registered draft values in `stage2/search.py`, `REGISTERED_DRAFT`)

- pycma 4.5.0: population 10, 12 generations (120 candidates); initial mean
  z = 0.5 in every coordinate; σ0 = 0.25; bounds [0, 1]^12 handled by pycma's
  default bound handling.
- Optimizer RNG seed 424242. It minimizes −fitness, with no restarts and no early
  stop.
- **Generation barrier:** a generation is asked only after every run of the
  previous one is recorded.
- **Resume:** state is rebuilt by replaying ask/tell from recorded fitness, and
  the controller refuses to continue if the replayed candidates differ from those
  recorded.

## Random search (equal budget)

- 120 candidates drawn i.i.d. uniform on [0, 1]^12 (numpy `default_rng(535353)`),
  decoded identically. The list is fixed before any search evidence and is
  committed with the lock.
- Candidates are batched in groups of 10, matching the CMA-ES generations, with
  the same seed-panel structure. Random-search runs fill slots not needed by
  CMA-ES.

## Seeds (never reused across roles)

| Role | Seeds |
|---|---|
| CMA-ES generation g (common panel for all 10 candidates) | 1000 + 3g + k, k = 0–2 → 1000–1035 |
| Random-search batch b | 3000 + 3b + k → 3000–3035 |
| Finalist re-evaluation | CMA-ES 1900–1909; random search 3900–3909 |
| Final evaluation (Stage 3), shared by every method | 2000–2019 |
| Tamper test (Stage 3) | 2020–2039 |
| Already used | paper 40–44; calibration 900–904; validation 905–909; determinism 910–911; smoke ≥ 5000 |

## Finalist re-evaluation

- The top 3 candidates per method by search fitness are re-evaluated (ties go to
  the lower candidate index).
- Each finalist is re-evaluated on 10 fresh seeds per training task at 2M: 60 runs
  per method and 120 in total.
- The winner per method is the finalist with the highest re-evaluated mean area.
  Ties go to the higher search fitness, then the lower index.
- **OPEN:** the number of finalists and of re-evaluation seeds.

## CPU handling

*(Filled in from the pinned determinism result; see the review package.)*

## Concurrency and compute

- **Concurrency:** at most 32 calls in flight (user decision), with per-function
  `max_containers = 32`. Modal's documented workspace-wide limit is 100 containers
  on Starter and 5,000 on Team.
- **Volume:** results go to a Modal Volumes v2 volume. v1 recommends at most five
  concurrent writers.
- **Ledger:** one Stage 2 ledger with the $30 cap. Each call reserves its
  3,600-second deadline plus a 60-second termination allowance before it is
  submitted.

## Final evaluation (Stage 3; registered now, run after separate approval)

- **Methods:**
  - E, the CMA-ES winner;
  - R, the random-search winner;
  - T, task-only;
  - N, episodic novelty with coefficient 1e-3.
  - The paper's fixed satiation reward (corrected detector) is descriptive only.
  - **OPEN:** the final roster.
- **Design:** 20 seeds (2000–2019) per kept task (DoorKey-8x8, UnlockPickup,
  KeyCorridorS3R2), nominal 2M steps, 64-episode evaluation quota.
- **Primary confirmatory family (Holm, m = 3):** E vs T, E vs N and E vs R on the
  held-out task, KeyCorridorS3R2, using training curve area. The test is a
  one-sided Mann–Whitney U (exact without ties; permutation with ties, 200,000
  resamples with seed 0, or full enumeration where feasible). A hit requires
  E > comparator with Holm-adjusted p < .05.
- **Secondary family (Holm, m = 6):** the same three comparisons on DoorKey-8x8 and
  UnlockPickup.
- **Descriptive:** solve counts with one-sided Fisher exact tests and
  Clopper–Pearson intervals; median censored first-solved step.
- **Pairing:** tests are unpaired unless the CPU-handling rule allows pairing by
  seed (**OPEN**).
- **Interpretation:** non-significance does not establish equivalence. No minimum
  worthwhile effect is set (**OPEN**).

## Tamper test (Stage 3)

- **Design:** E's reward is retrained from scratch on DoorKey-8x8 with tamper
  enabled (action 6 resets all needs before the reward is computed) and free
  presses, against tamper disabled. 20 seeds (2020–2039) per condition, 2M steps.
- **Endpoints:** task curve area (primary); tamper presses per episode and
  intrinsic return (descriptive).
- **Proposed resistance rule:** noninferiority of task area with tamper enabled.
  The lower one-sided 95% confidence bound of the Hodges–Lehmann shift (enabled
  minus disabled, from the Mann–Whitney inversion) must exceed −δ, with
  δ = 0.05 absolute curve area. Bounded return alone is not resistance.
- **OPEN:** δ; paid-press variants and costs; whether to add the held-out task;
  retraining vs a frozen policy.

## Cost projection and stopping

- **Projection:** computed by `scripts/stage2_projection.py` from measured Stage 1
  costs (see the review package).
- **Stopping:** stop before the next reservation could cross $30, or when provider
  evidence reaches it. Incomplete work is disclosed. There is no automatic budget
  increase.

## Remaining open decisions

Listed in the review package and in the OPEN markers above.
