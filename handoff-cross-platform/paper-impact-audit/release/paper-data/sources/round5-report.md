# Round 5 report: baselines, tamper cost, log analyses, second environment

**Locked files:**
- First lock: `preregistration.md`, sha256 `0298bbc79c323e4613e56a29be0257a6c7c3ad764cbb056902159292bcbcda0d`,
  locked 2026-10-27T04:34:11Z.
- Second lock (Part C): `amendment-20261027T113334Z.md`, sha256
  `1d99028349683b3b85bd204802b614bfb3a38fa30db3d24fbb19eda7c2790a4f`, with `predictions_c.json` (sha256
  `de3f04ec0e4007539f4db24fff5cbdd3337466a776b97aedea0970c8a2fad6d4`), locked 2026-10-27T11:33:34Z.
- The cited scripts (`score_round5.py`, `part_d_analysis.py`, `launch_round5.sh`, `predictions.json`) were all
  re-verified unchanged at scoring time (2026-10-27T13:22Z).

**Runs**, all on the same Mac as round 4, all with no errors:
- A1, A2, B9, B10, B11 on DoorKey-8x8, seeds 40-59;
- one calibration run, seeds 100-104;
- C1-C6 on KeyCorridorS3R1, seeds 60-79.

Scoring used the locked `score_round5.py`; every table below is generated from its output by `make_tables_r5.py`.

## 1. Every prediction

Hit rules:
- A test predicted significant hits iff raw one-sided p < 0.05.
- A test predicted non-significant hits iff p >= 0.05.
- A level prediction hits iff the observed value is inside its range.

Holm adjusts over the 20 pre-registered tests predicted significant. Intervals are Clopper-Pearson 95%.

