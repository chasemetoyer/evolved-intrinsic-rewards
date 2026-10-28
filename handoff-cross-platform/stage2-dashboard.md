# Read-only Stage 2 progress dashboard

The label is **in progress, not the stage-2 report**.

- Source: `scripts/stage2_dashboard.py` and its vendored offline chart assets.
- Detached observer PID: `81939` (recorded in `stage2-dashboard-process.json`).
- Refresh interval:600seconds, measured from the start of each refresh.
- Output: `/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/stage2-progress/stage2-dashboard.html`.
- Mac project mirror: `handoff-cross-platform/stage2-progress/stage2-dashboard.html`.
- Observer log: `handoff-cross-platform/stage2-dashboard.log`.
- Runtime status and cache: artifact folder `stage2-progress/`.

Inputs are only the saved run registry and Modal volume budget ledger/results.
The only volume operations are read_file/listdir; no controller handles, provider
functions, tracking writers, volume uploads, training or locked-source edits.
Tracking metrics cannot be published read-only, so the HTML fallback is used.
The page is self-contained and reloads every10minutes; its dropdown provides
fitness, logical-run progress, spending, failures/restarts and CPU mix views.

Only complete6-run candidate fitness and complete10-candidate CMA generations
are plotted. Candidate numerical failures score0 as registered. Finalist runs
count toward1560 but do not contaminate the search fitness plot. Historical
pre-lock runs count toward Stage2 spend but not the1560 progress denominator.

Multiple saved attempts establish restarts, not why they occurred. An explicit
termination reason is needed to count a confirmed preemption. Missing causes
remain unclassified/possible preemptions, and a missing exact preemption count
is not reported as0. CPU mix counts visible container attempts, including retries.
No uncertainty or scientific transfer inference is claimed in this progress view.

If switching agents, keep the observer running. Do not restart it if the recorded
PID is alive; its separate .observer.lock prevents duplicate observers. No change
to this observer requires restarting or touching the scientific controller.
