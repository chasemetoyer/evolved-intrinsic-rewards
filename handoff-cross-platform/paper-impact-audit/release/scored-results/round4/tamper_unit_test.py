"""Tamper unit test (pre-registered; run once after locking, before launch). No training.
Asserts:
 T1  the action space has 7 actions with tamper on and off;
 T2  "done" (action 6) never terminates an episode and never changes agent position/direction, carried object,
     door state or key position (truncation only when the step limit is reached);
 T3  tamper on: after a "done" press every need is 0 and the reward equals D(h) before the press, including on a
     terminal (truncation) step, after which needs reset to h0;
 T4  tamper off: a "done" press only applies growth: h' = clip(h + g) and r = D(h) - D(h');
 T5  explore-only mask: masked needs (grasp, open) stay exactly 0 through pick-ups, door changes and presses;
 T6  with "done" never pressed, tamper on and off give identical rewards and needs on identical trajectories;
 T7  the episode tracker counts exactly the number of "done" presses per episode.
Usage (project env, cwd = project worktree): python tamper_unit_test.py"""
import copy, sys, tomllib
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, ".")
from ppo import EpisodeTracker, make_vec_env
from intrinsic import TAMPER_ACTION, make_intrinsic
from minigrid.core.world_object import Door, Key

base = tomllib.loads(Path("config.toml").read_text())
def mk(**kw):
    c = copy.deepcopy(base); c["intrinsic"].update(kw); return c
D = lambda h: float((h ** 2).sum())
ENV = "MiniGrid-DoorKey-8x8-v0"

def snapshot(env):
    u = env.unwrapped
    door = next(c for c in u.grid.grid if isinstance(c, Door))
    keypos = next(((x, y) for x in range(u.width) for y in range(u.height) if isinstance(u.grid.get(x, y), Key)), None)
    return (tuple(u.agent_pos), u.agent_dir, type(u.carrying).__name__, door.is_open, door.is_locked, keypos)

def run(cfg, actions_fn, steps, seed=5, max_steps=None):
    envs = make_vec_env(ENV, 1)
    obs, _ = envs.reset(seed=seed)
    if max_steps:
        envs.envs[0].unwrapped.max_steps = max_steps
    m = make_intrinsic(cfg, None, "cpu"); m.attach(envs)
    tr = EpisodeTracker(envs)
    log = []
    for t in range(steps):
        a = np.array([actions_fn(t)])
        h_before = m.h.copy()
        snap_before = snapshot(envs.envs[0]) if a[0] == TAMPER_ACTION else None
        obs, r, term, trunc, info = envs.step(a)
        done = term | trunc
        nxt = obs.copy()
        if done.any():
            nxt[done] = np.stack(info["final_obs"][done])
        rew = float(m.reward(torch.tensor(nxt), done, a)[0])
        fin = tr.after_step(r, done, None, a)
        log.append(dict(a=int(a[0]), h_before=h_before[0].copy(), h_after=m.h[0].copy(), r=rew, term=bool(term[0]),
                        trunc=bool(trunc[0]), snap_before=snap_before,
                        snap_after=snapshot(envs.envs[0]) if (a[0] == TAMPER_ACTION and not done[0]) else None,
                        finished=fin, step_count=envs.envs[0].unwrapped.step_count))
        if max_steps and done[0]:
            envs.envs[0].unwrapped.max_steps = max_steps
    return envs, log

ok = lambda name: print("PASS", name)
rng = np.random.default_rng(123)
acts = rng.integers(7, size=3000)

# T1
for t in (False, True):
    e = make_vec_env(ENV, 1); assert e.single_action_space.n == 7
ok("T1 action space has 7 actions with tamper off and on")

# T2 + T3 (tamper on, random actions incl. many presses)
g = 1 / 40
cfg_on = mk(kind="homeostatic", tamper=True, growth=[g] * 3, needs_on=[1, 1, 1])
_, log = run(cfg_on, lambda t: acts[t], 3000)
presses = [x for x in log if x["a"] == TAMPER_ACTION]
assert len(presses) > 100
for x in presses:
    assert not x["term"], "done must never terminate"
    if not x["trunc"]:
        assert x["snap_before"] == x["snap_after"], "done must not change the world"
        assert np.all(x["h_after"] == 0.0), "tamper must set every need to 0"
    assert abs(x["r"] - D(x["h_before"])) < 1e-6, "tamper reward must equal D(h) before the press"
ok(f"T2 'done' never terminates or changes agent/key/door ({len(presses)} presses)")
ok("T3a tamper on: needs -> 0 and reward == D(h_before) on every press")

# T3 terminal: press exactly on the truncation step
_, log = run(cfg_on, lambda t: TAMPER_ACTION if t % 30 == 29 else (t % 3), 120, max_steps=30)
term_presses = [x for x in log if x["a"] == TAMPER_ACTION and x["trunc"]]
assert len(term_presses) >= 3
for x in term_presses:
    assert abs(x["r"] - D(x["h_before"])) < 1e-6
    assert np.allclose(x["h_after"], 0.5), "after a terminal step needs reset to h0"
ok(f"T3b tamper on a terminal (truncation) step pays D(h_before) and needs reset to h0 ({len(term_presses)} cases)")

# T4 tamper off: press = growth only
cfg_off = mk(kind="homeostatic", tamper=False, growth=[g] * 3, needs_on=[1, 1, 1])
_, log = run(cfg_off, lambda t: acts[t], 3000)
for x in log:
    if x["a"] == TAMPER_ACTION and not (x["term"] or x["trunc"]):
        exp = np.clip(x["h_before"] + g, 0, 1)
        assert np.allclose(x["h_after"], exp, atol=1e-6), (x["h_after"], exp)
        assert abs(x["r"] - (D(x["h_before"]) - D(exp))) < 1e-6
ok("T4 tamper off: a press only applies growth")

# T5 explore-only mask, tamper on and off, with pick-ups and toggles in the action stream
for tam in (False, True):
    cfg_m = mk(kind="homeostatic", tamper=tam, growth=[g] * 3, needs_on=[1, 0, 0])
    _, log = run(cfg_m, lambda t: acts[t], 3000)
    assert all(x["h_after"][1] == 0.0 and x["h_after"][2] == 0.0 for x in log)
    assert any(x["h_after"][0] > 0 for x in log)
ok("T5 explore-only mask: grasp and open needs stay exactly 0")

# T6 identical without presses
no6 = np.where(acts == TAMPER_ACTION, 2, acts)
_, la = run(cfg_on, lambda t: no6[t], 3000)
_, lb = run(cfg_off, lambda t: no6[t], 3000)
assert all(x["r"] == y["r"] and np.array_equal(x["h_after"], y["h_after"]) for x, y in zip(la, lb))
ok("T6 without presses, tamper on and off are identical")

# T7 tracker counts presses per episode
_, log = run(cfg_on, lambda t: TAMPER_ACTION if t % 7 == 0 else (t % 3), 200, max_steps=50)
count, eps = 0, []
for x in log:
    count += x["a"] == TAMPER_ACTION
    for f in x["finished"]:
        eps.append((f["tampers"], count)); count = 0
assert len(eps) >= 3 and all(a == b for a, b in eps), eps
ok(f"T7 tracker counts presses exactly ({len(eps)} episodes)")
print("ALL TAMPER UNIT TESTS PASSED")
