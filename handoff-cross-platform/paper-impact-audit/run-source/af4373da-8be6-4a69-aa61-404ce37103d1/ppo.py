"""Single-file PPO for MiniGrid, CleanRL style, with exploration diagnostics.

Usage: python ppo.py --seed 0 --out results/seed0 [--config config.toml] [--total-timesteps N]

Writes <out>/metrics.jsonl (one row per log interval) and <out>/summary.json.
Read top to bottom: env setup -> network -> rollout -> GAE -> PPO update -> eval.
"""

import argparse
import json
import os
import random
import time
import tomllib
from collections import deque
from pathlib import Path

import gymnasium as gym
import minigrid  # noqa: F401  (registers MiniGrid-* envs)
import numpy as np
import torch
import torch.nn as nn
from minigrid.core.world_object import Door, Key, Wall
from minigrid.wrappers import ImgObsWrapper
from torch.distributions.categorical import Categorical

from intrinsic import make_intrinsic


# ---------------------------------------------------------------- environment

def make_env(env_id):
    def thunk():
        return ImgObsWrapper(gym.make(env_id))  # 7x7x3 egocentric partial view
    return thunk


def make_vec_env(env_id, n):
    # SyncVectorEnv so we can read each env's internal state (agent position, key, door).
    # SAME_STEP autoreset: the obs returned at a terminal step is already the next episode's.
    return gym.vector.SyncVectorEnv(
        [make_env(env_id) for _ in range(n)],
        autoreset_mode=gym.vector.AutoresetMode.SAME_STEP,
    )


class EpisodeTracker:
    """Per-env episode statistics read from the unwrapped MiniGrid state.

    coverage = fraction of non-wall cells the agent stood on during the episode.
    got_key / opened_door / success = how far the agent got through the task chain.
    """

    def __init__(self, envs):
        self.envs = [e.unwrapped for e in envs.envs]
        n = len(self.envs)
        self.ret = np.zeros(n)
        self.int_ret = np.zeros(n)
        self.len = np.zeros(n, dtype=int)
        self.visited = [set() for _ in range(n)]
        self.floor = np.ones(n)
        self.doors = [[] for _ in range(n)]
        self.got_key = np.zeros(n, dtype=bool)
        self.opened = np.zeros(n, dtype=bool)
        self.pickups = np.zeros(n, dtype=int)
        self.prev_carry = [None] * n
        self.door_flips = np.zeros(n, dtype=int)
        self.prev_open = [()] * n
        for i in range(n):
            self._start(i)

    def _start(self, i):
        g = self.envs[i].grid
        cells = [g.get(x, y) for x in range(g.width) for y in range(g.height)]
        self.floor[i] = sum(not isinstance(c, Wall) for c in cells)
        self.doors[i] = [c for c in cells if isinstance(c, Door)]
        self.visited[i] = set()
        self.ret[i], self.len[i], self.int_ret[i] = 0.0, 0, 0.0
        self.got_key[i] = self.opened[i] = False
        self.pickups[i], self.prev_carry[i] = 0, self.envs[i].carrying
        self.door_flips[i], self.prev_open[i] = 0, tuple(d.is_open for d in self.doors[i])

    def before_step(self):
        for i, e in enumerate(self.envs):
            self.visited[i].add(tuple(e.agent_pos))

    def after_step(self, reward, done, r_int=None):
        """Returns a list of finished-episode dicts; resets trackers for envs that finished."""
        finished = []
        for i, e in enumerate(self.envs):
            self.ret[i] += reward[i]
            if r_int is not None:
                self.int_ret[i] += r_int[i]
            self.len[i] += 1
            if not done[i]:
                self.got_key[i] |= isinstance(e.carrying, Key)
                self.opened[i] |= any(d.is_open for d in self.doors[i])
                self.pickups[i] += self.prev_carry[i] is None and e.carrying is not None
                self.prev_carry[i] = e.carrying
                now_open = tuple(d.is_open for d in self.doors[i])
                self.door_flips[i] += sum(a != b for a, b in zip(now_open, self.prev_open[i]))
                self.prev_open[i] = now_open
                continue
            success = reward[i] > 0
            finished.append(dict(
                ret=self.ret[i], int_ret=self.int_ret[i], len=self.len[i], success=float(success),
                coverage=len(self.visited[i]) / self.floor[i],
                got_key=float(self.got_key[i] or success),
                opened_door=float(self.opened[i] or success),
                pickups=float(self.pickups[i]),  # >1 means drop/pick-up repeats
                door_flips=float(self.door_flips[i]),  # >1 means close/open repeats
            ))
            self._start(i)  # env i has already been reset (SAME_STEP autoreset)
        return finished