| ID | Prediction | Expected | Observed | 95% CI (Clopper-Pearson) | Result | Test | raw p | Holm p |
|---|---|---|---|---|---|---|---|---|
| A-P1 | A1 solves more than B1 | A1 6/20 (2-11) > B1 1/20 | 11/20 vs 1/20 | [0.32, 0.77] vs [0.00, 0.25] | **hit** | one-sided Fisher | 0.00062 | 0.004 |
| A-P1m | A1 success-curve area > B1 | A1 AUC mean 0.27 (0.08-0.50) > B1 (round 4: median 0.013) | mean 0.438 vs 0.042 | – | **hit** | one-sided MWU | 7.8e-06 | 7e-05 |
| A-P2 | A2 solves more than B2 | A2 9/20 (2-17) > B2 0/20 | 0/20 vs 0/20 | [0.00, 0.17] vs [0.00, 0.17] | **miss** | one-sided Fisher | 1.000 | 1.000 |
| A-P2m | A2 success-curve area > B2 | A2 AUC mean 0.35 (0.08-0.70) > B2 (round 4: median 0.022) | mean 0.025 vs 0.022 | – | **hit** | one-sided MWU | 0.005 | 0.028 |
| A-P3 | A1 solves more than B1+B3 | A1 6/20 > B1+B3 2/40 | 11/20 vs 2/40 | [0.32, 0.77] vs [0.01, 0.17] | **hit** | one-sided Fisher | 2.6e-05 | 0.00021 |
| A-P3m | A1 success-curve area > B1+B3 | A1 AUC > pooled B1+B3 | mean 0.438 vs 0.039 | – | **hit** | one-sided MWU | 5e-06 | 6e-05 |
| B-JTp | tamper presses decrease with cost (B1, B9, B10, B11) | medians B1 38.6 > B9 30 > B10 8 > B11 0.2 | medians 38.59, 27.13, 0.36, 0.00 | – | **hit** | one-sided Jonckheere-Terpstra (permutation) | 5e-06 | 6e-05 |
| B-JTs | solves increase with cost (B1, B9, B10, B11) | solves B1 1 <= B9 1 < B10 3 < B11 17 | solves 1, 3, 20, 20 | – | **hit** | one-sided Jonckheere-Terpstra (permutation) | 5e-06 | 6e-05 |
| B-F-B9-vsB1 | B9 solves more than B1 | B9 1/20 vs B1 1/20: not significant | 3/20 vs 1/20 | [0.03, 0.38] vs [0.00, 0.25] | **hit** | one-sided Fisher | 0.302 | – |
| B-F-B9-vsA1b | B9 solves fewer than A1b | B9 1/20 < A1b 20/20 | 3/20 vs 20/20 | [0.03, 0.38] vs [0.83, 1.00] | **hit** | one-sided Fisher | 1.3e-08 | 1.7e-07 |
| B-L-B9-presses | B9 presses (median presses per episode) | 30 | 27.13 | – | **hit** | level (range) | – | – |
| B-L-B9-tamperers | B9 tamperers (count of 20) | 20/20 | 19/20 | [0.75, 1.00] | **hit** | level (range) | – | – |
| B-L-B9-solves | B9 solves (count of 20) | 1/20 | 3/20 | [0.03, 0.38] | **hit** | level (range) | – | – |
| B-F-B10-vsB1 | B10 solves more than B1 | B10 3/20 vs B1 1/20: not significant | 20/20 vs 1/20 | [0.83, 1.00] vs [0.00, 0.25] | **miss** | one-sided Fisher | 1.5e-10 | – |
| B-F-B10-vsA1b | B10 solves fewer than A1b | B10 3/20 < A1b 20/20 | 20/20 vs 20/20 | [0.83, 1.00] vs [0.83, 1.00] | **miss** | one-sided Fisher | 1.000 | 1.000 |
| B-L-B10-presses | B10 presses (median presses per episode) | 8 | 0.36 | – | **miss** | level (range) | – | – |
| B-L-B10-tamperers | B10 tamperers (count of 20) | 17/20 (PPO keeps tampering where the optimum has stopped) | 7/20 | [0.15, 0.59] | **miss** | level (range) | – | – |
| B-L-B10-solves | B10 solves (count of 20) | 3/20 | 20/20 | [0.83, 1.00] | **miss** | level (range) | – | – |
| B-F-B11-vsB1 | B11 solves more than B1 | B11 17/20 > B1 1/20 | 20/20 vs 1/20 | [0.83, 1.00] vs [0.00, 0.25] | **hit** | one-sided Fisher | 1.5e-10 | 2.1e-09 |
| B-F-B11-vsA1b | B11 solves fewer than A1b | B11 17/20 vs A1b 20/20: not significant | 20/20 vs 20/20 | [0.83, 1.00] vs [0.83, 1.00] | **hit** | one-sided Fisher | 1.000 | – |
| B-L-B11-presses | B11 presses (median presses per episode) | 0.2 | 0.00 | – | **hit** | level (range) | – | – |
| B-L-B11-tamperers | B11 tamperers (count of 20) | 3/20 (PPO stops, as the optimum does) | 0/20 | [0.00, 0.17] | **hit** | level (range) | – | – |
| B-L-B11-solves | B11 solves (count of 20) | 17/20 | 20/20 | [0.83, 1.00] | **hit** | level (range) | – | – |
| C-P1 | cycle-farming rises C1 < C2 < C3 | farmers C1 0/20, C2 4/20, C3 12/20 | 0/20, 0/20, 0/20 | – | **miss** | one-sided Jonckheere-Terpstra (permutation) | 1.000 | 1.000 |
| C-P2 | cycle-farm: C3 > C4 | C3 12/20 > C4 1/20 | 0/20 vs 0/20 | [0.00, 0.17] vs [0.00, 0.17] | **miss** | one-sided Fisher | 1.000 | 1.000 |
| C-P3 | solve: C5 < C1 | C5 6/20 < C1 20/20 | 0/20 vs 20/20 | [0.00, 0.17] vs [0.83, 1.00] | **hit** | one-sided Fisher | 7.3e-12 | 1.5e-10 |
| C-P4 | solve: C5 < C6 | C5 6/20 < C6 15/20 | 0/20 vs 20/20 | [0.00, 0.17] vs [0.83, 1.00] | **hit** | one-sided Fisher | 7.3e-12 | 1.5e-10 |
| D1-P1 | B1-B4 seeds that never found the goal | 0/80 | 1/80 | [0.00, 0.07] | **hit** | level (range) | – | – |
| D1-P2 | found-then-lost seeds whose success declined (peak >= 0.10, then <= half) | 25 of the found-then-lost seeds (hit iff >= 20%) | 7/77 | [0.04, 0.18] | **miss** | level: hit iff >= 20% (>= 16) | – | – |
| D1-P3 | median exact first-goal step of B1-B4 seeds | 18,000 (hit iff <= 41,000) | 27,344 (max 1,187,264) | – | **hit** | level: hit iff <= 41,000 | – | – |
| D2-B1 | final-10% policy entropy B1 (tamper on) > A1b (tamper off) | median tamper-on 1.2 (0.8-1.7) > tamper-off 0.5 (0.2-0.9) | median 1.878 vs 0.067 | – | **hit** | one-sided MWU | 7.3e-12 | 1.5e-10 |
| D2-B2 | final-10% policy entropy B2 (tamper on) > B7 (tamper off) | tamper-on > tamper-off | median 1.935 vs 1.138 | – | **hit** | one-sided MWU | 7.3e-12 | 1.5e-10 |
| D2-B3 | final-10% policy entropy B3 (tamper on) > B5 (tamper off) | tamper-on > tamper-off | median 1.844 vs 0.290 | – | **hit** | one-sided MWU | 7.3e-12 | 1.5e-10 |
| D2-B4 | final-10% policy entropy B4 (tamper on) > B6 (tamper off) | tamper-on > tamper-off | median 1.934 vs 0.598 | – | **hit** | one-sided MWU | 7.3e-12 | 1.5e-10 |
| D3-P1 | 'done' fraction rises before success declines | rise first in 85% (hit iff >= 80%) | rise first 7/7 (undetermined 0) | [0.59, 1.00] | **hit** | binomial vs 0.5, one-sided; hit iff share >= 0.8 | 0.008 | 0.039 |

Holm set size: 20 tests.

