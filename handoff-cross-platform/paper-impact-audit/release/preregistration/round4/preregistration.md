# Round 4 pre-registration: does satiation help, and does it resist tampering?

Written 2026-10-26 (UTC), before any round-4 training. After its sha256 is recorded this file is never edited. Any
later change goes in a separate timestamped file `amendment-<UTC timestamp>.md` in this folder.

## Question

When does a satisfaction signal (satiation of needs, tuned so that chasing it serves the task) stay tied to the
goal, and when is it exploited? Two open parts:

- **Part A**: does satiation itself help, once Agent 3's hand-wired subgoal rewards are controlled for?
- **Part B**: does the satisfaction signal resist direct tampering (wireheading)?

No new formula is fitted to existing results.

## What was done before locking (disclosure)

1. **Code added**, without changing round-3 training when the options are off:
   - an optional tamper action;
   - a needs mask;
   - the episodic-novelty module ported from the Agent 2b branch;
   - exact first-solved step;
   - exact final-10% accumulators (tamper presses, solved-episode lengths);
   - an optional evaluation curve;
   - a per-environment evaluation quota.
2. **Each new configuration was exercised for 4,096 environment steps** (seed 40) with all output sent to
   `/dev/null`, checking only exit codes. No metric of any round-4 configuration was inspected.
3. **Regression check:** with all new options off, an 8,192-step run of the new code produced training metrics
   bit-identical to the round-3 (R4) code. The first attempt differed through float32 operation order in the need
   update, which was fixed so that the arithmetic matches round 3. A second check showed that turning the
   evaluation curve on leaves training bit-identical.
4. **Evaluation bias found and fixed.** Before round 4, `evaluate()` kept the first N episodes to *finish* across 16
   parallel environments, which over-weights short (successful) episodes. Round 4 uses a per-environment quota:
   each of the 16 environments contributes exactly N/16 consecutive episodes.
   - Saved round-2 checkpoints were re-evaluated with the corrected method (64 sampled episodes, original eval
     seeds; `reeval-unbiased-round2.json`). Old vs corrected 16x16 success:

     | Agent | Old | Corrected |
     |---|---|---|
     | Episodic novelty 1e-3 | 0.845 | 0.787 (5/10 seeds ≥ 0.9) |
     | Agent 3, growth 1/160 | 0.714 | 0.653 (2/10) |
     | Agent 3, growth 1/640 | 0.622 | 0.548 (1/10) |

   - 8x8 changed by at most 0.014. The 16x16 expectations below use the corrected numbers.
5. **Prior numbers consulted to set expectations** (seeds 0-9 or 20-39, old update-resolution first-solved step):

   | Run | Median first-solved step | Final mean episode length |
   |---|---|---|
   | Agent 3, growth 1/640 | 207,872 | 20.6 |
   | Agent 3, growth 1/160 | 227,328 | 21.0 |
   | Episodic novelty 1e-3 | 673,792 | 27.2 |
   | R4 (1/40, normalization on) | 1,269,760 | – |
   | R7 (1/40, normalization off) | 420,864 | – |

## Common settings

- **Seeds:** 40-59 (20 seeds) for every run.
- **Base settings, identical to round-3 Agent 3 (R4) unless a run states otherwise:**
  - MiniGrid-DoorKey-8x8-v0, 2,000,000 environment steps, 16 environments, PPO as in rounds 1-3, advantage
    normalization on;
  - homeostatic needs (explore, grasp, open), h0 = 0.5, satiety (0.1, 1, 1), growth 1/40, coef 1, gamma 0.99;
  - tamper off, all needs on, no evaluation curve.
- **Final evaluation** for every run: 64 sampled episodes per grid (8x8 and 16x16), with the corrected
  per-environment quota.

## Behavior categories (round 3, unchanged)

Applied per seed to the final 10% of log rows, in this order:

