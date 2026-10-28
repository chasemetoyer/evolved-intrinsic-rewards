"""Audit retained replay records only; never import an environment or run a policy.

Run after preregistration/paper-impact-audit.md is locked. Uses Python stdlib.
The outputs distinguish recorded quantities, structural exposure, and unknowns.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "handoff-cross-platform/paper-impact-audit/release"
DEPENDENCIES = ROOT / "handoff-cross-platform/paper-impact-audit/dependencies"
DEFAULT_OUT = Path("/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/paper-impact-audit")
USED: dict[str, str] = {}


def read(path: Path) -> str:
    raw = path.read_bytes()
    USED[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return raw.decode()


def js(relative: str) -> object:
    return json.loads(read(RELEASE / relative))


def evidence(relative: str, lines: str, reason: str) -> dict:
    read(RELEASE / relative)
    return {"file": str((RELEASE / relative).relative_to(ROOT)), "lines": lines, "reason": reason}


def range_of(values: list) -> list:
    return [min(values), max(values)]


def linear_quantile(values: list[float], q: float) -> float:
    """Independent stdlib equivalent of NumPy percentile's default linear rule."""
    values = sorted(values)
    position = (len(values) - 1) * q
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def assert_source(relative: str, fragments: list[str]) -> None:
    source = read(RELEASE / relative)
    for text in fragments:
        assert text in source, (relative, text)


