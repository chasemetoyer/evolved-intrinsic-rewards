"""Intrinsic reward modules — the only thing that differs between the agents.

Interface every module implements:
    attach(envs)                                     give the module the vector env (event detectors)
    reward(next_obs: Tensor[N, ...], done) -> [N]    called every env step, no grad
    state() -> Tensor[N, state_dim]                  internal state the policy observes (may be empty)
    update(obs: Tensor[B, ...]) -> dict[str, float]  called once per PPO update on the rollout
PPO then trains on r_ext + coef * r_int.
"""

import numpy as np
import torch
from minigrid.core.world_object import Box, Door


class NoIntrinsic:
    """Agent 1: task reward only."""

    state_dim = 0

    def __init__(self, cfg, obs_shape, device):
        self.device = device

    def attach(self, envs):
        self.n = envs.num_envs

    def reward(self, next_obs, done=None):
        return torch.zeros(next_obs.shape[0], device=self.device)

    def state(self):
        return torch.zeros(self.n, 0, device=self.device)

    def update(self, obs):
        return {}

    def parameters(self):
        return []


# ------------------------------------------------------------------ satiation

NEEDS = ("explore", "grasp", "open")


class EventDetector:
    """Detects three generic MiniGrid events per env per step, from the unwrapped env state:

    explore: the agent sees a 7x7 view it has not seen this episode
    grasp:   the agent picks something up (carrying goes None -> object)
    open:    a door or box changes state (unlock / open)

    These are privileged, hand-chosen detectors. The control agent uses exactly the same ones.
    """

    def __init__(self, envs):
        self.envs = [e.unwrapped for e in envs.envs]
        self.n = len(self.envs)
        self.seen = [set() for _ in range(self.n)]
        self.carrying = [None] * self.n
        self.objs = [[] for _ in range(self.n)]
        self.obj_state = [()] * self.n
        for i in range(self.n):
            self._start(i)

    def _start(self, i):
        e = self.envs[i]
        g = e.grid
        self.objs[i] = [c for c in g.grid if isinstance(c, (Door, Box))]
        self.obj_state[i] = self._state(i)
        self.carrying[i] = e.carrying
        self.seen[i] = set()

    def _state(self, i):
        return tuple((getattr(o, "is_open", None), getattr(o, "is_locked", None)) for o in self.objs[i])

    def step(self, next_obs, done):
        """Returns events [N, 3] in {0,1}. Call after env.step; on done, resets for the new episode."""
        ev = np.zeros((self.n, len(NEEDS)), dtype=np.float32)
        obs = next_obs.cpu().numpy()
        for i, e in enumerate(self.envs):
            k = obs[i].tobytes()
            if k not in self.seen[i]:
                self.seen[i].add(k)
                ev[i, 0] = 1
            if done[i]:
                self._start(i)  # env already reset (SAME_STEP autoreset); terminal-step pickups can't happen
                continue
            if self.carrying[i] is None and e.carrying is not None:
                ev[i, 1] = 1
            self.carrying[i] = e.carrying
            s = self._state(i)
            if s != self.obj_state[i]:
                ev[i, 2] = 1
            self.obj_state[i] = s
        return ev


class Homeostatic:
    """Agent 3: homeostatic satiation (Keramati & Gutkin, eLife 2014).

    The agent has internal needs h in [0,1]^3 (explore, grasp, open) with setpoint 0.
    Each step every need builds up by `growth`; an event of type k reduces h_k by `satiety[k]`.
    Drive D(h) = sum_k h_k^2 (convex, so the same event pays less when the need is already low).
    Satisfaction r_int = D(h_t) - D(h_{t+1}): positive when a need is relieved, slightly negative
    each step a need grows. The policy observes h, so it can act on its own internal state.

    Note: summed over an episode, r_int telescopes to D(h_0) - D(h_T). The undiscounted
    satisfaction return is bounded, so a drop/pick-up loop can't be farmed for unbounded reward;
    with discounting, it still pays to relieve needs sooner.
    The "learned proxy" part (Singh et al. 2010) is the outer search over growth/satiety: each
    sibling node is one candidate, scored by task return.
    """

    state_dim = len(NEEDS)

    def __init__(self, cfg, obs_shape, device):
        ic = cfg["intrinsic"]
        self.device = device
        self.growth = np.array(ic["growth"], dtype=np.float32)
        self.satiety = np.array(ic["satiety"], dtype=np.float32)
        self.h0 = float(ic["h0"])
        self.cfg_pay_once = ic.get("pay_once", False)

    def attach(self, envs):
        self.det = EventDetector(envs)
        self.h = np.full((envs.num_envs, len(NEEDS)), self.h0, dtype=np.float32)

    @staticmethod
    def drive(h):
        return (h ** 2).sum(-1)

    def reward(self, next_obs, done=None):
        ev = self.det.step(next_obs, done)
        h_next = np.clip(self.h + self.growth - self.satiety * ev, 0.0, 1.0)
        r = self.drive(self.h) - self.drive(h_next)
        self.events = ev
        self.h = h_next
        if done is not None:
            self.h[done] = self.h0  # new episode, fresh needs
        return torch.tensor(r, device=self.device)

    def state(self):
        return torch.tensor(self.h, device=self.device)

    def update(self, obs):
        return {f"need/{k}": float(self.h[:, j].mean()) for j, k in enumerate(NEEDS)}

    def parameters(self):
        return []


class EventBonus(Homeostatic):
    """Control for Agent 3: the same events, no needs, no satiation.

    Every event pays a constant bonus equal to what Agent 3 pays the first time an event
    relieves a need at h0: h0^2 - max(h0 - satiety, 0)^2. Repeats pay just as much,
    so a drop/pick-up loop can be farmed. The policy observes nothing extra.
    With `pay_once = true`, each event type pays only the first time per episode (explore still
    pays per new view): "reward each subgoal once", with no needs and no per-step cost.
    """

    state_dim = 0

    def attach(self, envs):
        super().attach(envs)
        self.bonus = self.h0 ** 2 - np.maximum(self.h0 - self.satiety, 0.0) ** 2
        self.pay_once = bool(self.cfg_pay_once)
        self.paid = np.zeros_like(self.h, dtype=bool)

    def reward(self, next_obs, done=None):
        ev = self.det.step(next_obs, done)
        if self.pay_once:
            ev[:, 1:] *= ~self.paid[:, 1:]          # grasp/open pay only the first time
            self.paid[:, 1:] |= ev[:, 1:] > 0
            if done is not None:
                self.paid[done] = False
        self.events = ev
        return torch.tensor((ev * self.bonus).sum(-1), device=self.device)

    def state(self):
        return torch.zeros(self.h.shape[0], 0, device=self.device)

    def update(self, obs):
        return {}


def make_intrinsic(cfg, obs_shape, device):
    kind = cfg["intrinsic"]["kind"]
    if kind == "none":
        return NoIntrinsic(cfg, obs_shape, device)
    if kind == "homeostatic":
        return Homeostatic(cfg, obs_shape, device)
    if kind == "event_bonus":
        return EventBonus(cfg, obs_shape, device)
    raise ValueError(f"intrinsic.kind={kind!r} is not implemented on this branch")
