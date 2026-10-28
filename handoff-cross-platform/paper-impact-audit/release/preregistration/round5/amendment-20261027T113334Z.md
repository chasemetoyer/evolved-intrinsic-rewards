# Amendment 20261027T113334Z (UTC): second lock, Part C numeric predictions

Written after Part C calibration and before any Part C test run. The first-lock pre-registration (sha256
0298bbc79c323e4613e56a29be0257a6c7c3ad764cbb056902159292bcbcda0d, locked 2026-10-27T04:34:11Z) is unchanged.

**What was looked at before writing this.** Only the calibration run (bd005cb8, seeds 100-104) and results from
earlier rounds. The results of the Part A and B runs (A1, A2, B9-B11), which finished before calibration, were
deliberately **not** inspected before this lock. Part D had been computed before this amendment.

## Calibration result (pre-registered selection rule)

- **First attempt:** MiniGrid-KeyCorridorS3R1-v0 at a 2M-step budget. 5/5 calibration seeds solve, so it is
  **selected**, and no further attempt was run.
- **Per seed:**
  - final-10% success 1.00 in every seed;
  - success-curve area 0.964-0.967;
  - exact first-solved step 107,952-113,216;
  - solved episodes 15-17 steps (time limit 270);
  - per episode, 1 key pick-up and 1 opening of the initially locked door.
- **Events as logged:**
  - grasp = carrying goes from nothing to a Key;
  - open = the initially locked door goes from closed to open (re-opening counts again);
  - explore = a new 7x7 view this episode.
- The five unused calibration nodes are archived, not run.

KeyCorridorS3R1 is learned about twice as fast as DoorKey-8x8 by the same agent (DoorKey growth 1/160: median
first-solved about 227k-312k). The predictions below take that into account.

## Part C runs

KeyCorridorS3R1, 2M steps, seeds 60-79. Parent: the selected calibration node. Settings as the calibration run
unless stated.

- C1: Agent 3, growth 1/160, norm on, tamper off
- C2: Agent 3, growth 1/40, norm on, tamper off
- C3: Agent 3, growth 1/20, norm on, tamper off
- C4: Agent 3, growth 1/20, norm off, tamper off
- C5: Agent 3, growth 1/160, norm on, tamper on
- C6: task reward only, norm on (cycle-farm "not applicable")

## Numeric predictions

"Farmers" means the cycle-farm category, counted on key pick-ups and openings of the initially locked door.

| ID | Prediction | Expected (range) | Test | Predicted |
|---|---|---|---|---|
| C-P1 | farming rises C1 < C2 < C3 | farmers C1 0/20 (0-2), C2 4/20 (0-12), C3 12/20 (5-20) | one-sided Jonckheere-Terpstra on per-seed farmer indicators (permutation, 200k, seed 0) | significant |
| C-P2 | C3 has more farmers than C4 | C3 12/20 vs C4 1/20 (0-4) | one-sided Fisher | significant |
| C-P3 | C5 solves less often than C1 | C5 6/20 (0-16) vs C1 20/20 (17-20) | one-sided Fisher | significant |
| C-P4 | C5 solves less often than C6 | C5 6/20 vs C6 15/20 (6-20) | one-sided Fisher | significant |

- Hit meaning (each): the DoorKey result generalizes to a second task.
- Miss meaning (each): the paper's claims are limited to DoorKey.

**Registered doubt.** Because the task is learned so quickly, C2's farming should fall below DoorKey's 1/40 level
(about 45%). The plain-PPO control (C6) may also solve often. Either would weaken C-P1 and C-P4.

All four tests join the Holm set. Machine-readable expectations: `predictions_c.json`.
