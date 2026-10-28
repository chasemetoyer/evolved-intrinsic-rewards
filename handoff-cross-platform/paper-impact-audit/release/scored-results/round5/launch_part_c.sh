#!/bin/bash
# Part C test runs (after the second lock): C1-C6 one at a time. Safe to re-run: skips experiments that already have a run.
P=1afd0818-4752-445e-80b2-5e37e0cc6797
DIR="$(cd "$(dirname "$0")" && pwd)"; LOG="$DIR/launch.log"
inflight() { orx runs $P 2>/dev/null | awk '$1 ~ /^[0-9a-f-]{36}$/ && $2 !~ /^(done|failed|cancelled|canceled)$/' | grep -q .; }
for k in C1 C2 C3 C4 C5 C6; do
  e=$(python3 -c "import json,sys;print(json.load(open('$DIR/node-ids.json'))[sys.argv[1]])" $k)
  orx exp status $e 2>/dev/null | grep -q "last run: —" || { echo "$(date -u +%FT%TZ) skip $k (already has a run)" >> "$LOG"; continue; }
  while inflight; do sleep 60; done
  echo "$(date -u +%FT%TZ) launching $k ($e)" >> "$LOG"; orx exp run $e --backend local 2>&1 | grep -E "run  |rror" >> "$LOG"
  until ! orx exp status $e 2>/dev/null | grep -q "last run: —"; do sleep 10; done
  sleep 30
done
while inflight; do sleep 60; done
echo "$(date -u +%FT%TZ) Part C finished" >> "$LOG"
