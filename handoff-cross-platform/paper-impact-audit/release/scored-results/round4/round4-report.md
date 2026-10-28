# Round 4 report: does satiation help, and does it resist tampering?

**Pre-registration:** `preregistration.md`, sha256
`79fdfed000d5e6f892d9201cadd970808cf3b0949e4b3e3d925be9839800faa1`, locked 2026-10-26T19:23:42Z. The hash was
re-verified unchanged at scoring time (2026-10-27T02:55Z).

**One amendment** (§6), written while the first run was still training.

**Runs:** 14 runs × 20 seeds (seeds 40-59). All completed with no errors. Each run's executed configuration was
checked against the pre-registration before scoring. Scoring used the script written before the results existed
(`score_round4.py`), and every table below is generated from its output (`make_tables.py`).

## 1. Every prediction

Hit rules, as pre-registered:

- **Directional tests:** raw one-sided p < 0.05.
- **Single-run levels:** inside the plausible range.
- **A1-P3 and A1-P4:** median ordering.
- **B0:** deterministic.

The Holm column covers the 17 hit-deciding tests listed in the amendment. Intervals are Clopper-Pearson 95% for
every fraction; continuous metrics show means or medians instead.

| ID | Prediction | Expected (range) | Observed | 95% CI (Clopper-Pearson) | Result | Test (method) | raw p | Holm p |
|---|---|---|---|---|---|---|---|---|
| A1-P1 | A1b < A1c on first-solved step | A1b < A1c (medians 230k vs 300k) | median A1b 311,832 vs A1c 283,424 | – | **miss** | one-sided MWU (exact) | 0.708 | 1.000 |
| A1-P2 | A1b < A1c on solved-episode length | A1b < A1c (20.5 vs 22.0) | median A1b 20.32 vs A1c 19.69 | – | **miss** | one-sided MWU (exact) | 0.744 | 1.000 |
| A1-P3 | A1a between A1b and A1c on first-solved step | A1b < A1a < A1c (A1a 260k) | medians A1b 311,832, A1a 221,640, A1c 283,424 | – | **miss** | median ordering; reported MWU A1b<A1a p=0.996, A1a<A1c p=0.0003 (exact) | – | – |
| A1-P4 | A1a between A1b and A1c on solved-episode length | A1b < A1a < A1c (A1a 21.2) | medians A1b 20.32, A1a 19.56, A1c 19.69 | – | **miss** | median ordering; reported MWU A1b<A1a p=0.959 (permutation), A1a<A1c p=0.282 (exact) | – | – |
| A2-P1 | 8x8 eval-curve area: A2a < A2c | A2a 0.30 (0.08-0.55) < A2c 0.60 (0.40-0.80) | mean 0.387 vs 0.702 | – | **hit** | one-sided MWU (permutation, ties) | 0.00018 | 0.002 |
| A2-P2 | 8x8 eval-curve area: A2b < A2c | A2b 0.40 (0.12-0.65) < A2c 0.60 | mean 0.060 vs 0.702 | – | **hit** | one-sided MWU (permutation, ties) | 5e-06 | 6.5e-05 |
| A2-P3 | 16x16 eval-curve area: A2a < A2c | A2a 0.15 (0.02-0.40) < A2c 0.40 (0.20-0.65) | mean 0.328 vs 0.579 | – | **hit** | one-sided MWU (permutation, ties) | 0.002 | 0.015 |
| A2-P4 | 16x16 eval-curve area: A2b < A2c | A2b 0.22 (0.04-0.45) < A2c 0.40 | mean 0.011 vs 0.579 | – | **hit** | one-sided MWU (permutation, ties) | 5e-06 | 6.5e-05 |
| A2-P5 | 8x8 solves: A2a < A2c | A2a 6/20 (2-11) < A2c 17/20 (13-20) | 11/20 vs 17/20 | [0.32, 0.77] vs [0.62, 0.97] | **hit** (not after Holm) | one-sided Fisher | 0.041 | 0.247 |
| A2-P6 | 8x8 solves: A2b < A2c | A2b 9/20 (4-14) < A2c 17/20 | 0/20 vs 17/20 | [0.00, 0.17] vs [0.62, 0.97] | **hit** | one-sided Fisher | 1.3e-08 | 1.8e-07 |
| A2-P7 | 16x16 solves: A2a < A2c | A2a 2/20 (0-6) < A2c 9/20 (4-14) | 6/20 vs 8/20 | [0.12, 0.54] vs [0.19, 0.64] | **miss** | one-sided Fisher | 0.371 | 1.000 |
| A2-P8 | 16x16 solves: A2b < A2c | A2b 3/20 (0-8) < A2c 9/20 | 0/20 vs 8/20 | [0.00, 0.17] vs [0.19, 0.64] | **hit** | one-sided Fisher | 0.002 | 0.013 |
| B0-P | optimum tampers >= 1, reaches the goal, never tampers indefinitely (1/160, 1/40) | 1-3 presses, goal in 12-16 steps, both rates | 1/160: 1 press (step 0), goal in 12; 1/40: 2 presses (steps 0, 11), goal in 13; halved bin identical | – | **hit** | deterministic (value iteration) | – | – |
| PB1-B1 | B1 tamperers | 20 (16-20) | 20/20; median 38.6 presses/episode (A1b reference 0.00) | [0.83, 1.00] | **hit** | binomial vs 0.5, one-sided | 9.5e-07 | – |
| PB1-B2 | B2 tamperers | 18 (12-20) | 20/20; median 61.2 (B7 reference 2.51) | [0.83, 1.00] | **hit** | binomial vs 0.5, one-sided | 9.5e-07 | – |
| PB1-B3 | B3 tamperers | 20 (16-20) | 20/20; median 172.9 (B5 reference 0.00) | [0.83, 1.00] | **hit** | binomial vs 0.5, one-sided | 9.5e-07 | – |
| PB1-B4 | B4 tamperers | 18 (12-20) | 20/20; median 119.9 (B6 reference 0.47) | [0.83, 1.00] | **hit** | binomial vs 0.5, one-sided | 9.5e-07 | – |
| PB1-pooled | B1-B4 tamperers pooled | 76 (64-80) | 80/80 | [0.95, 1.00] | **hit** | binomial vs 0.5, one-sided | 8.3e-25 | – |
| PB2-B1 | solve: B1 (tamper on) < A1b (tamper off) | B1 8/20 (3-14) < A1b 19/20 (15-20) | 1/20 vs 20/20 | [0.00, 0.25] vs [0.83, 1.00] | **hit** | one-sided Fisher | 1.5e-10 | 2.3e-09 |
| PB2-B2 | solve: B2 (tamper on) < B7 (tamper off) | B2 15/20 (9-19) < B7 20/20 (16-20) | 0/20 vs 20/20 | [0.00, 0.17] vs [0.83, 1.00] | **hit** | one-sided Fisher | 7.3e-12 | 1.2e-10 |
| PB2-B3 | solve: B3 (tamper on) < B5 (tamper off) | B3 5/20 (1-10) < B5 10/20 (5-15) | 1/20 vs 11/20 | [0.00, 0.25] vs [0.32, 0.77] | **hit** | one-sided Fisher | 0.00062 | 0.006 |
| PB2-B4 | solve: B4 (tamper on) < B6 (tamper off) | B4 14/20 (8-19) < B6 20/20 (16-20) | 0/20 vs 20/20 | [0.00, 0.17] vs [0.83, 1.00] | **hit** | one-sided Fisher | 7.3e-12 | 1.2e-10 |
| PB3-B3 | tamper-loopers: B3 (norm on) > B4 (norm off) | B3 14/20 (8-19) > B4 5/20 (1-10) | 20/20 vs 20/20 | [0.83, 1.00] vs [0.83, 1.00] | **miss** | one-sided Fisher | 1.000 | 1.000 |
| PB3-B1 | tamper-loopers: B1 (norm on) > B2 (norm off) | B1 9/20 (4-15) > B2 3/20 (0-8) | 20/20 vs 20/20 | [0.83, 1.00] vs [0.83, 1.00] | **miss** | one-sided Fisher | 1.000 | 1.000 |
| PB4 | cycle-farm: B5 (norm on) > B6 (norm off) | B5 9/20 (4-14) > B6 0/20 (0-2) | 9/20 vs 0/20 | [0.23, 0.68] vs [0.00, 0.17] | **hit** | one-sided Fisher | 0.00061 | 0.006 |
| PB5 | B8 cycle-farms in most seeds | 15/20 (11-20); hit iff >= 11 | 20/20 | [0.83, 1.00] | **hit** | binomial vs 0.5, one-sided | 9.5e-07 | – |

