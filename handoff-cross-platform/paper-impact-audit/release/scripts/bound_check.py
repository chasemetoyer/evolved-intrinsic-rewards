"""POST-HOC ANALYSIS (not pre-registered). Optimality bound for the satiation reward.

Bound: per-episode intrinsic return, discounted or not, is at most D(h0) for ANY policy (telescoping, D >= 0):
    G_int = D0 - (1-gamma) * sum_{t=1}^{T-1} gamma^(t-1) D_t - gamma^(T-1) D_T <= D0,   D0 = 3 * 0.5^2 = 0.75.
The tamper step pays D(h_t) - D(0) = D(h_t), the same telescoping form, so the bound holds with tampering too.
A non-solving policy earns no extrinsic reward, so its total return is <= 0.75.

This script computes, for each environment layout, the actual shortest solution path (breadth-first search over the
real MiniGrid dynamics), then replays it in the real environment with the real satiation module (intrinsic.py) to get
the exact return of (a) "tamper once at t=0, then the shortest path" and (b) "the shortest path without tamper"
(the solving trajectory that farming forgoes), undiscounted and discounted (gamma = 0.99), at every tested growth rate.
Check (a), also POST HOC: a richer family of solving policies. On top of the shortest path, insert one drop-and-regrab
of the key at the best point (searching over every position where the agent carries the key and the cell in front is
empty); in tamper settings also optionally tamper just before the goal step. The family's best return per layout is
compared with the same 0.75 ceiling. The tamper family is evaluated only at the tamper-tested growth rates.
Usage (project env, repo root): python paper/scripts/bound_check.py paper/data/bound-check.json [layouts]"""
import json, sys, time, copy
from collections import deque
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gymnasium as gym, minigrid  # noqa
from minigrid.core.grid import Grid
from minigrid.core.world_object import WorldObj, Ball, Box
from ppo import make_vec_env
from intrinsic import make_intrinsic, TAMPER_ACTION

GAMMA, D0 = 0.99, 0.75
ENVS = {"MiniGrid-DoorKey-8x8-v0": dict(mode="doorkey", growths=[0, 1/640, 1/160, 1/80, 1/60, 1/40, 1/30, 1/20], tamper_tested=[1/160, 1/40]),
        "MiniGrid-KeyCorridorS3R1-v0": dict(mode="locked_door_key", growths=[1/160, 1/40, 1/20], tamper_tested=[1/160])}
DROP, PICKUP = 4, 3
ACTS = [0, 1, 2, 3, 4, 5]  # left, right, forward, pickup, drop, toggle ("done" is a no-op and never shortens a path)

def target_of(u):
    return getattr(u, "obj", None)  # KeyCorridor: the ball to pick up; DoorKey: None (goal square)

def shortest_path(env_id, seed):
    env = gym.make(env_id); env.reset(seed=seed); u = env.unwrapped
    tgt = target_of(u); tkey = (tgt.type, tgt.color) if tgt is not None else None
    def snap():
        c = u.carrying.encode() if u.carrying is not None else None
        return (u.grid.encode().tobytes(), tuple(int(x) for x in u.agent_pos), int(u.agent_dir), c)
    shape = u.grid.encode().shape
    def restore(s):
        enc, pos, d, c = s
        u.grid, _ = Grid.decode(np.frombuffer(enc, dtype=np.uint8).reshape(shape))
        u.agent_pos, u.agent_dir, u.step_count = np.array(pos), d, 0
        u.carrying = WorldObj.decode(*c) if c is not None else None
    start = snap(); seen = {start: None}; q = deque([start])
    while q:
        s = q.popleft()
        for a in ACTS:
            restore(s)
            _, r, term, trunc, _ = env.step(a)
            done_goal = (tkey is None and term and r > 0) or (tkey is not None and u.carrying is not None and (u.carrying.type, u.carrying.color) == tkey)
            if done_goal:
                path = [a]; p = s
                while seen[p] is not None:
                    p, pa = seen[p]; path.append(pa)
                return path[::-1], int(u.max_steps)
            if term: continue
            n = snap()
            if n not in seen:
                seen[n] = (s, a); q.append(n)
    return None, int(u.max_steps)

def regrab_positions(env_id, seed, path):
    """Positions k (0..len-1) where, after path[:k], the agent carries a Key and the cell in front is empty, so that
    inserting [drop, pickup] there returns the agent to the same state and path[k:] stays valid."""
    from minigrid.core.world_object import Key
    env = gym.make(env_id); env.reset(seed=seed); u = env.unwrapped; ks = []
    for k in range(len(path)):
        fx, fy = u.front_pos
        if isinstance(u.carrying, Key) and u.grid.get(fx, fy) is None:
            ks.append(k)
        env.step(path[k])
    return ks

def family(path, ks, tamper):
    """Candidate action sequences of the richer solving family (the replay prepends nothing; tamper actions explicit)."""
    out = []
    for k in [None] + ks:
        base = list(path) if k is None else list(path[:k]) + [DROP, PICKUP] + list(path[k:])
        if not tamper:
            out.append(("regrab@%s" % k if k is not None else "shortest", base))
        else:
            out.append(("T0" + ("+regrab@%s" % k if k is not None else ""), [TAMPER_ACTION] + base))
            out.append(("T0+Tgoal" + ("+regrab@%s" % k if k is not None else ""), [TAMPER_ACTION] + base[:-1] + [TAMPER_ACTION, base[-1]]))
    return out

