# Handoff: code, reference results and scripts for the cross-platform check

These files come from the "Satisfied, Not Solving" project, Zenodo doi:10.5281/zenodo.23708846.

## code/

| Folder | What it is | Use it for |
|---|---|---|
| `a1b-run-commit-1533734/` | The exact code and `config.toml` of run 3629f9a7 (git commit 1533734): satiation, growth 1/160, no tamper, normalization on, DoorKey-8x8, seeds 40-59, 2M steps. | **Reproducing the reference run bit-for-bit.** This is what produced the numbers in `scored-results/`. |
| `final-round5/` | The final version, as archived on Zenodo. It adds options (press cost, KeyCorridor event mode, counters) that are off by default. Its `config.toml` is the last run's (KeyCorridor, task-only), not A1b's. | Carrying the code forward. To rerun A1b with it, use `a1b-run-commit-1533734/config.toml`. |

Where things live in the code:
- **`ppo.py`:** the PPO learner, the network (small CNN plus linear actor and critic heads), and the MiniGrid
  wrappers. The wrappers are `make_vec_env`, `ImgObsWrapper` and `EarlyGoalStart`.
- **`intrinsic.py`:** the satiation module (`Homeostatic`), the event detector, and the tamper action
  (`tamper = true` turns action 6, "done", into a need reset). It also holds the controls `EventBonus` and
  `EpisodicCount`.
- **`run_seeds.py` and `run.sh`:** run every seed in `config.toml` in parallel, one single-threaded process per
  seed.
- **`pyproject.toml` and `uv.lock`:** the pinned environment (torch 2.14.1, gymnasium 1.4.0, minigrid 3.2.0, numpy
  2.4.6).

**Run it:** `uv sync --locked`, then `./run.sh`. Results go to `results/seed*/`.

**Bit-identity caveat.** The round-5 pre-registration records an 8,192-step regression check: with the new options
off, the final code was bit-identical to the round-4 code on the B1 (tamper on) and R4 (tamper off, growth 1/40)
configurations. A1b's exact configuration was not part of that check. Use the commit-1533734 code if you need the
same numbers.

## scored-results/

| File | Contents |
|---|---|
| `A1b-scored.json` | The scored entry for run 3629f9a7, taken from `round4-scores.json`. It holds categories (20/20 solve) and medians (first-solved 311,832; solved length 20.32; training AUC 0.912). `seeds` has one record per seed 40-59: `category`, `first_solved`, `solved_len`, `train_auc`, `eval8`, `eval16`, `done_per_episode`, `final10_episodes`. |
| `round4-scores.json` | The full round-4 scored file, all runs, for context. |
| `a1b-run-3629f9a7/seed*/` | The raw per-seed outputs: `summary.json` (incl. exact first-solved and final-10% accumulators) and `metrics.jsonl` (one row per 10 PPO updates). `aggregate.json` is the run-level summary. |

The per-seed numbers to compare against are `A1b-scored.json` → `seeds`, recomputed from `metrics.jsonl` and
`summary.json` by `scripts/score_round4.py`.

## scripts/

| File | What to reuse |
|---|---|
| `score_round4.py` | The script that scored A1b. It defines `category()`, the behaviour categories (solve, cycle-farm, prolong, fail, on the final 10% of rows), `cp()` (Clopper-Pearson), `mwu()` (exact, or permutation when tied, one-sided) and `fisher()`. |
| `score_round5.py` | The round-5 scorer. It has the same tests plus `jt()`, a Jonckheere-Terpstra permutation trend test (200k permutations, seed 0), and the round-5 rule that cycle-farm applies only where repeats are paid. |
| `check_numbers.py`, plus `make_numbers.py` and `make_tables.py` | The paper's number checker. It is written for this paper's layout (`paper/main.tex`, `paper/data/`), so it won't run as-is elsewhere. Reusable pieces: `fp()` (p-value formatting), the regenerate-and-diff pattern, the literal-number scan, and the worded-count check. |

Both scoring scripts read run outputs from the local run store by run ID (`load()`). Point `load()` at the
`a1b-run-3629f9a7/` folder, or at your new run's `results/`, before using them.

## preregistration-template/

Round 5's pre-registration, to use as a format template:
- **`preregistration.md`** is the locked file. Its sections are, in order: question, a pre-lock disclosure of what
  was done and seen before locking, common settings, categories, statistics and hit rules, the Holm set, the
  predictions per part (each with expected value, plausible range, test, and what a hit or a miss would mean), and
  the report plan.
- **`preregistration.sha256`** is its lock record: the file's sha256 and the UTC time it was written.
- **`amendment-20261027T113334Z.md`** shows the format of a timestamped amendment. This one is the second lock,
  holding numeric predictions written after calibration.
- **`predictions.json`** is the machine-readable form of the expectations, which the scoring script reads.

Lesson from this project: these lock records were self-reported. For stage 2, commit the pre-registration file to
git and push it at lock time, or deposit it with a timestamping service, so that the lock time can be verified
independently.
