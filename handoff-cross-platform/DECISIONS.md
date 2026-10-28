# Shared decisions and authorizations

## Goal and stopping boundary

Complete Stage 1 of evolved-intrinsic-rewards: private repository, reused PPO,
generic signed reward, unit verification, Modal packaging, determinism check,
descriptive platform/detector checks, baseline task calibration, measured cost
projections, and an unlocked Stage 2 outline. Stop after `stage1-report.md`, or
at the $15 spending guard with incomplete results disclosed. No evolution or
random search is authorized. Stop at stage boundaries for the user's approval.

## Paper audit and approved changes

The user requested and received the retrospective detector impact audit, then
approved the paper correction drafts and explicitly resumed Stage 1. Original
archive and manuscript were not edited. The audit and raw evidence are under
`paper-impact-audit/` and durable project artifacts. Historical missed-event
counts that cannot be recovered from retained traces remain unknown.

The user approved three separate detector verification components: bit-identical
reward arithmetic on recorded paper events; targeted corrected-detector bug
tests; and both detectors on the same recorded trajectories, reporting every
disagreement by type and count.

The user then explicitly authorized:

- Mac-versus-Modal check uses the **archived** detector and exact A1b snapshot.
- Add five corrected-detector descriptive runs with the same satiation 1/160
  DoorKey configuration, paper seeds 40–44, nominal 2M steps. Show solve counts
  and curve areas next to archived Modal and Mac; no inferential tests or
  comparative conclusions.
- The new project uses corrected detection. Final-step events count; box
  openings count; successful target pickups are excluded; attach after reset.
  These four definitions must each be flagged as an open Stage 2 decision.
- Preserve the agreed arithmetic-only reduction test using recorded paper events.

## Fixed scientific conventions

PPO and CNN are archived, with Table 10 settings and per-minibatch advantage
normalization on everywhere. Generic dynamics use the paper's actual single
clip after growth minus relief. Four needs start at .5; signed weights [-1,1],
reliefs [0,1], growth zero or [1/640,1/20]. Tamper action 6 resets all needs;
optional press cost is charged to extrinsic training reward only.

Calibration uses seeds 900–904, task-only and episodic novelty coefficient
1e-3, all seven named tasks and separate 1M/2M runs. Use the user's mechanical
selection rule and report rejected tasks. Never tune a task to make it pass.
Training curve area is the paper's arithmetic mean of logged success; solve is
final-10%-of-log-rows success >=.9. Evaluation uses a per-environment quota.
Future roles: evolution1000–1999, random3000–3999, final2000–2999. Historical
40–44 are an explicit descriptive exception, not calibration/final seeds.

## Infrastructure and evidence

All scientific workers run on Modal, one Function input per configuration/task/
seed. A local tracked controller only orchestrates and downloads results. Pinned
Python3.12.12/NumPy2.5.4 follow the archived Mac log and dependency markers, as
disclosed in the audit; the unqualified paper NumPy2.4.6 claim was incomplete.
Record all installed versions, source commits, CPU, memory, time and cost.

Hash-lock and commit/push Stage 1 registration before evidence. Keep locked
registration files immutable. Implementation repairs require timestamped,
committed/pushed amendments with replacement hashes. Scoring and interpretation
are separate; all report numbers come from scripts and independent checks.

The user requested model-independent continuity: keep this shared handoff and
source checkpoint current, allow switching between agents, and record available
usage information honestly. No provider-wide remaining quota is exposed so far.

## Additional infrastructure-repair approval

After two container-build failures, the user explicitly answered
**"Continue setup repairs within $15"**. Further infrastructure repairs and
setup attempts are authorized within the unchanged total Stage 1 cap; do not
ask again solely because those two failures occurred. Retain their history and
cost reservations. The scientific protocol and Stage 2 boundary remain fixed.
The observed build issue was Modal's injected index mirror differing from the
public PyPI index in uv.lock; an explicit build index has been prepared.

## Additional approvals, 2026-10-28 (Claude session)

The user moved the project from Astra to Claude and approved: claiming the
lease without stopping controller run 177e7cf9 or its Modal app; logging the
CPU type of every Modal container from the saved cpuinfo, including the
preempted attempt on the volume, with no worker-code changes; CLAUDE.md on
`main` and on the research branch; committing and pushing Astra's report-only
amendment and a second report-only amendment (container CPU table and the
determinism explanation).

New open Stage 2 decision: test whether forcing `ATEN_CPU_CAPABILITY=avx2` and
`MKL_CBWR=AVX2` makes seed 910 bit-identical across Zen 3 and Zen 4 containers.
If it does, use those settings in Stage 2. If not, record the CPU type for
every run and treat same-seed results as unpaired. The test is not run in
Stage 1. Exact quotes are in `approvals-log.jsonl`.

## Stage 2 decisions (2026-10-28; exact quotes in approvals-log.jsonl entries 19–23)

- **Concurrency:** about 32 Modal calls in flight, after confirming the
  account-wide limit. Modal documents 100 containers on Starter and 5,000 on Team;
  the 50 shown in the dashboard is a per-function setting. Confirmed in practice:
  32 containers ran at once.