def main(out: Path) -> None:
    lock = json.loads(read(ROOT / "preregistration/paper-impact-audit-lock.json"))
    for relative, expected in lock["sha256"].items():
        read(ROOT / relative)
        assert USED[relative] == expected, "Audit protocol changed after lock"
    assert_source("scored-results/mechanism/replay_checkpoints.py", [
        'envs = make_vec_env(cfg["env"]["id"], 1)',
        'intr = make_intrinsic(cfg, envs.single_observation_space.shape, "cpu"); intr.attach(envs)',
        'obs, _ = envs.reset(seed=2_000_000 + seed)',
        'cur["pickups"] += ai == 3 and not carrying; cur["drops"] += ai == 4 and carrying; cur["toggles"] += ai == 5',
        'h = np.array(cur.pop("h")); vv = cur.pop("v")',
    ])
    old_script = read(RELEASE / "scored-results/mechanism/replay_checkpoints.py")
    assert old_script.index("intr.attach(envs)") < old_script.index("obs, _ = envs.reset")
    assert "torch.manual_seed" not in old_script and "torch.Generator" not in old_script
    doorkey_source = read(DEPENDENCIES / "minigrid/envs/doorkey.py")
    assert "class DoorKeyEnv" in doorkey_source
    assert "Box(" not in doorkey_source and '"box"' not in doorkey_source

    # Run associations checked against released run-list names, configurations,
    # intrinsic configuration and policy-seed sets, rather than filename alone.
    associations = [
        ("scored-results/mechanism/replay-growth-1-40.json", "6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69", "Agent 3: homeostatic satiation, growth 1/40", None),
        ("scored-results/mechanism/replay-n1.json", "ed5147b6-c861-48b2-b9ff-1952774d5658", "N1: anchor replicate", None),
        ("scored-results/mechanism/replay-n6.json", "bced806e-eccb-434b-be50-ad91f57a9dfb", "N6: growth 1/20", None),
        ("scored-results/mechanism/replay-payonce.json", "5b13189d-614e-48c4-96b7-431838a41e1c", "Control: pay each event once", None),
        ("scored-results/round4/exploratory-replay-A2b.json", "7a364fed-a875-4d3d-a366-21a162be994d", "A2b: explore-only satiation", 3),
    ]
    run_list = read(RELEASE / "run-records/run-list.txt")
    records = []
    for relative, run, title, episodes in associations:
        d = js(relative)
        cfg = tomllib.loads(read(RELEASE / f"run-records/{run}/config.toml"))
        assert cfg["env"]["id"] == "MiniGrid-DoorKey-8x8-v0"
        assert any(line.startswith(run) and title in line for line in run_list.splitlines())
        assert set(map(int, d["seeds"])) == set(cfg["run"]["seeds"])
        for key, value in d["config"].items():
            assert value == cfg["intrinsic"][key], (relative, key)
        seeds = sorted(map(int, d["seeds"]))
        fields = sorted(set().union(*(v.keys() for v in d["seeds"].values())))
        n = len(seeds)
        open_enabled = bool(d["config"].get("needs_on", [1, 1, 1])[2])
        if episodes is not None:
            report = read(RELEASE / "scored-results/round4/round4-report.md")
            assert "3 episodes per seed" in report
        records.append({
            "family": Path(relative).stem, "source_file": relative, "source_runs": [run],
            "task": cfg["env"]["id"], "policy_seeds": seeds, "policy_count": n,
            "episodes_per_policy": episodes, "episode_count": n * episodes if episodes else None,
            "episode_count_evidence": "Archived round4 report explicitly says 3 episodes per seed" if episodes else
                "Not recorded in JSON or retained launch command. Writer default 8 is overridable and is not evidence of actual invocation.",
            "saved_fields": fields, "granularity": "Per-policy averages over episodes; action frequencies/mean needs rounded",
            "success_is_fraction_of_replay_episodes": True,
            "success_fraction_by_policy": {s: p["success"] for s, p in d["seeds"].items()},
            "pickups_drops_toggles_are_per_episode_means_not_literal_counts": True,
            "ordered_actions_saved": False, "event_sequence_saved": False, "state_sequence_saved": False,
            "initial_cache_exposed_episodes": n,
            "initial_cache_exposure_class": "structurally proved exposure: one env created and attached before explicit reset per policy",
            "open_reward_enabled": open_enabled,
            "initial_cache_reward_relevant_exposed_episodes": n if open_enabled else 0,
            "missed_door_transitions": None, "missed_terminal_pickups": None,
            "missed_box_openings": 0,
            "box_evidence_class": "structurally proved zero: DoorKey generator creates no Box",
            "counts_are_attempts": True,
            "sampling": "Sampled categorical actions; environment seed=2000000+policy seed; action RNG seed/state not retained or explicitly set",
            "counterfactual_corrected_replay_identifiable": False,
            "sources": [evidence("scored-results/mechanism/replay_checkpoints.py", "21-28", "one env per policy; attach precedes reset"),
                        evidence("scored-results/mechanism/replay_checkpoints.py", "45-70", "attempt counters; transient histories discarded; per-seed averages saved")],
        })

    farm = js("paper-data/farming-policy-returns.json")
    assert_source("scripts/farming_policy_returns.py", ['envs = make_vec_env(ENV, n); obs, _ = envs.reset(seed=b)', 'intr.attach(envs)',
                                                       'live &= ~done; t += 1'])
    farm_source = read(RELEASE / "scripts/farming_policy_returns.py")
    assert farm_source.index("envs.reset(seed=b)") < farm_source.index("intr.attach(envs)")
    layouts = farm["layouts"]
    for p in farm["policies"].values():
        assert all(len(p[k]) == len(layouts) for k in ("discounted", "undiscounted", "success"))
    farm_episodes = sum(len(p["success"]) for p in farm["policies"].values())
    assert farm_episodes == len(layouts) * len(farm["policies"])
    records.append({
        "family": "farming-policy-returns", "source_file": "paper-data/farming-policy-returns.json",
        "source_runs": [farm["run"]], "task": "MiniGrid-DoorKey-8x8-v0",
        "policy_seeds": sorted(map(int, farm["policies"])), "policy_count": len(farm["policies"]),
        "layout_seeds": layouts, "episodes_per_policy": len(layouts), "episode_count": farm_episodes,
        "saved_fields": sorted(next(iter(farm["policies"].values())).keys()), "granularity": "Per-policy, per-layout episode scalars plus policy means",
        "ordered_actions_saved": False, "event_sequence_saved": False, "state_sequence_saved": False,
        "initial_cache_exposed_episodes": 0, "initial_cache_exposure_class": "structurally proved zero: attach after reset in every batch",
        "missed_box_openings": 0, "box_evidence_class": "structurally proved zero: DoorKey generator creates no Box",
        "missed_door_transitions": 0, "missed_terminal_pickups": None,
        "missed_door_transitions_scope": "initial-cache defect only; no count of other events inferred",
        "sampling": "Sampled multinomial actions with explicit generator seed=1000000*policy_seed+batch_start_layout; batches of at most 16",
        "counterfactual_corrected_replay_identifiable": False,
        "sources": [evidence("scripts/farming_policy_returns.py", "21-42", "reset/attach order; seeded sampling; live mask; retained scalars")],
    })
    tamper = js("paper-data/tamper-policy-returns.json")
    ts = read(RELEASE / "scripts/tamper_policy_returns.py")
    assert ts.index("envs.reset(seed=b)") < ts.index("intr.attach(envs)")
    for p in tamper["policies"].values():
        assert len(set(len(p[k]) for k in ("disc_int", "undisc_int", "mean_drive", "success", "length", "press_share", "disc_total"))) == 1
    neps = sum(len(p["success"]) for p in tamper["policies"].values())
    nlayouts = tamper["layouts"][1] - tamper["layouts"][0] + 1
    assert neps == nlayouts * len(tamper["policies"])
    records.append({
        "family": "tamper-policy-returns", "source_file": "paper-data/tamper-policy-returns.json",
        "source_runs": list(tamper["runs"].values()), "run_labels": tamper["runs"], "task": "MiniGrid-DoorKey-8x8-v0",
        "policy_ids": sorted(tamper["policies"]), "policy_count": len(tamper["policies"]),
        "layout_seed_range": tamper["layouts"], "episodes_per_policy": nlayouts, "episode_count": neps,
        "saved_fields": sorted(next(iter(tamper["policies"].values())).keys()), "granularity": "Per-policy, per-layout episode scalars plus policy means",
        "ordered_actions_saved": False, "event_sequence_saved": False, "state_sequence_saved": False,
        "initial_cache_exposed_episodes": 0, "initial_cache_exposure_class": "structurally proved zero: attach after reset in every batch",
        "missed_box_openings": 0, "box_evidence_class": "structurally proved zero: DoorKey generator creates no Box",
        "missed_door_transitions": 0, "missed_terminal_pickups": None,
        "missed_door_transitions_scope": "initial-cache defect only; no count of other events inferred",
        "sampling": "Sampled multinomial actions with explicit generator seed=1000000*policy_seed+batch_start_layout; batches of at most 16",
        "counterfactual_corrected_replay_identifiable": False,
        "sources": [evidence("scripts/tamper_policy_returns.py", "35-75", "reset/attach order; seeded sampling; live mask; retained scalars")],
    })
    # Check Table 2 from retained per-layout arrays, independent of stored means
    # and the original NumPy-based table generator. Original table is a byte copy
    # from the paper worktree, not edited manuscript material.
    table_path = ROOT / "handoff-cross-platform/paper-impact-audit/paper-tables/replay.tex"
    original_table = read(table_path)
    original_rows = [line for line in original_table.splitlines() if line.startswith("growth ")]
    table_rows = []
    mean_checks = []
    for label, old_row in zip(("B1", "B2", "B3", "B4"), original_rows, strict=True):
        pol = {key: p for key, p in tamper["policies"].items() if key.startswith(label + "/")}
        recalculated = {}
        for key, p in pol.items():
            recalculated[key] = {}
            for field in ("disc_int", "undisc_int", "mean_drive", "success", "length", "press_share", "disc_total"):
                value = math.fsum(p[field]) / len(p[field])
                error = abs(value - p["mean_" + field])
                mean_checks.append({"policy": key, "field": field, "absolute_error": error})
                assert error <= 1e-12, (key, field, error)
                recalculated[key][field] = value
        rendered = []
        summaries = {}
        for field in ("disc_int", "disc_total", "mean_drive"):
            values = [p[field] for p in recalculated.values()]
            q1, median, q3 = [linear_quantile(values, q) for q in (.25, .5, .75)]
            summaries[field] = {"q1": q1, "median": median, "q3": q3}
            rendered.append(f"{median:.3f} [{q1:.3f}, {q3:.3f}]")
        press = statistics.median(p["press_share"] for p in recalculated.values())
        train_press = statistics.median(p["train_press_share"] for p in pol.values())
        rendered.append(f"{press:.3f} ({train_press:.3f})")
        original_cells = [x.strip().removesuffix("\\\\").strip() for x in old_row.split("&")][1:]
        assert rendered == original_cells, (label, rendered, original_cells)
        table_rows.append({"run_label": label, "policy_count": len(pol), "recalculated": summaries,
                           "median_press_share": press, "median_training_press_share": train_press,
                           "rendered_cells": rendered, "original_cells": original_cells, "exact_display_match": True})
    table2_check = {"rows": table_rows, "stored_mean_checks": len(mean_checks),
                    "max_stored_mean_absolute_error": max(x["absolute_error"] for x in mean_checks),
                    "displayed_numeric_values_checked": sum(len(re.findall(r"\d+\.\d+", " ".join(r["rendered_cells"]))) for r in table_rows),
                    "all_displayed_values_match": True,
                    "training_press_share_scope": "Copied per-policy training scalar checked through displayed median only; source training-log audit is separate",
                    "original_table_file": str(table_path.relative_to(ROOT))}
    bc = js("paper-data/bound-check.json")
    bs = read(RELEASE / "scripts/bound_check.py")
    assert bs.index("envs.reset(seed=seed)") < bs.index("m.attach(envs)")
    family_count = sum(len(e["growth"]) for e in bc["envs"].values())
    records.append({
        "family": "bound-check", "source_file": "paper-data/bound-check.json", "source_runs": [],
        "tasks": list(bc["envs"]), "policy_count": None,
        "layout_count_per_task": bc["layouts"], "task_growth_cells": family_count,
        "simple_family_episode_count": 2 * bc["layouts"] * family_count,
        "episode_count": None, "episode_count_evidence": "Two simple families have fixed calls per layout/cell; richer candidate count varies and action paths/candidate counts are not retained",
        "saved_fields": sorted(bc.keys()),
        "cell_saved_fields": {env: {g: {family: sorted(v.keys()) for family, v in row.items()}
                                    for g, row in detail["growth"].items()} for env, detail in bc["envs"].items()},
        "granularity": "Aggregate per task/growth/family; richer family also retains per-layout best discounted returns",
        "ordered_actions_saved": False, "event_sequence_saved": False, "state_sequence_saved": False,
        "initial_cache_exposed_episodes": 0, "initial_cache_exposure_class": "structurally proved zero: every replay attaches after reset",
        "missed_box_openings_doorkey": 0, "box_evidence_class": "structurally proved zero for DoorKey; KeyCorridor key/locked-door mode does not target boxes",
        "missed_door_transitions": 0, "missed_door_transitions_scope": "initial-cache defect only",
        "missed_terminal_pickups": None,
        "sampling": "Deterministic BFS solution paths and explicit regrab/tamper insertions; no learned policy sampling",
        "counterfactual_corrected_replay_identifiable": False,
        "sources": [evidence("scripts/bound_check.py", "91-107", "single-env replay resets before attach"),
                    evidence("scripts/bound_check.py", "112-144", "paths and candidate evaluations transient; aggregated outputs")],
    })

    # Reproduce the values directly quoted from the old N6 replay, retaining the
    # original selection/rounding and identifying the attempt-counter semantics.
    n6 = js("scored-results/mechanism/replay-n6.json")
    selected = {s: p for s, p in n6["seeds"].items() if p["success"] < .5}
    n6_claims = {
        "selected_policy_seeds": sorted(map(int, selected)), "selected_policy_count": len(selected),
        "mean_episode_length_range": range_of([p["len"] for p in selected.values()]),
        "pickup_attempt_mean_range": range_of([p["pickups"] for p in selected.values()]),
        "pickup_attempt_mean_range_printed": [f"{x:.0f}" for x in range_of([p["pickups"] for p in selected.values()])],
        "pickup_drop_action_share_range_from_rounded_inputs": range_of([p["action_freq"]["pickup"] + p["action_freq"]["drop"] for p in selected.values()]),
        "pickup_drop_share_percent_printed": [f"{100*x:.0f}" for x in range_of([p["action_freq"]["pickup"] + p["action_freq"]["drop"] for p in selected.values()])],
        "intrinsic_return_mean_range": range_of([p["r_int"] for p in selected.values()]),
        "mean_need_ranges": {name: range_of([p["mean_need"][i] for p in selected.values()])
                             for i, name in enumerate(("explore", "grasp", "open"))},
        "interpretation": "These reproduce archived replay summaries, not realized pickup counts or corrected-detector values.",
    }
    number_sources = js("paper-data/numbers.json")
    dependent_numbers = {k: v for k, v in number_sources.items()
                         if isinstance(v, dict) and any(token in v.get("source", "") for token in
                            ("round2-replay-n6.json", "tamper-policy-returns.json", "bound-check.json", "bound-summary.json"))}
    claims = [
        {"paper_location": "Section 5.5, DoorKey farming description", "families": ["replay-n6"],
         "numbers": n6_claims,
         "issue": "Paper's pickup range is computed from eligible pickup action attempts, not successful pickups. Initial-episode door cache exposure also applies to this replay. Corrected event counts, needs and returns cannot be recovered.",
         "sources": [evidence("scripts/make_numbers.py", "324-341", "N6 ranges and needs generated from archived summaries")]},
        {"paper_location": "Corrections concerning pay-once and explore-only farming labels", "families": ["replay-payonce", "exploratory-replay-A2b"],
         "issue": "Replay descriptions support qualitative interpretations; aggregate attempt counts do not establish realized cycles. A2b's open need is disabled, so the stale open cache cannot alter that reward/state coordinate.",
         "sources": [evidence("scored-results/round4/round4-report.md", "89-95", "A2b replay scope and novelty ranges")]},
        {"paper_location": "Section 4 check (b)", "families": ["farming-policy-returns", "bound-check"],
         "issue": "Later reset-before-attach path has no initial cache exposure. Existing scalar returns support recomputation of printed arithmetic, but not changed-detector counterfactuals or corrected-training policies.",
         "sources": [evidence("scripts/bound_summary.py", "5-24", "per-layout comparisons and return summaries"),
                     evidence("scripts/make_numbers.py", "389-400", "printed learned-farmer quantities")]},
        {"paper_location": "Table 2, Sections 5.1 and 7", "families": ["tamper-policy-returns"],
         "issue": "Later reset-before-attach path has no initial cache exposure. Returns/drive/press-share table can be recomputed from retained per-layout scalars; repaired training outcomes remain unidentified.",
         "sources": [evidence("scripts/make_tables.py", "179-194", "Table 2 generator"),
                     evidence("scripts/make_numbers.py", "158-171", "printed tamper-replay ranges")]},
        {"paper_location": "Table 1 and Section 4 check (a)", "families": ["bound-check"],
         "issue": "No initial cache exposure. Stored family returns support displayed arithmetic; action/event sequences were not preserved. KeyCorridor mode deliberately excludes terminal target-ball pickups.",
         "sources": [evidence("scripts/make_tables.py", "86-112", "bound table generator"),
                     evidence("scripts/make_numbers.py", "367-388", "printed bound-check quantities")]},
    ]
    total_exposed = sum(r["initial_cache_exposed_episodes"] for r in records)
    total_relevant = sum(r.get("initial_cache_reward_relevant_exposed_episodes", 0) for r in records)
    result = {
        "scope": "Retained-record and source audit only; no new environment steps or policy execution",
        "protocol_lock_commit": "26c14faf193a4bd21388b0f4673ace0d712aee71",
        "replays": records,
        "totals": {"replay_families": len(records), "older_replay_initial_cache_exposed_episodes": total_exposed,
                   "older_replay_exposures_with_open_reward_enabled": total_relevant,
                   "recorded_per_layout_learned_replay_episodes": farm_episodes + neps,
                   "all_historical_replay_episode_count": None},
        "claims": claims, "printed_numbers_with_direct_replay_sources": dependent_numbers,
        "table2_arithmetic_check": table2_check,
        "identifiability": {
            "exact_missed_events_from_aggregates": False,
            "corrected_training_outcomes_from_final_checkpoints": False,
            "reason": "No retained ordered actions, object states or event sequences; floating-point aggregate returns do not uniquely identify event histories.",
            "exception": "Structural zeros/exposures follow source logic, not aggregate inversion. Tamper episode press totals may be recovered from length*press_share, but do not identify door/box/pickup transitions.",
        },
        "source_sha256": dict(sorted(USED.items())),
    }
    assert total_exposed == sum(len(js(x[0])["seeds"]) for x in associations)
    out.mkdir(parents=True, exist_ok=True)
    (out / "replay-audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = ["# Archived replay coverage audit", "",
             "No new policy trajectories were generated. A cache exposure is an initial episode in which the detector was attached before reset; it is not an observed missed event.", "",
             "| Replay family | Policies | Recorded episodes | Initial cache exposures | Open reward enabled on exposures | Saved detail |",
             "|---|---:|---:|---:|---:|---|"]
    for r in records:
        n = r.get("episode_count")
        episodes_text = str(n) if n is not None else "Not recorded"
        if r["family"] == "bound-check":
            episodes_text += f" (simple families: {r['simple_family_episode_count']}; richer total unknown)"
        lines.append(f"| {r['family']} | {r.get('policy_count') if r.get('policy_count') is not None else 'Path families'} | {episodes_text} | {r['initial_cache_exposed_episodes']} | {r.get('initial_cache_reward_relevant_exposed_episodes', 0)} | {r['granularity']} |")
    lines += ["", f"The older replay paths expose {total_exposed} first episodes, with the open reward enabled in {total_relevant}. Their exact missed door transitions and terminal pickups are not identifiable. DoorKey box-opening omissions are structurally zero because its generator creates no boxes.", "",
              "The older JSON files omit the episode count. The writer's default is overridable, so it does not establish the actual denominator. The A2b report alone explicitly supplies its denominator. The two later learned-policy replay families retain per-layout episode scalars; both attach after reset and have zero initial-cache exposure.", "",
              "## Numerical claim implications", ""]
    for claim in claims:
        lines += [f"- **{claim['paper_location']}:** {claim['issue']}"]
    lines += ["", "## Table 2 arithmetic check", "",
              f"Independent reconstruction from the retained per-layout arrays matches all {table2_check['displayed_numeric_values_checked']} displayed numerical values. All {table2_check['stored_mean_checks']} stored per-policy means agree within an absolute tolerance of 1e-12. Training press-share medians use the saved training scalar; the raw training-log audit is separate.", "",
              "## N6 wording correction", "",
              f"The printed pickup range ({'–'.join(n6_claims['pickup_attempt_mean_range_printed'])} per episode) is reproducible from the saved `pickups` field, but the writer counted pickup actions while not carrying. It did not test whether an object was acquired. The matching pickup/drop action-share range ({'–'.join(n6_claims['pickup_drop_share_percent_printed'])}%) is a share of action attempts. Preserve the numerical description as attempts; successful pickup counts are unavailable.", "",
              "A corrected counterfactual numerical result cannot be reconstructed from these aggregates. Saved checkpoints enable new diagnostics, but neither those diagnostics nor a corrected replay are historical training evidence.", "",
              "## Sources", ""]
    for relative in sorted(USED):
        lines.append(f"- `{relative}` (SHA-256 in the companion JSON)")
    (out / "replay-audit.md").write_text("\n".join(lines) + "\n")
    correction = ["# Draft correction to the replay description", "",
        "This is proposed replacement wording only. The original manuscript and release were not edited.", "",
        "## Original passage", "",
        '> “The DoorKey farming is genuine. Replays of the 1/20 farmers show 137–184 pick-ups per 640-step episode, with pick-up and drop taking 48–63% of their actions.”', "",
        "Location: supplied preprint, Section 5.5, DoorKey/normalization-on bullet, PDF page 12. The original sentence is supported by the N6 replay fields and generated number keys listed in the companion audit.", "",
        "## Proposed replacement", "",
        f"> **Repeated pickup/drop attempts in the recorded replays.** For the policies classified as 1/20 farmers, the archived replay summaries record per-policy means of {'–'.join(n6_claims['pickup_attempt_mean_range_printed'])} pickup attempts while not carrying per episode, with a mean episode length of {n6_claims['mean_episode_length_range'][0]:.0f} steps. Pickup and drop actions together account for {'–'.join(n6_claims['pickup_drop_share_percent_printed'])}% of actions. These counters measure attempted actions and do not establish how many pickups succeeded or how many drop–pickup cycles completed.", "",
        "## Companion qualification", "",
        "> The older replay script attached its event detector before the first explicit environment reset, exposing each policy’s first replay episode to stale initial door references. Its saved summaries contain no action or state trajectories. The effect on the recorded need and return averages cannot be quantified from those summaries. These summaries describe the implementation actually replayed, rather than a corrected replay or corrected training run.", "",
        "The following return/need bullet may retain its archived numerical values only with this qualification; no corrected numerical replacement is identified by the retained records.", "",
        "## Counter semantics", "",
        "The writer increments `pickups` for action 3 while not carrying, `drops` for action 4 while carrying, and `toggles` for action 5. It does not verify state transitions. It then averages these counts across replay episodes. Its `success` field is also an episode-average fraction, not a literal success count or a whole-training solve label. Fractional success values cannot determine the missing episode denominator uniquely. Action frequencies are rounded to three decimal places before saving.", "",
        f"Table 2 was independently reconstructed from retained per-layout arrays: all {table2_check['displayed_numeric_values_checked']} displayed numerical values match, and all {table2_check['stored_mean_checks']} per-policy means agree within the numerical-check tolerance of 1e-12. This checks arithmetic for the retained replay, not corrected-detector counterfactuals.", "",
        "Sources: `handoff-cross-platform/preprintpaper.pdf`; `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay_checkpoints.py:45-70`; `handoff-cross-platform/paper-impact-audit/release/scripts/make_numbers.py:324-341`; `handoff-cross-platform/paper-impact-audit/paper-tables/replay.tex`. Reproduction script: `audits/audit_replays.py`.", ""]
    (ROOT / "audits/replay-wording-correction.md").write_text("\n".join(correction))
    print(json.dumps({"outputs": [str(out / "replay-audit.json"), str(out / "replay-audit.md")], "totals": result["totals"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    main(parser.parse_args().out)
