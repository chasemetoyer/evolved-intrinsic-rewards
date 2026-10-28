# Stage 2 infrastructure interruption audit

This is an interruption audit, not the Stage 2 report. No scientific comparison or winner is reported.

## Cause and effect

Tracked run `55d43a42-6cbd-493c-b74d-202f5714f064` exited after 3h26m. Its traceback shows a local DNS lookup failure for `clobber.modal-storage.com` during `hooks.sync(result)`, while downloading an already completed output. The scheduler records a completion before downloading and recording it in the search plan. Its exception cleanup cancels outstanding calls and marks them uncertain. Log cancellation messages corroborate that cleanup. The Mac could resolve the hostname again during this audit; that does not establish persistent network reliability.

## Read-only reconciliation

At 2026-10-28T18:01:30Z, the persisted volume ledger records 438 completed scientific search inputs of 1,560, plus 30 uncertain inputs. Pre-lock tests account for another 192 completed ledger entries. No candidate-caused failures were recorded among the 438 completed scientific inputs.

Read-only provider call-graph queries resolve all 30 uncertain handles: 7 SUCCESS and 23 TERMINATED. All 7 successful handles have durable complete markers whose identity and specification hash match the ledger; every listed spec, metrics, summary, usage and outcome file was hash-checked when present and matched its marker. These 7 are additional recoverable completed inputs, but remain uncertain in the untouched authoritative ledger. The 23 terminated handles have no durable completion markers. Provider termination alone is not a candidate failure and must not be scored zero.

The ledger guard is $9.89138651596235 against the $35 cap and retains reservations for unresolved calls. Saved measured compute totals $6.31409122061897, and the last saved Modal complete-interval billing is $4.99288965. These are separate estimates/snapshots, not a final invoice; partial terminated-attempt costs and delayed billing require reconciliation before releasing any reservation. There is no basis to claim the budget is exhausted.

## Isolation and dashboard

All 41 locked input hashes match. This audit used only volume reads/listing and FunctionCall.get_call_graph; it did not collect results with FunctionCall.get, submit, cancel, mutate a provider ledger, or restart anything. The controller processes have exited. Read-only dashboard PID81939 remains alive; its latest refresh at 18:01:24Z validated 438 saved completions with zero read errors. Its progress is based on the authoritative ledger and therefore does not yet include the 7 recovered-but-unreconciled outputs.

## Concrete recovery plan requiring approval

Do not blindly relaunch: Stage2Ledger.assert_can_launch rejects the uncertain entries; reconnecting a terminated call cannot resume its training. Preserve the original ledger, every call handle, all charges and all output directories. Under an explicit timestamped infrastructure amendment, reconcile the 7 successful calls from their existing outputs without rerunning; account for the 23 terminated attempts, then allow fresh provider attempts of their identical registered inputs with retained prior costs and explicit new deadlines. No candidate, seed, genome, optimizer, scoring or selection change is proposed. Add bounded output-download retries so another transient read failure does not immediately abort the full controller. Test recovery and retry behavior with lightweight fixtures before committing any replacement hashes and restarting one tracked controller. Completed inputs must never be retrained.

Approval is required because SESSION-RULES.md forbids replacing/restarting the controller without explicit user approval and the latest dashboard instruction forbids controller/locked-file changes. Any implementation repair must be a timestamped amendment, preserving every existing locked file.

Evidence: `failure-log-excerpt.txt`, `interruption-audit.json`, `ledger-snapshot.json`, `frozen-input-check.json`, and generating script `audit.py` in this folder.
