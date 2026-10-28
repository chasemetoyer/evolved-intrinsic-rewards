# Consolidated pre-registered results, rounds 2-5

Source table for the preprint. Every pre-registered prediction or test from rounds 2-5, generated from each round's scored JSON (`mechanism/prediction-results.json`, `round3/round3-scores.json`, `round3/race-results.json`, `round3/value-iteration-results.json`, `round4/round4-scores.json`, `round5/round5-scores.json`). Round 1 was exploratory and is not included. p is the raw p-value of the pre-registered test (one-sided where directional); Holm-adjusted values are in each round's report.

**Totals:** 94 pre-registered rows: 60 hits, 32 misses, 2 unresolvable or not scored.

| Round | ID | Prediction | Observed | Test | raw p | Result |
|---|---|---|---|---|---|---|
| 2 | N1 | farmers in 2-8 of 10 (E=0.764) | 7/10 | level (range) | – | hit |
| 2 | N2 | farmers in 0-2 of 10 (E=0.281) | 7/10 | level (range) | – | miss |
| 2 | N3 | farmers in 1-4 of 10 (E=0.593) | 0/10 | level (range) | – | miss |
| 2 | N4 | farmers in 2-8 of 10 (E=0.764) | 0/10 | level (range) | – | miss |
| 2 | N5 | farmers in 0-1 of 10 (E=0.382) | 3/10 | level (range) | – | miss |
| 2 | N6 | farmers in 6-10 of 10 (E=0.87) | 10/10 | level (range) | – | hit |
| 2 | pay-once control | farmers in 0-0 of 10 | 10/10 | level (range) | – | miss |
| 2 | logistic | farming rises with predicted temptation E (slope > 0) | slope 1.06 | logistic, one-sided | 0.193 | miss |
| 2 | N2 < N1 | N2 < N1 (farmer counts) | 7/10 vs 7/10 | Fisher, one-sided | 0.686 | miss |
| 2 | N5 < N4 | N5 < N4 (farmer counts) | 3/10 vs 0/10 | Fisher, one-sided | 1.000 | miss |
| 2 | N6 > N3 | N6 > N3 (farmer counts) | 10/10 vs 0/10 | Fisher, one-sided | 5.4e-06 | hit |
| 3 | P1 | farmers: lock-in before first goal >= 80% | 21/30 undetermined | binomial | – | unresolvable / not scored |
| 3 | P2 | solvers: first goal before lock-in >= 80% | 60/60 | binomial, one-sided | 8.7e-19 | hit |
| 3 | P3 | earlier first goal predicts not farming | 2 distinct first-goal windows | logistic | – | unresolvable / not scored |
| 3 | P4 | exact optimum reaches the goal at gamma 0.99 for g in {1/80, 1/40, 1/20} | 3/3 | deterministic | – | hit |
| 3 | R1 | R1 cycle-farm in 1-10 of 20 | 4/20 | level (range) | – | hit |
| 3 | R2 | R2 cycle-farm in 12-20 of 20 | 18/20 | level (range) | – | hit |
| 3 | R3 | R3 cycle-farm in 3-13 of 20 | 6/20 | level (range) | – | hit |
| 3 | R4 | R4 cycle-farm in 6-16 of 20 | 9/20 | level (range) | – | hit |
| 3 | R5 | R5 cycle-farm in 8-18 of 20 | 12/20 | level (range) | – | hit |
| 3 | R6 | R6 cycle-farm in 0-9 of 20 | 0/20 | level (range) | – | hit |
| 3 | R7 | R7 cycle-farm in 5-15 of 20 | 0/20 | level (range) | – | miss |
| 3 | R8 | R8 cycle-farm in 11-20 of 20 | 0/20 | level (range) | – | miss |
| 3 | R9 | R9 cycle-farm in 0-4 of 20 | 10/20 | level (range) | – | miss |
| 3 | R10 cycle-farm | R10 cycle-farm in 0-1 of 20 | 0/20 | level (range) | – | hit |
| 3 | R10 prolong | R10 prolong in 0-1 of 20 | 0/20 | level (range) | – | hit |
| 3 | R10 solve | R10 solve in 12-20 of 20 | 20/20 | level (range) | – | hit |
| 3 | R1 < R4 | R1 < R4 (cycle-farmers) | 4/20 vs 9/20 | Fisher, one-sided | 0.088 | miss |
| 3 | R2 > R4 | R2 > R4 (cycle-farmers) | 18/20 vs 9/20 | Fisher, one-sided | 0.003 | hit |
| 3 | R8 > R6 | R8 > R6 (cycle-farmers) | 0/20 vs 0/20 | Fisher, one-sided | 1.000 | miss |
| 3 | R9 < R4 | R9 < R4 (cycle-farmers) | 10/20 vs 9/20 | Fisher, one-sided | 0.736 | miss |
| 3 | logistic b1 | logistic b1 (log2 coef) > 0 | b = -3.2e-08 (not estimable: quasi-separation) | logistic Wald, one-sided | – | miss |
| 3 | logistic b3 | logistic b3 (log2 coef x norm_on) < 0 | b = 0.626 (not estimable: quasi-separation) | logistic Wald, one-sided | – | miss |
| 4 | A1-P1 | A1b < A1c on first-solved step | median A1b 311832 vs A1c 283424 | one-sided MWU | 0.708 | miss |
| 4 | A1-P2 | A1b < A1c on solved-episode length | median A1b 20.3231 vs A1c 19.6918 | one-sided MWU | 0.744 | miss |
| 4 | A1-P3 | A1a between A1b and A1c on first-solved step (median order) | medians A1b 311832, A1a 221640, A1c 283424 | median ordering (MWU reported) | – | miss |
| 4 | A1-P4 | A1a between A1b and A1c on solved-episode length (median order) | medians A1b 20.3231, A1a 19.5622, A1c 19.6918 | median ordering (MWU reported) | – | miss |
| 4 | A2-P1 | 8x8 eval-curve area: A2a < A2c | mean 0.387 vs 0.702 | one-sided MWU | 0.00018 | hit |
| 4 | A2-P2 | 8x8 eval-curve area: A2b < A2c | mean 0.060 vs 0.702 | one-sided MWU | 5e-06 | hit |
| 4 | A2-P3 | 16x16 eval-curve area: A2a < A2c | mean 0.328 vs 0.579 | one-sided MWU | 0.002 | hit |
| 4 | A2-P4 | 16x16 eval-curve area: A2b < A2c | mean 0.011 vs 0.579 | one-sided MWU | 5e-06 | hit |
| 4 | A2-P5 | 8x8 solves: A2a < A2c | 11/20 vs 17/20 | one-sided Fisher | 0.041 | hit |
| 4 | A2-P6 | 8x8 solves: A2b < A2c | 0/20 vs 17/20 | one-sided Fisher | 1.3e-08 | hit |
| 4 | A2-P7 | 16x16 solves: A2a < A2c | 6/20 vs 8/20 | one-sided Fisher | 0.371 | miss |
| 4 | A2-P8 | 16x16 solves: A2b < A2c | 0/20 vs 8/20 | one-sided Fisher | 0.002 | hit |
| 4 | B0-P | optimum tampers >= 1, reaches goal, never tampers indefinitely (1/160, 1/40) | 1/160 (g): reaches goal, 1 tamper(s) at steps [0], 12 steps; 1/40 (g): reaches goal, 2 tamper(s) at steps [0, 11], 13 steps; 1/40 (g/2): reaches goal, 2 tamper(s) at steps [0, 11], 13 steps | deterministic | – | hit |
| 4 | PB1-B1 | B1 tamperers (reference A1b median done/episode 4.8e-05) | 20/20 (median done/episode 38.6) | binomial vs 0.5, one-sided | 9.5e-07 | hit |
| 4 | PB1-B2 | B2 tamperers (reference B7 median done/episode 2.51) | 20/20 (median done/episode 61.2) | binomial vs 0.5, one-sided | 9.5e-07 | hit |
| 4 | PB1-B3 | B3 tamperers (reference B5 median done/episode 0.000789) | 20/20 (median done/episode 173) | binomial vs 0.5, one-sided | 9.5e-07 | hit |
| 4 | PB1-B4 | B4 tamperers (reference B6 median done/episode 0.475) | 20/20 (median done/episode 120) | binomial vs 0.5, one-sided | 9.5e-07 | hit |
| 4 | PB1-pooled | B1-B4 tamperers pooled | 80/80 | binomial vs 0.5, one-sided | 8.3e-25 | hit |
| 4 | PB2-B1 | solve B1 (tamper on) < A1b (tamper off) | 1/20 vs 20/20 | one-sided Fisher | 1.5e-10 | hit |
| 4 | PB2-B2 | solve B2 (tamper on) < B7 (tamper off) | 0/20 vs 20/20 | one-sided Fisher | 7.3e-12 | hit |
| 4 | PB2-B3 | solve B3 (tamper on) < B5 (tamper off) | 1/20 vs 11/20 | one-sided Fisher | 0.00062 | hit |
| 4 | PB2-B4 | solve B4 (tamper on) < B6 (tamper off) | 0/20 vs 20/20 | one-sided Fisher | 7.3e-12 | hit |
| 4 | PB3-B3 | tamper-loopers B3 (norm on) > B4 (norm off) | 20/20 vs 20/20 | one-sided Fisher | 1.000 | miss |
| 4 | PB3-B1 | tamper-loopers B1 (norm on) > B2 (norm off) | 20/20 vs 20/20 | one-sided Fisher | 1.000 | miss |
| 4 | PB4 | cycle-farm B5 (norm on) > B6 (norm off) | 9/20 vs 0/20 | one-sided Fisher | 0.00061 | hit |
| 4 | PB5 | B8 cycle-farms in most seeds | 20/20 | binomial vs 0.5, one-sided | 9.5e-07 | hit |
| 5 | A-P1 | A1 solves more than B1 | 11/20 vs 1/20 | one-sided Fisher | 0.00062 | hit |
| 5 | A-P1m | A1 success-curve area > B1 | mean 0.438 vs 0.042 | one-sided MWU | 7.8e-06 | hit |
| 5 | A-P2 | A2 solves more than B2 | 0/20 vs 0/20 | one-sided Fisher | 1.000 | miss |
| 5 | A-P2m | A2 success-curve area > B2 | mean 0.025 vs 0.022 | one-sided MWU | 0.005 | hit |
| 5 | A-P3 | A1 solves more than B1+B3 | 11/20 vs 2/40 | one-sided Fisher | 2.6e-05 | hit |
| 5 | A-P3m | A1 success-curve area > B1+B3 | mean 0.438 vs 0.039 | one-sided MWU | 5e-06 | hit |
| 5 | B-JTp | tamper presses decrease with cost (B1, B9, B10, B11) | medians 38.59, 27.13, 0.36, 0.00 | one-sided Jonckheere-Terpstra (permutation) | 5e-06 | hit |
| 5 | B-JTs | solves increase with cost (B1, B9, B10, B11) | solves 1, 3, 20, 20 | one-sided Jonckheere-Terpstra (permutation) | 5e-06 | hit |
| 5 | B-F-B9-vsB1 | B9 solves more than B1 | 3/20 vs 1/20 | one-sided Fisher | 0.302 | hit |
| 5 | B-F-B9-vsA1b | B9 solves fewer than A1b | 3/20 vs 20/20 | one-sided Fisher | 1.3e-08 | hit |
| 5 | B-L-B9-presses | B9 presses (median presses per episode) | 27.13 | level (range) | – | hit |
| 5 | B-L-B9-tamperers | B9 tamperers (count of 20) | 19/20 | level (range) | – | hit |
| 5 | B-L-B9-solves | B9 solves (count of 20) | 3/20 | level (range) | – | hit |
| 5 | B-F-B10-vsB1 | B10 solves more than B1 | 20/20 vs 1/20 | one-sided Fisher | 1.5e-10 | miss |
| 5 | B-F-B10-vsA1b | B10 solves fewer than A1b | 20/20 vs 20/20 | one-sided Fisher | 1.000 | miss |
| 5 | B-L-B10-presses | B10 presses (median presses per episode) | 0.36 | level (range) | – | miss |
| 5 | B-L-B10-tamperers | B10 tamperers (count of 20) | 7/20 | level (range) | – | miss |
| 5 | B-L-B10-solves | B10 solves (count of 20) | 20/20 | level (range) | – | miss |
| 5 | B-F-B11-vsB1 | B11 solves more than B1 | 20/20 vs 1/20 | one-sided Fisher | 1.5e-10 | hit |
| 5 | B-F-B11-vsA1b | B11 solves fewer than A1b | 20/20 vs 20/20 | one-sided Fisher | 1.000 | hit |
| 5 | B-L-B11-presses | B11 presses (median presses per episode) | 0.00 | level (range) | – | hit |
| 5 | B-L-B11-tamperers | B11 tamperers (count of 20) | 0/20 | level (range) | – | hit |
| 5 | B-L-B11-solves | B11 solves (count of 20) | 20/20 | level (range) | – | hit |
| 5 | C-P1 | cycle-farming rises C1 < C2 < C3 | 0/20, 0/20, 0/20 | one-sided Jonckheere-Terpstra (permutation) | 1.000 | miss |
| 5 | C-P2 | cycle-farm: C3 > C4 | 0/20 vs 0/20 | one-sided Fisher | 1.000 | miss |
| 5 | C-P3 | solve: C5 < C1 | 0/20 vs 20/20 | one-sided Fisher | 7.3e-12 | hit |
| 5 | C-P4 | solve: C5 < C6 | 0/20 vs 20/20 | one-sided Fisher | 7.3e-12 | hit |
| 5 | D1-P1 | B1-B4 seeds that never found the goal | 1/80 | level (range) | – | hit |
| 5 | D1-P2 | found-then-lost seeds whose success declined (peak >= 0.10, then <= half) | 7/77 | level: hit iff >= 20% (>= 16) | – | miss |
| 5 | D1-P3 | median exact first-goal step of B1-B4 seeds | 27,344 (max 1,187,264) | level: hit iff <= 41,000 | – | hit |
| 5 | D2-B1 | final-10% policy entropy B1 (tamper on) > A1b (tamper off) | median 1.878 vs 0.067 | one-sided MWU | 7.3e-12 | hit |
| 5 | D2-B2 | final-10% policy entropy B2 (tamper on) > B7 (tamper off) | median 1.935 vs 1.138 | one-sided MWU | 7.3e-12 | hit |
| 5 | D2-B3 | final-10% policy entropy B3 (tamper on) > B5 (tamper off) | median 1.844 vs 0.290 | one-sided MWU | 7.3e-12 | hit |
| 5 | D2-B4 | final-10% policy entropy B4 (tamper on) > B6 (tamper off) | median 1.934 vs 0.598 | one-sided MWU | 7.3e-12 | hit |
| 5 | D3-P1 | 'done' fraction rises before success declines | rise first 7/7 (undetermined 0) | binomial vs 0.5, one-sided; hit iff share >= 0.8 | 0.008 | hit |