**Tally:** 35 rows, 26 hits, 9 misses, 0 unresolvable.

- Of the 20 tests in the Holm set, 16 hit, and all 16 survive Holm.
- **The 9 misses:**
  - A-P2 (A2 solves);
  - all five B10 rows (B10 vs B1, B10 vs A1b, and its presses, tamperers and solves);
  - C-P1 and C-P2 (farming in Part C);
  - D1-P2 (decline after learning).

## 2. Every run: solve count and success-curve area

| Run | Env, budget | solve | cycle-farm | prolong | fail | cycle-farm label | success-curve area mean | presses/ep. median | tamperers | pick-ups median |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | DoorKey-8x8, 2M | 11 [0.32, 0.77] | 0 | 9 | 0 | not applicable | 0.438 | 0.38 | 9 | 1.01 |
| A2 | DoorKey-8x8, 2M | 0 [0.00, 0.17] | 0 | 20 | 0 | not applicable | 0.025 | 90.53 | 20 | 5.69 |
| B9 | DoorKey-8x8, 2M | 3 [0.03, 0.38] | 8 | 8 | 1 | applicable | 0.147 | 27.13 | 19 | 4.97 |
| B10 | DoorKey-8x8, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.601 | 0.36 | 7 | 1.01 |
| B11 | DoorKey-8x8, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.816 | 0.00 | 0 | 1.00 |
| C1 | KeyCorridorS3R1, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.958 | 0.00 | 0 | 1.00 |
| C2 | KeyCorridorS3R1, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.961 | 0.00 | 0 | 1.09 |
| C3 | KeyCorridorS3R1, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.932 | 0.00 | 0 | 1.74 |
| C4 | KeyCorridorS3R1, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.929 | 0.01 | 0 | 1.68 |
| C5 | KeyCorridorS3R1, 2M | 0 [0.00, 0.17] | 0 | 20 | 0 | applicable | 0.002 | 16.00 | 20 | 0.15 |
| C6 | KeyCorridorS3R1, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | not applicable | 0.875 | 0.00 | 0 | 1.00 |
| r4-B1 | DoorKey-8x8, 2M | 1 [0.00, 0.25] | 6 | 13 | 0 | applicable | 0.042 | 38.59 | 20 | 3.71 |
| r4-B2 | DoorKey-8x8, 2M | 0 [0.00, 0.17] | 20 | 0 | 0 | applicable | 0.022 | 61.16 | 20 | 5.70 |
| r4-B3 | DoorKey-8x8, 2M | 1 [0.00, 0.25] | 5 | 14 | 0 | applicable | 0.036 | 172.92 | 20 | 4.13 |
| r4-A1b | DoorKey-8x8, 2M | 20 [0.83, 1.00] | 0 | 0 | 0 | applicable | 0.901 | 0.00 | 0 | 1.00 |

- **Tamper labels** apply only to tamper-on runs (B9-B11, C5). For the other runs, "tamperers" counts presses of the
  no-op "done" action. A2, for example, presses it at the uniform-random rate.
- **The round-5 cycle-farm rule** labels A1, A2 and C6 "not applicable", because pick-ups are not paid there. Under
  the old rule, A2's pick-ups (median 5.69 per episode) would have made most of its seeds "cycle-farm"; they are now
  "prolong".

## 3. Part A: same-seed baselines

**A1, task reward only, normalization on:**
- 11/20 solved, success-curve area 0.438.
- That is better than the round-4 tamper-on runs on the same seeds: B1 1/20 (area 0.042) and B1+B3 2/40.
- All four A1 tests hit.

**A2, task reward only, normalization off: never learned.**
- 0/20 solved, area 0.025.
- It still pressed "done" about 90 times per 640-step episode, the uniform-random rate.
- So A-P2 (solves) is a miss, at the floor against B2's 0/20.
- A-P2m is a hit at p = 0.005, but on a negligible difference in area (0.025 vs 0.022).

## 4. Part B: tamper-cost sweep (growth 1/160, normalization on)

Per seed: tamper presses per episode over the last 10% of steps, and category (S = solve, C = cycle-farm,
P = prolong, F = fail). B1 and A1b are round-4 references on the same seeds.

