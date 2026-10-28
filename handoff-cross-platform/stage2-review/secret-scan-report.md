# Secret scan of repository history — evolved-intrinsic-rewards

Scanned 2026-10-28 ~12:46Z by claude_opus_5_5_chat_864bae6d, read-only. Scope: all 6 refs
(main 228fe48; orx/stage-1-infrastructure-and-calibration c39f0c1; orx/stage-2-pre-check-cpu-isa-pinning-determinism
c39f0c1; and their refs/remotes/github/* counterparts), 15 reachable commits, 2,532 unique blobs, all commit
messages. No refs/stash, tags or notes. No .gitleaks.toml/.gitleaksignore anywhere in history.
Commits added after this scan (Stage 2 branch) require a re-run of checks 1–3 before the repository is made public.

1. Exact-value credential check: 8 values present on this Mac (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET, the two
   ~/.modal.toml token values, `gh auth token`, HF_TOKEN, RUNPOD_API_KEY, CLAUDE_CODE_MESSAGING_TOKEN) were
   streamed against every blob and commit message in-process; values were never printed or passed as arguments.
   Result: none found anywhere.
2. Token-format regexes over all blobs (Modal ak-/as-, GitHub, AWS, PEM private keys, Hugging Face, sk-/sk-ant-):
   no matches. Sensitive filenames ever committed (.env*, .modal.toml, id_rsa, *credentials*.json, *.pem, *.key,
   *.p12, *.pfx): none.
3. gitleaks 8.30.0 (`gitleaks git --log-opts="--all --full-history" --redact`): 14 commits, 82.84 MB, 7 findings,
   all rule generic-api-key, all false positives:
   - stage1-compute-references/function-call.html and pricing.html: saved copies of Modal's public web pages
     embedding Modal's own public client-side analytics key (phc_… PostHog project key); not a user credential.
   - paper-impact-audit/release/scored-results/round5/node-ids.json (4): experiment names mapped to UUIDs.
   - paper-impact-audit/report/replay-audit.json (1): a file name mapped to its sha256.

Non-credential exposure (owner's decision before going public):
- Commit identity on 14 commits: Chase Metoyer <cmetoyerbusiness@gmail.com>; 1 commit by OpenResearch <local@openresearch.sh>.
- Email inside files: metoyer.c@northeastern.edu (location listed in the scan log); contact@farama.org (public
  package metadata).
- 592 absolute local paths containing /Users/chasemetoyer (handoff records, CLAUDE.md imports, scripts).
- Largest blobs: tamper-policy-returns.json (2.1 MB), per-run.json (1.3 MB); no binaries above 1 MB.

The repository's history is already on GitHub (remote-tracking refs equal local tips). If a credential were ever
found later, it would need rotation; rewriting history alone would not remove it from GitHub.

## Re-scan after the Stage 2 commits (2026-10-28 ~13:10Z)
Scope: 8 refs (adds orx/stage-2-pre-check-cpu-isa-pinning-determinism 613ef15 and
orx/stage-2-cma-es-vs-equal-budget-random-search-2m 45f80a3, plus their github/* copies), 17 commits, 2,557 blobs.
- Exact-value check: all 8 credential values absent from every blob and commit message.
- gitleaks 8.30.0: the same 7 generic-api-key false positives; no new findings.
- Final exact-value re-check after commit 1c714b4: 18 commits, all blobs and messages, no credential found.
- Final re-scan after commit ca8ce97 (handoff milestone copies): 19 commits, 2,567 blobs; exact-value check found no
  credential in any blob or commit message; gitleaks reports the same 7 false positives and nothing new. GitHub's live
  refs (`git ls-remote`) all point to scanned commits.