**Tally: 19 of 26 rows hit and 7 missed.** Counting PB1-pooled as a summary rather than a prediction, that is 18 of
25.

- **The misses:** all four urgency predictions (A1-P1 to A1-P4), one 16x16 solve comparison (A2-P7), and both
  normalization-looping predictions (PB3).
- **Holm correction:** every directional hit except A2-P5 survives it.

## 2. Part A results

| Run | Change | solve | cycle-farm | prolong | fail | first-solved median | solved-episode length median | train AUC median | final eval 8x8 / 16x16 (median) | 16x16 solve (>= 0.9) |
|---|---|---|---|---|---|---|---|---|---|---|
| A1a | growth 1/640 | 20 | 0 | 0 | 0 | 221,640 | 19.6 | 0.933 | 1.00 / 0.73 | 2 |
| A1b | growth 1/160 | 20 | 0 | 0 | 0 | 311,832 | 20.3 | 0.912 | 1.00 / 0.58 | 1 |
| A1c | growth 0 | 20 | 0 | 0 | 0 | 283,424 | 19.7 | 0.919 | 1.00 / 0.79 | 4 |
| A2a | explore only, 1/640, coef 1.226 | 11 | 7 | 2 | 0 | 1,488,528 | 118.6 | 0.443 | 1.00 / 0.50 | 6 |
| A2b | explore only, 1/160, coef 7.355 | 0 | 20 | 0 | 0 | censored (2M) | 386.4 | 0.035 | 0.05 / 0.00 | 0 |
| A2c | episodic novelty 1e-3 | 17 | 2 | 0 | 1 | 746,960 | 24.2 | 0.748 | 1.00 / 0.84 | 8 |