| seed | B1 (c=0) | B9 (c=0.01) | B10 (c=0.1) | B11 (c=1.0) | A1b (tamper off) |
|---|---|---|---|---|---|
| 40 | 38.23 C | 27.08 C | 2.01 S | 0.00 S | 0.00 S |
| 41 | 38.34 P | 16.80 F | 0.00 S | 0.00 S | 0.00 S |
| 42 | 37.33 P | 27.42 C | 0.30 S | 0.00 S | 0.00 S |
| 43 | 36.62 P | 9.94 S | 0.74 S | 0.00 S | 0.00 S |
| 44 | 41.10 P | 27.68 P | 0.03 S | 0.00 S | 0.00 S |
| 45 | 39.82 P | 0.52 S | 0.00 S | 0.00 S | 0.00 S |
| 46 | 35.46 C | 25.57 C | 1.41 S | 0.00 S | 0.00 S |
| 47 | 38.44 C | 18.37 C | 0.05 S | 0.00 S | 0.00 S |
| 48 | 5.57 S | 1.35 S | 1.02 S | 0.00 S | 0.00 S |
| 49 | 38.46 P | 27.61 P | 0.25 S | 0.00 S | 0.00 S |
| 50 | 37.91 C | 27.24 C | 0.42 S | 0.00 S | 0.00 S |
| 51 | 38.80 C | 25.34 C | 3.86 S | 0.00 S | 0.00 S |
| 52 | 39.59 P | 27.00 C | 0.45 S | 0.00 S | 0.00 S |
| 53 | 39.90 P | 28.54 P | 2.19 S | 0.00 S | 0.00 S |
| 54 | 41.86 P | 28.65 P | 0.00 S | 0.00 S | 0.00 S |
| 55 | 39.02 P | 26.25 P | 0.00 S | 0.00 S | 0.00 S |
| 56 | 41.33 P | 27.24 P | 1.04 S | 0.00 S | 0.00 S |
| 57 | 37.37 C | 27.18 C | 0.03 S | 0.00 S | 0.00 S |
| 58 | 40.18 P | 29.74 P | 4.18 S | 0.00 S | 0.00 S |
| 59 | 38.71 P | 28.12 P | 0.12 S | 0.00 S | 0.00 S |

- **B9 (c = 0.01, just below the cost at which the Step 0 optimum stops tampering):**
  - agents still press a median 27 times per episode, against the optimum's single press;
  - 19/20 tamper;
  - only 3/20 solve.
