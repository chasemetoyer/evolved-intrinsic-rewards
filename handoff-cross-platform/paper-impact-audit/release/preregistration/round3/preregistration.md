# Round 3 pre-registration: the learning-trap account of farming

Written 2026-10-26T15:17Z, before any round-3 analysis or training. This file is never edited after its
sha256 is recorded. Any change goes in a separate timestamped file `amendment-<UTC timestamp>.md` in this folder.

## Hypothesis

Farming is a local attractor of learning, not the optimum of the reward. A seed falls into it if the
drop-and-regrab (or door close/open) loop locks in before the agent has found the goal. This account was formed
after seeing the round-2 data, so round-2 data is used here only for the race analysis (Step 1), whose
predictions are written below before that analysis is run. No new formula is fitted to existing results.

## Common definitions

Environment and agent: MiniGrid-DoorKey-8x8-v0, PPO, 2M environment steps per seed, 16 envs, as in round 2.
Time limit: 640 steps per episode.

Logging window: one row of `metrics.jsonl` = 10 PPO updates = 20,480 environment steps. `train/*` values in a row
are means over the most recent 100 completed episodes at that moment.

Final 10%: the last `max(1, floor(rows / 10))` rows of `metrics.jsonl` (about 10 rows, the last ~200k steps).

### Behavior categories (per seed, final 10% of training; applied in this order)

1. **solve**: mean of `train/success` over the final-10% rows >= 0.9. Solve takes precedence. Report separately
   how many solvers also exceed the repeat threshold of category 2.
2. **cycle-farm**: not solve, and mean `train/pickups` > 5 or mean `train/door_flips` > 5 over the final-10% rows.
   Pick-ups and door state changes are the paid repeatable events (`door_flips` counts door open/close/unlock
   changes, which is what the event detector pays). Runs logged before `door_flips` existed (round-1 calibration
   runs) use pick-ups only.
3. **prolong**: not solve, not cycle-farm, and the median episode reaches the time limit. For round-3 runs this is
   the median over final-10% rows of the newly logged `train/len_median` (the median length of the last 100
   episodes) >= 640. Earlier runs did not log a median. When they are re-scored (exploratory only), mean
   `train/len` >= 600 is used as a proxy.
4. **fail**: anything else.

Cycle-farm fraction = cycle-farm seeds / all seeds in the run (denominator 20 for round-3 runs).
All fractions are reported with exact Clopper-Pearson 95% intervals.

### Seeds

All new training runs use fresh seeds 20-39 (20 seeds).

## STEP 1: race analysis on existing logs (no training)

Population: every Agent 3 (homeostatic) seed already run: round-1 calibration runs at growth 1/640, 1/160 and
1/40 (seeds 0-9 each), and round-2 nodes N1-N6 (N1 seeds 10-19; N2-N6 seeds 0-9). That is 90 seeds. Each seed's
final category is computed with the definitions above.

- **first-goal step**: the `global_step` of the first log row with `train/success` > 0, meaning at least one of
  the last 100 completed episodes reached the goal. Resolution is one window (20,480 steps). If no row has
  success > 0, the seed never reached the goal.
- **lock-in step**: the `global_step` of the first log row r such that every row from r through the end of
  training has `train/pickups` > 5 or `train/door_flips` > 5. Each row is tested on the metric that crosses 5;
  pick-ups only where `door_flips` was not logged. If no such row exists, lock-in is never.
- **Order**: "lock-in first" if lock-in step < first-goal step, or lock-in exists and the goal was never
  reached. "Goal first" if first-goal step < lock-in step, or the goal was reached and lock-in is never.
  "Undetermined" if both fall in the same window.

**Resolution stopping rule.** If more than 25% of the seeds in P1's or P2's denominator are undetermined, that
prediction is declared unresolvable at the logs' time resolution and is not scored. P3 is declared unresolvable
if the growth-1/40 seeds have fewer than 3 distinct first-goal windows. In either case the report says so, and
nothing is approximated.