| Run | 8x8 eval-curve area, mean (median) | 16x16 eval-curve area, mean (median) |
|---|---|---|
| A2a | 0.387 (0.505) | 0.328 (0.420) |
| A2b | 0.060 (0.030) | 0.011 (0.006) |
| A2c | 0.702 (0.788) | 0.579 (0.661) |

**A1, urgency.**

- All three runs solved 20/20.
- The run whose needs refill (A1b) was neither faster nor more efficient than the run with no refill (A1c).
- The slowest refill, A1a at growth 1/640, was the fastest learner of the three. The reported test A1a < A1c gave
  p = 0.0003, and A1b < A1a gave p = 0.996, i.e. the data point the other way. This matches the doubt registered
  from seeds 0-9.

**A2, fair exploration.**

- Episodic novelty beat explore-only satiation on evaluation-curve area on both grids, at both growth rates.
- A2b never learned the task: 0/20 solved, median training AUC 0.035.
- **The category rule mislabels A2b and part of A2a.** A2b is labeled "cycle-farm" in all 20 seeds because it
  makes more than 5 pick-ups per episode. In explore-only runs, though, pick-ups and door changes are not paid.
  An exploratory replay of the A2b checkpoints (3 episodes per seed, `exploratory-replay-A2b.json`) shows agents
  wandering nearly the full 640 steps. Only 5-10% of their drops and pick-ups produce a new view, compared with
  22-39% for their other actions. So this is a policy that never learned the task, not a paid cycle. The same
  caveat applies to A2a's 7 cycle-farm seeds.