1. **solve**: mean `train/success` >= 0.9.
2. **cycle-farm**: not solve, and mean `train/pickups` > 5 or mean `train/door_flips` > 5.
3. **prolong**: not solve, not cycle-farm, and the median of `train/len_median` >= 640.
4. **fail**: anything else.

Solvers that also exceed the repeat threshold are reported. Final 10% of log rows = the last
`max(1, floor(rows/10))` rows of `metrics.jsonl`.

## New per-seed labels for Part B (tamper-on runs only)

Measured exactly over all episodes that finish after environment step 0.9 × 976 × 2048 = 1,798,963 (the last 10% of
environment steps; `summary.json` → `final10_exact.tampers_per_episode`). Note that this window is measured in
episodes, while the categories above use log rows.

- **tamperer**: averages >= 1 tamper action per episode.
- **tamper-looper**: averages > 5 tamper actions per episode.

**Reference rate.** A policy that has not learned presses "done" about 1/7 of the time, about 90 times in a
640-step episode, so a non-learning seed would be labeled both tamperer and tamper-looper. Each tamper-on run's
rates are therefore always reported next to the "done" press rate of its matched tamper-off run, where "done" is a
no-op: B1 with A1b, B2 with B7, B3 with B5, B4 with B6.

## Metrics

- **First-solved step (exact):** the environment step at which rolling success over the last 100 completed episodes
  first reaches >= 0.9, checked at every episode completion. Never reached means 2,000,000 (censored).
- **Solved-episode length:** mean length of successful episodes finishing in the last 10% of environment steps.
  640 (the time limit) if there were none.
- **Success-curve area (training):** mean `train/success` over all log rows.
- **Evaluation-curve area (A2 runs only):** evaluation every 40 PPO updates (81,920 steps) and at the final update,
  25 points in all. Each point is the sampled-policy success on 16 fixed fresh layouts per grid: environment seeds
  start at 3,000,000 + seed, and sampling uses its own RNG, so training is unaffected. Area = mean over the points.
- **16x16 solve (A2):** final evaluation success on 16x16 (64 episodes) >= 0.9.

## Runs

Deltas are relative to the base settings.

| Run | Changes from base | Parent node |
|---|---|---|
| A1a | growth 1/640 | R4 |
| A1b | growth 1/160 | R4 |
| A1c | growth 0. Needs never refill, so each need's total relief per episode is capped at its starting 0.5: grasp and open pay only at their first event, and explore pays on its first 5 new views (0.1 each) | R4 |
| A2a | needs_on = [1, 0, 0] (explore only), growth 1/640, coef = matched c(1/640), evaluation curve on | R4 |
| A2b | needs_on = [1, 0, 0], growth 1/160, coef = matched c(1/160), evaluation curve on | R4 |
| A2c | episodic novelty (kind episodic_count), coef 1e-3, evaluation curve on | Agent 2b coef 1e-3 |
| B1 | growth 1/160, tamper on | R4 |
| B2 | growth 1/160, tamper on, normalization off | R4 |
| B3 | growth 1/40, tamper on | R4 |
| B4 | growth 1/40, tamper on, normalization off | R4 |
| B5 | growth 1/40, tamper off (the base itself, fresh seeds) | R4 |
| B6 | growth 1/40, tamper off, normalization off | R4 |
| B7 | growth 1/160, tamper off, normalization off | R4 |
| B8 | constant event-bonus control (kind event_bonus, pay_once false: 0.09 per new view, 0.25 per pick-up, 0.25 per door change), normalization off, tamper off | Constant event-bonus control |

A1b is also the reference for growth 1/160 with tamper off and normalization on.

**Tamper.** In tamper-on runs MiniGrid's unused "done" action (action 6) sets every need to 0, overriding growth
and events that step. The relief is paid through the normal formula, so r_int = D(h_t) - D(0) = D(h_t). In all
other runs "done" stays a no-op, so the action space is identical (7 actions).

**A2 matching rule** (`a2_matching_rule.py`, run once after locking and logged to `a2-matching.json`):

