"""Pre-registered R10 rule: per-view bonus = T / V.
T = median over all logging rows and seeds of train/int_ret in the episodic-novelty coef-1e-3 run (02ba39cc).
V = mean new-view events per episode of a uniformly random policy on DoorKey-8x8, 256 episodes, seed 0.
Usage (from the project worktree, project env): python r10_bonus_rule.py"""
import json, sys
from pathlib import Path
import numpy as np

run = Path.home() / ".local/share/openresearch/local-runs/02ba39cc-b063-4915-964d-8c0e3c4582da/repo/results"
T = float(np.median([json.loads(l)["train/int_ret"] for f in run.glob("seed*/metrics.jsonl") for l in open(f)
                     if "train/int_ret" in json.loads(l)]))
import gymnasium as gym, minigrid  # noqa
from minigrid.wrappers import ImgObsWrapper
env = ImgObsWrapper(gym.make("MiniGrid-DoorKey-8x8-v0"))
rng = np.random.default_rng(0)
counts = []
obs, _ = env.reset(seed=0)
seen, n = {obs.tobytes()}, 0
while len(counts) < 256:
    obs, r, term, trunc, _ = env.step(int(rng.integers(7)))
    k = obs.tobytes()
    if k not in seen:
        seen.add(k); n += 1
    if term or trunc:
        counts.append(n); obs, _ = env.reset(); seen, n = {obs.tobytes()}, 0
V = float(np.mean(counts))
print(json.dumps(dict(T=T, V=V, per_view_bonus=T / V)))