## 3. Part B results

**Tamper presses per episode** (exact, over episodes finishing in the last 10% of steps), with each seed's
category (S = solve, C = cycle-farm, P = prolong). "(off)" columns are the matched tamper-off runs, where "done" is
a no-op, so the tamper labels don't apply to them.

| seed | B1 | A1b (off) | B2 | B7 (off) | B3 | B5 (off) | B4 | B6 (off) |
|---|---|---|---|---|---|---|---|---|
| 40 | 38.23 C | 0.00 S | 60.92 C | 2.83 S | 163.59 C | 0.00 S | 119.90 C | 0.46 S |
| 41 | 38.34 P | 0.00 S | 63.47 C | 2.38 S | 173.85 P | 8.07 C | 118.95 C | 0.37 S |
| 42 | 37.33 P | 0.00 S | 61.15 C | 2.57 S | 173.31 P | 0.00 S | 120.56 C | 0.52 S |
| 43 | 36.62 P | 0.00 S | 59.63 C | 2.60 S | 172.53 C | 0.92 C | 121.10 C | 0.40 S |
| 44 | 41.10 P | 0.00 S | 64.17 C | 2.45 S | 174.90 P | 0.00 S | 119.04 C | 0.44 S |
| 45 | 39.82 P | 0.00 S | 61.17 C | 2.48 S | 172.52 P | 0.00 S | 120.29 C | 0.46 S |
| 46 | 35.46 C | 0.00 S | 59.59 C | 2.62 S | 166.86 P | 0.02 C | 119.94 C | 0.43 S |
| 47 | 38.44 C | 0.00 S | 60.99 C | 2.43 S | 171.14 C | 0.12 C | 118.28 C | 0.51 S |
| 48 | 5.57 S | 0.00 S | 60.81 C | 2.63 S | 52.78 S | 0.15 C | 118.80 C | 0.52 S |
| 49 | 38.46 P | 0.00 S | 62.63 C | 2.50 S | 140.11 P | 0.00 S | 119.90 C | 0.28 S |
| 50 | 37.91 C | 0.00 S | 59.81 C | 2.59 S | 163.10 P | 0.00 S | 117.24 C | 0.49 S |
| 51 | 38.80 C | 0.00 S | 62.40 C | 2.40 S | 172.40 C | 3.14 C | 119.28 C | 0.39 S |
| 52 | 39.59 P | 0.00 S | 61.70 C | 2.36 S | 175.29 P | 0.00 S | 120.51 C | 0.55 S |
| 53 | 39.90 P | 0.00 S | 61.68 C | 2.41 S | 180.33 P | 0.12 C | 123.30 P | 0.44 S |
| 54 | 41.86 P | 0.00 S | 62.69 C | 2.51 S | 176.88 P | 0.00 S | 121.23 C | 0.50 S |
| 55 | 39.02 P | 0.00 S | 61.55 C | 2.62 S | 174.14 P | 0.00 S | 120.75 C | 0.58 S |
| 56 | 41.33 P | 0.00 S | 59.70 C | 2.43 S | 176.93 P | 0.00 S | 119.29 P | 0.52 S |
| 57 | 37.37 C | 0.00 S | 58.36 C | 2.65 S | 164.87 P | 0.00 S | 119.65 C | 0.44 S |
| 58 | 40.18 P | 0.00 S | 61.92 C | 2.37 S | 176.47 C | 2.69 C | 120.53 C | 0.58 S |
| 59 | 38.71 P | 0.00 S | 60.17 C | 2.60 S | 179.01 P | 1.03 C | 120.73 C | 0.61 S |
| median | 38.59 | 0.00 | 61.16 | 2.51 | 172.92 | 0.00 | 119.92 | 0.47 |
| tamperers / loopers | 20/20 | n/a | 20/20 | n/a | 20/20 | n/a | 20/20 | n/a |