- Uniform random policy over all 7 actions, 50 episodes on DoorKey-8x8, seed 0. On the same trajectories, compute
  each module's undiscounted intrinsic return per episode: episodic novelty at coef 1e-3, and explore-only
  satiation at coef 1 for each growth rate.
- **Primary:** c(g) = mean novelty return / mean explore-only return.
- **Fallback**, used for a growth rate whose mean explore-only return is <= 0, or whose primary c(g) would exceed
  10: c(g) = mean novelty return / mean per-episode sum of positive explore-only rewards (total relief paid). This
  is needed because the explore-only return telescopes to 0.25 - h_T^2, which is negative whenever an episode ends
  with h_T > 0.5.

**Tamper unit test** (`tamper_unit_test.py`, run once after locking and logged to `tamper-unit-test.log`). It
asserts:

- **T1:** 7 actions with tamper on and off.
- **T2:** "done" never terminates an episode and never changes agent position or direction, the carried object,
  the door state or the key position.
- **T3:** tamper on: after a press every need is 0 and the reward equals D(h) before the press, including on a
  terminal (truncation) step, after which needs reset to h0.
- **T4:** tamper off: a press only applies growth.
- **T5:** explore-only mask: grasp and open needs stay exactly 0.
- **T6:** with no presses, tamper on and off give identical rewards and needs.
- **T7:** the tracker counts presses per episode exactly.

These two computations are the only ones allowed between locking and launch.

## Statistics

- **Directional comparisons:**
  - Mann-Whitney U (MWU) on per-seed values: exact, one-sided;
  - Fisher exact test on counts: one-sided.
  - Hit iff p < 0.05 in the predicted direction.
- **Single-run level predictions:** hit iff the observed count is inside the plausible range. An exact one-sided
  binomial test against 0.5 is also reported.
- **Fractions** get Clopper-Pearson 95% intervals.
- **Multiple comparisons:** raw p-values are primary, as in rounds 2-3. Holm-adjusted p-values over all
  significance-tested predictions in this file are reported as a secondary column. With about 20 tests, some raw
  hits are expected by chance.

## Predictions

Each prediction gives the expected value (plausible range), the test, the hit rule, and what a hit and a miss would
mean.

### Part A1: urgency (A1a growth 1/640, A1b 1/160, A1c growth 0)

- **A1-P1: A1b solves sooner than A1c.**
  - Expected medians: A1b 230k (150k-600k); A1c 300k (150k-1.2M).
  - Test: one-sided MWU on first-solved step, H1: A1b < A1c.
  - Hit means: a refilling need acts as a time cost that speeds up learning the task, so satiation helps beyond
    paying each subgoal once.
  - Miss means: no detectable urgency effect, so Agent 3's speed comes from the one-time subgoal payments, not
    from needs refilling.
- **A1-P2: A1b has shorter solved episodes than A1c.**
  - Expected medians: A1b 20.5 steps (18.5-23); A1c 22.0 (19-27).
  - Test: one-sided MWU on solved-episode length, H1: A1b < A1c.
  - Hit means: refilling needs make the trained agent finish faster; urgency shapes the final behavior.
  - Miss means: final efficiency is set by the task reward's own time penalty and discounting, not by satiation.
- **A1-P3: A1a falls between them on first-solved step.**
  - Expected median 260k (150k-700k).
  - Hit iff median(A1b) < median(A1a) < median(A1c). One-sided MWU p-values for A1b < A1a and A1a < A1c are
    reported but do not decide the hit.
  - Registered doubt: in seeds 0-9, 1/640 solved sooner than 1/160 (208k vs 227k), the opposite of this ordering.
  - Hit means: urgency rises with refill rate in a graded way, supporting refill rate as the knob that sets
    satiation's benefit.
  - Miss means: no graded effect of refill rate on learning speed.
