"""Compare nodes: per-seed success AUC (mean train/success over training), solved count, eval, pickups."""
import json, sys, subprocess
from pathlib import Path
import numpy as np
P = "1afd0818-4752-445e-80b2-5e37e0cc6797"
ROOT = Path.home() / ".local/share/openresearch/local-runs"
import re
txt = subprocess.run(["orx", "runs", P], capture_output=True, text=True).stdout
runs = []
for line in txt.splitlines():
    m = re.match(r"^([0-9a-f-]{36})\s+(\w+)\s+(.*?)\s+([0-9a-f]{7})\s", line)
    if m:
        runs.append(dict(id=m[1], status=m[2], experimentTitle=m[3]))
runs = runs[::-1]  # oldest first
out = []
rng = np.random.default_rng(0)
base_auc = None
for r in sorted(runs, key=lambda r: r.get("createdAt", "")):
    if r.get("status") != "done":
        continue
    rid = r["id"]; title = r.get("experimentTitle") or r.get("experiment", {}).get("title", "?")
    seeds = sorted((ROOT / rid / "repo/results").glob("seed*/metrics.jsonl"))
    aucs, solved, ev8, ev16, pick, cov, length = [], 0, [], [], [], [], []
    for f in seeds:
        rows = [json.loads(l) for l in open(f)]
        aucs.append(np.mean([x.get("train/success", 0) for x in rows]))
        last = rows[-max(1, len(rows) // 10):]
        pick.append(np.mean([x.get("train/pickups", np.nan) for x in last]))
        cov.append(np.mean([x["train/coverage"] for x in last]))
        length.append(np.mean([x["train/len"] for x in last]))
        s = json.loads((f.parent / "summary.json").read_text())
        solved += s["first_solved_step"] is not None
        ev8.append(s["eval"]["DoorKey-8x8/sample"]["success"]); ev16.append(s["eval"]["DoorKey-16x16/sample"]["success"])
    aucs = np.array(aucs)
    boot = [rng.choice(aucs, len(aucs)).mean() for _ in range(5000)]
    out.append(dict(run=rid, title=title, n=len(aucs), auc=aucs.mean(), auc_lo=np.percentile(boot, 2.5), auc_hi=np.percentile(boot, 97.5),
                    auc_seeds=aucs.round(3).tolist(), solved=solved, eval8=np.mean(ev8), eval16=np.mean(ev16),
                    pickups=np.nanmean(pick) if not np.all(np.isnan(pick)) else None, coverage=np.mean(cov), ep_len=np.mean(length)))
for o in out:
    pk = f"{o['pickups']:.1f}" if o["pickups"] is not None else "  - "
    print(f"{o['title'][:48]:48s} n={o['n']:2d} AUC {o['auc']:.3f} [{o['auc_lo']:.3f},{o['auc_hi']:.3f}] solved {o['solved']}/{o['n']} "
          f"eval8 {o['eval8']:.2f} eval16 {o['eval16']:.2f} pick {pk} cov {o['coverage']:.2f} len {o['ep_len']:.0f}  {o['run'][:8]}")
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, default=float))
