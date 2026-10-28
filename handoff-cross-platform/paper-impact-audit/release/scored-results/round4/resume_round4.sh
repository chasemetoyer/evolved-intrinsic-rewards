#!/bin/bash
# Resume round 4: launch B3-B8 one at a time. Safe to re-run: skips experiments that already have a run.
# A run counts as in flight unless its status is done/failed/cancelled (fixes the round-4 launcher, which
# missed a setup status and let B1 and B2 overlap).
P=1afd0818-4752-445e-80b2-5e37e0cc6797
LOG="$(cd "$(dirname "$0")" && pwd)/launch.log"
inflight() { orx runs $P 2>/dev/null | awk '$1 ~ /^[0-9a-f-]{36}$/ && $2 !~ /^(done|failed|cancelled|canceled)$/' | grep -q .; }
for e in 1555e2da-d1f4-4fbd-ba57-edf3bbef3492 65421aab-94df-4b7b-9b40-b2f537b6cc43 05a7c021-947c-4293-a03a-03bece9a3403 \
         da7cfdd2-7405-4436-a815-648ae0e85011 0aa091bc-5240-4c0d-bbe5-2b82ff2cbfc5 dc8bd3c7-0e6a-40e6-a4c8-468a40b952d1; do
  orx exp status $e 2>/dev/null | grep -q "last run: —" || { echo "$(date -u +%FT%TZ) skip $e (already has a run)" >> "$LOG"; continue; }
  while inflight; do sleep 60; done
  echo "$(date -u +%FT%TZ) launching $e" >> "$LOG"; orx exp run $e --backend local 2>&1 | grep -E "run  |rror" >> "$LOG"
  until ! orx exp status $e 2>/dev/null | grep -q "last run: —"; do sleep 10; done   # wait until the run is registered
  sleep 30
done
while inflight; do sleep 60; done
echo "$(date -u +%FT%TZ) all launched runs finished" >> "$LOG"