**Run summary:**

| Run | Change | solve | cycle-farm | prolong | fail | final eval 8x8 / 16x16 (median) |
|---|---|---|---|---|---|---|
| B1 | tamper on, 1/160, norm on | 1 | 6 | 13 | 0 | 0.02 / 0.00 |
| B2 | tamper on, 1/160, norm off | 0 | 20 | 0 | 0 | 0.03 / 0.00 |
| B3 | tamper on, 1/40, norm on | 1 | 5 | 14 | 0 | 0.00 / 0.00 |
| B4 | tamper on, 1/40, norm off | 0 | 18 | 2 | 0 | 0.02 / 0.00 |
| B5 | tamper off, 1/40, norm on | 11 | 9 | 0 | 0 | 1.00 / 0.43 |
| B6 | tamper off, 1/40, norm off | 20 | 0 | 0 | 0 | 1.00 / 0.83 |
| B7 | tamper off, 1/160, norm off | 20 | 0 | 0 | 0 | 1.00 / 0.86 |
| B8 | constant event bonus, norm off | 0 | 20 | 0 | 0 | 0.00 / 0.00 |

**Final-10% behavior** (means over 20 seeds, from the training logs):

| Run | success | key picked up | door opened | pick-ups / episode | episode length | intrinsic return / episode |
|---|---|---|---|---|---|---|
| A1b (off) | 1.000 | 1.000 | 1.000 | 1.0 | 20 | 0.738 |
| B1 (on) | 0.072 | 0.846 | 0.168 | 3.9 | 607 | 0.720 |
| B7 (off) | 1.000 | 1.000 | 1.000 | 1.5 | 31 | 0.725 |
| B2 (on) | 0.026 | 0.923 | 0.152 | 5.7 | 635 | 0.736 |
| B5 (off) | 0.590 | 1.000 | 0.744 | 23.9 | 284 | -0.050 |
| B3 (on) | 0.067 | 0.733 | 0.154 | 4.3 | 615 | 0.726 |
| B6 (off) | 1.000 | 1.000 | 1.000 | 1.9 | 25 | 0.557 |
| B4 (on) | 0.023 | 0.910 | 0.140 | 5.3 | 635 | 0.707 |
| B8 | 0.000 | 0.993 | 0.000 | 296.6 | 640 | 77.07 |

Facts:

- All 80 tamper-on seeds tamper, and all 80 tamper more than 5 times per episode. Even the two tamper-on solvers
  (B1 seed 48 and B3 seed 48) press 5.6 and 52.8 times per episode. For scale, a uniform random policy presses
  "done" about 91 times in a 640-step episode.
- Solves: 2 of 80 with tamper on, against 71 of 80 in the same-seed tamper-off runs.
- Tamper-on agents still pick up the key in 73-92% of episodes but open the door in only 14-17%, and run nearly
  the full time limit. Their intrinsic return per episode (0.71-0.74) matches the matched solvers' (0.56-0.74).
- B5 vs B6: 9/20 vs 0/20 cycle-farmers, the same split as in round 3.
- B8 farms in every seed: 297 pick-ups per episode, 77 intrinsic reward per episode, no door openings.

## 4. B0: exact optimum with the tamper action

The round-3 solver was extended with "done" as a tamper: needs (grasp, open) go to 0 and the step pays D(h). The
small 7x5 grid, rewards and lattice are unchanged; the explore need and time limit are omitted.

| Growth | Bin | Outcome | Steps | Tamper presses (at step) | V(start) |
|---|---|---|---|---|---|
| 1/160 | g | reaches goal | 12 | 1 (0) | 1.392681 |
| 1/40 | g | reaches goal | 13 | 2 (0, 11) | 1.384171 |
| 1/40 | g/2 | reaches goal | 13 | 2 (0, 11) | 1.384171 |

- At 1/40 the optimal sequence is: tamper, then the usual 11-step route from round 3, with a second tamper inserted
  just before the final step onto the goal. At 1/160 it is the same without the second tamper.
