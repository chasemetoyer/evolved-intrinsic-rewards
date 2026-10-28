"""Re-evaluate saved checkpoints with the round-4 per-env-quota evaluator (64 sampled episodes per grid, same
eval seeds as the original runs) and compare with the stored first-N-to-finish numbers.
Usage (project env, cwd = project worktree): python reeval_unbiased.py <out.json> <label=run_id> ..."""
import json, sys, tomllib
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, ".")
from ppo import Agent, evaluate, make_vec_env
from intrinsic import make_intrinsic

RUNS = Path.home() / ".local/share/openresearch/local-runs"
torch.set_num_threads(1)
out = {}
for arg in sys.argv[2:]:
    label, run = arg.split("=")
    repo = RUNS / run / "repo"
    cfg = tomllib.loads((repo / "config.toml").read_text())
    rows = []
    for ck in sorted((repo / "results").glob("seed*/agent.pt"), key=lambda p: int(p.parent.name[4:])):
        seed = int(ck.parent.name[4:])
        envs = make_vec_env(cfg["env"]["id"], 1)
        intr = make_intrinsic(cfg, envs.single_observation_space.shape, "cpu"); intr.attach(envs)
        agent = Agent(envs.single_observation_space.shape, envs.single_action_space.n, intr.state_dim)
        agent.load_state_dict(torch.load(ck)); agent.eval()
        old = json.loads((ck.parent / "summary.json").read_text())["eval"]
        torch.manual_seed(10**6 + seed)
        r = dict(seed=seed)
        for env_id in cfg["env"]["eval_ids"]:
            name = env_id.removeprefix("MiniGrid-").removesuffix("-v0")
            r[name + "/unbiased"] = evaluate(agent, cfg, env_id, 64, 10**6 + seed, "cpu", False)["success"]
            r[name + "/stored"] = old[name + "/sample"]["success"]
        rows.append(r)
        print(label, r, flush=True)
    out[label] = dict(run=run, seeds=rows, mean={k: float(np.mean([x[k] for x in rows])) for k in rows[0] if k != "seed"},
                      n_ge_0p9_16x16_unbiased=sum(x["DoorKey-16x16/unbiased"] >= 0.9 for x in rows))
Path(sys.argv[1]).write_text(json.dumps(out, indent=2))
for k, v in out.items():
    print(k, {a: round(b, 3) for a, b in v["mean"].items()}, "16x16 seeds >= 0.9 (unbiased):", v["n_ge_0p9_16x16_unbiased"])
