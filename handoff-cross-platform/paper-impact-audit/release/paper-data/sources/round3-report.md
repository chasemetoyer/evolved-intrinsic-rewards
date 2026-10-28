# Round 3 report: testing the learning-trap account of farming

Pre-registration: `preregistration.md`, sha256 `b5e845c978ec96c2746eb81098c0bea3bf8dc14a1dc174e4f77844352b621ae7`,
locked 2026-10-26T15:17:42Z. The hash still matches.

**Amendments: none.** No amendment file was written. The only computation run between locking and launch was
R10's pre-registered bonus rule (`r10-bonus.json`: T = 0.0561, V = 70.05, per-view bonus 0.000801).

## 1. Every prediction

Fractions are cycle-farm seeds out of 20 (seeds 20-39) unless stated. Intervals are Clopper-Pearson 95%.
"n.e." = not estimable.

| Prediction | Expected (range) | Observed | 95% CI | Hit? | Test | p |
|---|---|---|---|---|---|---|
| P1 farmers: lock-in before first goal >= 80% | 90% (80-100%) | 21/30 undetermined | – | **unresolvable** | binomial vs 0.5 | not scored |
| P2 solvers: first goal before lock-in >= 80% | 95% (80-100%) | 60/60 | [0.94, 1.00] | hit (near-definitional) | binomial vs 0.5, one-sided | 8.7e-19 |
| P3 earlier first goal predicts not farming | slope < 0 | 2 distinct first-goal windows | – | **unresolvable** | logistic, one-sided | not scored |
| P4 VI optimum reaches goal at gamma 0.99, g in {1/80, 1/40, 1/20} | 3/3 | 3/3 | – | hit | deterministic | – |
| R1 growth 1/60 | 6 (1-10) | 4 | [0.06, 0.44] | hit | Fisher R1 < R4, one-sided | 0.088 |
| R2 growth 1/30 | 16 (12-20) | 18 | [0.68, 0.99] | hit | Fisher R2 > R4, one-sided | 0.0029 |
| R3 coef 0.5, norm on | 8 (3-13) | 6 | [0.12, 0.54] | hit | (logistic) | – |
| R4 coef 1, norm on (reference) | 11 (6-16) | 9 | [0.23, 0.68] | hit | – | – |
| R5 coef 2, norm on | 13 (8-18) | 12 | [0.36, 0.81] | hit | (logistic) | – |
| R6 coef 0.5, norm off | 4 (0-9) | 0 | [0.00, 0.17] | hit | – | – |
| R7 coef 1, norm off | 10 (5-15) | 0 | [0.00, 0.17] | **miss** | – | – |
| R8 coef 2, norm off | 16 (11-20) | 0 | [0.00, 0.17] | **miss** | Fisher R8 > R6, one-sided | 1.0 |
| Logistic b1 (log2 coef) > 0 | > 0 | n.e. | – | **miss (not estimable)** | one-sided Wald | n.e. |
| Logistic b3 (log2 coef x norm_on) < 0 | < 0 | n.e. | – | **miss (not estimable)** | one-sided Wald | n.e. |
| R9 early-goal intervention | 2 (0-4), <= 20% | 10 | [0.27, 0.73] | **miss** | Fisher R9 < R4, one-sided | 0.74 |
| R10 cycle-farm | 0 (0-1) | 0 | [0.00, 0.17] | hit | – | – |
| R10 prolong | 0 (0-1) | 0 | [0.00, 0.17] | hit | – | – |
| R10 solve | 17 (12-20) | 20 | [0.83, 1.00] | hit | – | – |

Notes on the table:

- **Logistic model.** All 60 normalization-off seeds solved, with zero farmers. That makes the pre-registered
  model quasi-completely separated, and its coefficients diverge (|b2| ≈ 24, CIs ≈ ±5×10^4). The b1 and b3
  predictions are counted as not confirmed.
- **Solvers that also exceed the repeat threshold** (more than 5 repeats while solving): 1 in R2, 2 in R3, 1 in R9.

## 2. Race analysis (Step 1, existing logs)

Logs have a 20,480-step logging window. All 90 Agent 3 seeds, farmers included, first reached the goal by
step 81,920; 88 of 90 did so in the first two windows. Of the 30 final cycle-farmers:

- 21 have first goal and lock-in in the same window (undetermined), which is over the 25% stopping rule;
- 9 locked in first;
- 0 never reached the goal.

So P1 is unresolvable at this resolution. P3 is unresolvable because the growth-1/40 seeds have only 2 distinct
first-goal windows. P2 is a hit, but nearly by construction: a final solver can hardly stay above 5 repeats to
the end of training.

2x2 table (final category by order):

| | goal first | lock-in first | undetermined |
|---|---|---|---|
| solve (60) | 60 | 0 | 0 |
| cycle-farm (30) | 0 | 9 | 21 |

