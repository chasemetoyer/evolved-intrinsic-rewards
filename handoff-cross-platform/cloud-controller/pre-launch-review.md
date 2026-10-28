# Modal controller migration: pre-launch review gate

No Modal verification run or training restart has launched. The current controller is stopped. This is an infrastructure preflight, not the Stage2report.

## Authorization and budget interpretation

Approval28 authorizes one combined infrastructure amendment, a Modal-hosted controller and one restart, with no scientific changes. Removal of the runtime35USD cap is approved. The same message separately requires stopping for review if the forecast guard peak exceeds33USD. This report applies that review rule; it does not reinstate the runtime35USD cap. No new monetary cap has been invented from the user's stated120USD balance.

## Replay and duplicate prevention

The read-only Mac reconstruction passes. It rebuilds CMA-ES from the saved fitness evidence using the frozen SearchPlan/CMAReplay code. All528recorded input specifications reproduce their saved SHA256 values. All60recorded candidate vectors across generations0–5 match; the latest recorded ask panel has10vectors.492saved scientific results are available. No hypothetical unasked generation is claimed to match nonexistent records.

Dry-run ready queue: {'requires_terminal_reconciliation_before_retry': 27, 'previously_authorized_retry': 9, 'new': 552}. No completed result is scheduled again. The36intentional retries preserve registered logical input IDs but require fresh provider execution IDs; no old provider invocation is resubmitted. All remaining new inputs retain the original task/seed/genome settings. There are1068logical training inputs left in the full1560-input plan, including those36retries.

Linux/Modal replay is NOT YET VERIFIED. It must pass the same exact-spec check before any training submission. The cost-review gate was reached before launching that verification compute, so no cross-platform compatibility is assumed and no claim of laptop independence is made yet.

## Updated remaining cost projection

| Quantity | USD |
|---|---:|
| Current retained guard | 12.58599 |
| Remaining1068training inputs, measured per-task guard means | 16.72447 |
| Additional maximum32worker reservations | 2.05428 |
| Remote Sandbox, expected8hours | 1.51949 |
| Remote Sandbox, protective12-hour reservation | 2.27923 |
| Verification/setup allowance | 0.10000 |
| Nominal guard peak | 32.98424 |
| Conservative guard peak used for launch gate | 33.74398 |

The remote-controller forecast uses an envelope of1physical CPU core and2GiB for12hours, enough timeout margin over the user's approximate8hours. This is a planning envelope, not a provisioned or measured resource limit. Modal Sandboxes currently use non-preemptible rates (CPU0.00003942USD/core-second and memory0.00000667USD/GiB-second), distinct from the training Function prices. Rates verified2026-10-28 at https://modal.com/pricing and https://modal.com/docs/guide/sandbox-resources .

The projection retains the entire current ledger guard, including the50terminated provider-call reservations (3.20982USD), historical charges and all pending calls. It then adds future retry/training cost, controller lifetime reservation, setup allowance and the earlier conservative maximum-worker-reservation convention. No terminated charge is released or set to zero. This is a projection, not an invoice or a guarantee; actual controller usage and complete billing still need validation.

GATE: STOP. The conservative33.74398USD peak exceeds the explicit33USD pre-launch review threshold. Runtime-cap removal is already approved; the remaining question is whether this separate review threshold is also waived/approved for this forecast. No launch happens until that is settled.

## Reporting and execution requirements carried forward

The Stage2report must enumerate both controller interruptions, every physical terminated attempt and retry, CPU metadata and cost evidence. The preliminary terminated-provider-calls.csv lists50distinct terminated calls; per-attempt rows must be expanded from saved volume metadata in the final audit. Actual costs missing from abruptly terminated containers remain unknown, alongside retained guard charges; they must not be fabricated or silently reported as zero.

If launch is approved after this gate, configure sufficient remote timeout, persist state on the Modal volume, preserve exact replay checks, and allow only the authorized single search restart. If the controller stops again, report without restarting. After successful remote startup, a real laptop-closed observation is still needed before claiming that check passed. Stage3 remains unauthorized.

Reproduction: scripts/stage2_cloud_preflight.py and scripts/stage2_remaining_projection.py; JSON evidence in this folder. No trainer was imported or submitted by the replay script.