## Known misclassifications and corrections

1. **Round 2, temptation formula F redefined after seeing data.** The first F did not fit the three calibration runs and was redefined before the round-2 test; the calibration runs were therefore excluded as evidence (disclosed in round 2).
2. **Round 2, pay-once control labelled 'farmer' by the >5 rule** although replay showed episode-prolonging, not repetition; the round-3 exploratory re-score repeats this label.
3. **Round 2 claim dropped: 'the critic prefers farming'.** The value rising with need is the +D(h_t) term of the return and holds for solvers too; not evidence of preference.
4. **Round 1 claim corrected: LP-curiosity seeds 2 and 4 'entropy collapse'.** Entropy stayed high; the cause was left open.
5. **Event-bonus per-new-view payment** was written as 0.0975 in round-2 notes; the code pays h0^2 - (h0 - 0.1)^2 = 0.09 (corrected in round 3).
6. **Round 3, coef x normalization logistic model not estimable** (all 60 normalization-off seeds solved); recorded as misses.
7. **Evaluation bias, rounds 1-3.** `evaluate()` kept the first N episodes to finish across 16 parallel envs, over-weighting short successful episodes. Re-evaluation (round 4): 16x16 novelty 1e-3 0.845 -> 0.787; Agent 3 1/160 0.714 -> 0.653; 1/640 0.622 -> 0.548; ranking unchanged. Fixed from round 4 on (per-environment quota).
8. **Round 4, explore-only runs (A2a, A2b) labelled 'cycle-farm'** although pick-ups were not paid in those runs; replay showed non-learning policies. Led to the round-5 rule: cycle-farm applies only where pick-ups or door toggles are paid.
9. **Round 4, B1 and B2 ran concurrently** because a launcher missed a setup status; seeded single-threaded computation, so results are unaffected.
10. **Round 5, Step 0 at growth 1/160** used a certified early stop (validated against full convergence on all 21 growth-1/40 cases) instead of full convergence.
11. **Round 5, A-P2m is a 'hit' on a negligible effect** (success-curve area 0.025 vs 0.022); both runs are at the floor and the solve test (A-P2) missed. Do not cite A-P2m as evidence.
12. **Round 5, tamper labels in tamper-off runs.** The 'tamperers' column for tamper-off runs counts presses of the no-op 'done' action (e.g. A2 presses at the uniform-random rate); the labels apply only to tamper-on runs.
13. **Round 5, Part D 'found then lost'** includes seeds that only met the goal by chance; only 7/77 declined after real learning (D1-P2 miss), and D3 rests on those 7 seeds.