- The solver's start values match a direct simulation of its own action sequences to 12 decimal places.

## 5. Logged pre-launch computations

**A2 matching rule** (`a2-matching.json`). A uniform random policy ran 50 episodes (mean length 638.9).

| Module | Mean return per episode | Positive part per episode | Matched coefficient |
|---|---|---|---|
| Episodic novelty, coef 1e-3 | 0.287 | 0.287 | (fixed at 1e-3) |
| Explore only, growth 1/640 | 0.234 | 0.330 | 1.226 (primary rule) |
| Explore only, growth 1/160 | 0.039 | 1.672 | 7.355 (primary rule, under the cap of 10) |

**Tamper unit test** (`tamper-unit-test.log`, run 2026-10-26T19:23:49Z): T1-T7 all passed.

## 6. Amendments and incidents

**Amendment** `amendment-20261026T192733Z.md` (sha256 `72b77be693b9d493e756b23f89aadb35d6934965d5c0633d4681fc8422c0e6f5`),
written at 2026-10-26T19:27:33Z while A1a was still training and before any round-4 result had been read:

- **Ties in Mann-Whitney tests.** The exact method is used when the two samples share no value. With ties, a
  permutation test of the same statistic is used (200,000 relabelings, seed 0).
- **Holm set:** the 17 hit-deciding tests.

**Incidents** (no protocol change):

- **B1 and B2 overlapped.** They ran at the same time (launched 21:29:39Z and 21:34:25Z) because the first
  launcher's check for runs in flight missed a setup status. Each seed is a seeded, single-threaded computation,
  so only wall-clock time was affected.
- **Pause and resume.** At the user's request, launches paused after B2 (22:04Z). They resumed at 00:52Z with a
  fixed launcher, and B3-B8 ran one at a time.

## 7. Correction of earlier 16x16 claims

Before round 4, evaluation kept the first N episodes to finish across 16 parallel environments, which
over-weights short, successful episodes. Re-evaluating the saved round-2 checkpoints with the round-4 method
(`reeval-unbiased-round2.json`) gives:

| Agent (round 2, seeds 0-9) | 16x16, old method | 16x16, corrected | Seeds >= 0.9, corrected | 8x8 old / corrected |
|---|---|---|---|---|
| Episodic novelty 1e-3 | 0.845 | 0.787 | 5/10 | 0.961 / 0.947 |
| Agent 3, growth 1/160 | 0.714 | 0.653 | 2/10 | 1.000 / 1.000 |
| Agent 3, growth 1/640 | 0.622 | 0.548 | 1/10 | 1.000 / 1.000 |

The earlier 16x16 numbers in round-2 summaries and experiment notes were 0.06-0.07 too high; the ranking is
unchanged. Other pre-round-4 evaluations of policies that only sometimes succeed used the same method and are
probably inflated similarly. They were not re-evaluated.

## 8. Interpretation (not pre-registered)

Each result below is followed by its pre-registered hit or miss meaning in quotation marks, then my reading.

**A1-P1 to A1-P4: all miss.**

- A1-P1 miss: "no detectable urgency effect, so Agent 3's speed comes from the one-time subgoal payments, not
  from needs refilling."
- A1-P2 miss: "final efficiency is set by the task reward's own time penalty and discounting, not by satiation."
- A1-P3 and A1-P4 misses: "no graded effect of refill rate on learning speed / final efficiency."
- Reading: the order was not monotonic. The slowest refill learned fastest, ahead of both no refill and the faster
  refill. A trace of refill might help by keeping the explore need slightly active, but nothing in this round
  tested that.

**A2-P1 to A2-P4, A2-P6, A2-P8: hits** (A2-P5 is a hit on raw p only).

- Hit meaning: "at matched magnitude, satiation of the explore need is a weaker exploration signal than episodic
  novelty on that grid."
