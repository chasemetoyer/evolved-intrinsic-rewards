"""Generate the Stage 1 report and its machine-readable numbers from records.

Run after the preregistration lock and the evidence collection. Missing evidence
remains pending; partial cells cannot select a task. No training is invoked.
An independent check_numbers script must verify the generated handoff.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from stage1.score import aggregate_calibration, load_completed_scores, score_seed

ARTIFACTS = Path("/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/stage1")


def read_optional(path):
    return json.loads(path.read_text()) if path.exists() else None


def number(value, digits=4):
    if value is None:
        return "pending"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] +
                     ["| " + " | ".join(str(value).replace("|", "/") for value in row) + " |" for row in rows])


def validation_records(results, manifest):
    records = []
    for spec in manifest["runs"]:
        if spec["purpose"] != "validation":
            continue
        markers = [p for p in results.rglob("complete.json") if p.parent.name == spec["id"]]
        if len(markers) > 1:
            raise ValueError("Duplicate validation completion records")
        record = {"id": spec["id"], "complete": False, "tests": None, "failures": None,
                  "errors": None, "skipped": None, "passed": None, "unit_data": {}}
        if markers:
            complete = read_optional(markers[0])
            out = markers[0].parent / "attempts" / complete["attempt"]
            xml = out / "validation.xml"
            if xml.exists():
                tree = ET.parse(xml).getroot()
                suites = list(tree.iter("testsuite"))
                totals = {key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
                          for key in ("tests", "failures", "errors", "skipped")}
                record.update(complete=True, **totals, passed=totals["tests"] > 0 and totals["failures"] == totals["errors"] == 0)
            record["directory"] = str(out)
            for path in sorted((out / "unit-tests").glob("*.json")):
                record["unit_data"][path.name] = read_optional(path)
        records.append(record)
    return records


def comparison_records(manifest, scores):
    result = []
    reference = read_optional(ROOT / "handoff-cross-platform/scored-results/A1b-scored.json")
    stored = {row["seed"]: row for row in reference["seeds"]}
    for seed in range(40, 45):
        directory = ROOT / "handoff-cross-platform/scored-results/a1b-run-3629f9a7" / f"seed{seed}"
        mac = score_seed(directory, 2_000_000)
        assert math.isclose(mac["curve_area"], stored[seed]["train_auc"], abs_tol=1e-12)
        assert mac["solved"] == (stored[seed]["category"] == "solve")
        row = {"seed": seed, "mac": mac, "archived_modal": None, "corrected_modal": None}
        for purpose, key in (("cross_platform", "archived_modal"), ("cross_platform_corrected", "corrected_modal")):
            matches = [spec for spec in manifest["runs"] if spec["purpose"] == purpose and spec["seed"] == seed]
            if len(matches) != 1:
                raise ValueError(f"Expected one descriptive reference run per seed: {purpose}/{seed}")
            row[key] = scores.get(matches[0]["id"])
        result.append(row)
    aggregates = {}
    for key in ("mac", "archived_modal", "corrected_modal"):
        observed = [row[key] for row in result if row[key] is not None]
        aggregates[key] = {"n": len(observed), "complete": len(observed) == 5,
                           "solves": sum(row["solved"] for row in observed),
                           "mean_area": mean(row["curve_area"] for row in observed) if observed else None}
    return {"seeds": result, "aggregates": aggregates, "inferential_tests": False,
            "interpretation": "Descriptive counts and curve areas only; no cross-platform inference or adjustment."}


def determinism_records(manifest, scores):
    groups = {}
    for spec in manifest["runs"]:
        if spec["purpose"] == "determinism":
            groups.setdefault((spec["task"], spec["method"], spec["seed"], spec["total_timesteps"]), []).append(spec)
    records = []
    for (task, method, seed, budget), specs in sorted(groups.items()):
        completed = [scores[spec["id"]] for spec in sorted(specs, key=lambda s: s["replicate"]) if spec["id"] in scores]
        fingerprints = [score["fingerprints"] for score in completed]
        finished = len(specs) == len(completed) == 2 and all(bool(value) for value in fingerprints)
        records.append(dict(task=task, method=method, seed=seed, budget=budget, completed=len(completed),
                            bit_identical=(fingerprints[0] == fingerprints[1]) if finished else None,
                            fingerprints=fingerprints,
                            definition="Learning metrics except sps, summary, and ordered parameter tensor bytes; timing and serializer metadata excluded."))
    return records


def cost_projection(calibration):
    selections = calibration["selection"]
    complete = all(row["status"] != "incomplete" for row in selections)
    training = [row["task"] for row in selections if row["role"] == "training" and row["kept"]]
    kept = [row["task"] for row in selections if row["kept"]]
    per_task = {}
    for task in kept:
        per_task[task] = {}
        for budget in (1_000_000, 2_000_000):
            observations = [score["cost_estimate_usd"] for cell in calibration["cells"]
                            if cell["task"] == task and cell["budget"] == budget
                            for score in cell["seeds"] if score.get("cost_estimate_usd") is not None]
            per_task[task][str(budget)] = {"n": len(observations), "mean_cost_estimate_usd": mean(observations) if observations else None}
    answer = {"selection_complete": complete, "training_tasks": training, "all_kept_tasks": kept,
              "basis": "Measured function wall time times pinned requested CPU/RAM prices; provider invoice is separate. Baseline costs proxy unrun candidate costs.",
              "per_task": per_task, "stage2": [], "stage3": [], "tamper_extra": [],
              "excluded": "Candidate re-evaluation, storage/egress, image builds, failed calls, and billing changes need additional allowance."}
    if not complete:
        return answer
    for budget in (1_000_000, 2_000_000):
        estimates = [per_task[task][str(budget)]["mean_cost_estimate_usd"] for task in training]
        available = all(value is not None for value in estimates)
        answer["stage2"].append({"fitness_budget": budget, "candidate_evaluations_per_method": 10 * 12,
             "candidate_evaluations_both_methods": 2 * 10 * 12, "seeds_per_candidate_task": 3,
             "training_runs": 2 * 10 * 12 * 3 * len(training),
             "cost_estimate_usd": 2 * 10 * 12 * 3 * sum(estimates) if available else None})
    estimates = [per_task[task]["2000000"]["mean_cost_estimate_usd"] for task in kept]
    unit = sum(estimates) if all(value is not None for value in estimates) else None
    for methods in (3, 4, 5):
        answer["stage3"].append({"method_count_scenario": methods, "seeds_per_method_task": 20,
             "training_runs": methods * 20 * len(kept), "cost_estimate_usd": methods * 20 * unit if unit is not None else None})
        for extra_conditions in (1, 2):
            answer["tamper_extra"].append({"method_count_scenario": methods, "additional_training_conditions": extra_conditions,
                "additional_runs": extra_conditions * methods * 20 * len(kept),
                "additional_cost_estimate_usd": extra_conditions * methods * 20 * unit if unit is not None else None})
    return answer


def draft_outline():
    return """# Stage 2 pre-registration outline — DRAFT, NOT LOCKED