- **P1**: Among final cycle-farmers that reached the goal at least once, lock-in comes before first goal in at
  least 80%. Expected 90%, plausible range 80-100%. Test: exact one-sided binomial test of the lock-in-first
  share against 0.5 (H1: > 0.5), counting undetermined seeds as not-lock-in-first. Hit if the observed share is
  >= 80%. Farmers that never reached the goal are reported as a separate count.
- **P2**: Among final solvers, first goal comes before any lock-in in at least 80%. Expected 95%, plausible range
  80-100%. Test: exact one-sided binomial test against 0.5 (H1: > 0.5), counting undetermined as not-goal-first.
  Hit if the observed share is >= 80%.
- **P3**: Within growth-1/40 seeds (calibration 1/40, N1, N2 and N5; 40 seeds), an earlier first-goal step
  predicts not farming. Logistic regression of not-cycle-farm (1 = solve, prolong or fail; 0 = cycle-farm) on
  first-goal step in units of 100k steps. Seeds that never reached the goal get first-goal step = 2,000,000
  (right-censored). Expected slope < 0. Test: one-sided Wald test of slope < 0. Hit if slope < 0 and p < 0.05.

Outputs: a per-seed table (setting, seed, first-goal step, lock-in step, order, final category) and a 2x2 table
(goal-first vs lock-in-first, by final category cycle-farm vs solve; undetermined listed separately).

## STEP 2: exact solution on a small grid (no training)

MDP: a fixed DoorKey-style layout, 7 wide x 5 high including outer walls. Interior 5 x 3. Wall column x=3 with a
locked door at (3,2). Left room x in {1,2}, right room x in {4,5}, y in {1,2,3}. Agent starts at (1,1) facing
east; key at (2,3); goal at (5,3). Actions as in MiniGrid: left, right, forward, pickup, drop, toggle ("done" is
omitted because it has no effect).

- forward moves onto empty floor, an open door or the goal. Reaching the goal ends the episode.
- pickup takes the key from the cell in front.
- drop places the carried key on an empty floor cell in front.
- toggle opens a locked door only while carrying the key, opens a closed door, and closes an open door.

Rewards: extrinsic +1 on reaching the goal. MiniGrid's time-dependent discount on the goal reward and the
640-step limit are omitted, so the problem is infinite-horizon and discounted. Intrinsic reward is the same as
Agent 3, with coef 1:

- needs h = (h_grasp, h_open), start 0.5 each;
- each step h <- clip(h + g - satiety * event, 0, 1), satiety 1.0;
- grasp event = successful pick-up; open event = any change in the door's (open, locked) state, including closing;
- D(h) = sum of squared needs;
- r_int = D(h_t) - D(h_{t+1}), including on the terminal step.

**The explore need is omitted.** It depends on visit history, which cannot be in a tabular state. Because D is
a sum, omitting it removes only that channel's separable term.

Needs live on a lattice. Bin size = g: with h0 = 0.5 and these dynamics, every reachable need value is a multiple
of g when 0.5/g is an integer, so this lattice is exact. The check halves the bin size to g/2. On an exact
lattice the result is expected to be identical; any difference indicates an implementation error.

Solved by value iteration to max |delta V| < 1e-7. Greedy actions break ties in the order above. "Reaches the
goal" = the greedy rollout from the start state reaches the goal within 10,000 steps. Otherwise "cycles". The
rollout is deterministic, so failure implies a loop; the paid events per loop are reported.

Grid: g in {1/80, 1/40, 1/20} x gamma in {0.99, 0.95}. The search for the smallest cycling growth rate uses
g in {1/160, 1/80, 1/60, 1/40, 1/30, 1/20, 1/10, 1/6, 1/4, 1/2} at both gammas. It is limited to these values.

- **P4**: At gamma 0.99 the optimal policy reaches the goal, and never cycles, at all three growth rates
  {1/80, 1/40, 1/20}. Expected: 3 of 3 reach the goal. Deterministic; hit if 3/3, no statistical test.

