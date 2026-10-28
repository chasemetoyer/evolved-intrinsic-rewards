"""Render the paper impact audit from checked archival audit outputs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/paper-impact-audit')
MAC_PROJECT = Path('/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards')


def ref(relative, label):
    return f'[{label}]({MAC_PROJECT / "handoff-cross-platform/paper-impact-audit" / relative})'


def main():
    data = json.loads((OUT / 'per-run.json').read_text())
    integrity = json.loads((OUT / 'archive-integrity.json').read_text())
    replay = json.loads((OUT / 'replay-audit.json').read_text())
    checked = json.loads((OUT / 'number-check.json').read_text())
    assert checked['status'] == 'pass' and not checked['failures'], 'Independent audit checks must pass before the report is generated'
    s = data['summary']
    lines = [
        '# Paper detector impact audit',
        '',
        '**Stage 1 is paused. This report audits existing paper records; no new training or policy replays were run. The Zenodo release and manuscript were not modified.**',
        '',
        f'The audit covers every actual round 2–5 run: {s["actual_runs"]} runs and {s["completed_seed_runs"]} seed-runs, including the selected round-5 calibration. '
        'The records establish the scope of the defects, but do not retain enough transition information to count every historically missed event. Unknown counts below are not zero. '
        '[Machine-readable per-run evidence](per-run.json) · [CSV](per-run.csv) · [Independent number checks](number-check.json).',
        '',
        '## What changes, and what remains unknown',
        '',
        '| Question | Audit finding |',
        '|---|---|',
        '| Missed box openings | Structurally zero opportunities in the completed DoorKey and default KeyCorridor tasks: neither places boxes. The documented generic detector nevertheless failed to detect box opening/removal. The Setup must say that open covered doors only. |',
        '| Terminal pickups | The detector skips physical events on every terminating or truncating transition. Whole-training counts of omitted eligible pickups are not recoverable. Successful KeyCorridor target-ball pickups can be counted in the retained final window, but were deliberately ineligible under the registered key-only reward. |',
        f'| Door references after reset | More precisely, an empty pre-reset door cache. It exposes {s["exposed_initial_episodes"]:,} initial training episodes across {s["detector_enabled_runs"]} runs; the open reward/state channel is active in {s["reward_state_exposed_initial_episodes"]:,} of those episodes. These are exposed episodes, **not counts of missed openings**. Actual missed transitions are unknown. The cache refreshes after the first episode of each environment. |',
        f'| Existing solve counts and curve areas | All {s["archived_score_checked_runs"]} applicable round-4/round-5 solve-count comparisons and {s["archived_auc_seed_comparisons"]} per-seed curve-area comparisons match the raw logs. No correction to these archived numbers is demonstrated by the audit. This is not an exhaustive regeneration of every number or p-value in the paper. |',
        '| An additional reported quantity | The farming replay’s reported “pickups per episode” counted **pickup-action attempts made while carrying nothing**, not successful pickups. Its numeral is reproducible, but its description needs correction; the successful-pickup count is unavailable. |',
        '| Conclusions after repairing the implementation | Not established. The paper’s empirical comparisons remain descriptions of the implementation actually run. The audit cannot certify that retraining with corrected detectors would preserve solve counts, learning speed, statistical significance, or the wireheading/farming conclusions. The mathematical bounded-return proof remains valid for the archived reward. |',
        '',
        'The definite corrections are to the methods and interpretation of the replay counter. There is no evidence here for replacing measured learning results with hypothetical corrected-agent results. Equally, the absence of historical event traces does not establish that the defects were harmless.',
        '',
        '## Every round 2–5 run',
        '',
        'DK = DoorKey-8x8; KC = KeyCorridorS3R1. U = not identifiable from retained records. '
        'N/A = the intrinsic event detector or the relevant event definition does not apply. '
        '“Blind episodes” counts the initial episode of each parallel environment, not omitted door transitions. '
        'All tasks in this table have zero box opportunities; “0” in the box column is a structural result. '
        '“Off” marks the explore-only mask, where the missing door/pickup events cannot change those reward/state coordinates.',
        '',
        '| Round / arm | Run | Task | Seeds | Box omissions | Eligible terminal pickups omitted | Blind episodes | Open channel |',
        '|---|---|---|---:|---|---|---:|---|',
    ]
    for r in data['runs']:
        enabled = r['detector_enabled']
        box = '0' if r['missed_box_openings']['count'] == 0 else 'N/A; no boxes'
        exposure = r['initial_door_cache']['exposed_initial_episodes']
        arm = r['arm'].replace('Control: pay each event once', 'pay-once')
        run_link = ref(f'release/run-records/{r["run"]}/config.toml', r['run'][:8])
        lines.append(f'| {r["round"]} / {arm} | {run_link} | {"KC" if "KeyCorridor" in r["task"] else "DK"} | {r["seed_count"]} | {box} | {"U" if enabled else "N/A"} | {exposure if exposure is not None else "N/A"} | {"On" if r["open_need_active"] else "Off" if enabled else "N/A"} |')
    lines += [
        '',
        'For every enabled detector, the actual number of door transitions missed during the initial blind period is U. Eligible terminal door events are likewise U. The saved rolling means cannot locate actions at the first episode or at timeout, and overlapping means cannot be summed into event totals. The physical episode tracker starts after reset, so its door counter does not automatically share the detector’s initial blind period; it does also skip terminal physical events.',
        '',
        'The run index follows the scored round maps. Earlier exploratory runs reused as reference comparators are not relabeled as round-2 runs. The older growth-1/40 replay is covered separately below. UnlockPickup was a planned calibration candidate, but no completed UnlockPickup run appears in this release’s round-5 calibration.',
        '',
        '## What can be counted at terminal pickups',
        '',
        'The following are exact counts of successful target-ball pickups among episodes completing in the last training window, aggregated over the configured seeds. The window begins after 90% of actual training steps. These ball pickups are deliberately excluded by `locked_door_key`; they are **not counts of erroneously omitted rewarded key pickups**. A successful target pickup also explains why the original comment “terminal-step pickups can’t happen” was incorrect. Additional pickup events on timeout are not identifiable.',
        '',
        '| Round-5 arm | Target-ball pickups | Completed episodes in window | Intrinsic detector skipped these target events? |',
        '|---|---:|---:|---|',
    ]
    for r in data['runs']:
        t = r['terminal_pickups']
        if t['final10_target_ball_pickups'] is not None:
            lines.append(f'| {r["arm"]} | {t["final10_target_ball_pickups"]:,} | {t["final10_completed_episodes"]:,} | {"Yes; intentionally ineligible" if r["detector_enabled"] else "N/A; task-only control"} |')
    lines += [
        '',
        'In DoorKey, successful termination is entering the goal, not picking up an object. Nevertheless, a pickup or door toggle can occur on the time-limit step, so “no terminal pickups” cannot be inferred for all DoorKey transitions.',
        '',
        '## Archived replay coverage',
        '',
        '| Replay family | Policies | Retained episode count | Initial cache exposures | Open channel active on exposures |',
        '|---|---:|---|---:|---:|',
    ]
    for r in replay['replays']:
        active = r.get('initial_cache_reward_relevant_exposed_episodes')
        if active is None and r['initial_cache_exposed_episodes'] == 0:
            active = 0
        assert active is not None
        lines.append(f'| {r["family"]} | {r.get("policy_count") if r.get("policy_count") is not None else "Path families"} | {r.get("episode_count") if r.get("episode_count") is not None else "Not recorded as a total"} | {r["initial_cache_exposed_episodes"]} | {active} |')
    lines += [
        '',
        f'The older mechanism replays expose {replay["totals"]["older_replay_initial_cache_exposed_episodes"]} initial episodes, of which {replay["totals"]["older_replay_exposures_with_open_reward_enabled"]} have an active open channel. Their stored summaries contain action-attempt frequencies and averaged needs, not ordered trajectories. The later learned-policy replay families retain {replay["totals"]["recorded_per_layout_learned_replay_episodes"]:,} per-layout episode summaries and initialize after reset. They still omit the action/state/event sequences needed to reconstruct corrected terminal rewards.',
        '',
        'The older replay writer’s default episode count is overridable and is not evidence of its historical invocation. Its action sampler also lacks an explicitly seeded Torch generator. A fresh replay of a final checkpoint would be a new diagnostic, not reconstruction of the historical training trajectory. [Detailed replay evidence](replay-audit.md) · [Structured replay inventory](replay-audit.json).',
        '',
        '## Exact proposed paper corrections',
        '',
        'The complete replacement text for Setup, the tamper paragraph, and a limitations/corrections entry is in [Setup corrections — draft](setup-corrections.md). The core changes are: open covered doors only; physical events were skipped at termination and truncation; training began with an empty door cache until the first episode ended; evaluation initialized after reset; and KeyCorridor’s target-ball pickup was intentionally outside the key-only reward.',
        '',
        'The replay wording correction is in [Replay wording — draft](replay-wording-correction.md). Both documents describe the implementation that generated the archived results. Neither has been applied to the paper or archive.',
        '',
        'The paper’s potential-difference ceiling does not require correct event detection. Each need remains in its prescribed bounded interval, and tampering remains a valid zero-need transition. This algebraic validity does not determine the effect of detector fixes on learning or empirical conclusions.',
        '',
        '## Provenance and checks',
        '',
        f'The local release ZIP matches the size and checksum returned by Zenodo for DOI `{integrity["zenodo_doi"]}`. All {integrity["manifest_entries"]:,} entries in its SHA256 manifest passed; the extracted files also match the ZIP. SHA256 of the unchanged ZIP: `{integrity["archive_sha256"]}`. [Integrity record](archive-integrity.json).',
        '',
        f'The exact historical learner, intrinsic module, configuration and seed runner were recovered for every audited run. All {s["historical_source_files_verified"]} files match the recorded Git commits byte for byte. The effective configuration printed in each released log matches its saved configuration, and every configured seed has a complete metric sequence and summary. [Source verification](source-verification.json).',
        '',
        'The audit protocol was hash-locked and committed before these numerical calculations, then pushed to the private project repository. The saved GitHub ref and server `pushed_at` corroborate publication; the author timestamp alone is not used as proof. This remains a retrospective audit: the bug hypotheses, existing paper results, source code and selected records were already known when the audit protocol was locked.',
        '',
        'An additional runtime-provenance discrepancy needs resolution before any future cross-platform claim: the A1b log identifies Python 3.12.12, while the archived requirements select NumPy 2.5.4 on that Python branch. The unqualified NumPy 2.4.6 statement in the handoff/paper does not identify that runtime. This selection follows from log plus dependency markers; the release does not retain a per-run installed-package inventory. It is not a measured import-version result. The preserved MiniGrid/Gymnasium source versions support the detector control-flow audit.',
        '',
        'All new tables are generated from the archived records by the audit scripts, and the independent checker recomputes their counts from raw inputs. Numerical score checks use the paper’s arithmetic mean of logged training success and its final-log-window solve threshold; the standardized audit values do not replace the original round-2 farming classifications. See [number-check.json](number-check.json) for the precise checks and their limits.',
        '',
        '**Stop point:** no Stage 1 validation rollouts, determinism runs, cross-platform runs, calibration, evolution, or random search were launched. Stage 1 will remain on hold pending review of this audit.',
        '',
    ]
    (OUT / 'paper-impact-audit.md').write_text('\n'.join(lines))
    for name in ('setup-corrections.md', 'replay-wording-correction.md'):
        text = (ROOT / 'audits' / name).read_text()
        text = text.replace('../handoff-cross-platform/', str(MAC_PROJECT / 'handoff-cross-platform') + '/')
        (OUT / name).write_text(text)
    print(OUT / 'paper-impact-audit.md')


if __name__ == '__main__':
    main()
