"""Read-only analysis of historical runs under the locked detector-audit protocol.

This program never imports a historical learner or instantiates an environment.
It copies reference source without changing its bytes, verifies recorded commits,
reads existing evidence, and generates audit tables. No new trajectories exist.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import tomllib
from pathlib import Path
from statistics import fmean

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "handoff-cross-platform/paper-impact-audit"
RELEASE = REF / "release"
OLD_RUNS = Path("/Users/chasemetoyer/.local/share/openresearch/local-runs")
OLD_GIT = Path("/Users/chasemetoyer/Desktop/Agents")
OUT = Path("/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/paper-impact-audit")
FILES = ("ppo.py", "intrinsic.py", "config.toml", "run_seeds.py")
LOCK_COMMIT = "26c14faf193a4bd21388b0f4673ace0d712aee71"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def assert_protocol():
    path = ROOT / "preregistration/paper-impact-audit.md"
    lock = read_json(ROOT / "preregistration/paper-impact-audit-lock.json")
    assert sha(path.read_bytes()) == lock["sha256"][str(path.relative_to(ROOT))]
    committed = subprocess.check_output(["git", "show", f"{LOCK_COMMIT}:preregistration/paper-impact-audit.md"], cwd=ROOT)
    assert committed == path.read_bytes(), "Audit protocol differs from the published lock commit"


def manifest():
    """Use scored mappings as the arm index; do not infer rounds from dates."""
    scored = RELEASE / "scored-results"
    r2 = read_json(scored / "mechanism/prediction-results.json")
    r3 = read_json(scored / "round3/round3-scores.json")["round3"]
    r4 = read_json(scored / "round4/round4-scores.json")["runs"]
    r5 = read_json(scored / "round5/round5-scores.json")["runs"]
    calibration = read_json(scored / "round5/calibration-selection.json")
    answer = []
    for label in ("N1", "N2", "N3", "N4", "N5", "N6", "Control: pay each event once"):
        answer.append({"round": 2, "arm": label, "run": r2[label]["run"], "stored": r2[label]})
    for label in sorted(r3, key=lambda name: int(name[1:])):
        answer.append({"round": 3, "arm": label, "run": r3[label]["run"], "stored": r3[label]})
    for number, data in ((4, r4), (5, r5)):
        for label, row in sorted(data.items()):
            if not label.startswith("r4-"):
                answer.append({"round": number, "arm": label, "run": row["run"], "stored": row})
    answer.append({"round": 5, "arm": "calibration", "run": calibration["run"], "stored": None})
    assert len(answer) == 43 and len({row["run"] for row in answer}) == 43
    assert {r: sum(row["round"] == r for row in answer) for r in range(2, 6)} == {2: 7, 3: 10, 4: 14, 5: 12}
    return answer


def recorded_runs():
    data = {}
    pattern = re.compile(r"^([0-9a-f-]{36})\s+(\w+)\s+(.*?)\s{2,}([0-9a-f]{7,40})\s+(\S+)\s+")
    for line in (RELEASE / "run-records/run-list.txt").read_text().splitlines():
        match = pattern.match(line)
        if match:
            rid, status, title, commit, duration = match.groups()
            data[rid] = dict(status=status, title=title, commit=commit, recorded_duration=duration)
    return data


def preserve_source(run, commit):
    """Every byte copied from the local run must match its recorded Git commit."""
    dest = REF / "run-source" / run
    dest.mkdir(parents=True, exist_ok=True)
    full_commit = subprocess.check_output(["git", "rev-parse", commit], cwd=OLD_GIT, text=True).strip()
    records = {}
    for name in FILES:
        source = OLD_RUNS / run / "repo" / name
        raw = source.read_bytes()
        git_bytes = subprocess.check_output(["git", "show", f"{full_commit}:{name}"], cwd=OLD_GIT)
        if raw != git_bytes:
            raise ValueError(f"Historical source differs from recorded commit: {run}/{name}")
        target = dest / name
        if target.exists():
            assert target.read_bytes() == raw, f"Refusing to overwrite changed reference: {target}"
        else:
            target.write_bytes(raw)
        records[name] = {"sha256": sha(raw), "bytes": len(raw), "matches_recorded_commit": True,
                         "reference": str(target.relative_to(ROOT))}
    assert (dest / "config.toml").read_bytes() == (RELEASE / "run-records" / run / "config.toml").read_bytes()
    return dest, {"run": run, "recorded_commit": commit, "full_commit": full_commit, "files": records}


def source_locations(directory):
    source = (directory / "ppo.py").read_text()
    tree = ast.parse(source)
    answer = {}
    for function in ("main", "evaluate"):
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
        lines = {}
        for call in ast.walk(node):
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                continue
            attr = call.func
            if isinstance(attr.value, ast.Name) and (attr.value.id, attr.attr) in {
                    ("intrinsic", "attach"), ("envs", "reset")}:
                lines.setdefault(attr.attr, []).append(call.lineno)
        answer[function] = {key: min(value) for key, value in lines.items()}
        assert {"attach", "reset"} <= answer[function].keys()
    assert answer["main"]["attach"] < answer["main"]["reset"]
    assert answer["evaluate"]["reset"] < answer["evaluate"]["attach"]
    intrinsic = (directory / "intrinsic.py").read_text()
    assert 'getattr(o, "is_open", None), getattr(o, "is_locked", None)' in intrinsic
    assert "if done[i]:" in intrinsic and "self._start(i)" in intrinsic
    return answer


def read_seed(path, cfg):
    rows = [json.loads(line) for line in (path / "metrics.jsonl").read_text().splitlines() if line.strip()]
    summary = read_json(path / "summary.json")
    seed = int(path.name.removeprefix("seed"))
    assert summary["seed"] == seed
    assert summary["intrinsic"] == cfg["intrinsic"]
    if "env_id" in summary:
        assert summary["env_id"] == cfg["env"]["id"]
    batch = cfg["env"]["num_envs"] * cfg["ppo"]["num_steps"]
    actual = cfg["run"]["total_timesteps"] // batch * batch
    expected = list(range(batch * cfg["run"]["log_every_updates"], actual + 1, batch * cfg["run"]["log_every_updates"]))
    if not expected or expected[-1] != actual:
        expected.append(actual)
    assert [r["global_step"] for r in rows] == expected
    assert summary["total_timesteps"] == actual
    values = [float(row.get("train/success", 0)) for row in rows]
    assert all(math.isfinite(value) and 0 <= value <= 1 for value in values)
    last = values[-max(1, len(values) // 10):]
    f10 = summary.get("final10_exact")
    if f10:
        assert isinstance(f10["episodes"], int) and isinstance(f10["solved_episodes"], int)
        assert 0 <= f10["solved_episodes"] <= f10["episodes"]
        assert math.isclose(f10["start_step"], 0.9 * actual, abs_tol=1e-8)
    return {
        "seed": seed, "actual_training_steps": actual, "logged_rows": len(rows),
        "standardized_train_auc": fmean(values), "standardized_final_success": fmean(last),
        "standardized_solve": fmean(last) >= 0.9,
        "first_solved_step_stored": summary.get("first_solved_step"),
        "first_goal_step_stored": summary.get("first_goal_step"),
        "has_exact_final10_accumulators": f10 is not None,
        "final10_start_step": None if f10 is None else f10["start_step"],
        "final10_completed_episodes": None if f10 is None else f10["episodes"],
        "final10_solved_episodes": None if f10 is None else f10["solved_episodes"],
        "metrics_sha256": sha((path / "metrics.jsonl").read_bytes()),
        "summary_sha256": sha((path / "summary.json").read_bytes()),
        "metric_keys": sorted(set().union(*(row.keys() for row in rows))),
    }


def crosscheck(entry, seeds):
    stored = entry["stored"]
    if entry["round"] not in {4, 5} or stored is None:
        return {"applicable": False, "reason": "No replacement of original round-2 farmer rules or absent scored calibration file"}
    observed = {seed["seed"]: seed for seed in seeds}
    archived = {seed["seed"]: seed for seed in stored["seeds"]}
    assert observed.keys() == archived.keys()
    solved = sum(seed["standardized_solve"] for seed in seeds)
    assert solved == stored["categories"]["solve"], f"Archived solve count mismatch: {entry['run']}"
    errors = []
    auc_key = "train_auc" if entry["round"] == 4 else "auc"
    for seed, score in observed.items():
        archive = archived[seed]
        assert score["standardized_solve"] == (archive["category"] == "solve")
        delta = abs(score["standardized_train_auc"] - archive[auc_key])
        assert delta <= 1e-12, f"Archived per-seed AUC mismatch: {entry['run']} seed{seed}"
        errors.append(delta)
    if entry["round"] == 5:
        assert abs(fmean(seed["standardized_train_auc"] for seed in seeds) - stored["auc_mean"]) <= 1e-12
    return {"applicable": True, "passed": True, "per_seed_auc_comparisons": len(seeds),
            "solve_count_matches": True, "max_auc_absolute_difference": max(errors), "tolerance": 1e-12}


def audit(entry, index):
    run = entry["run"]
    metadata = index[run]
    assert metadata["status"] == "done"
    historical, provenance = preserve_source(run, metadata["commit"])
    cfg = tomllib.loads((historical / "config.toml").read_text())
    record = RELEASE / "run-records" / run
    assert (record / "exit_code").read_text().strip() == "0"
    log = (record / "log").read_text()
    logged_cfg, _ = json.JSONDecoder().raw_decode(log.split("effective config:\n", 1)[1].lstrip())
    assert logged_cfg == cfg, f"Logged effective configuration mismatch: {run}"
    assert "===== SUMMARY" in log
    seed_paths = sorted((record / "results").glob("seed*"), key=lambda path: int(path.name[4:]))
    assert [int(path.name[4:]) for path in seed_paths] == sorted(cfg["run"]["seeds"])
    seeds = [read_seed(path, cfg) for path in seed_paths]
    for seed in cfg["run"]["seeds"]:
        assert f"[seed {seed}] step" in log, f"Seed missing from released stdout: {run}/{seed}"
    location = source_locations(historical)
    ic = cfg["intrinsic"]
    enabled = ic["kind"] in {"homeostatic", "event_bonus"}
    assert enabled or ic["kind"] in {"none", "episodic_count"}
    mode = ic.get("event_mode", "doorkey") if enabled else None
    on = ic.get("needs_on", [1, 1, 1])
    open_active = enabled and (ic["kind"] == "event_bonus" or bool(on[2]))
    key_corridor = cfg["env"]["id"] == "MiniGrid-KeyCorridorS3R1-v0"
    assert key_corridor or cfg["env"]["id"] == "MiniGrid-DoorKey-8x8-v0"
    exposures = len(seeds) * cfg["env"]["num_envs"] if enabled else None
    final10 = key_corridor and all(seed["has_exact_final10_accumulators"] for seed in seeds)
    target_count = sum(seed["final10_solved_episodes"] for seed in seeds) if final10 else None
    completed = sum(seed["final10_completed_episodes"] for seed in seeds) if final10 else None
    check = crosscheck(entry, seeds)
    row = {
        "round": entry["round"], "arm": entry["arm"], "run": run, **metadata,
        "full_commit": provenance["full_commit"], "config": cfg,
        "task": cfg["env"]["id"], "method": ic["kind"], "seed_count": len(seeds),
        "seeds": seeds, "detector_enabled": enabled, "detector_mode": mode,
        "open_need_active": open_active, "source_locations": location,
        "standardized_solve_count": sum(seed["standardized_solve"] for seed in seeds),
        "standardized_mean_train_auc": fmean(seed["standardized_train_auc"] for seed in seeds),
        "standardized_scoring_note": "Mean logged train/success; solve if final floor(10%) of log rows averages at least 0.9. This does not redefine original round-2 farmer labels.",
        "crosscheck_archived_scores": check,
        "initial_door_cache": {
            "class": "structurally_proved_exposure" if enabled else "not_applicable",
            "exposed_initial_episodes": exposures,
            "reward_state_exposed_initial_episodes": exposures if open_active else (0 if enabled else None),
            "exact_missed_opens": None,
            "missed_opens_class": "not_identifiable_from_retained_records" if enabled else "not_applicable",
            "maximum_environment_steps_per_exposed_episode": (270 if key_corridor else 640) if enabled else None,
            "latest_global_step_for_initial_episode_completion": cfg["env"]["num_envs"] * (270 if key_corridor else 640) if enabled else None,
            "reason": "Detector caches objects before initial reset; refresh occurs at each environment's first done. Exposure does not imply a door transition happened.",
            "open_mask_note": "Open channel disabled: its omitted events cannot change reward or need state." if enabled and not open_active else None,
            "evaluation_initialization": "Reset precedes attachment; initialization defect absent in evaluation.",
        },
        "missed_box_openings": {
            "class": "not_applicable" if not enabled or mode == "locked_door_key" else "structurally_proved_zero",
            "count": 0 if enabled and mode == "doorkey" else None,
            "structural_box_opportunities": 0,
            "reason": "Completed task generators contain no boxes; key/locked-door mode also does not claim to reward boxes. Disabled detectors are not observed zeroes.",
        },
        "terminal_pickups": {
            "whole_training_eligible_missed_count": None,
            "whole_training_eligible_missed_class": "not_identifiable_from_retained_records" if enabled else "not_applicable",
            "whole_training_all_object_pickup_count": None,
            "whole_training_all_object_pickup_class": "not_identifiable_from_retained_records",
            "terminal_target_ball_eligible": False if key_corridor and enabled else None,
            "final10_target_ball_pickups": target_count,
            "final10_target_ball_pickup_class": "exact_recorded_count" if final10 else "not_applicable",
            "final10_completed_episodes": completed,
            "final10_target_count_is_exact_from_success": bool(final10),
            "final10_intrinsic_detector_skipped_ineligible_target_pickups": target_count if final10 and enabled else None,
            "final10_intrinsic_skip_class": "exact_recorded_count" if final10 and enabled else "not_applicable",
            "final10_any_object_skips_lower_bound": target_count if final10 and enabled else None,
            "window": "Episodes completing after 0.9 * actual_training_steps; numerator counts terminal target-ball pickups, denominator all completed episodes in that same window." if final10 else None,
            "reason": "KeyCorridor success requires target-ball pickup, intentionally ineligible under key-only reward. Truncation-step key pickups are eligible but unavailable in retained logs. DoorKey successful goal steps are not pickups; timeout-step pickups remain possible.",
        },
        "eligible_terminal_door_omissions": {
            "class": "not_identifiable_from_retained_records" if enabled else "not_applicable", "count": None,
            "reason": "A door change can occur on the truncation step, which detector skips; no historical transition trace was retained.",
        },
        "record_evidence": {
            "log_sha256": sha((record / "log").read_bytes()), "effective_config_matches": True,
            "all_configured_seeds_complete": True, "exit_code": 0,
            "reference": str(record.relative_to(ROOT)),
        },
    }
    return row, provenance


def flat(row):
    init = row["initial_door_cache"]
    terminal = row["terminal_pickups"]
    return {
        "round": row["round"], "arm": row["arm"], "run": row["run"], "task": row["task"],
        "method": row["method"], "seed_count": row["seed_count"],
        "detector_enabled": row["detector_enabled"], "detector_mode": row["detector_mode"],
        "open_need_active": row["open_need_active"],
        "standardized_solve_count": row["standardized_solve_count"],
        "standardized_mean_train_auc": row["standardized_mean_train_auc"],
        "initial_episode_exposures": init["exposed_initial_episodes"],
        "reward_state_initial_episode_exposures": init["reward_state_exposed_initial_episodes"],
        "initial_missed_opens": None, "initial_missed_opens_class": init["missed_opens_class"],
        "box_missed_class": row["missed_box_openings"]["class"],
        "box_missed_count": row["missed_box_openings"]["count"],
        "whole_training_eligible_terminal_pickups_missed": None,
        "whole_training_eligible_terminal_pickups_class": terminal["whole_training_eligible_missed_class"],
        "final10_target_ball_pickups": terminal["final10_target_ball_pickups"],
        "final10_completed_episodes": terminal["final10_completed_episodes"],
        "final10_intrinsic_skipped_ineligible_target_pickups": terminal["final10_intrinsic_detector_skipped_ineligible_target_pickups"],
        "full_commit": row["full_commit"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    assert_protocol()
    index = recorded_runs()
    audited, provenance = [], []
    for entry in manifest():
        row, source = audit(entry, index)
        audited.append(row); provenance.append(source)
    stats = {
        "actual_runs": len(audited), "completed_seed_runs": sum(row["seed_count"] for row in audited),
        "runs_by_round": {str(r): sum(row["round"] == r for row in audited) for r in range(2, 6)},
        "detector_enabled_runs": sum(row["detector_enabled"] for row in audited),
        "detector_disabled_runs": sum(not row["detector_enabled"] for row in audited),
        "exposed_initial_episodes": sum(row["initial_door_cache"]["exposed_initial_episodes"] or 0 for row in audited),
        "reward_state_exposed_initial_episodes": sum(row["initial_door_cache"]["reward_state_exposed_initial_episodes"] or 0 for row in audited),
        "open_disabled_detector_runs": sum(row["detector_enabled"] and not row["open_need_active"] for row in audited),
        "archived_score_checked_runs": sum(row["crosscheck_archived_scores"]["applicable"] for row in audited),
        "archived_auc_seed_comparisons": sum(row["crosscheck_archived_scores"].get("per_seed_auc_comparisons", 0) for row in audited),
        "all_applicable_archived_score_checks_passed": all(row["crosscheck_archived_scores"].get("passed", True) for row in audited),
        "historical_source_files_verified": sum(len(record["files"]) for record in provenance),
    }
    output = {"protocol_commit": LOCK_COMMIT, "schema": 1, "scope": "43 actual round 2-5 runs, including selected round-5 calibration; no new trajectories", "summary": stats, "runs": audited}
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "per-run.json", output)
    write_json(args.out / "source-verification.json", provenance)
    rows = [flat(row) for row in audited]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
    (args.out / "per-run.csv").write_text(buffer.getvalue())
    print(json.dumps({"outputs": [str(args.out / name) for name in ("per-run.json", "per-run.csv", "source-verification.json")], "summary": stats}, sort_keys=True))


if __name__ == "__main__":
    main()