- **Fitness budget:** nominal 2M steps.
- **Stage 2 spending cap:** $30, including the pre-lock checks.
- **Event definitions:** all four Stage 1 corrected definitions are kept.
- **Pinning test:** `ATEN_CPU_CAPABILITY=avx2`, `MKL_CBWR=AVX2` and
  `ONEDNN_MAX_CPU_ISA=AVX2` on seed 910 across Zen 3, Zen 4 and Intel.
  - Result: not bit-identical. The MKL pin was not applied on AMD; Zen 3 and Zen 4
    were identical with each other.
  - Rule: record the CPU type for every run, treat same-seed results as unpaired,
    and run unpinned.
- **Process:** review before lock.
  - The pre-lock determinism test, secret scan and pass/fail smoke tests are done.
  - The user makes the repository public before the lock.
  - Do not lock, push the lock, or launch until the user approves the review
    package.


## Approved update and takeover, 2026-10-28 (approval 24)

The user asked Codex to continue from Claude. The Stage 2 research branch is now
owned by chat_d92e34bd_codex in the worktree recorded by session-state.json;
Claude's idle worktree was detached without changing files. No compute was active.
The latest approval supersedes the older Stage 1-only and Stage 2 $30 notes:
Stage 2 cap is $35 including pre-lock checks, Stage 3 cap is $10. Keep the
3600-second deadline, 3 finalists per method and 10 re-evaluation seeds, coef 1,
50% zero-growth encoding, initial mean .5/sigma .25, raw equal fitness weights.
Run unpinned, record every CPU, compare unpaired; skip COMPATIBLE testing.
Candidate numerical failures score zero; infrastructure retries preserve input
identity; stop above 5% as defined in the updated unlocked draft.
The primary Holm m=3 family is the one held-out task, with a .05 observed mean
area difference required to call an effect meaningful. Tamper retrains with free
presses only; freeze the winner and compute P0=.25 sum effective weights before
any tamper run: P0>0 predicts collapse, otherwise noninferiority delta=.05.

NEXT GATE: implement and run the exact search-mode controller/worker-validator/
plan branch using tiny budgets and seeds>=5000. Report only PASS/FAIL. Deliver
the updated unlocked draft. The user then makes the repo public; only afterward
lock, push, verify and launch. Never create a lock in advance of a PASS.


## Registered Stage 2 search launched, 2026-10-28

This supersedes the pre-lock next-action notes above. Exact search-path smoke
7bed813b-0ebe-48f2-a725-88d8cf7d4010 is PASS. All mandatory runtime hashes match
its tested commit ae53fdd. The repository was independently observed PUBLIC.
The scientific protocol was locked at f75769211c5b05201234827325a9f2bf5a987d44,
pushed and corroborated by the GitHub receipt in commit b94171f. No new runtime
implementation was introduced by those commits.

FULL SEARCH is now tracked run 55d43a42-6cbd-493c-b74d-202f5714f064, source
b94171f2cfe10d4dc1476bcc1bafcda33d90ef59, on experiment85df77cf. All training
is on Modal; its supervised local controller only orchestrates. Do not start
a replacement controller or resubmit any recorded key. Follow the canonical
stage2-runtime-state.json, stage2-run-registry.json and shared budget.json.
The cap is35USD including pre-lock checks; the full plan has1560 training calls,
32 concurrent inputs and3600-second deadlines. Stage3 cap10USD is separate and
its execution still requires approval after the Stage2 report.

On completion reconcile logs/ledger/output hashes, write checked Stage2 results,
then STOP before Stage3. A failed or uncertain provider input must be reconciled
through its recorded call ID before any retry action. Never alter frozen inputs
or change scientific rules to improve the results. The model-independent source
checkpoint and exact next action are updated automatically.


## Read-only progress observer (approval25)

Separate dashboard process PID81939 refreshes every600seconds. Read
`stage2-dashboard.md` and `stage2-dashboard-process.json` for paths and role.
It reads only saved registry and volume ledger/results; it does not write to
Modal or the tracker. Keep it independent from running controller55d43a42.
No locked files or controller code were changed.


## Approved recovery (approval26)

User said Resume after the interruption audit and controller-restart approval request. Follow stage2-interruption/approved-recovery.md and preregistration/stage2-recovery-amendment-20261028.json. Original locked registration is unchanged; four original runtime versions are preserved in preregistration/frozen-original-stage2/ and replacements are hash-authorized.93fixture tests pass. Resume445saved scientific inputs, retry23confirmed-terminated identical inputs with all old charges retained. One tracked replacement controller only; noStage3.


## Replacement controller running after approval26

Tracked run13b2db55-d617-48f4-8c3e-78093f0be19a replaces failed55d43a42, source739b3ad32becfb55c2fcd4ce699a1aeaaba7b42d. Public amendment commit verified. Production reconciliation recovered7saved successes without retraining and marked23confirmed-terminated inputs for identical retries; allpriorchargesretained.445scientific completions now inledger, plus192pre-lock checks. Completion wake registered. ControllerPID43575; caffeinate idle-sleep inhibitorPID44276 exits withcontroller; keep lidopen andapponline. Dashboard observer81939 remains independent. Do not launch another controller. Reconcile latest ledger/logs, then checkedStage2report andSTOPbeforeStage3.
