"""Replay saved Agent 3 checkpoints step by step: actions, needs, rewards, value estimates.

Usage: python replay_checkpoints.py <run_repo_dir> <out.json> [episodes]
Run with the run's own environment, e.g. <run_repo_dir>/.venv/bin/python, with cwd outside the repo.
MiniGrid actions: 0 left, 1 right, 2 forward, 3 pickup, 4 drop, 5 toggle, 6 done.
"""
import json, sys, tomllib
from collections import Counter
from pathlib import Path

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
episodes = int(sys.argv[3]) if len(sys.argv) > 3 else 8
sys.path.insert(0, str(repo))
import numpy as np, torch
from ppo import Agent, make_vec_env
from intrinsic import make_intrinsic

cfg = tomllib.loads((repo / "config.toml").read_text())
torch.set_num_threads(1)
report = {"config": cfg["intrinsic"], "gamma": cfg["ppo"]["gamma"], "seeds": {}}
for ckpt in sorted((repo / "results").glob("seed*/agent.pt")):
    seed = int(ckpt.parent.name[4:])
    envs = make_vec_env(cfg["env"]["id"], 1)
    intr = make_intrinsic(cfg, envs.single_observation_space.shape, "cpu"); intr.attach(envs)
    agent = Agent(envs.single_observation_space.shape, envs.single_action_space.n, intr.state_dim)
    agent.load_state_dict(torch.load(ckpt)); agent.eval()
    obs, _ = envs.reset(seed=2_000_000 + seed)
    acts, eps, cur = Counter(), [], dict(len=0, pickups=0, drops=0, toggles=0, ret=0.0, r_int=0.0, v=[], h=[])
    manip = dict(n=0, novel=0); other = dict(n=0, novel=0)  # does a drop/pick-up produce a never-seen-this-episode view?
    probe = None
    with torch.no_grad():
        while len(eps) < episodes:
            o = torch.tensor(obs); st = intr.state()
            a, _, _, v = agent.get_action_and_value(o, st)
            carrying = envs.envs[0].unwrapped.carrying is not None
            # Counterfactual probe (first time the agent holds something): how does the critic's
            # value change if only the grasp need is varied 0 -> 1, with the same observation?
            if carrying and probe is None and intr.state_dim > 0:
                hs = np.linspace(0, 1, 6); vals = []
                for hg in hs:
                    s2 = st.clone(); s2[0, 1] = float(hg); vals.append(float(agent.get_value(o, s2)))
                pol = torch.softmax(agent.actor(agent.features(o, st)), -1)[0]
                probe = dict(grasp_need=hs.round(2).tolist(), value=np.round(vals, 3).tolist(),
                             p_drop=float(pol[4]), p_pickup=float(pol[3]), p_forward=float(pol[2]))
            ai = int(a); acts[ai] += 1
            cur["pickups"] += ai == 3 and not carrying; cur["drops"] += ai == 4 and carrying; cur["toggles"] += ai == 5
            cur["v"].append(float(v)); cur["h"].append(st[0].tolist())
            obs, r, term, trunc, info = envs.step(a.numpy())
            done = term | trunc
            nxt = obs.copy()
            if done.any(): nxt[done] = np.stack(info["final_obs"][done])
            ri = float(intr.reward(torch.tensor(nxt), done)[0])
            nov = float(intr.events[0, 0]) if hasattr(intr, "events") else 0.0
            bucket = manip if ai in (3, 4) else other
            bucket["n"] += 1; bucket["novel"] += nov
            cur["len"] += 1; cur["ret"] += float(r[0]); cur["r_int"] += ri
            if done[0]:
                h = np.array(cur.pop("h")); vv = cur.pop("v")
                cur.update(success=float(cur["ret"] > 0), v_start=vv[0], v_mean=float(np.mean(vv)),
                           mean_need=h.mean(0).round(3).tolist())
                eps.append(cur); cur = dict(len=0, pickups=0, drops=0, toggles=0, ret=0.0, r_int=0.0, v=[], h=[])
    envs.close()
    tot = sum(acts.values())
    s = {k: float(np.mean([e[k] for e in eps])) for k in ("success", "len", "pickups", "drops", "toggles", "ret", "r_int", "v_start", "v_mean")}
    s["mean_need"] = np.mean([e["mean_need"] for e in eps], 0).round(3).tolist()
    s["action_freq"] = {n: round(acts[i] / tot, 3) for i, n in enumerate(["left", "right", "forward", "pickup", "drop", "toggle", "done"])}
    s["grasp_probe"] = probe
    s["p_novel_after_drop_or_pickup"] = manip["novel"] / max(1, manip["n"])
    s["p_novel_after_other_action"] = other["novel"] / max(1, other["n"])
    report["seeds"][seed] = s
    print(f"seed {seed}: success {s['success']:.2f} len {s['len']:.0f} pickups {s['pickups']:.1f} drops {s['drops']:.1f} "
          f"toggles {s['toggles']:.1f} r_int {s['r_int']:.2f} V0 {s['v_start']:.2f} need {s['mean_need']} "
          f"novel|manip {s['p_novel_after_drop_or_pickup']:.2f} novel|other {s['p_novel_after_other_action']:.2f}", flush=True)
out.write_text(json.dumps(report, indent=2))
