"""A2 matching rule (pre-registered; run once after locking, before launch).

Uniform random policy (all 7 actions), 50 episodes on DoorKey-8x8, seed 0, one env. On the same trajectories,
compute per-episode undiscounted intrinsic return of:
  - episodic novelty (episodic_count) at coef 1e-3 (A2c's setting);
  - explore-only satiation (homeostatic, needs_on = [1, 0, 0]) at coef 1, growth 1/640 (A2a) and 1/160 (A2b).
Primary rule: coef_g = mean novelty return / mean explore-only return at coef 1.
Fallback (used for a growth rate if its mean explore-only return is <= 0, or the primary coef would exceed 10):
  coef_g = mean novelty return / mean per-episode sum of positive explore-only rewards (total relief paid).
Usage (project env, cwd = project worktree): python a2_matching_rule.py <out.json>"""
import copy, json, sys, tomllib
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, ".")
from ppo import make_vec_env
from intrinsic import make_intrinsic

base = tomllib.loads(Path("config.toml").read_text())
def cfg_with(**kw):
    c = copy.deepcopy(base); c["intrinsic"].update(kw); return c
mods = {
    "novelty": (make_intrinsic(cfg_with(kind="episodic_count", coef=1e-3), None, "cpu"), 1e-3),
    "explore_1/640": (make_intrinsic(cfg_with(kind="homeostatic", needs_on=[1, 0, 0], tamper=False,
                                              growth=[1 / 640] * 3), None, "cpu"), 1.0),
    "explore_1/160": (make_intrinsic(cfg_with(kind="homeostatic", needs_on=[1, 0, 0], tamper=False,
                                              growth=[1 / 160] * 3), None, "cpu"), 1.0),
}
envs = make_vec_env("MiniGrid-DoorKey-8x8-v0", 1)
obs, _ = envs.reset(seed=0)
for m, _ in mods.values():
    m.attach(envs)
rng = np.random.default_rng(0)
ret = {k: [] for k in mods}; pos = {k: [] for k in mods}; cur = {k: 0.0 for k in mods}; cpos = {k: 0.0 for k in mods}
lens, n = [], 0
while len(lens) < 50:
    a = np.array([rng.integers(7)])
    obs, r, term, trunc, info = envs.step(a)
    done = term | trunc
    nxt = obs.copy()
    if done.any():
        nxt[done] = np.stack(info["final_obs"][done])
    n += 1
    for k, (m, coef) in mods.items():
        x = coef * float(m.reward(torch.tensor(nxt), done, a)[0])
        cur[k] += x; cpos[k] += max(x, 0.0)
    if done[0]:
        for k in mods:
            ret[k].append(cur[k]); pos[k].append(cpos[k]); cur[k] = cpos[k] = 0.0
        lens.append(n); n = 0
R = {k: float(np.mean(v)) for k, v in ret.items()}; Pp = {k: float(np.mean(v)) for k, v in pos.items()}
out = dict(episodes=len(lens), mean_episode_length=float(np.mean(lens)), mean_return=R, mean_positive_part=Pp, coef={})
for g in ("explore_1/640", "explore_1/160"):
    primary = R["novelty"] / R[g] if R[g] > 0 else None
    if primary is not None and primary <= 10:
        out["coef"][g] = dict(rule="primary (match mean return)", value=primary)
    else:
        out["coef"][g] = dict(rule="fallback (match total positive relief)", value=R["novelty"] / Pp[g],
                              primary_would_be=primary)
Path(sys.argv[1]).write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
