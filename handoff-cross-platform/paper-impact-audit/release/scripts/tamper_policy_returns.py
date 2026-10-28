"""POST HOC, descriptive, not pre-registered: replay the saved round-4 tamper-on checkpoints on the 200 check layouts.

For each round-4 tamper-on run (growth 1/160 or 1/40, normalization on or off; seeds 40-59), every checkpoint plays one
sampled-action episode on each of the layouts used by bound_check.py (seeds 10000-10199), exactly as in check (b).
Per episode it records:
  - discounted intrinsic return  G = sum_t gamma^t r_int_t   (gamma = 0.99, coef 1), which PPO's objective weights;
  - undiscounted intrinsic return, which telescopes to D(h0) - D(h_T);
  - time-averaged drive, mean over the episode's steps of D(h_t) after each step (the drive the agent carries);
  - success, episode length and the share of steps on "done" (tamper presses).
Checks: the tracked drive equals D of the module's real need state at every non-terminal step, and the telescoping
identity of Proposition 1 holds for every episode.

Usage (project env, repo root):
  uv run --locked python paper/scripts/tamper_policy_returns.py run RUN SEEDS OUT   # e.g. run B1 40,41 part.json
  uv run --locked python paper/scripts/tamper_policy_returns.py merge OUT PART...   # combine parts
"""
import json, sys, tomllib
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
RUNS = {"B1": "bb00e7e5-65d0-4411-a236-2dacc19f0e63", "B2": "a8f5efc4-63e7-4a55-8020-08f7e7cff7bb",
        "B3": "78c44406-6e63-466f-b309-8dfb82bfe663", "B4": "f0a40d20-3702-4087-803c-8db52fefaf1e"}
ENV, GAMMA, L0, NL, D0 = "MiniGrid-DoorKey-8x8-v0", 0.99, 10_000, 200, 0.75


def replay(key, seed):
    from ppo import Agent, make_vec_env
    from intrinsic import make_intrinsic
    root = Path.home() / ".local/share/openresearch/local-runs" / RUNS[key] / "repo"
    cfg = tomllib.loads((root / "config.toml").read_text())
    ic = cfg["intrinsic"]
    assert ic["tamper"] is True and ic["coef"] == 1.0 and ic["kind"] == "homeostatic" and ic["h0"] == 0.5
    ck = root / "results" / f"seed{seed}" / "agent.pt"
    out = {k: [] for k in ("disc_int", "undisc_int", "mean_drive", "success", "length", "press_share")}
    for b in range(L0, L0 + NL, 16):
        n = min(16, L0 + NL - b)
        envs = make_vec_env(ENV, n); obs, _ = envs.reset(seed=b)
        intr = make_intrinsic(cfg, envs.single_observation_space.shape, "cpu"); intr.attach(envs)
        agent = Agent(envs.single_observation_space.shape, envs.single_action_space.n, intr.state_dim)
        agent.load_state_dict(torch.load(ck)); agent.eval()
        gen = torch.Generator().manual_seed(1_000_000 * seed + b)
        live = np.ones(n, bool); t = 0
        G, U, Dsum, presses = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        S, T = np.zeros(n, bool), np.zeros(n, int)
        Dcur = np.full(n, D0)
        # for the identity check: D0 - (1-g) sum_{t=1}^{T-1} g^(t-1) D_t - g^(T-1) D_T
        tele, lastD = np.zeros(n), np.zeros(n)
        with torch.no_grad():
            while live.any():
                st = intr.state(); logits = agent.actor(agent.features(torch.tensor(obs), st))
                a = torch.multinomial(torch.softmax(logits, -1), 1, generator=gen).squeeze(-1).numpy()
                obs, r, term, trunc, info = envs.step(a); done = term | trunc
                nxt = obs.copy()
                if done.any():
                    nxt[done] = np.stack(info["final_obs"][done])
                ri = intr.reward(torch.tensor(nxt), done, a).numpy().astype(np.float64)
                Dnext = Dcur - ri                       # D(h_{t+1}) = D(h_t) - r_int, valid also on the terminal step
                G[live] += (GAMMA ** t) * ri[live]; U[live] += ri[live]; Dsum[live] += Dnext[live]
                presses[live] += (a[live] == 6)
                ended = live & done
                cont_ = live & ~done                    # the module's real need state must match the tracked drive
                if cont_.any():
                    assert np.allclose((intr.h[cont_].astype(np.float64) ** 2).sum(-1), Dnext[cont_], atol=1e-4)
                # accumulate the telescoped form: terms for t+1 = 1..T-1 use D_{t+1} with weight (1-g) g^t
                cont = live & ~done
                tele[cont] += (1 - GAMMA) * (GAMMA ** t) * Dnext[cont]
                lastD[ended] = (GAMMA ** t) * Dnext[ended]
                S[ended] = r[ended] > 0; T[ended] = t + 1
                live &= ~done; t += 1; Dcur = np.where(done, D0, Dnext)
        envs.close()
        ident = D0 - tele - lastD
        assert np.allclose(ident, G, atol=1e-4), (key, seed, b, float(np.abs(ident - G).max()))
        out["disc_int"] += G.tolist(); out["undisc_int"] += U.tolist(); out["mean_drive"] += (Dsum / T).tolist()
        out["success"] += [bool(x) for x in S]; out["length"] += T.tolist(); out["press_share"] += (presses / T).tolist()
    return out