The per-seed table is in `race-results.json`.

## 3. Exact solution (Step 2)

Value iteration on the 7x5 grid converged exactly; max|dV| = 0 in every job. The explore need was omitted. The
optimal policy reaches the goal at every pre-registered setting:

- **gamma 0.99:** g = 1/80 in 11 steps, 1/40 in 11, 1/20 in 17;
- **gamma 0.95:** 11 steps at all three growth rates;
- **halving the bin size** changed no value or policy in any of the 6 cells.

In the wider sweep, the smallest cycling growth rate is **1/2** at both discounts. There the optimum is a
2-step door close/open loop with no key pick-ups. Every g <= 1/4 reaches the goal.

So the reward's optimum does not farm anywhere near the growth rates where trained agents farm
(1/40-1/20).

## 4. What the evidence says (interpretation, not pre-registered)

- **Farming is not the optimum.** This is confirmed by P4 and the sweep: the cycling optimum appears only at
  g = 1/2, about 20x faster growth than where PPO farms.
- **The "found the goal too late" account is not supported.**
  - R9 is a clean intervention. Goal-room starts raised early success to about 27% of episodes and moved the
    median first goal from step 17,920 to step 760. Farming was unchanged: 10/20 vs 9/20.
  - Pick-ups climbed to about 40 per episode *during* the intervention window.
  - In the old logs, every farmer had reached the goal at least once.
  - So early goal experience does not prevent lock-in.
- **Advantage normalization is the strongest effect measured in this project.** This was not predicted, so it is
  exploratory:
  - farming was 27/60 with normalization on vs 0/60 with it off (Fisher two-sided p = 3.3e-10);
  - R7 vs R4 alone: 0/20 vs 9/20, p = 0.0012;
  - every normalization-off seed solved, at every coef.
- **Growth rate still orders farming:** R1 (1/60) 4/20, R4 (1/40) 9/20, R2 (1/30) 18/20. Only R2 > R4 is
  significant.
- **Bonus size has no clear effect with normalization on:** R3 (coef 0.5) 6/20, R4 (coef 1) 9/20, R5 (coef 2) 12/20.
- **The fixed pay-once control** (all events once per episode, view bonus scaled down) solved 20/20 with no
  farming and no prolonging.

## 5. Exploratory re-scoring of earlier runs under the round-3 categories

Old runs did not log a median episode length. For them, prolong uses the mean-length proxy (mean `train/len` >= 600).

| Run | n | solve | cycle-farm | prolong | fail |
|---|---|---|---|---|---|
| Agent 1 (5 seeds) | 5 | 2 | 0 | 1 | 2 |
| Agent 2 RND | 5 | 1 | 0 | 3 | 1 |
| LP curiosity (round 1) | 5 | 3 | 0 | 2 | 0 |
| Agent 1 @ 10 seeds | 10 | 3 | 0 | 3 | 4 |
| Episodic novelty 3e-4 / 1e-3 / 3e-3 | 10 each | 7 / 9 / 3 | 0 / 0 / 0 | 0 / 0 / 4 | 3 / 1 / 3 |
| LP fixed-lag 0.1 / 0.3 / 1.0 | 10 each | 1 / 5 / 0 | 0 / 0 / 0 | 4 / 3 / 10 | 5 / 2 / 0 |
| Agent 3 growth 1/640 / 1/160 / 1/40 | 10 each | 10 / 10 / 5 | 0 / 0 / 5 | 0 | 0 |
| Constant event-bonus control | 10 | 0 | 10 | 0 | 0 |
| N1 / N2 / N3 / N4 / N5 / N6 | 10 each | 4 / 3 / 10 / 10 / 7 / 1 | 6 / 7 / 0 / 0 / 3 / 9 | 0 | 0 |
| Pay-once control (round 2) | 10 | 0 | 10 | 0 | 0 |

The round-2 pay-once control is re-scored cycle-farm because its incidental pick-ups exceed 5. The round-2
replay showed its actual behavior was episode-prolonging, so the category rule misclassifies this run.

## Limitations

- Step 1 is limited by the 20k-step logging window. Round-3 runs record the exact first-goal step but were not
  part of the pre-registered race analysis.
- The value-iteration grid is much smaller than DoorKey-8x8, omits the explore need and the time limit, and uses
  a fixed layout.
- With advantage normalization off, PPO's effective step size also changes. The normalization effect may come
  from optimization scale rather than from anything specific to the reward.
- Correction to round-2 notes: the event-bonus per-new-view payment at h0 = 0.5 and relief 0.1 is 0.09, not
  0.0975 as written.

## Files

- `preregistration.md` and `preregistration.sha256`
- `race_analysis.py` and `race-results.json`
- `value_iteration.py` and `value-iteration-results.json`
- `score_round3.py` and `round3-scores.json`
- `r10_bonus_rule.py` and `r10-bonus.json`