No evolutionary or random-search evaluation has been run. Every proposal below
needs approval at the Stage 1 boundary before it becomes a Stage 2 commitment.

- Genome: four events, each with weight in [-1,1], relief in [0,1], and growth either zero or log-scaled in [1/640,1/20]; h0=.5 fixed. Preserve the corrected generic event definitions approved for Stage 1, including exclusion of success-terminal target pickup. Twelve physical parameters. A proposed latent representation uses direct bounded weight/relief coordinates and a growth coordinate with a zero atom plus a positive logarithmic interval. OPEN: zero-atom probability/threshold, transformation, clipping/reflection at CMA boundaries, initialization and sigma.
- Fitness proposal: equal-weight mean training-success curve area over the kept training tasks and three seeds per candidate at the chosen fitness budget. No task-specific fitted formula and no held-out-task feedback. OPEN: confirm the budget, aggregation, treatment of failed/time-limited evaluations, and safeguards for repeated positively paid events.
- CMA-ES: population ten, twelve generations. OPEN: optimizer/library version, seed and initial mean/covariance/sigma; stopping behavior under numerical failure; number of finalists and independent re-evaluation seeds/budget; winner tie-break and whether to reserve candidate evaluations for re-evaluation.
- Random-search control: the same number of candidate evaluations, task set, training budgets and seed counts. OPEN: prior over mixed zero/log growth, matched handling of boundary atoms, winner re-evaluation, and whether random-search winner joins final evaluation. No search starts in Stage 1.
- Seeds: calibration 900–999, evolution 1000–1999, random search 3000–3999, final evaluation 2000–2999. OPEN: exact within-role allocation, common versus fresh candidate seed panels, independent finalist panel, and layout seed mapping. Never reuse seeds across roles.
- Final evaluation: best evolved reward and approved baselines, twenty fresh seeds per kept task, nominal two-million-step training, fixed per-environment evaluation quota. OPEN: baseline roster (task-only, episodic novelty, random-search winner, fixed satiation); whether task aggregation or individual tasks are primary; independent versus paired seed comparisons; minimum worthwhile effect; multiplicity family. Proposed tests retain exact Fisher for solves and exact MWU without ties/permutation MWU with ties for area, Clopper–Pearson intervals, and Holm adjustment. A superiority hit should require the registered direction and adjusted p<.05; numerical level predictions need prewritten intervals. Non-significance does not establish equivalence.
- Tamper test: introduce the done-action need reset only after search. OPEN: freeze policy versus retrain/fine-tune a learner under the selected reward; matched no-tamper condition; free versus paid presses and costs; tasks/methods; budget/seeds; performance noninferiority margin and test; whether press frequency is a separate endpoint. Keep presses and repeated paid events descriptive unless explicit hit rules are locked. Resistance requires a defined performance criterion; bounded return alone is insufficient.
- Budget: approve measured cost projection, re-evaluation overhead, and a hard spending limit. Make the repository public before the Stage 2 lock, commit and push every lock file, and record timestamped amendments. No Stage 3 lock is implied by this draft.
"""


def render(data):
    cal = data["calibration"]
    lines = ["# Stage 1 report", "", "Status: " + ("complete" if data["complete"] else "incomplete; unavailable evidence is marked pending") + ". Stage 2 has not started.", "",
        "All empirical numbers below are generated from retained outputs. `stage1-numbers.json` contains the full precision values and provenance. The independent number-check result is required for final handoff.", "",
        "## Carryover verification", "",
        table(["Item", "Location", "Verification / disposition"], [
            ("A1 PPO / CNN", "handoff-cross-platform/code/*/ppo.py; stage1/corrected_ppo.py", "Archived source retained; corrected adapter keeps learner/CNN and Table 10 settings."),
            ("A2 wrappers / modes", "generic_reward.py; stage1/corrected_ppo.py; archived intrinsic.py", "Corrected reset/terminal capture; legacy locked_door_key remains available; validation records below."),
            ("A3 satiation / tamper", "generic_reward.py; archived intrinsic.py", "Need reset and extrinsic press cost covered by validation."),
            ("A4 statistical procedures", "stage1/statistics.py; tests/test_scoring.py", "Archived procedures reused; known statistical examples checked in validation."),
            ("A5 quota evaluation", "archived ppo.py:evaluate", "Per-environment episode quota preserved."),
            ("A6 number checking", "scripts/report_stage1.py; scripts/check_numbers.py", "Generated JSON and report; independent cross-check required."),
            ("B1 generic events", "generic_reward.py", "Four generic events; successful terminal target pickup excluded under the approved correction."),
            ("B2 refill / farming / tamper", "generic_reward.py; stage1/manifest.json", "Growth bounds enforced; repeated paid events retained; tamper experiment deferred."),
            ("B3 advantage normalization", "stage1/manifest.json", "Enabled in every Stage 1 arm."),
            ("B4 easy-task calibration", "stage1/score.py", "Fixed room-to-improve rule applied without tuning."),
            ("B5 primary metrics", "stage1/score.py", "Curve area and solve count primary; behavior labels descriptive."),
            ("C1 immutable lock", "preregistration/stage1-lock.json; scripts/verify_lock.py", "Input hashes checked before runs; later changes need timestamped amendments."),
            ("C2 corroborated lock", "preregistration/stage1-github-receipt.json", "Committed lock and GitHub receipt checked before launch."),
            ("C3 seed roles", "stage1/manifest.json", "Calibration roles separated; paper seeds restricted to descriptive reproduction."),
            ("C4 same platform / pins", "stage1/modal_app.py; pyproject.toml; uv.lock", "All new evidence uses Modal; per-attempt complete installed package inventory retained."),
            ("C5 fixed scoring", "stage1/score.py; preregistration", "No formulas fitted to outcomes; failures and unavailable cells retained."),
            ("C6 credentials", ".gitignore; environment / Modal configuration", "Credential ignore rules established before source publication."),
            ("C7 stage boundary", "this report and draft outline", "Stop for approval before Stage 2."),
        ]), "", "## Validation and signed ceiling", ""]
    for validation in data["validation"]:
        lines.append(f"Validation `{validation['id']}`: complete={number(validation['complete'])}; tests={number(validation['tests'])}, failures={number(validation['failures'])}, errors={number(validation['errors'])}, skipped={number(validation['skipped'])}; passed={number(validation['passed'])}.")
        for filename, value in validation["unit_data"].items():
            if filename == "bound-check.json":
                checks = value.get("episode_checks", [])
                violations = sum(not row["lower"] - value["tolerance"] <= row["return_value"] <= row["upper"] + value["tolerance"] for row in checks)
                lines.append(f"Numerical bound checks: {len(checks)} episode/prefix records; {violations} tolerance violations; tolerance={value['tolerance']}.")
            elif isinstance(value, dict) and "seeds" in value:
                lines.extend(["", f"`{filename}`:", "", table(["Seed", "Scalar steps", "Bit identical"],
                    [(row["seed"], row.get("scalar_steps", "pending"), number(row.get("bit_identical"))) for row in value["seeds"]])])
    lines += ["", r"Let $V(h)=\sum_k w_k h_k^2$, $L=\sum_k\min(w_k,0)$, and $U=\sum_k\max(w_k,0)$. The archived dynamics apply one clip after growth minus event relief: $h_{t+1}=\operatorname{clip}(h_t+g-s e_t,0,1)$, followed by an optional tamper reset. For one episode or finite prefix with $0<\gamma\le1$:", "",
        r"$$G_T=V(h_0)-(1-\gamma)\sum_{t=1}^{T-1}\gamma^{t-1}V(h_t)-\gamma^{T-1}V(h_T).$$", "",
        r"The coefficients on future potentials are nonnegative and sum to one. Consequently $V(h_0)-U\le G_T\le V(h_0)-L$. At fixed $h_0=.5$, the upper bound is $\frac14\sum_{w_k\ge0}w_k+\frac34\sum_{w_k<0}|w_k|\le3$. For nonnegative unit weights on the three legacy needs this reduces to $.75$. Episode resets are not paid transitions; adding returns over repeated episodes does not inherit a single-episode constant ceiling. Floating-point checks use an explicit numerical tolerance.", "",
        "## Modal, reproducibility and spending", "", "Declared environment:", "", "```json", json.dumps(data["environment"], indent=2), "```", "",
        "One function input represents one configuration/task/seed/budget. Outputs and complete package inventories are stored on the Modal volume and synchronized with hashes. Raw timing and serializer metadata are excluded from numerical bit-identity checks.", "",
        table(["Task / method", "Seed", "Budget", "Completed repeats", "Numerically bit identical"],
              [(row["task"] + " / " + row["method"], row["seed"], row["budget"], row["completed"], number(row["bit_identical"])) for row in data["determinism"]]), "",
        "Spending record (guard estimates and provider-reported completed intervals are distinct from an invoice):", "", "```json", json.dumps(data["spending"], indent=2), "```", "",
        "## Descriptive Mac reference", "", "The two Modal groups are compared with the same original Mac reference using counts and curve areas only. No inferential tests or cross-platform conclusions are drawn, and no configuration is adjusted from this comparison.", "",
        table(["Seed", "Mac solve / area", "Archived Modal solve / area", "Corrected Modal solve / area"],
              [(row["seed"], *[("pending" if row[key] is None else f"{int(row[key]['solved'])} / {row[key]['curve_area']:.6f}")
                                for key in ("mac", "archived_modal", "corrected_modal")]) for row in data["cross_platform"]["seeds"]]), "",
        table(["Group", "Completed", "Solve count", "Mean curve area"], [(key, value["n"], value["solves"], number(value["mean_area"], 6)) for key, value in data["cross_platform"]["aggregates"].items()]), "",
        "## Calibration", "", "AUC is the arithmetic mean of logged rolling training success. Solve requires mean success at least .9 over the final floor(10%) of log rows. First-solved medians include unsolved seeds right-censored at the nominal budget. Actual training stops at the last complete PPO batch. Cost columns are function-compute estimates, with invoices retained separately. Partial cells are descriptive and cannot select a task.", "",
        table(["Task", "Method", "Budget", "Completed", "Solves", "Mean AUC", "Median first solve", "Censored", "Mean wall seconds", "Mean estimated USD"],
              [(c["task"], c["method"], c["budget"], f"{c['n']}/{c['expected_n']}", c["solve_count"], number(c["mean_curve_area"],6), number(c["median_first_solved_step"],1), c["first_solved_censored_count"], number(c["mean_wall_seconds"],1), number(c["mean_cost_estimate_usd"],6)) for c in cal["cells"]]), "",
        table(["Task", "Role", "Selection", "Best mean AUC", "Reason"], [(row["task"], row["role"], row["status"], number(row["best_mean_curve_area"],6), "; ".join(row["reasons"]) or "Fixed rule passed") for row in cal["selection"]]), "",
        "Training-task baseline separation at the fitness budget uses two-sided MWU (exact without ties, permutation with ties), Holm-adjusted across the three planned tasks. A missing or non-significant result does not establish equal performance; the fitness budget remains a user decision.", "",
        table(["Task", "Novelty − task-only mean AUC", "p", "Holm p", "Detected separation"], [(row["task"], number(row["mean_area_difference_novelty_minus_task_only"],6), number(row["p"],6), number(row["p_holm"],6), number(row["separates"])) for row in cal["separation_at_1M"]]), "",
        "## Cost projection", "", "Stage 2 requires 240 candidates across both search methods, three training seeds per task: 720 training runs per kept training task, before finalist re-evaluation. Candidate runtime is not yet measured; the baseline mean is a planning proxy. No projection selects tasks from incomplete cells.", ""]
    project = data["cost_projection"]
    if not project["selection_complete"]:
        lines.append("Total projections are pending because task selection is incomplete. Per-task measured costs remain in the machine-readable data.")
    else:
        lines += [table(["Stage 2 fitness budget scenario", "Training runs", "Estimated USD"], [(r["fitness_budget"], r["training_runs"], number(r["cost_estimate_usd"],4)) for r in project["stage2"]]), "",
            "Stage 3 baseline-roster scenarios (not commitments):", "", table(["Methods", "Training runs", "Estimated USD"], [(r["method_count_scenario"], r["training_runs"], number(r["cost_estimate_usd"],4)) for r in project["stage3"]]), "",
            "Additional tamper training scenarios, if the no-tamper Stage 3 runs serve as controls:", "", table(["Methods", "Extra tamper conditions", "Additional runs", "Additional estimated USD"], [(r["method_count_scenario"], r["additional_training_conditions"], r["additional_runs"], number(r["additional_cost_estimate_usd"],4)) for r in project["tamper_extra"]])]
    lines += ["", "Excluded from these projections: " + project["excluded"], "", "## Stage 2 draft and decisions", "", draft_outline().replace("# Stage 2 pre-registration outline — DRAFT, NOT LOCKED", "DRAFT, NOT LOCKED"), "", "Stage boundary: no evolution or random search starts from this report. User approval and resolution of the listed open decisions are required.", ""]
    if data["invalid_completed_attempts"]:
        lines += ["Invalid completed-attempt records:", "", "```json", json.dumps(data["invalid_completed_attempts"], indent=2), "```", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    parser.add_argument("--manifest", type=Path, default=ROOT / "stage1/manifest.json")
    parser.add_argument("--out", type=Path, default=ARTIFACTS)
    args = parser.parse_args()
    manifest = read_optional(args.manifest)
    scores, failures = load_completed_scores(args.results, manifest)
    calibration = aggregate_calibration(manifest, scores)
    validations = validation_records(args.results, manifest)
    ledger = read_optional(args.results / "budget-ledger.json")
    spend = {"completed_training_calls": len(scores), "guard_total_usd": None,
             "provider_invoice_cost_usd": None, "provider_reported_complete_intervals_cost_usd": None}
    if ledger:
        for key in ("guard_total_usd", "provider_invoice_cost_usd", "provider_reported_complete_intervals_cost_usd", "limit_usd", "overhead_allowance_usd"):
            spend[key] = ledger.get(key)
        spend["ledger_call_count"] = len(ledger.get("calls", {}))
    environment = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    data = {"schema": 1, "manifest": str(args.manifest), "validation": validations,
        "environment": {"python": (ROOT / ".python-version").read_text().strip(), "dependencies": environment["dependencies"]},
        "calibration": calibration, "determinism": determinism_records(manifest, scores),
        "cross_platform": comparison_records(manifest, scores), "spending": spend,
        "cost_projection": cost_projection(calibration), "scores_by_run": scores,
        "invalid_completed_attempts": failures,
        "complete": len(scores) == sum(spec["purpose"] != "validation" for spec in manifest["runs"])
                    and all(value["passed"] for value in validations) and bool(validations) and not failures}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "stage1-numbers.json").write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")
    (args.out / "stage1-report.md").write_text(render(data))
    (args.out / "stage2-preregistration-draft.md").write_text(draft_outline())
    print(json.dumps({"complete": data["complete"], "report": str(args.out / "stage1-report.md"), "numbers": str(args.out / "stage1-numbers.json")}))


if __name__ == "__main__":
    main()
