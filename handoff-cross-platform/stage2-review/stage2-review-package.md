# Stage 2 updated review — exact search path PASS

Pre-lock review snapshot. The scientific registration is not locked by this
document. The approved implementation has passed the exact-path rehearsal.

## Exact search-mode smoke

**PASS.** Tracked run `7bed813b-0ebe-48f2-a725-88d8cf7d4010`, source `ae53fdd64abb734f20f3d4f5062c4ba2660573b3`.
The real search-mode controller, worker validator and plan wiring executed with
tiny budgets and seeds >=5000. Retained-output verification passed and its
receipt binds every mandatory runtime hash. Smoke learned performance, candidate
fitness and winner parameters are deliberately not reported.

[Pass/fail receipt](search-mode-smoke-result.json) ·
[Updated unlocked draft](stage2-preregistration-draft.md) ·
[Local safety checks](search-path-local-tests.xml).

## Current spending — separate quantities

| Quantity | USD |
|---|---:|
| Stage 2 budget guard, including allowance | 1.1377 |
| Measured function compute estimate | 0.1786 |
| Modal-reported complete billing intervals | 0.1689 |
| Stage 2 approved cap | 35.00 |
| Stage 3 separate approved cap | 10.00 |

Do not add the three spending figures. Recent provider charges can be absent;
none is claimed to be a final invoice. Every prior check and charge remains in
the shared Stage 2 ledger. [Exact accounting](current-spending.json).

## Refreshed unpinned projection

| Quantity | USD |
|---|---:|
| Future Stage 2 measured-compute proxy | 20.40 |
| Future Stage 2 expected-billed proxy | 21.04 |
| Stage 2 guard at end, including pre-lock work | 24.52 |
| Stage 2 conservative guard peak | 26.57 |
| Headroom below Stage 2 cap at peak | 8.43 |
| Stage 3 measured-compute proxy | 4.49 |
| Stage 3 expected-billed proxy | 4.64 |
| Stage 3 guard at end | 5.65 |
| Stage 3 conservative guard peak | 7.70 |

Stage 2 duration proxy is 10.5 hours at 32 concurrent
calls. Baseline runtime and Stage 1 lifecycle ratios proxy unrun candidates;
these estimates do not guarantee completion under either cap. Stage 3 execution
still requires the Stage 2 boundary approval. [Projection inputs and exact values](stage2-cost-projection.json).

## Approved decisions carried into the draft

- Unpinned runs; CPU logged per attempt; unpaired comparisons; exact
  cross-machine reproducibility is a limitation. No COMPATIBLE follow-up.
- 2M fitness, 3600-second call deadline, raw equal task weighting; coefficient 1;
  50% zero-growth encoding, initial mean .5, sigma .25; three finalists per
  method and ten fresh finalist seeds per training task.
- Candidate numerical failures score area zero without replacement. Infrastructure
  retries preserve the same input/call, at most three retries. Exhaustion stops
  for reconciliation. The per-plan >5% completed-logical-run failure guard is
  latched and drains active calls; its exact denominator is in the draft.
- E/R/T/N roster, descriptive fixed satiation; Holm m=3 on KeyCorridorS3R2 area.
  Meaningful comparisons also require observed mean-area gain >=.05. The primary
  transfer claim rests on one held-out task.
- Free-press tamper retraining only. Freeze the winner and compute the signed
  start payoff before tamper data: positive predicts off>on collapse; zero or
  negative predicts location-shift noninferiority with delta .05. The draft
  states the estimand and the exact conditional rule.

## Gate to launch

Deliver this draft and PASS result, corroborate that the user made the repository
public, then commit/push/verify the scientific lock and launch. The lock must
freeze exactly the exercised implementation; it may change the execution profile
data from smoke to registered but may add no new runtime code. No lock is
created by this report generator.

Earlier pre-check evidence remains available:
[CPU pinning](pinned-determinism-summary.json),
[history secret scan](secret-scan-report.md),
[incremental scan](incremental-secret-scan.json),
[old smoke mode](smoke-test-result.json).
