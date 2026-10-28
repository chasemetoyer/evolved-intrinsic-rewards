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
