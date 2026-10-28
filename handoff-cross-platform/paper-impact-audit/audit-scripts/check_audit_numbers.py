"""Independent retained-record number check; no learner imports or environment steps.

Scope is reconstructed from raw run-list titles, not the audit producer's arm
manifest. Metrics are recalculated from archived JSONL, with missing event counts
kept unknown. All checks write a durable success/failure record before exit.
"""
from pathlib import Path
from collections import Counter
from statistics import fmean
import ast
import csv
import hashlib
import json
import math
import re
import subprocess
import tomllib
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'handoff-cross-platform/paper-impact-audit'
REL = BASE / 'release'
OUT = Path('/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/paper-impact-audit')
failures, counts, findings = [], Counter(), {}

def read(path):
    return json.loads(path.read_text())

def check(condition, label, detail=None):
    counts[label.split(':')[0]] += 1
    if not condition:
        failures.append({'check': label, 'detail': detail})

def close(a, b):
    return math.isclose(a, b, rel_tol=0, abs_tol=1e-12)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    audit = read(OUT / 'per-run.json')
    byrun = {x['run']: x for x in audit['runs']}
    chosen = {}
    for line in (REL / 'run-records/run-list.txt').read_text().splitlines():
        fields = re.split(r'\s{2,}', line.strip())
        if not fields or not re.fullmatch(r'[a-f0-9-]{36}', fields[0]):
            continue
        rid, status, title, commit = fields[:4]
        r = (5 if title.startswith('R5-') else
             4 if re.match(r'^(A[12][abc]|B[1-8]):', title) else
             3 if re.match(r'^R([1-9]|10):', title) else
             2 if re.match(r'^N[1-6]:', title) or title == 'Control: pay each event once per episode' else None)
        if r is not None:
            chosen[rid] = (r, commit)
            check(status == 'done', 'scope:completed:' + rid)
    check(set(chosen) == set(byrun), 'scope:run_identity')
    totals = Counter(actual_runs=len(chosen))
    perround = Counter()
    kc = {'all_runs': 0, 'all_seeds': 0, 'target_pickups': 0, 'completed_episodes': 0,
          'detector_runs': 0, 'detector_seeds': 0, 'detector_target_pickups': 0, 'detector_completed_episodes': 0}
    rebuilt = {}
    tasks = Counter()
    for rid, (round_number, commit) in chosen.items():
        record = REL / 'run-records' / rid
        cfg = tomllib.loads((record / 'config.toml').read_text())
        row = byrun[rid]
        check(row['round'] == round_number and row['commit'] == commit, 'scope:round_commit:' + rid)
        check(row['config'] == cfg, 'config:match:' + rid)
        perround[str(round_number)] += 1
        tasks[cfg['env']['id']] += 1
        enabled = cfg['intrinsic']['kind'] in ('homeostatic', 'event_bonus')
        open_on = enabled and (cfg['intrinsic']['kind'] == 'event_bonus' or bool(cfg['intrinsic'].get('needs_on', [1,1,1])[2]))
        mode = cfg['intrinsic'].get('event_mode', 'doorkey') if enabled else None
        check(row['detector_enabled'] == enabled and row['open_need_active'] == open_on, 'classification:enabled:' + rid)
        check(row['detector_mode'] == mode, 'classification:mode:' + rid)
        totals['detector_enabled_runs' if enabled else 'detector_disabled_runs'] += 1
        totals['open_disabled_detector_runs'] += int(enabled and not open_on)
        observed = {}
        seed_records = {x['seed']: x for x in row['seeds']}
        paths = sorted((record / 'results').glob('seed*/summary.json'))
        check({int(x.parent.name[4:]) for x in paths} == set(cfg['run']['seeds']), 'seeds:complete:' + rid)
        for summary_path in paths:
            summary = read(summary_path)
            seed = int(summary_path.parent.name[4:])
            metrics_path = summary_path.parent / 'metrics.jsonl'
            metrics = [json.loads(x) for x in metrics_path.read_text().splitlines() if x]
            values = [float(x.get('train/success', 0)) for x in metrics]
            auc = fmean(values)
            last = fmean(values[-max(1, len(values)//10):])
            observed[seed] = {'auc': auc, 'solve': last >= .9}
            stored = seed_records[seed]
            check(close(auc, stored['standardized_train_auc']), 'metrics:auc:' + rid + ':' + str(seed))
            check(close(last, stored['standardized_final_success']) and stored['standardized_solve'] == (last >= .9), 'metrics:solve:' + rid + ':' + str(seed))
            check(digest(metrics_path) == stored['metrics_sha256'] and digest(summary_path) == stored['summary_sha256'], 'metrics:hash:' + rid + ':' + str(seed))
            check(summary['seed'] == seed and summary['intrinsic'] == cfg['intrinsic'], 'metrics:summary_config:' + rid + ':' + str(seed))
        n = len(observed)
        totals['completed_seed_runs'] += n
        exposure = n * cfg['env']['num_envs'] if enabled else None
        check(row['seed_count'] == n and row['initial_door_cache']['exposed_initial_episodes'] == exposure, 'exposure:count:' + rid)
        check(row['initial_door_cache']['reward_state_exposed_initial_episodes'] == (exposure if open_on else 0 if enabled else None), 'exposure:active:' + rid)
        totals['exposed_initial_episodes'] += exposure or 0
        totals['reward_state_exposed_initial_episodes'] += exposure if open_on else 0
        check(row['initial_door_cache']['exact_missed_opens'] is None, 'unknown:not_zero_initial:' + rid)
        check(row['terminal_pickups']['whole_training_eligible_missed_count'] is None, 'unknown:not_zero_terminal:' + rid)
        check(row['eligible_terminal_door_omissions']['count'] is None, 'unknown:not_zero_door:' + rid)
        check(row['missed_box_openings']['count'] == (0 if enabled and mode == 'doorkey' else None), 'classification:boxes:' + rid)
        check(row['standardized_solve_count'] == sum(x['solve'] for x in observed.values()), 'metrics:aggregate_solves:' + rid)
        check(close(row['standardized_mean_train_auc'], fmean(x['auc'] for x in observed.values())), 'metrics:aggregate_auc:' + rid)
        if cfg['env']['id'] == 'MiniGrid-KeyCorridorS3R1-v0':
            acc = [read(p)['final10_exact'] for p in paths]
            target, episodes = sum(x['solved_episodes'] for x in acc), sum(x['episodes'] for x in acc)
            check(row['terminal_pickups']['final10_target_ball_pickups'] == target, 'terminal:target_count:' + rid)
            check(row['terminal_pickups']['final10_completed_episodes'] == episodes, 'terminal:denominator:' + rid)
            check(row['terminal_pickups']['final10_intrinsic_detector_skipped_ineligible_target_pickups'] == (target if enabled else None), 'terminal:ineligible_skips:' + rid)
            kc['all_runs'] += 1; kc['all_seeds'] += n; kc['target_pickups'] += target; kc['completed_episodes'] += episodes
            if enabled:
                kc['detector_runs'] += 1; kc['detector_seeds'] += n; kc['detector_target_pickups'] += target; kc['detector_completed_episodes'] += episodes
        rebuilt[rid] = observed
    for rn in (4, 5):
        scored = read(REL / f'scored-results/round{rn}/round{rn}-scores.json')['runs']
        for label, item in scored.items():
            if label.startswith('r4-') or item['run'] not in chosen:
                continue
            obs = rebuilt[item['run']]
            check(sum(v['solve'] for v in obs.values()) == item['categories']['solve'], 'archived:solves:' + item['run'])
            totals['archived_score_checked_runs'] += 1
            for seed in item['seeds']:
                check(close(obs[seed['seed']]['auc'], seed['train_auc' if rn == 4 else 'auc']), 'archived:auc:' + item['run'] + ':' + str(seed['seed']))
                totals['archived_auc_seed_comparisons'] += 1
    for key, value in totals.items():
        check(audit['summary'][key] == value, 'summary:' + key)
    check(audit['summary']['runs_by_round'] == dict(perround), 'summary:rounds')
    check(not any('UnlockPickup' in task for task in tasks), 'scope:no_completed_unlockpickup')
    findings.update(training=dict(totals), runs_by_round=dict(perround), task_inventory=dict(tasks), keycorridor_final10=kc)
    csv_rows = list(csv.DictReader((OUT / 'per-run.csv').open()))
    check({r['run'] for r in csv_rows} == set(chosen), 'table:csv_scope')
    for item in csv_rows:
        row = byrun[item['run']]
        for name in ('round', 'task', 'method', 'seed_count', 'detector_enabled', 'open_need_active', 'standardized_solve_count'):
            check(item[name] == str(row[name]), 'table:csv:' + item['run'] + ':' + name)
        check(close(float(item['standardized_mean_train_auc']), row['standardized_mean_train_auc']), 'table:csv_auc:' + item['run'])
        for name in ('initial_missed_opens', 'whole_training_eligible_terminal_pickups_missed'):
            check(item[name] == '', 'table:csv_unknown:' + item['run'] + ':' + name)

    # Independently inspect preserved source order and hashes, never execute it.
    source_records = read(OUT / 'source-verification.json')
    source_file_count = 0
    for record in source_records:
        for name, item in record['files'].items():
            source_file_count += 1
            path = ROOT / item['reference']
            check(digest(path) == item['sha256'], 'source:hash:' + record['run'] + ':' + name)
            git_bytes = subprocess.check_output(['git','show',f"{record['full_commit']}:{name}"], cwd='/Users/chasemetoyer/Desktop/Agents')
            check(path.read_bytes() == git_bytes, 'source:commit:' + record['run'] + ':' + name)
        tree = ast.parse((BASE / 'run-source' / record['run'] / 'ppo.py').read_text())
        for fn, attach_first in [('main', True), ('evaluate', False)]:
            node = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == fn)
            positions = {}
            for x in ast.walk(node):
                if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name):
                    key = (x.func.value.id, x.func.attr)
                    if key in [('intrinsic','attach'),('envs','reset')]:
                        positions.setdefault(key, []).append(x.lineno)
            check((min(positions[('intrinsic','attach')]) < min(positions[('envs','reset')])) == attach_first, 'source:order:' + record['run'] + ':' + fn)
    check(source_file_count == audit['summary']['historical_source_files_verified'], 'source:count')
    findings['source_files_checked'] = source_file_count
    for item in read(BASE / 'dependencies/versions.json')['files']:
        check(digest(BASE / 'dependencies' / item['path']) == item['sha256'], 'dependency:hash:' + item['path'])

    archive = (BASE / 'release.zip').read_bytes()
    integrity = read(OUT / 'archive-integrity.json')
    remote = next(x for x in read(BASE / 'zenodo-record.json')['files'] if x['key'] == 'release.zip')
    check('md5:' + hashlib.md5(archive).hexdigest() == remote['checksum'], 'archive:zenodo_md5')
    check(len(archive) == remote['size'] == integrity['archive_size_bytes'], 'archive:size')
    check(hashlib.sha256(archive).hexdigest() == integrity['archive_sha256'], 'archive:sha256')
    manifest = (REL / 'SHA256SUMS').read_text().splitlines()
    for line in manifest:
        expected, rel = line.split(maxsplit=1)
        check(digest(REL / rel.lstrip('*')) == expected, 'archive:manifest:' + rel)
    check(len(manifest) == integrity['manifest_entries'], 'archive:manifest_count')
    with zipfile.ZipFile(BASE / 'release.zip') as z:
        for info in z.infolist():
            if not info.is_dir():
                path = REL / info.filename.removeprefix('release/')
                check(hashlib.sha256(z.read(info)).hexdigest() == digest(path), 'archive:zip_entry:' + info.filename)
    findings['archive_manifest_files'] = len(manifest)

    replay = read(OUT / 'replay-audit.json')
    families = {x['family']: x for x in replay['replays']}
    initial, active = 0, 0
    for name in ['replay-growth-1-40','replay-n1','replay-n6','replay-payonce','exploratory-replay-A2b']:
        row = families[name]; raw = read(REL / row['source_file']); n = len(raw['seeds'])
        check(n == row['policy_count'] == row['initial_cache_exposed_episodes'], 'replay:initial:' + name)
        initial += n
        if name != 'exploratory-replay-A2b':
            active += n
            check(row['episode_count'] is None and row['episodes_per_policy'] is None, 'unknown:older_episode_count:' + name)
        else:
            report = (REL / 'scored-results/round4/round4-report.md').read_text()
            check('3 episodes' in report and row['episode_count'] == 3*n, 'replay:A2b_recorded_episode_count')
        check(row['missed_door_transitions'] is None and row['missed_terminal_pickups'] is None, 'unknown:replay_events:' + name)
    farming = read(REL / 'paper-data/farming-policy-returns.json')
    tamper = read(REL / 'paper-data/tamper-policy-returns.json')
    fc = sum(len(x['discounted']) for x in farming['policies'].values())
    tc = sum(len(x['disc_int']) for x in tamper['policies'].values())
    check(fc == families['farming-policy-returns']['episode_count'], 'replay:farming_episode_count')
    check(tc == families['tamper-policy-returns']['episode_count'], 'replay:tamper_episode_count')
    for seed, p in farming['policies'].items():
        for array, mean in [('discounted','mean_discounted'),('undiscounted','mean_undiscounted'),('success','success_rate')]:
            check(close(fmean(p[array]), p[mean]), 'replay:farming_mean:' + seed + ':' + mean)
    for seed, p in tamper['policies'].items():
        for array, mean in [('disc_int','mean_disc_int'),('disc_total','mean_disc_total'),('undisc_int','mean_undisc_int'),('mean_drive','mean_mean_drive'),('success','mean_success'),('press_share','mean_press_share'),('length','mean_length')]:
            check(close(fmean(p[array]), p[mean]), 'replay:tamper_mean:' + seed + ':' + mean)
    table = (BASE / 'paper-tables/replay.tex').read_text()
    original_rows = [line for line in table.splitlines() if line.startswith('growth ')]
    displayed = 0
    for index, label in enumerate(('B1','B2','B3','B4')):
        policies = [v for k,v in tamper['policies'].items() if k.startswith(label + '/')]
        cells = []
        for field in ('disc_int','disc_total','mean_drive'):
            means = [np.mean(v[field]) for v in policies]
            q1, med, q3 = np.percentile(means, [25,50,75], method='linear')
            cells.append(f'{med:.3f} [{q1:.3f}, {q3:.3f}]')
            displayed += 3
        press = np.median([np.mean(v['press_share']) for v in policies])
        train = np.median([v['train_press_share'] for v in policies])
        cells.append(f'{press:.3f} ({train:.3f})')
        displayed += 2
        check(' & '.join(cells) in original_rows[index], 'table:original_table2:' + label)
    check(displayed == replay['table2_arithmetic_check']['displayed_numeric_values_checked'], 'table:displayed_value_count')
    check(7 * len(tamper['policies']) == replay['table2_arithmetic_check']['stored_mean_checks'], 'table:stored_mean_count')
    bound = read(REL / 'paper-data/bound-check.json')
    simple = 2 * bound['layouts'] * sum(len(e['growth']) for e in bound['envs'].values())
    check(simple == families['bound-check']['simple_family_episode_count'], 'replay:simple_family_count')
    check(replay['totals']['older_replay_initial_cache_exposed_episodes'] == initial and replay['totals']['older_replay_exposures_with_open_reward_enabled'] == active, 'replay:total_exposures')
    check(replay['totals']['recorded_per_layout_learned_replay_episodes'] == fc + tc, 'replay:total_recorded')
    check(replay['totals']['all_historical_replay_episode_count'] is None, 'unknown:all_replay_episodes')
    check(replay['totals']['replay_families'] == len(families), 'replay:family_count')
    n6 = read(REL / 'scored-results/mechanism/replay-n6.json')['seeds']
    selected = {k:v for k,v in n6.items() if v['success'] < .5}
    claim = next(x['numbers'] for x in replay['claims'] if x['families'] == ['replay-n6'])
    ranges = {
        'pickup_attempt_mean_range': [min(x['pickups'] for x in selected.values()), max(x['pickups'] for x in selected.values())],
        'intrinsic_return_mean_range': [min(x['r_int'] for x in selected.values()), max(x['r_int'] for x in selected.values())],
        'pickup_drop_action_share_range_from_rounded_inputs': [min(x['action_freq']['pickup'] + x['action_freq']['drop'] for x in selected.values()), max(x['action_freq']['pickup'] + x['action_freq']['drop'] for x in selected.values())],
    }
    check(sorted(map(int,selected)) == claim['selected_policy_seeds'] and len(selected) == claim['selected_policy_count'], 'replay:n6_selection')
    for key, values in ranges.items():
        check(all(close(a,b) for a,b in zip(values,claim[key])), 'replay:n6_range:' + key)
    lengths = [x['len'] for x in selected.values()]
    check(claim['mean_episode_length_range'] == [min(lengths),max(lengths)], 'replay:n6_lengths')
    check(claim['pickup_attempt_mean_range_printed'] == [f'{v:.0f}' for v in ranges['pickup_attempt_mean_range']], 'replay:n6_printed_attempts')
    check(claim['pickup_drop_share_percent_printed'] == [f'{100*v:.0f}' for v in ranges['pickup_drop_action_share_range_from_rounded_inputs']], 'replay:n6_printed_shares')
    for i,name in enumerate(['explore','grasp','open']):
        vals = [x['mean_need'][i] for x in selected.values()]
        check(claim['mean_need_ranges'][name] == [min(vals),max(vals)], 'replay:n6_needs:' + name)
    for path, sha in replay['source_sha256'].items():
        check(digest(ROOT / path) == sha, 'replay:source_hash:' + path)
    findings['replay'] = dict(families=len(families), older_initial_exposures=initial, older_active_exposures=active,
                               farming_episodes=fc, tamper_episodes=tc, simple_family_episodes=simple,
                               all_historical_episode_count=None, n6_selected_policies=len(selected), n6_ranges=ranges)
    findings['table2'] = {'displayed_values_verified': displayed, 'stored_policy_means_verified': 7 * len(tamper['policies'])}

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        failures.append({'check':'checker_exception','type':type(exc).__name__,'detail':str(exc)})
    result = {'status':'pass' if not failures else 'fail', 'checks':sum(counts.values()), 'checks_by_area':dict(counts),
              'failures':failures, 'independently_reconstructed':findings,
              'scope':'Existing files only; no environment creation, checkpoint execution, or training.',
              'missing_count_policy':'Unknown event counts remain null; structural exposure is not a count of realized missed events.'}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'number-check.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(failures))