def main():
    if sys.argv[1] == "run":
        key, seeds, path = sys.argv[2], [int(s) for s in sys.argv[3].split(",") if s.strip()], Path(sys.argv[4])
        torch.set_num_threads(1)
        res = {}
        for s in seeds:
            o = replay(key, s)
            res[f"{key}/{s}"] = {**{f"mean_{k}": float(np.mean(v)) for k, v in o.items()}, **o}
            print(f"{key} seed {s}: disc int {np.mean(o['disc_int']):.3f} | undisc int {np.mean(o['undisc_int']):.3f} | "
                  f"mean drive {np.mean(o['mean_drive']):.3f} | success {np.mean(o['success']):.2f} | "
                  f"len {np.mean(o['length']):.0f} | press share {np.mean(o['press_share']):.3f}", flush=True)
        path.write_text(json.dumps(res))
    elif sys.argv[1] == "merge":
        path, parts = Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]]
        merged = {}
        for p in parts:
            merged.update(json.loads(p.read_text()))
        out = dict(note="POST HOC, descriptive, not pre-registered. Round-4 tamper-on checkpoints replayed with sampled "
                        "actions on the bound-check layouts (seeds 10000-10199), one episode per layout; gamma = 0.99.",
                   runs=RUNS, gamma=GAMMA, layouts=[L0, L0 + NL - 1], D0=D0, policies={})
        # task reward arrives only on the final step: 1 - 0.9 T/640 on success (round 4 has no press cost)
        pd = json.loads((Path(__file__).resolve().parents[1] / "data/sources/part-d-results.json").read_text())
        for k in sorted(merged, key=lambda x: (x.split("/")[0], int(x.split("/")[1]))):
            v = merged[k]
            tot = [g + (GAMMA ** (T - 1)) * (1 - 0.9 * T / 640) * s for g, T, s in zip(v["disc_int"], v["length"], v["success"])]
            v["disc_total"] = tot; v["mean_disc_total"] = float(np.mean(tot))
            key, seed = k.split("/")
            v["train_press_share"] = pd["seeds"][key][seed]["done_frac_final10"]   # training-log share, final 10% of rows
            out["policies"][k] = v
        assert len(out["policies"]) == 80, len(out["policies"])
        diff = [abs(v["mean_press_share"] - v["train_press_share"]) for v in out["policies"].values()]
        out["press_share_check"] = dict(max_abs_diff=float(max(diff)), median_abs_diff=float(np.median(diff)))
        print(f"press share, replay vs training log: median |diff| {np.median(diff):.4f}, max {max(diff):.4f}")
        path.write_text(json.dumps(out, indent=1))
        for key in RUNS:
            pol = [v for k, v in out["policies"].items() if k.startswith(key + "/")]
            f = lambda m: np.median([p[m] for p in pol])
            print(f"{key}: median over seeds of per-seed means: disc int {f('mean_disc_int'):.3f}, disc total "
                  f"{f('mean_disc_total'):.3f}, undisc int {f('mean_undisc_int'):.3f}, mean drive {f('mean_mean_drive'):.3f}, "
                  f"success {f('mean_success'):.3f}, press share {f('mean_press_share'):.3f}")


if __name__ == "__main__":
    main()