def replay(env_id, seed, actions, growth, mode, tamper):
    cfg = dict(intrinsic=dict(kind="homeostatic", coef=1.0, h0=0.5, growth=[growth] * 3, satiety=[0.1, 1.0, 1.0],
                              needs_on=[1, 1, 1], tamper=bool(tamper), event_mode=mode))
    envs = make_vec_env(env_id, 1); envs.reset(seed=seed)
    m = make_intrinsic(cfg, None, "cpu"); m.attach(envs)
    seq = ([TAMPER_ACTION] if tamper is True else []) + list(actions)   # tamper="explicit": sequence already has presses
    ext = intr = disc = 0.0; success = False
    for t, a in enumerate(seq):
        o, r, term, trunc, info = envs.step(np.array([a]))
        done = term | trunc
        nxt = o.copy()
        if done.any(): nxt[done] = np.stack(info["final_obs"][done])
        ri = float(m.reward(torch.tensor(nxt), done, np.array([a]))[0])
        ext += float(r[0]); intr += ri; disc += GAMMA ** t * (float(r[0]) + ri)
        if done[0]:
            success = bool(r[0] > 0); break
    return dict(success=success, steps=len(seq), ext=ext, intr=intr, total=ext + intr, disc_total=disc)

def main(out, n_layouts):
    res = dict(note="POST-HOC analysis, not pre-registered", gamma=GAMMA, D0=D0, layouts=n_layouts, envs={})
    for env_id, spec in ENVS.items():
        t0 = time.time(); paths = {}
        for s in range(n_layouts):
            p, ms = shortest_path(env_id, 10_000 + s); assert p is not None, (env_id, s); paths[s] = p
        lens = [len(p) for p in paths.values()]
        er = dict(max_steps=ms, shortest_len=dict(min=min(lens), median=float(np.median(lens)), max=max(lens)), growth={})
        for g in spec["growths"]:
            row = {}
            for tam in (True, False):
                rr = [replay(env_id, 10_000 + s, paths[s], g, spec["mode"], tam) for s in range(n_layouts)]
                assert all(x["success"] for x in rr), (env_id, g, tam)
                key = "tamper_once_then_shortest" if tam else "shortest_no_tamper"
                row[key] = dict(undiscounted_min=min(x["total"] for x in rr), undiscounted_median=float(np.median([x["total"] for x in rr])),
                                discounted_min=min(x["disc_total"] for x in rr), discounted_median=float(np.median([x["disc_total"] for x in rr])),
                                intr_min=min(x["intr"] for x in rr), ext_min=min(x["ext"] for x in rr),
                                exceeds_D0_every_layout=all(x["total"] > D0 and x["disc_total"] > D0 for x in rr),
                                layouts_undiscounted_at_or_below_D0=sum(x["total"] <= D0 for x in rr),
                                layouts_discounted_at_or_below_D0=sum(x["disc_total"] <= D0 for x in rr),
                                shortest_len_of_worst_discounted=len(paths[int(np.argmin([x["disc_total"] for x in rr]))]))
            # check (a): richer solving family
            ks = {s: regrab_positions(env_id, 10_000 + s, paths[s]) for s in range(n_layouts)}
            for tam in ([False, True] if g in spec["tamper_tested"] else [False]):
                best = []
                for s in range(n_layouts):
                    cands = [(name, replay(env_id, 10_000 + s, seq, g, spec["mode"], "explicit" if tam else False)) for name, seq in family(paths[s], ks[s], tam)]
                    assert all(x["success"] for _, x in cands), (env_id, g, s)
                    nd, xd = max(cands, key=lambda t: t[1]["disc_total"]); nu, xu = max(cands, key=lambda t: t[1]["total"])
                    best.append(dict(disc=xd["disc_total"], disc_name=nd, undisc=xu["total"], undisc_name=nu, n_regrab_positions=len(ks[s])))
                key = "rich_tamper_family" if tam else "rich_no_tamper_family"
                row[key] = dict(discounted_min=min(b_["disc"] for b_ in best), undiscounted_min=min(b_["undisc"] for b_ in best),
                                layouts_discounted_at_or_below_D0=sum(b_["disc"] <= D0 for b_ in best),
                                layouts_undiscounted_at_or_below_D0=sum(b_["undisc"] <= D0 for b_ in best),
                                best_variant_counts_discounted={n: sum(b_["disc_name"].split("@")[0] == n for b_ in best) for n in sorted({b_["disc_name"].split("@")[0] for b_ in best})},
                                per_layout_best_discounted=[round(b_["disc"], 6) for b_ in best])
            er["growth"][f"1/{round(1/g)}" if g else "0"] = row
        er["seconds"] = round(time.time() - t0, 1); res["envs"][env_id] = er
        print(env_id, json.dumps(er["shortest_len"]), "max_steps", ms, f"({er['seconds']}s)", flush=True)
        for gk, row in er["growth"].items():
            a, b = row["tamper_once_then_shortest"], row["shortest_no_tamper"]
            print(f"  growth {gk:>6}: tamper+shortest min undisc {a['undiscounted_min']:.3f} disc {a['discounted_min']:.3f} | "
                  f"shortest min undisc {b['undiscounted_min']:.3f} disc {b['discounted_min']:.3f} | layouts <= 0.75 (undisc/disc): tamper {a['layouts_undiscounted_at_or_below_D0']}/{a['layouts_discounted_at_or_below_D0']}, no-tamper {b['layouts_undiscounted_at_or_below_D0']}/{b['layouts_discounted_at_or_below_D0']}", flush=True)
            for key in ("rich_no_tamper_family", "rich_tamper_family"):
                if key in row:
                    x = row[key]
                    print(f"      {key}: min undisc {x['undiscounted_min']:.3f} disc {x['discounted_min']:.3f} | layouts <= 0.75 (undisc/disc) {x['layouts_undiscounted_at_or_below_D0']}/{x['layouts_discounted_at_or_below_D0']} | best variants {x['best_variant_counts_discounted']}", flush=True)
    Path(out).write_text(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 200)
