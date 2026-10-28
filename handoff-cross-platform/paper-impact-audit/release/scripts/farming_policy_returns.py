"""POST HOC check (b), not pre-registered: discounted return from the start state of the LEARNED DoorKey growth-1/20
farming policies (round-2 node N6, run bced806e, seeds 0-9; seed 5 is the run's one solver), on the same 200 layouts
(seeds 10000-10199) used by bound_check.py. One sampled episode per policy and layout; gamma = 0.99; coef 1.
Usage (project env, repo root): python paper/scripts/farming_policy_returns.py paper/data/farming-policy-returns.json"""
import json, sys, tomllib
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ppo import Agent, make_vec_env
from intrinsic import make_intrinsic

RUN = Path.home() / ".local/share/openresearch/local-runs/bced806e-eccb-434b-be50-ad91f57a9dfb/repo"
ENV, GAMMA, L0, NL = "MiniGrid-DoorKey-8x8-v0", 0.99, 10_000, 200
torch.set_num_threads(1)
cfg = tomllib.loads((RUN / "config.toml").read_text())
assert cfg["intrinsic"]["growth"] == [0.05, 0.05, 0.05] and cfg["intrinsic"]["coef"] == 1.0
res = dict(note="POST HOC, not pre-registered", run="bced806e-eccb-434b-be50-ad91f57a9dfb", growth="1/20", gamma=GAMMA,
           layouts=list(range(L0, L0 + NL)), policies={})
for ck in sorted((RUN / "results").glob("seed*/agent.pt"), key=lambda p: int(p.parent.name[4:])):
    seed = int(ck.parent.name[4:]); disc, undisc, succ = [], [], []
    for b in range(L0, L0 + NL, 16):
        n = min(16, L0 + NL - b)
        envs = make_vec_env(ENV, n); obs, _ = envs.reset(seed=b)
        intr = make_intrinsic(cfg, envs.single_observation_space.shape, "cpu"); intr.attach(envs)
        agent = Agent(envs.single_observation_space.shape, envs.single_action_space.n, intr.state_dim)
        agent.load_state_dict(torch.load(ck)); agent.eval()
        gen = torch.Generator().manual_seed(1_000_000 * seed + b)
        live = np.ones(n, bool); t = 0; D = np.zeros(n); U = np.zeros(n); S = np.zeros(n, bool)
        with torch.no_grad():
            while live.any():
                st = intr.state(); logits = agent.actor(agent.features(torch.tensor(obs), st))
                a = torch.multinomial(torch.softmax(logits, -1), 1, generator=gen).squeeze(-1).numpy()
                obs, r, term, trunc, info = envs.step(a); done = term | trunc
                nxt = obs.copy()
                if done.any(): nxt[done] = np.stack(info["final_obs"][done])
                ri = intr.reward(torch.tensor(nxt), done, a).numpy()
                tot = r + cfg["intrinsic"]["coef"] * ri
                D[live] += (GAMMA ** t) * tot[live]; U[live] += tot[live]; S[live & done] = r[live & done] > 0
                live &= ~done; t += 1
        envs.close(); disc += D.tolist(); undisc += U.tolist(); succ += S.tolist()
    res["policies"][seed] = dict(discounted=disc, undiscounted=undisc, success=[bool(x) for x in succ],
                                 mean_discounted=float(np.mean(disc)), mean_undiscounted=float(np.mean(undisc)), success_rate=float(np.mean(succ)))
    print(f"policy seed {seed}: mean discounted {np.mean(disc):.3f} (min {min(disc):.3f}, max {max(disc):.3f}) | mean undiscounted {np.mean(undisc):.3f} | success {np.mean(succ):.2f}", flush=True)
Path(sys.argv[1]).write_text(json.dumps(res, indent=1)); print("written")