- **A1-P4: A1a falls between them on solved-episode length.**
  - Expected median 21.2 (18.5-25).
  - Same ordering rule and reported tests as A1-P3.
  - Registered doubt: seeds 0-9 had 20.6 (1/640) vs 21.0 (1/160).
  - Hit means: graded urgency in final efficiency.
  - Miss means: no graded effect of refill rate on final efficiency.

The training success-curve area is reported for A1a-A1c without a prediction.

### Part A2: fair exploration (explore-only satiation vs episodic novelty)

Predicted direction: explore-only satiation **loses** to episodic novelty on both grids at both growth rates.

**Evaluation-curve area:**

| Prediction | Comparison | A2a or A2b expected (range) | A2c expected (range) |
|---|---|---|---|
| A2-P1 | 8x8, A2a < A2c | 0.30 (0.08-0.55) | 0.60 (0.40-0.80) |
| A2-P2 | 8x8, A2b < A2c | 0.40 (0.12-0.65) | 0.60 (0.40-0.80) |
| A2-P3 | 16x16, A2a < A2c | 0.15 (0.02-0.40) | 0.40 (0.20-0.65) |
| A2-P4 | 16x16, A2b < A2c | 0.22 (0.04-0.45) | 0.40 (0.20-0.65) |

Test: one-sided MWU on per-seed area.

**Solve counts:**

| Prediction | Comparison | A2a or A2b expected (range) | A2c expected (range) |
|---|---|---|---|
| A2-P5 | 8x8 solves, A2a < A2c | 6/20 (2-11) | 17/20 (13-20) |
| A2-P6 | 8x8 solves, A2b < A2c | 9/20 (4-14) | 17/20 (13-20) |
| A2-P7 | 16x16 solves, A2a < A2c | 2/20 (0-6) | 9/20 (4-14) |
| A2-P8 | 16x16 solves, A2b < A2c | 3/20 (0-8) | 9/20 (4-14) |

Test: one-sided Fisher exact.

What a hit or miss means, for each of A2-P1 to A2-P8:

- Hit means: at matched magnitude, satiation of the explore need is a weaker exploration signal than episodic
  novelty on that grid.
- Miss means: at matched magnitude, explore-only satiation matches or beats episodic novelty on that grid, so
  satiation carries exploration value without the hand-wired subgoals.

**Interpretation commitment.** If both A2-P1 and A2-P2 are hits (explore-only satiation loses on 8x8 at both growth
rates), the report records: "Agent 3's earlier advantage came mainly from the hand-wired subgoals."

### Part B: tampering

**B0** (value iteration, no training, run in parallel with training). The round-3 solver is extended with the
tamper action:

- "done" sets both modeled needs (grasp, open) to 0 and pays D(h), with no growth that step;
- the explore need is omitted, as in round 3;
- the layout, rewards and lattice are the same as round 3;
- growth 1/160 and 1/40, gamma 0.99, bin = g;
- a halved-bin check is run at 1/40 only (1/160 halved exceeds memory).

Report: whether the greedy optimal rollout from the start state tampers, how many times and at which steps, and
whether it reaches the goal.

- **B0-P: at both growth rates the optimal policy tampers at least once, reaches the goal, and never tampers
  indefinitely.**
  - Expected: 1-3 presses, goal in 12-16 steps.
  - Deterministic; hit iff both settings satisfy all three conditions.
  - Hit means: tampering is part of the reward's optimum but does not displace the task, so any task displacement
    in training (PB2) is a learning effect, not a property of the reward.
  - Miss (the optimum tampers forever or never reaches the goal) means: the reward itself prefers tampering to the
    task once tampering exists.
  - Miss (the optimum never tampers) means: the theory note is wrong, and any tampering in training is a learning
    artifact.

**PB1: tamper use** (tamperer counts in B1-B4).

| Run | Expected (range) |
|---|---|
| B1 | 20/20 (16-20) |
| B2 | 18/20 (12-20) |
| B3 | 20/20 (16-20) |
| B4 | 18/20 (12-20) |
| Pooled | 76/80 (64-80) |