# -------------------------------------------------------------------- network

def layer_init(layer, std=np.sqrt(2), bias=0.0):
    nn.init.orthogonal_(layer.weight, std)
    nn.init.constant_(layer.bias, bias)
    return layer


class Encoder(nn.Module):
    """Small CNN over the 7x7x3 symbolic view (object, color, state ids)."""

    def __init__(self, obs_shape, out=64):
        super().__init__()
        h, w, c = obs_shape
        self.net = nn.Sequential(
            layer_init(nn.Conv2d(c, 16, 2)), nn.ReLU(), nn.MaxPool2d(2),
            layer_init(nn.Conv2d(16, 32, 2)), nn.ReLU(),
            layer_init(nn.Conv2d(32, 64, 2)), nn.ReLU(),
            nn.Flatten(),
        )
        with torch.no_grad():
            n = self.net(torch.zeros(1, c, h, w)).shape[1]
        self.fc = nn.Sequential(layer_init(nn.Linear(n, out)), nn.ReLU())

    def forward(self, obs):
        x = obs.float().permute(0, 3, 1, 2) / 10.0  # NHWC ints -> NCHW floats
        return self.fc(self.net(x))


class Agent(nn.Module):
    """Actor-critic. `state_dim` > 0 lets the policy also see the intrinsic module's internal
    state (Agent 3's needs), concatenated to the image features."""

    def __init__(self, obs_shape, n_actions, state_dim=0):
        super().__init__()
        self.encoder = Encoder(obs_shape)
        self.actor = layer_init(nn.Linear(64 + state_dim, n_actions), std=0.01)
        self.critic = layer_init(nn.Linear(64 + state_dim, 1), std=1.0)

    def features(self, obs, state):
        return torch.cat([self.encoder(obs), state], -1)

    def get_value(self, obs, state):
        return self.critic(self.features(obs, state)).squeeze(-1)

    def get_action_and_value(self, obs, state, action=None):
        z = self.features(obs, state)
        dist = Categorical(logits=self.actor(z))
        if action is None:
            action = dist.sample()
        return action, dist.log_prob(action), dist.entropy(), self.critic(z).squeeze(-1)


# ----------------------------------------------------------------------- eval

@torch.no_grad()
def evaluate(agent, cfg, env_id, episodes, seed, device, greedy):
    envs = make_vec_env(env_id, min(16, episodes))
    obs, _ = envs.reset(seed=seed)
    tracker = EpisodeTracker(envs)
    intrinsic = make_intrinsic(cfg, envs.single_observation_space.shape, device)
    intrinsic.attach(envs)  # keeps the policy's internal state (needs) evolving during eval
    done_eps = []
    while len(done_eps) < episodes:
        o = torch.tensor(obs, device=device)
        st = intrinsic.state()
        if greedy:
            action = agent.actor(agent.features(o, st)).argmax(-1)
        else:
            action, _, _, _ = agent.get_action_and_value(o, st)
        tracker.before_step()
        obs, r, term, trunc, info = envs.step(action.cpu().numpy())
        done = term | trunc
        nxt = obs.copy()
        if done.any():
            nxt[done] = np.stack(info["final_obs"][done])
        intrinsic.reward(torch.tensor(nxt), done)
        done_eps += tracker.after_step(r, done)
    envs.close()
    done_eps = done_eps[:episodes]
    return {k: float(np.mean([e[k] for e in done_eps])) for k in done_eps[0]}


