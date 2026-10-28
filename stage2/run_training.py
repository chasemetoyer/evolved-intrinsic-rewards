"""Execute one validated Stage 2 entry on Modal with the unchanged corrected trainer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import tomli_w

from stage1.run_training import fingerprint
from stage2.common import ISA_PINS, ROOT
from stage2.specs import validate

SOURCE_FILES = ("generic_reward.py", "stage1/corrected_ppo.py", "stage2/run_training.py",
                "stage2/specs.py", "stage2/common.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get("MODAL_IS_REMOTE") and not os.environ.get("MODAL_TASK_ID"):
        raise SystemExit("Training must execute on Modal; local training is disabled.")
    spec = json.loads(args.spec.read_text())
    validate(spec)
    pins = spec.get("isa_pins") or {}
    observed = {name: os.environ.get(name) for name in ISA_PINS}
    if pins and any(observed[name] != value for name, value in pins.items()):
        raise SystemExit("ISA pins requested by the spec are not set in the training environment")
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    cfg_path = out / "config.toml"
    cfg_path.write_bytes(tomli_w.dumps(spec["config"]).encode())
    paths = [ROOT / "handoff-cross-platform/code" / spec["source"] / name for name in ("ppo.py", "intrinsic.py")]
    paths += [ROOT / name for name in SOURCE_FILES]
    provenance = dict(spec=spec, commit=os.environ.get("ORX_COMMIT"), run_id=os.environ.get("ORX_RUN_ID"),
                      python=sys.version, platform=platform.platform(), isa_environment=observed,
                      packages={d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
                      source_files={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in paths})
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    print("EFFECTIVE_CONFIG " + json.dumps(provenance, sort_keys=True), flush=True)
    command = [sys.executable, "-m", "stage1.corrected_ppo", "--source", spec["source"],
               "--seed", str(spec["seed"]), "--config", str(cfg_path), "--out", str(out)]
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = subprocess.run(command, cwd=ROOT, env=dict(os.environ), check=False)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    usage = dict(wall_seconds=time.monotonic() - start,
                 process_core_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                 peak_rss_bytes=after.ru_maxrss * 1024, exit_code=proc.returncode,
                 memory_measurement="child process peak RSS; billing uses requested/actual provider memory",
                 cost_source="controller/provider accounting; process CPU time is not billed allocation time")
    (out / "process_usage.json").write_text(json.dumps(usage, indent=2) + "\n")
    if proc.returncode:
        raise SystemExit(proc.returncode)
    identity = fingerprint(out)
    (out / "fingerprint.json").write_text(json.dumps(identity, indent=2) + "\n")
    print("RUN_SUMMARY " + json.dumps(dict(id=spec["id"], usage=usage, fingerprint=identity,
                                           result=json.loads((out / "summary.json").read_text())),
                                      sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
