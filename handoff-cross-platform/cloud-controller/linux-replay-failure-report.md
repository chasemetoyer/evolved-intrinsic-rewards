# Exact Linux replay failed — stopped before training

Verification run: `4e1c708d-d0da-4898-8c9d-1b9d27f9f523`. Source: `d235a13659692ca5a00ebd01c3b3de27226ecfb1`. Modal Sandbox: `sb-01M626CZV8NAHC9RHBDJYK8DWN`.

The verification exited with code 3. It submitted **zero training inputs**, started no search controller, and made no change to the shared training ledger. No further test or restart was launched.

The first recorded input failed its specification hash check: `search_cma-g00-c000-DoorKey-8x8-2000000-seed1000` (generation 1, zero-based 0, candidate 0).

- Recorded SHA256: `6984a4a2f4eedf4408a645b4986ea825c4a60e6153769374f0cd58b26ef3fa3a`
- Linux-generated SHA256: `f65304c4d5315a0ac775bb302457e86220ccf47f2b00b6f719a726f41212b639`
- Matched inputs before failure: **0**.

The receipt does not isolate the differing field or float. A platform-dependent numerical difference is a possible explanation, not an established diagnosis. This first ask precedes historical fitness consumption; Linux did not reach the historical ask/tell reconstruction. No approximate comparison or replacement candidate was used to bypass the failed gate.

An intermediate progress message incorrectly placed the mismatch in generation 2. The full log and persisted receipt establish the first-input mismatch above; the message was corrected immediately after those were read. This report follows the persisted evidence.

The earlier Mac replay still verifies all 528 saved input hashes and 60 candidate vectors. It does not establish Linux compatibility. The cloud source preserves recorded fitness values exactly, rather than fitting new formulas; the required exact-input gate still failed.

## Preserved state

Runtime identity matches the committed combined amendment. The canonical training-ledger digest is unchanged. Its authoritative state remains 488 scientific completions, 31 uncertain inputs and 9 prior pending retries. Four uncertain inputs have previously verified successful output markers: **492 scientific completions remain recoverable**. Those four were not written into the authoritative ledger because the controller never started.

Prior results, provider handles, reservations and history remain intact. The final scientific comparison is unfinished: no winner, final hypothesis test or complete Stage 2 report is claimed.

## Cost and CPU evidence

The tracked run lasted 32 seconds including setup. Replay-body wall time was 1.680 seconds. Process CPU usage was 9.25 seconds and peak RSS was 508002304 bytes. CPU time includes Python initialization before the replay body; body wall time excludes dependency installation, so these cover different intervals.

CPU: Intel, vendor `GenuineIntel`, family 6, model 85. Retain the **0.10 USD setup guard allowance** separately. Actual provider-billed cost is unknown/delayed, not zero; the allowance is not an invoice. The prior audit retains 50 terminated provider-call records and 3.20982 USD of protective charges. Final reporting must expand per-container attempts, CPUs and costs, marking unavailable measurements as unknown.

The normal log cache became unavailable after completion. The complete 2,642-byte stdout was recovered by a read-only call to the already-stopped Sandbox and is preserved in `linux-verification.log`. No command or container was restarted to recover it. The independently persisted volume receipt supplies the same failure evidence.

## Authorization and stopping rule

Approval 30 waived the 33 USD review threshold, and approval 28 removed the runtime 35 USD cap. Money did not block this verification. The prepared source removes monetary caps while retaining identity, uncertainty, duplicate, scientific-budget and deadline checks. Verification never reached the cap-removal/accounting code, so the inactive historical training ledger still records its previous policy; it was intentionally not rewritten during this read-only test.

No remote search controller is running. The laptop-closed search-continuation check is **not performed**. Running this verification remotely does not prove that the search can resume there.

Per the user's instruction, **stop and report; do not restart or run another repair**. Further execution requires new user instructions. Stage 3 remains unauthorized.

Evidence: `linux-replay-check.json`, `linux-gate-audit.json`, `linux-verification.log`, `verification-cost-record.json`, and `cloud-tests.xml` (113 local fixture checks passed; those are not proof of Linux replay).