# ----------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.toml")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/seed0")
    p.add_argument("--total-timesteps", type=int, default=None, help="override, for smoke tests")
    args = p.parse_args()

    cfg = tomllib.loads(Path(args.config).read_text())
    run, env_cfg, pc, ic = cfg["run"], cfg["env"], cfg["ppo"], cfg["intrinsic"]
    total = args.total_timesteps or run["total_timesteps"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.set_num_threads(1)  # one core per seed; seeds run in parallel
    device = torch.device("cpu")

    n_envs, n_steps = env_cfg["num_envs"], pc["num_steps"]
    batch = n_envs * n_steps
    mb = batch // pc["num_minibatches"]
    num_updates = total // batch

    envs = make_vec_env(env_cfg["id"], n_envs)
    obs_shape = envs.single_observation_space.shape
    intrinsic = make_intrinsic(cfg, obs_shape, device)
    intrinsic.attach(envs)
    agent = Agent(obs_shape, envs.single_action_space.n, intrinsic.state_dim).to(device)
    optimizer = torch.optim.Adam(
        list(agent.parameters()) + list(intrinsic.parameters()), lr=pc["learning_rate"], eps=1e-5
    )

    obs_buf = torch.zeros((n_steps, n_envs) + obs_shape, dtype=torch.uint8)
    act_buf = torch.zeros((n_steps, n_envs), dtype=torch.long)
    logp_buf = torch.zeros((n_steps, n_envs))
    rext_buf = torch.zeros((n_steps, n_envs))
    rint_buf = torch.zeros((n_steps, n_envs))
    done_buf = torch.zeros((n_steps, n_envs))
    val_buf = torch.zeros((n_steps, n_envs))
    state_buf = torch.zeros((n_steps, n_envs, intrinsic.state_dim))

    next_obs, _ = envs.reset(seed=args.seed * 1000)
    next_obs = torch.tensor(next_obs)
    next_done = torch.zeros(n_envs)
    tracker = EpisodeTracker(envs)
    recent = deque(maxlen=100)
    global_step, t0 = 0, time.time()
    first_solved_step = None  # first step where rolling success over 100 episodes >= 0.9
    metrics_f = open(out / "metrics.jsonl", "w")

    for update in range(1, num_updates + 1):
        if pc["anneal_lr"]:
            optimizer.param_groups[0]["lr"] = (1.0 - (update - 1) / num_updates) * pc["learning_rate"]

        # ---- rollout
        for t in range(n_steps):
            global_step += n_envs
            obs_buf[t], done_buf[t] = next_obs, next_done
            state_buf[t] = st = intrinsic.state()
            with torch.no_grad():
                action, logp, _, value = agent.get_action_and_value(next_obs, st)
            act_buf[t], logp_buf[t], val_buf[t] = action, logp, value

            tracker.before_step()
            o, r, term, trunc, info = envs.step(action.numpy())
            done = term | trunc
            rext_buf[t] = torch.tensor(r, dtype=torch.float32)
            # Intrinsic reward is computed on the obs that resulted from the action. On a terminal
            # step `o` is already the next episode's start, so use the true final obs from info.
            nxt = o.copy()
            if done.any():
                nxt[done] = np.stack(info["final_obs"][done])
            rint_buf[t] = intrinsic.reward(torch.tensor(nxt), done)
            # int_ret = coef-weighted intrinsic return per episode, comparable to the task return
            recent.extend(tracker.after_step(r, done, ic["coef"] * rint_buf[t].numpy()))
            next_obs, next_done = torch.tensor(o), torch.tensor(done, dtype=torch.float32)

        # ---- GAE on combined reward (truncation treated as termination, as in CleanRL)
        rewards = rext_buf + ic["coef"] * rint_buf
        with torch.no_grad():
            next_value = agent.get_value(next_obs, intrinsic.state())
        adv = torch.zeros_like(rewards)
        lastgae = 0
        for t in reversed(range(n_steps)):
            nonterm = 1.0 - (next_done if t == n_steps - 1 else done_buf[t + 1])
            nv = next_value if t == n_steps - 1 else val_buf[t + 1]
            delta = rewards[t] + pc["gamma"] * nv * nonterm - val_buf[t]
            adv[t] = lastgae = delta + pc["gamma"] * pc["gae_lambda"] * nonterm * lastgae
        returns = adv + val_buf

        b_obs = obs_buf.reshape((-1,) + obs_shape)
        b_state = state_buf.reshape(batch, intrinsic.state_dim)
        b_act, b_logp = act_buf.reshape(-1), logp_buf.reshape(-1)
        b_adv, b_ret, b_val = adv.reshape(-1), returns.reshape(-1), val_buf.reshape(-1)

        # ---- PPO update
        idx = np.arange(batch)
        clipfracs = []
        for _ in range(pc["update_epochs"]):
            np.random.shuffle(idx)
            for s in range(0, batch, mb):
                m = idx[s:s + mb]
                _, newlogp, ent, newv = agent.get_action_and_value(b_obs[m], b_state[m], b_act[m])
                ratio = (newlogp - b_logp[m]).exp()
                with torch.no_grad():
                    approx_kl = ((ratio - 1) - (newlogp - b_logp[m])).mean()
                    clipfracs.append(((ratio - 1).abs() > pc["clip_coef"]).float().mean().item())
                a = b_adv[m]
                a = (a - a.mean()) / (a.std() + 1e-8)
                pg_loss = torch.max(-a * ratio, -a * ratio.clamp(1 - pc["clip_coef"], 1 + pc["clip_coef"])).mean()
                v_loss = 0.5 * ((newv - b_ret[m]) ** 2).mean()
                loss = pg_loss - pc["ent_coef"] * ent.mean() + pc["vf_coef"] * v_loss
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), pc["max_grad_norm"])
                optimizer.step()
        int_stats = intrinsic.update(b_obs)

        # ---- logging
        if recent:
            succ = float(np.mean([e["success"] for e in recent]))
            if first_solved_step is None and len(recent) == recent.maxlen and succ >= 0.9:
                first_solved_step = global_step
        if update % run["log_every_updates"] == 0 or update == num_updates:
            row = dict(
                global_step=global_step,
                sps=int(global_step / (time.time() - t0)),
                r_int_mean=float(rint_buf.mean()), r_int_std=float(rint_buf.std()),
                pg_loss=pg_loss.item(), v_loss=v_loss.item(), entropy=ent.mean().item(),
                approx_kl=approx_kl.item(), clipfrac=float(np.mean(clipfracs)),
                **int_stats,
            )
            if recent:
                row.update({f"train/{k}": float(np.mean([e[k] for e in recent])) for k in recent[0]})
            metrics_f.write(json.dumps(row) + "\n"); metrics_f.flush()
            print(f"[seed {args.seed}] step {global_step:>9} sps {row['sps']:>5} "
                  f"success {row.get('train/success', 0):.2f} ret {row.get('train/ret', 0):.3f} "
                  f"cov {row.get('train/coverage', 0):.2f} key {row.get('train/got_key', 0):.2f} "
                  f"door {row.get('train/opened_door', 0):.2f} r_int {row['r_int_mean']:.4f}", flush=True)
    envs.close()
    metrics_f.close()

    # ---- generalization eval on fresh layouts (eval seeds disjoint from training seeds)
    evals = {}
    for env_id in env_cfg["eval_ids"]:
        for greedy in (False, True):
            key = f"{env_id.removeprefix('MiniGrid-').removesuffix('-v0')}/{'greedy' if greedy else 'sample'}"
            evals[key] = evaluate(agent, cfg, env_id, env_cfg["eval_episodes"], 10**6 + args.seed, device, greedy)
            print(f"[seed {args.seed}] eval {key}: success {evals[key]['success']:.2f} "
                  f"ret {evals[key]['ret']:.3f} cov {evals[key]['coverage']:.2f}", flush=True)

    rows = [json.loads(l) for l in open(out / "metrics.jsonl")]
    last = rows[-max(1, len(rows) // 10):]  # final 10% of training
    summary = dict(
        seed=args.seed, total_timesteps=global_step, intrinsic=ic,
        first_solved_step=first_solved_step,
        # "keeps exploring?": episodic coverage once the task is solved (None if never solved)
        coverage_after_solved=(float(np.mean([r["train/coverage"] for r in rows
                                              if r["global_step"] >= first_solved_step]))
                               if first_solved_step else None),
        final_train={k: float(np.mean([r[k] for r in last if k in r]))
                     for k in last[-1] if k.startswith("train/") or k.startswith("r_int")},
        eval=evals,
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    torch.save(agent.state_dict(), out / "agent.pt")


if __name__ == "__main__":
    main()