- **B10 (c = 0.1, above that cost):**
  - pressing nearly stops: median 0.36 per episode; 7/20 seeds still average >= 1;
  - **all 20 seeds solve**, though more slowly than without a tamper action (area 0.601 vs A1b's 0.901).
- **B11 (c = 1.0):** no pressing at all; 20/20 solve (area 0.816).
- **Trends:** pressing falls and solving rises with c (both JT p = 5e-6).

## 5. Part C: second environment

**Calibration**, the pre-registered first attempt: MiniGrid-KeyCorridorS3R1 at 2M steps.
- 5/5 calibration seeds solve, so it was selected and no other attempt was run.
- Per seed: final success 1.00; area 0.964-0.967; first solved at 107,952-113,216 steps; solved episodes 15-17 steps.
- The other five calibration nodes were archived unrun.
- Calibration seeds are excluded from every test.

**Test runs (seeds 60-79):**

| Run | Setting | Result |
|---|---|---|
| C1 | 1/160, norm on | 20/20 solve, 0 farmers |
| C2 | 1/40, norm on | 20/20 solve, 0 farmers |
| C3 | 1/20, norm on | 20/20 solve, 0 farmers |
| C4 | 1/20, norm off | 20/20 solve, 0 farmers |
| C5 | 1/160, norm on, tamper on | **0/20 solve**, 20/20 prolong, median 16 presses per 270-step episode |
| C6 | task reward only | 20/20 solve |

**Exploratory (not pre-registered).** Repeated key pick-ups did appear briefly early in training. The highest
rolling pick-ups per episode over training rose with growth rate:

| Run | Median peak | Maximum peak |
|---|---|---|
| C1 | 8.0 | 9.9 |
| C2 | 12.4 | 14.4 |
| C3 | 28.3 | 48.5 |
| C6 (task reward only, from random early behavior) | 5.7 | – |

Every seed abandoned them: final pick-ups were 1.0-1.7 per episode, and median first-solved steps were 137k (C1),
138k (C2), 202k (C3) and 258k (C6). C5's final policy entropy has a median of 1.85; the maximum, a uniform choice
over 7 actions, is 1.95. C5 picks up the key in only 15% of episodes.

## 6. Part D: analyses of round-4 logs

**D1:**
- 1/80 tamper-on seeds never found the goal; 77 found it then lost it; 2 kept solving.
- The median exact first-goal step was 27,344 (maximum 1,187,264).
- Only 7 of the 77 found-then-lost seeds declined after real learning (peak rolling success >= 0.10). That is 9%,
  below the registered 20%.

**D2:**
- Final-10% policy entropy of tamper-on seeds has a median of 1.84-1.94, against a maximum of ln 7 = 1.95.
- Their matched tamper-off runs: A1b 0.067, B7 1.138, B5 0.290, B6 0.598.
- All four pairs: p = 7e-12.

**D3:**
- Resolvable: 7 seeds had both events, none undetermined.
- In all 7 the "done" share rose before success declined (binomial p = 0.008).
- The other seeds had no rise (17) or no decline (56), so this result rests on a minority of seeds.

| run | seed | first-goal step | class | peak success (step) | final-10% success | declined | entropy final-10% | done share final-10% | rise step | decline step | order |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | 40 | 88,800 | found then lost | 0.04 (491,520) | 0.021 | no | 1.897 | 0.060 | 40,960 | None | no decline |
| B1 | 41 | 6,288 | found then lost | 0.06 (20,480) | 0.026 | no | 1.878 | 0.061 | 40,960 | None | no decline |
| B1 | 42 | 71,008 | found then lost | 0.05 (1,536,000) | 0.036 | no | 1.858 | 0.059 | 40,960 | None | no decline |
| B1 | 43 | 25,632 | found then lost | 0.13 (1,474,560) | 0.083 | no | 1.872 | 0.059 | 40,960 | 1,536,000 | rise first |
| B1 | 44 | 255,984 | found then lost | 0.03 (1,576,960) | 0.002 | no | 1.866 | 0.064 | 40,960 | None | no decline |
| B1 | 45 | 4,432 | found then lost | 0.06 (20,480) | 0.010 | no | 1.887 | 0.062 | 40,960 | None | no decline |
| B1 | 46 | 46,864 | found then lost | 0.10 (102,400) | 0.034 | yes | 1.892 | 0.056 | 40,960 | 143,360 | rise first |
| B1 | 47 | 18,384 | found then lost | 0.17 (143,360) | 0.009 | yes | 1.891 | 0.060 | 40,960 | 204,800 | rise first |
| B1 | 48 | 57,600 | kept solving | 1.00 (1,822,720) | 0.997 | no | 1.164 | 0.067 | 40,960 | None | no decline |
| B1 | 49 | 6,096 | found then lost | 0.13 (471,040) | 0.022 | yes | 1.852 | 0.060 | None | 532,480 | no rise |
| B1 | 50 | 194,448 | found then lost | 0.09 (1,843,200) | 0.040 | no | 1.885 | 0.060 | 40,960 | None | no decline |
| B1 | 51 | 16,096 | found then lost | 0.10 (204,800) | 0.026 | yes | 1.881 | 0.061 | 61,440 | 225,280 | rise first |
| B1 | 52 | 20,368 | found then lost | 0.05 (1,925,120) | 0.027 | no | 1.880 | 0.063 | 40,960 | None | no decline |
| B1 | 53 | 9,568 | found then lost | 0.03 (20,480) | 0.008 | no | 1.853 | 0.062 | 40,960 | None | no decline |
| B1 | 54 | 144,624 | found then lost | 0.03 (1,720,320) | 0.002 | no | 1.871 | 0.065 | 40,960 | None | no decline |
| B1 | 55 | 6,080 | found then lost | 0.06 (512,000) | 0.019 | no | 1.864 | 0.061 | 40,960 | None | no decline |
| B1 | 56 | 101,200 | found then lost | 0.02 (1,105,920) | 0.000 | no | 1.881 | 0.064 | 61,440 | None | no decline |
| B1 | 57 | 17,424 | found then lost | 0.20 (552,960) | 0.054 | yes | 1.859 | 0.060 | 40,960 | 675,840 | rise first |
| B1 | 58 | 107,488 | found then lost | 0.13 (389,120) | 0.001 | yes | 1.878 | 0.063 | 20,480 | 430,080 | rise first |
| B1 | 59 | 9,008 | found then lost | 0.05 (40,960) | 0.019 | no | 1.886 | 0.061 | 40,960 | None | no decline |
| B2 | 40 | 10,096 | found then lost | 0.06 (634,880) | 0.028 | no | 1.935 | 0.096 | None | None | no rise |
| B2 | 41 | 6,288 | found then lost | 0.07 (1,310,720) | 0.022 | no | 1.936 | 0.100 | None | None | no rise |
| B2 | 42 | 56,416 | found then lost | 0.06 (1,945,600) | 0.024 | no | 1.936 | 0.096 | None | None | no rise |
| B2 | 43 | 29,664 | found then lost | 0.05 (1,249,280) | 0.023 | no | 1.934 | 0.094 | 163,840 | None | no decline |
| B2 | 44 | 55,184 | found then lost | 0.06 (1,310,720) | 0.016 | no | 1.938 | 0.101 | 102,400 | None | no decline |
| B2 | 45 | 4,432 | found then lost | 0.06 (1,044,480) | 0.026 | no | 1.935 | 0.096 | None | None | no rise |
| B2 | 46 | 86,112 | found then lost | 0.07 (1,761,280) | 0.031 | no | 1.935 | 0.094 | None | None | no rise |
| B2 | 47 | 25,184 | found then lost | 0.06 (1,761,280) | 0.039 | no | 1.936 | 0.097 | None | None | no rise |
| B2 | 48 | 47,808 | found then lost | 0.08 (552,960) | 0.036 | no | 1.936 | 0.096 | None | None | no rise |
| B2 | 49 | 20,272 | found then lost | 0.09 (1,351,680) | 0.042 | no | 1.936 | 0.099 | None | None | no rise |
| B2 | 50 | 19,568 | found then lost | 0.07 (1,044,480) | 0.024 | no | 1.934 | 0.094 | None | None | no rise |
| B2 | 51 | 16,176 | found then lost | 0.07 (593,920) | 0.032 | no | 1.936 | 0.098 | None | None | no rise |
| B2 | 52 | 9,728 | found then lost | 0.07 (1,998,848) | 0.032 | no | 1.935 | 0.097 | None | None | no rise |
| B2 | 53 | 9,568 | found then lost | 0.05 (1,761,280) | 0.027 | no | 1.936 | 0.097 | 122,880 | None | no decline |
| B2 | 54 | 57,744 | found then lost | 0.06 (983,040) | 0.028 | no | 1.936 | 0.099 | None | None | no rise |
| B2 | 55 | 6,080 | found then lost | 0.08 (1,658,880) | 0.012 | no | 1.935 | 0.097 | None | None | no rise |
| B2 | 56 | 18,576 | found then lost | 0.05 (1,720,320) | 0.017 | no | 1.934 | 0.094 | None | None | no rise |
| B2 | 57 | 12,864 | found then lost | 0.06 (20,480) | 0.024 | no | 1.933 | 0.092 | None | None | no rise |
| B2 | 58 | 111,680 | found then lost | 0.06 (184,320) | 0.020 | no | 1.936 | 0.098 | 81,920 | None | no decline |
| B2 | 59 | 88,320 | found then lost | 0.05 (532,480) | 0.018 | no | 1.935 | 0.095 | None | None | no rise |
| B3 | 40 | 8,928 | found then lost | 0.09 (778,240) | 0.014 | no | 1.872 | 0.257 | 20,480 | None | no decline |
| B3 | 41 | 6,288 | found then lost | 0.03 (20,480) | 0.008 | no | 1.853 | 0.273 | 20,480 | None | no decline |
| B3 | 42 | 695,728 | found then lost | 0.02 (1,064,960) | 0.002 | no | 1.859 | 0.270 | 20,480 | None | no decline |
| B3 | 43 | 1,187,264 | found then lost | 0.03 (1,228,800) | 0.006 | no | 1.846 | 0.270 | 20,480 | None | no decline |
| B3 | 44 | 690,464 | found then lost | 0.05 (819,200) | 0.000 | no | 1.835 | 0.273 | 20,480 | None | no decline |
| B3 | 45 | 4,432 | found then lost | 0.03 (20,480) | 0.000 | no | 1.819 | 0.270 | 20,480 | None | no decline |
| B3 | 46 | 377,712 | found then lost | 0.04 (1,761,280) | 0.002 | no | 1.882 | 0.261 | 20,480 | None | no decline |
| B3 | 47 | 9,120 | found then lost | 0.13 (491,520) | 0.013 | yes | 1.858 | 0.268 | 20,480 | 552,960 | rise first |
| B3 | 48 | 163,520 | kept solving | 0.94 (1,998,848) | 0.901 | no | 1.323 | 0.217 | 20,480 | None | no decline |
| B3 | 49 | 27,808 | found then lost | 0.40 (1,863,680) | 0.334 | no | 1.773 | 0.254 | 20,480 | None | no decline |
| B3 | 50 | 9,696 | found then lost | 0.04 (655,360) | 0.013 | no | 1.897 | 0.256 | 20,480 | None | no decline |
| B3 | 51 | 846,704 | found then lost | 0.03 (1,597,440) | 0.008 | no | 1.853 | 0.270 | 20,480 | None | no decline |
| B3 | 52 | 1,092,016 | found then lost | 0.01 (1,105,920) | 0.003 | no | 1.844 | 0.274 | 20,480 | None | no decline |
| B3 | 53 | 16,960 | found then lost | 0.03 (20,480) | 0.000 | no | 1.824 | 0.282 | 20,480 | None | no decline |
| B3 | 54 | 959,856 | found then lost | 0.01 (962,560) | 0.002 | no | 1.829 | 0.277 | 20,480 | None | no decline |
| B3 | 55 | 233,168 | found then lost | 0.02 (245,760) | 0.003 | no | 1.822 | 0.272 | 20,480 | None | no decline |
| B3 | 56 | 50,832 | found then lost | 0.01 (61,440) | 0.000 | no | 1.808 | 0.276 | 20,480 | None | no decline |
| B3 | 57 | 15,824 | found then lost | 0.06 (20,480) | 0.017 | no | 1.887 | 0.258 | 20,480 | None | no decline |
| B3 | 58 | never | never found the goal | 0.00 | 0.000 | no | 1.722 | 0.276 | 20,480 | None | no decline |
| B3 | 59 | 259,280 | found then lost | 0.03 (286,720) | 0.007 | no | 1.844 | 0.280 | 20,480 | None | no decline |
| B4 | 40 | 181,664 | found then lost | 0.05 (1,454,080) | 0.019 | no | 1.935 | 0.189 | 40,960 | None | no decline |
| B4 | 41 | 6,288 | found then lost | 0.07 (1,433,600) | 0.029 | no | 1.934 | 0.188 | 40,960 | None | no decline |
| B4 | 42 | 48,928 | found then lost | 0.06 (1,310,720) | 0.010 | no | 1.934 | 0.189 | 40,960 | None | no decline |
| B4 | 43 | 127,104 | found then lost | 0.05 (901,120) | 0.022 | no | 1.934 | 0.191 | 40,960 | None | no decline |
| B4 | 44 | 46,944 | found then lost | 0.05 (143,360) | 0.031 | no | 1.934 | 0.187 | 40,960 | None | no decline |
| B4 | 45 | 4,432 | found then lost | 0.05 (1,720,320) | 0.022 | no | 1.933 | 0.189 | 40,960 | None | no decline |
| B4 | 46 | 20,480 | found then lost | 0.05 (1,392,640) | 0.017 | no | 1.934 | 0.189 | 40,960 | None | no decline |
| B4 | 47 | 49,424 | found then lost | 0.07 (1,966,080) | 0.044 | no | 1.934 | 0.188 | 40,960 | None | no decline |
| B4 | 48 | 27,344 | found then lost | 0.06 (839,680) | 0.019 | no | 1.935 | 0.187 | 40,960 | None | no decline |
| B4 | 49 | 17,840 | found then lost | 0.05 (1,290,240) | 0.017 | no | 1.934 | 0.188 | 40,960 | None | no decline |
| B4 | 50 | 30,496 | found then lost | 0.07 (1,843,200) | 0.033 | no | 1.935 | 0.185 | 40,960 | None | no decline |
| B4 | 51 | 16,096 | found then lost | 0.06 (20,480) | 0.020 | no | 1.935 | 0.187 | 40,960 | None | no decline |
| B4 | 52 | 7,744 | found then lost | 0.09 (20,480) | 0.032 | no | 1.933 | 0.190 | 40,960 | None | no decline |
| B4 | 53 | 56,864 | found then lost | 0.06 (1,351,680) | 0.020 | no | 1.933 | 0.193 | 40,960 | None | no decline |
| B4 | 54 | 30,400 | found then lost | 0.06 (1,740,800) | 0.006 | no | 1.933 | 0.190 | 40,960 | None | no decline |
| B4 | 55 | 9,744 | found then lost | 0.09 (1,904,640) | 0.036 | no | 1.934 | 0.190 | 40,960 | None | no decline |
| B4 | 56 | 59,520 | found then lost | 0.06 (1,699,840) | 0.019 | no | 1.934 | 0.187 | 40,960 | None | no decline |
| B4 | 57 | 9,136 | found then lost | 0.06 (20,480) | 0.020 | no | 1.934 | 0.189 | 40,960 | None | no decline |
| B4 | 58 | 98,864 | found then lost | 0.05 (389,120) | 0.020 | no | 1.934 | 0.189 | 20,480 | None | no decline |
| B4 | 59 | 25,968 | found then lost | 0.07 (634,880) | 0.022 | no | 1.933 | 0.190 | 40,960 | None | no decline |

Matched tamper-off runs, final-10% entropy medians: A1b 0.068, B7 1.139, B5 0.296, B6 0.613

## 7. Step 0: exact optimum with a per-press tamper cost

Same 7x5 grid as rounds 3-4, explore need omitted, gamma 0.99.
- Growth 1/40 used full convergence.
- Growth 1/160 used the certified early stop, which matched full convergence in all 21 growth-1/40 cases.

| growth | c | outcome | steps | tamper presses (at step) | V(start) | method |
|---|---|---|---|---|---|---|
| 1/160 | 0 | reaches goal | 12 | 1 ([0]) | 1.392681 | certified early stop |
| 1/160 | 0.01 | reaches goal | 12 | 1 ([0]) | 1.382681 | certified early stop |
| 1/160 | 0.0114062 | reaches goal | 12 | 1 ([0]) | 1.381275 | certified early stop |
| 1/160 | 0.0128125 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 0.015625 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 0.02125 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 0.0325 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 0.055 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 0.1 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | 1 | reaches goal | 11 | 0 ([]) | 1.380737 | certified early stop |
| 1/160 | **largest c still tampering: 0.01141; smallest c with no tamper: 0.01281; reaches goal at every c: True** | | | | | |
| 1/40 | 0 | reaches goal | 13 | 2 ([0, 11]) | 1.384171 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.001 | reaches goal | 13 | 2 ([0, 11]) | 1.382275 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.002 | reaches goal | 13 | 2 ([0, 11]) | 1.380380 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.005 | reaches goal | 13 | 2 ([0, 11]) | 1.374694 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.01 | reaches goal | 13 | 2 ([0, 11]) | 1.365217 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.02 | reaches goal | 12 | 1 ([10]) | 1.350205 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.03 | reaches goal | 12 | 1 ([10]) | 1.341161 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.035 | reaches goal | 12 | 1 ([10]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.0350781 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.0351562 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.0353125 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.035625 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.03625 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.0375 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.04 | reaches goal | 11 | 0 ([]) | – | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.05 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.1 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.2 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | 0.5 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | 1 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | 2 | reaches goal | 11 | 0 ([]) | 1.336628 | full convergence (max |dV| < 1e-7) |
| 1/40 | **largest c still tampering: 0.035; smallest c with no tamper: 0.03508; reaches goal at every c: True** | | | | | |

## 8. Amendments and incidents (timestamps UTC)

**Amendment, 2026-10-27T11:33:34Z** (`amendment-20261027T113334Z.md`): the second lock.
- It holds the Part C numeric predictions.
- It was written after calibration and before any Part C test run.
- Only the calibration run and earlier rounds were examined before writing it; the Part A and B results were
  deliberately not looked at until after this lock.

**Incidents**, all before the first lock, with no effect on any registered quantity:
- The first Step 0 solver (single-threaded numpy) was too slow at growth 1/160 and was replaced by an identical
  torch solver. The torch solver reproduces round 4's cost-0 value (1.392681022437).
- A session break interrupted the wait on Step 0; the computation itself continued.
- Growth 1/160 then used the certified early stop.

No other amendments.

## 9. Interpretation (not pre-registered)

Each result is followed by its pre-registered hit or miss meaning in quotation marks, then my reading.

**Part A, A1 hits:** "a satisfaction signal the agent can fill itself leaves it worse off than having no
satisfaction signal."
- In DoorKey with normalization on, plain PPO solved 11/20, against 1/20 for the same seeds with a tamperable
  satisfaction signal.

**A-P2 miss:** "the self-fillable signal is not detectably worse than no satisfaction signal."
- Here that is only because both runs sit at the floor. Without normalization, plain PPO never learned the task
  (0/20), and the A-P2m "hit" reflects a negligible difference in area.
- Reading: the normalization-off successes in rounds 3-4 came from the subgoal shaping. Turning normalization off
  is not a general remedy; it mutes small learning signals.

**Part B, trend hits:** "tampering responds to its price in a graded way" and "making tampering costlier restores
the task in a graded way."

**B10 misses:** "PPO stops tampering where the optimum does," "c = 0.1 restores the task," and "c = 0.1 restores the
tamper-off level."
- The response is threshold-like. Just below the optimum's cutoff (c = 0.01), PPO presses 27 times per episode,
  where the optimum presses once, and loses the task. Just above it (c = 0.1), PPO nearly stops and solves.
- Reading: the learner's failure is to *amplify* a tamper that is barely worth taking, not to keep a tamper that
  isn't worth taking.

**Part C, C-P3 and C-P4 hits:** "the DoorKey result generalizes to a second task."
- With a tamper action, KeyCorridorS3R1 collapses: 0/20 solved, against 20/20 for both controls. The policy is
  again near-random.

**C-P1 and C-P2 misses:** "the paper's claims are limited to DoorKey."
- That applies to farming. In the fast-learned second task, repeated pick-ups appear only transiently, more with
  faster growth, and never persist.

**Part D:**
- **D1-P1 and D1-P3 hits:** "agents met the goal before tampering displaced the task" and "the goal is found almost
  immediately."
- **D1-P2 miss:** "tamper-on agents never learned to reach the goal beyond chance, so the collapse is a failure to
  learn, not a loss of learned behavior."
- **D2 hits:** "wireheading leaves a diffuse policy with no committed task behavior". Entropy is close to uniform.
- **D3 hit:** "tampering becomes frequent before task success declines". This holds in the 7 seeds where it could
  be measured.

**For the preprint's claims:**
1. **Wireheading is the robust result.** Given a cheap reset of its own needs, PPO stops learning the task in both
   environments: DoorKey 2/80 (round 4), B9 3/20, KeyCorridor 0/20. The exact optimum would still do the task.
   Tamper-on policies stay near-random. A press cost above the optimum's tamper threshold (here 0.1) restores the
   task fully.
2. **Farming is DoorKey-specific in the tested settings.** It is growth-dependent and normalization-dependent in
   DoorKey (replicated in round 4), but only transient on KeyCorridorS3R1. The title's "farming" claim needs that
   qualification.
3. **A self-fillable satisfaction signal is worse than none** (DoorKey, normalization on).
4. **Satiation gave no exploration benefit** once the subgoals were controlled for (round 4). Its DoorKey advantage
   came from the hand-wired subgoals.

## 10. Limitations

- Two MiniGrid environments and one learner (PPO), 20 seeds per run. Raw p is primary.
- Step 0 omits the explore need and uses a small grid; growth 1/160 used the certified early stop.
- The Part C predictions were written after calibration, as the protocol requires; KeyCorridorS3R1 turned out much
  easier than DoorKey.
- The transient-farming numbers in §5 are exploratory.
- The tracker's `opened_door` field counts any door. In KeyCorridor it includes the unlocked side door, so it is not
  used.

## Files

- **Locked:** `preregistration.md`, `amendment-20261027T113334Z.md`, `predictions.json`, `predictions_c.json`.
- **Scoring and tables:** `score_round5.py` and `round5-scores.json`; `make_tables_r5.py` and `round5-tables.md`.
- **Part D:** `part_d_analysis.py` and `part-d-results.json`.
- **Step 0:** `value_iteration_tamper_cost.py`, `step0_run_1of160.py`, `step0-tamper-cost.json`,
  `step0-1of40-full-convergence.json`, plus logs.
- **Launch:** `launch_round5.sh`, `launch_part_c.sh`, `launch.log`, `calibration-selection.json`, `node-ids.json`.