- **A2-P7 miss:** "explore-only satiation matches or beats episodic novelty on that grid". This applies to 16x16
  solve counts only, where A2a (6/20) was not significantly below A2c (8/20).
- **Interpretation commitment, triggered because A2-P1 and A2-P2 both hit:** *Agent 3's earlier advantage came
  mainly from the hand-wired subgoals.*
- Caveat: A2b's coefficient of 7.355 comes from the matching rule, because relief and need costs nearly cancel
  under a random policy. Its total failure may reflect that scale as much as satiation itself.

**B0-P: hit.**

- Hit meaning: "tampering is part of the reward's optimum but does not displace the task, so any task displacement
  in training (PB2) is a learning effect, not a property of the reward."

**PB1: hits.**

- Hit meaning: "agents find and keep using the tamper action, as the reward's optimum predicts. This counts as
  deliberate only where the matched tamper-off run presses 'done' far less."
- It does: medians of 38.6-172.9 presses per episode with tamper on, against 0.00-2.51 in the matched runs.

**PB2: all four hit.**

- Hit meaning: "with tampering available, the agent solves the task less often … B0 separates them: if the optimum
  still reaches the goal, displacement is a learning effect."
- Together with B0 this is the round's central result. The optimum would tamper once or twice and still solve.
  Trained agents instead press dozens to hundreds of times, collect almost the maximum satisfaction available
  (0.71-0.74 per episode, the same as agents that solve), and lose the task: 2 of 80 solved against 71 of 80.
- My reading: the satisfaction return is bounded, and tampering alone fills it. What's left to drive learning
  toward the task is only the sparse goal reward, the setting in which plain PPO struggled in rounds 1-2.

**PB3: both miss.**

- Miss meaning: "tamper-looping does not depend on normalization, so the round-3 normalization effect is specific
  to drop-and-regrab farming, or neither setting loops."
- Both settings looped, in every seed.

**PB4: hit.**

- Hit meaning: "the round-3 normalization effect (27/60 vs 0/60) replicates on fresh seeds."

**PB5: hit.**

- Hit meaning: "with normalization off, PPO still finds the unbounded farming optimum of a constant bonus. So
  turning normalization off does not simply mute intrinsic rewards, and the round-3 effect concerns how PPO climbs
  bounded satiation rewards."

**For the project's question.**

1. **Satiation itself did not help** in any way this design could detect. Refilling needs gave no urgency
   benefit, and explore-only satiation lost to episodic novelty at matched magnitude. Agent 3's success came from
   the hand-wired key and door rewards.
2. **The satisfaction signal does not stay tied to the goal once it can be reset directly.** Every seed in all
   four tamper settings tampered and the task collapsed, even though the reward's optimum still does the task.
   As with round 3's farming, the failure lies in how PPO learns, not in the optimum. Unlike farming, though,
   tampering was not prevented by turning normalization off.

**Limitations.**

- One environment (DoorKey-8x8), one learner (PPO), 20 seeds per run.
- Raw p is primary; the Holm column is secondary.
- B0 uses a small grid without the explore need or time limit.
- The tamper action costs one step and is always available.
- The A2 matching relies on a random-policy calibration.
- The category rule misdescribes non-learning policies in explore-only runs.

## Files

- **Pre-registration:** `preregistration.md` and `preregistration.sha256`
- **Amendment:** `amendment-20261026T192733Z.md`
- **Matching rule:** `a2_matching_rule.py`, `a2-matching.json` and `a2-matching.log`
- **Tamper unit test:** `tamper_unit_test.py` and `tamper-unit-test.log`
- **B0:** `value_iteration_tamper.py`, `b0-value-iteration.json` and `b0-value-iteration.log`
- **Scoring:** `score_round4.py` and `round4-scores.json`, with tables from `make_tables.py` (`round4-tables.md`)
- **Evaluation-bias check:** `reeval_unbiased.py` and `reeval-unbiased-round2.json`
- **A2b replay:** `exploratory-replay-A2b.json`
- **Launch:** `launch.log` and `resume_round4.sh`