## STEP 3: training runs (seeds 20-39, DoorKey-8x8, 2M steps)

Unless stated otherwise every setting equals round-2 Agent 3 at growth 1/40 (N1): homeostatic, coef 1,
gamma 0.99, h0 0.5, satiety (0.1, 1, 1), advantage normalization on. Code changes, which add no behavior when
off:

- a switch for per-minibatch advantage normalization;
- an optional early-goal start wrapper;
- an optional explore-bonus override for the event-bonus control;
- logging of `train/len_median` and the exact first-goal step.

| Run | Change | Predicted cycle-farm (of 20) | Plausible range |
|---|---|---|---|
| R1 | growth 1/60 | 6 (30%) | 1-10 |
| R2 | growth 1/30 | 16 (80%) | 12-20 |
| R3 | growth 1/40, coef 0.5, norm on | 8 (40%) | 3-13 |
| R4 | growth 1/40, coef 1, norm on (reference) | 11 (55%) | 6-16 |
| R5 | growth 1/40, coef 2, norm on | 13 (65%) | 8-18 |
| R6 | growth 1/40, coef 0.5, norm off | 4 (20%) | 0-9 |
| R7 | growth 1/40, coef 1, norm off | 10 (50%) | 5-15 |
| R8 | growth 1/40, coef 2, norm off | 16 (80%) | 11-20 |
| R9 | R4 + early-goal starts | 2 (10%) | 0-4 |
| R10 | fixed pay-once control | 0 | 0-1 |

Tests:

- **R1 vs R4**: one-sided Fisher exact, H1: R1 cycle-farm fraction < R4's.
- **R2 vs R4**: one-sided Fisher exact, H1: R2 > R4.
- **Bonus size (R3-R8)**:
  - one-sided Fisher exact, H1: R8 (coef 2, norm off) > R6 (coef 0.5, norm off);
  - logistic regression over the 120 seeds: cycle-farm ~ b0 + b1·log2(coef) + b2·norm_on + b3·log2(coef)·norm_on.
    Predicted b1 > 0 (one-sided Wald) and b3 < 0 (one-sided Wald; the coef effect is smaller with normalization).
    The interaction prediction is a hit if b3 < 0 with one-sided p < 0.05.
- **R9 (early-goal intervention)**: for the first 200,000 environment steps, each training episode starts, with
  probability 0.25, inside the goal room with the door unlocked and open. The agent is placed on a random empty
  cell right of the wall, facing a random direction, and the key stays where the layout put it. After 200k steps
  every episode uses standard starts. Evaluation and the final-10% categories use standard starts only.
  Predicted cycle-farm <= 20% (expected 2/20). Test: one-sided Fisher exact, H1: R9 < R4 (same seeds 20-39).
  A growth-only account predicts no difference.
- **R10 (fixed pay-once control)**: event-bonus agent, growth 0, no needs. Key pick-up and door change each pay
  their constant bonus at most once per episode. Each distinct new 7x7 view pays once per episode, as before, but
  the per-view bonus is rescaled by this rule, fixed now:
  - T = median, over all logging rows and seeds, of `train/int_ret` in the episodic-novelty coef-1e-3 run
    (02ba39cc), i.e. that agent's typical bonus per episode;
  - V = mean number of new-view events per episode of a uniformly random policy on DoorKey-8x8, over 256
    episodes, seed 0;
  - per-view bonus = T / V. The computed T, V and bonus are recorded in R10's description before launch.

  Predicted: 0 cycle-farm (range 0-1), 0 prolong (range 0-1), solve 17/20 (range 12-20). No significance test;
  each count is a hit if inside its range.

## STEP 4: report

One table covering every prediction above: expected value, observed value, hit or miss, test and p-value, with
Clopper-Pearson intervals. Then the race tables, the value-iteration results and any amendments with their
timestamps. Then a re-scoring of all earlier runs under these categories, labeled exploratory. No round 4.
