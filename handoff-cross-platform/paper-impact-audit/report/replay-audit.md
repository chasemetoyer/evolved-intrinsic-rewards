# Archived replay coverage audit

No new policy trajectories were generated. A cache exposure is an initial episode in which the detector was attached before reset; it is not an observed missed event.

| Replay family | Policies | Recorded episodes | Initial cache exposures | Open reward enabled on exposures | Saved detail |
|---|---:|---:|---:|---:|---|
| replay-growth-1-40 | 10 | Not recorded | 10 | 10 | Per-policy averages over episodes; action frequencies/mean needs rounded |
| replay-n1 | 10 | Not recorded | 10 | 10 | Per-policy averages over episodes; action frequencies/mean needs rounded |
| replay-n6 | 10 | Not recorded | 10 | 10 | Per-policy averages over episodes; action frequencies/mean needs rounded |
| replay-payonce | 10 | Not recorded | 10 | 10 | Per-policy averages over episodes; action frequencies/mean needs rounded |
| exploratory-replay-A2b | 20 | 60 | 20 | 0 | Per-policy averages over episodes; action frequencies/mean needs rounded |
| farming-policy-returns | 10 | 2000 | 0 | 0 | Per-policy, per-layout episode scalars plus policy means |
| tamper-policy-returns | 80 | 16000 | 0 | 0 | Per-policy, per-layout episode scalars plus policy means |
| bound-check | Path families | Not recorded (simple families: 4400; richer total unknown) | 0 | 0 | Aggregate per task/growth/family; richer family also retains per-layout best discounted returns |

The older replay paths expose 60 first episodes, with the open reward enabled in 40. Their exact missed door transitions and terminal pickups are not identifiable. DoorKey box-opening omissions are structurally zero because its generator creates no boxes.

The older JSON files omit the episode count. The writer's default is overridable, so it does not establish the actual denominator. The A2b report alone explicitly supplies its denominator. The two later learned-policy replay families retain per-layout episode scalars; both attach after reset and have zero initial-cache exposure.

## Numerical claim implications

- **Section 5.5, DoorKey farming description:** Paper's pickup range is computed from eligible pickup action attempts, not successful pickups. Initial-episode door cache exposure also applies to this replay. Corrected event counts, needs and returns cannot be recovered.
- **Corrections concerning pay-once and explore-only farming labels:** Replay descriptions support qualitative interpretations; aggregate attempt counts do not establish realized cycles. A2b's open need is disabled, so the stale open cache cannot alter that reward/state coordinate.
- **Section 4 check (b):** Later reset-before-attach path has no initial cache exposure. Existing scalar returns support recomputation of printed arithmetic, but not changed-detector counterfactuals or corrected-training policies.
- **Table 2, Sections 5.1 and 7:** Later reset-before-attach path has no initial cache exposure. Returns/drive/press-share table can be recomputed from retained per-layout scalars; repaired training outcomes remain unidentified.
- **Table 1 and Section 4 check (a):** No initial cache exposure. Stored family returns support displayed arithmetic; action/event sequences were not preserved. KeyCorridor mode deliberately excludes terminal target-ball pickups.

## Table 2 arithmetic check

Independent reconstruction from the retained per-layout arrays matches all 44 displayed numerical values. All 560 stored per-policy means agree within an absolute tolerance of 1e-12. Training press-share medians use the saved training scalar; the raw training-log audit is separate.

## N6 wording correction

The printed pickup range (137–184 per episode) is reproducible from the saved `pickups` field, but the writer counted pickup actions while not carrying. It did not test whether an object was acquired. The matching pickup/drop action-share range (48–63%) is a share of action attempts. Preserve the numerical description as attempts; successful pickup counts are unavailable.

A corrected counterfactual numerical result cannot be reconstructed from these aggregates. Saved checkpoints enable new diagnostics, but neither those diagnostics nor a corrected replay are historical training evidence.

## Sources

- `handoff-cross-platform/paper-impact-audit/dependencies/minigrid/envs/doorkey.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/paper-tables/replay.tex` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/paper-data/bound-check.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/paper-data/farming-policy-returns.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/paper-data/numbers.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/paper-data/tamper-policy-returns.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/5b13189d-614e-48c4-96b7-431838a41e1c/config.toml` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69/config.toml` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/7a364fed-a875-4d3d-a366-21a162be994d/config.toml` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/bced806e-eccb-434b-be50-ad91f57a9dfb/config.toml` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/ed5147b6-c861-48b2-b9ff-1952774d5658/config.toml` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/run-records/run-list.txt` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay-growth-1-40.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay-n1.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay-n6.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay-payonce.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/mechanism/replay_checkpoints.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/round4/exploratory-replay-A2b.json` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scored-results/round4/round4-report.md` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/bound_check.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/bound_summary.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/farming_policy_returns.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/make_numbers.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/make_tables.py` (SHA-256 in the companion JSON)
- `handoff-cross-platform/paper-impact-audit/release/scripts/tamper_policy_returns.py` (SHA-256 in the companion JSON)
- `preregistration/paper-impact-audit-lock.json` (SHA-256 in the companion JSON)
- `preregistration/paper-impact-audit.md` (SHA-256 in the companion JSON)
