# Second Stage 2 controller interruption

This is an infrastructure audit, not the Stage 2 report. No scientific comparison or winner is reported.

## Verified cause

Run `13b2db55-d617-48f4-8c3e-78093f0be19a` exited after 37m44s. The traceback ends with modal.exception.ConnectionError: Deadline exceeded from FunctionGetOutputs, through ModalBackend.poll -> FunctionCall.get(timeout=0). The scheduler then canceled outstanding inputs and marked them uncertain. This was a polling transport error, distinct from the earlier saved-file DNS download error. The first repair added bounded retries for downloads but left result polling unprotected. That incomplete transport coverage is an implementation miss. The log does not establish whether the Mac, local network or provider caused the timeout, and does not establish laptop sleep.

## Preserved work and unresolved inputs

Saved volume ledger at 2026-10-28T20:24:24Z:

- 488scientific inputs complete out of1560;192additional pre-lock inputs complete.
- 31scientific inputs uncertain after this stop: read-only call graphs show4 SUCCESS and27 TERMINATED.
- The 4successes have durable completion markers with ledger-matching identity/specification hashes; all marker-listed spec, metrics, summary, usage and outcome files were hash-checked when present and matched. They are recoverable without retraining. They remain uncertain in the untouched authoritative ledger;492is a recoverable total, not a reconciled ledger count.
- 9 inputs remain retry_pending from the first approved recovery. Their old provider handles remainTERMINATED and they have no durable completion markers. These were not newly canceled by this controller stop.
- In total the read-only audit queried40 unresolved handles:4 SUCCESS,36 TERMINATED; none remained active. No result collection, submission, cancellation, ledger mutation or controller restart was performed by this audit.
- The prior recovery did retry 14 of the original 23 terminated inputs before this stop. Their old provider records and full charges are preserved in infrastructure_history. No history entries were deleted.

Guard:$12.58599429114390/$35. Saved measured completed-call compute:$7.01460373055692. Last saved Modal complete-hour billing:$7.10709246. These have different coverage, are not additive, and are not a final invoice. Reservations for uncertain/pending inputs and all 14 historical canceled-call charges remain in the guard. Partial attempt use or delayed billing must not be discarded.

The amended registration gate passes, and all 41 original registered input versions remain intact (37 unchanged live paths and 4 preserved original runtime copies). No runtime or scientific file changed during this audit. Controller43575 and its idle-sleep inhibitor44276 have exited; the independent read-only observer46043 remains running.

## Concrete next repair for review

Keep completed outputs, all old call IDs, costs and the existing optimizer/seed/input specifications. Reconcile these 31 new uncertain calls using exact provider terminal states and output hashes, recovering 4 successes without retraining and preserving the 9 already-authorized pending retries. Retain full canceled-attempt charges before authorizing identical-input retries for the 27 newly terminated inputs.

Add bounded handling of explicitly classified transient transport failures to result polling on the SAME call handle, with backoff and the existing absolute deadline enforced; do not swallow candidate/training errors or extend a training deadline. Cover ledger-upload and other controller network boundaries as well as downloads. A failure during submission remains uncertain and requires reconciliation; it must never trigger a blind duplicate spawn. Unknown errors fail closed. Retain original runtime versions and record replacement hashes in a new timestamped amendment, committed and pushed before use. Fixture tests must exercise transport-failure-then-recovery on polling and persistence, exhaustions, unchanged call identity, retained costs, preserved deadline and refusal of unrelated uncertain calls. Then one tracked restart may proceed only with approval.

No third controller has been launched. Approval26 authorized one replacement; it has been used. The experiment-tree skill also requires asking the user after two consecutive infrastructure-failed runs before another repair run. Stage3 remains unauthorized.

Evidence files in this folder: interruption-audit.json, ledger-snapshot.json, failure-log-excerpt.txt, registered-input-verification.json, audit.py.