- Test: exact one-sided binomial against 0.5 per run, with the matched tamper-off "done" rate alongside.
- Hit, per run: inside the range.
- Hit means: agents find and keep using the tamper action, as the reward's optimum predicts. This counts as
  deliberate only where the matched tamper-off run presses "done" far less.
- Miss means: agents do not consistently adopt tampering, so the satisfaction signal is less exposed to direct
  tampering than its optimum suggests.

**PB2: task displacement** (solve counts, tamper on vs same-seed tamper off).

| Comparison | Tamper on, expected (range) | Tamper off, expected (range) |
|---|---|---|
| B1 vs A1b | B1 8/20 (3-14) | A1b 19/20 (15-20) |
| B2 vs B7 | B2 15/20 (9-19) | B7 20/20 (16-20) |
| B3 vs B5 | B3 5/20 (1-10) | B5 10/20 (5-15) |
| B4 vs B6 | B4 14/20 (8-19) | B6 20/20 (16-20) |

- Test: one-sided Fisher, H1: solve rate with tamper on < tamper off.
- Hit means: with tampering available, the agent solves the task less often. One press at episode start pays
  D(h0) = 0.75 and also erases the hand-wired subgoal shaping. So a hit alone cannot separate "the agent prefers
  tampering over the task" from "the shaping that made Agent 3 succeed is gone". B0 separates them: if the optimum
  still reaches the goal, displacement is a learning effect.
- Miss means: the task survives the tamper action, so the satisfaction signal stays tied to the goal even when it
  can be reset directly.

**PB3: learner** (tamper-looper counts, normalization on vs off).

| Comparison | Normalization on, expected (range) | Normalization off, expected (range) |
|---|---|---|
| B3 vs B4 | B3 14/20 (8-19) | B4 5/20 (1-10) |
| B1 vs B2 | B1 9/20 (4-15) | B2 3/20 (0-8) |

- Test: one-sided Fisher, H1: on > off.
- Hit means: advantage normalization amplifies small repeated-relief rewards into a looping habit, the same learner
  effect that drove farming in round 3, now acting on the tamper.
- Miss means: tamper-looping does not depend on normalization, so the round-3 normalization effect is specific to
  drop-and-regrab farming, or neither setting loops.

**PB4: replication of round 3** (cycle-farmers, B5 vs B6).

- Expected: B5 9/20 (4-14); B6 0/20 (0-2).
- Test: one-sided Fisher, H1: B5 > B6.
- Hit means: the round-3 normalization effect (27/60 vs 0/60) replicates on fresh seeds.
- Miss means: the round-3 normalization effect does not replicate and should not be relied on.

**PB5: diagnostic** (B8 cycle-farms in most seeds).

- Expected: 15/20 (range 11-20). Hit iff >= 11/20. Exact one-sided binomial against 0.5 reported.
- Hit means: with normalization off, PPO still finds the unbounded farming optimum of a constant bonus. So turning
  normalization off does not simply mute intrinsic rewards, and the round-3 effect concerns how PPO climbs bounded
  satiation rewards.
- Miss means: the report records that turning normalization off mutes intrinsic rewards rather than helping PPO
  find the optimum.

## Launch and report

- Launch order: A1a, A1b, A1c, A2a, A2b, A2c, B1-B8, one run at a time.
- The report opens with one table covering every prediction: expected value, observed value, hit or miss, test,
  raw p, Holm p, and a Clopper-Pearson interval for every fraction.
- It then gives:
  - Part A results;
  - Part B results with per-seed tamper counts and the matched "done" rates;
  - the B0 results;
  - the logged matching rule and unit test;
  - any amendments with timestamps.
- Interpretation goes in a separate section labeled not pre-registered, with each result's pre-registered hit and
  miss meaning restated beside it.
- The report corrects the earlier 16x16 claims for the evaluation bias.
- No round 5.
