#!/bin/bash
# Round 5 launcher (detached). Runs the A/B experiments one at a time, then the Part C calibration attempts in the
# pre-registered order (candidate outer, budget inner: 2M then 5M), stopping at the first attempt where >= 4 of 5
# calibration seeds solve. Writes calibration-selection.json. Never launches Part C test runs (those need the
# second lock). Safe to re-run: skips experiments that already have a run.
P=1afd0818-4752-445e-80b2-5e37e0cc6797
DIR="$(cd "$(dirname "$0")" && pwd)"; LOG="$DIR/launch.log"; IDS="$DIR/node-ids.json"
inflight() { orx runs $P 2>/dev/null | awk '$1 ~ /^[0-9a-f-]{36}$/ && $2 !~ /^(done|failed|cancelled|canceled)$/' | grep -q .; }
node() { python3 -c "import json,sys;print(json.load(open('$IDS'))[sys.argv[1]])" "$1"; }
run_node() {  # $1 = key in node-ids.json; prints the run id
  local e; e=$(node "$1")
  local last; last=$(orx exp status $e 2>/dev/null | grep "last run" )
  if ! echo "$last" | grep -q "last run: —"; then echo "$(date -u +%FT%TZ) skip $1 ($e already has a run)" >> "$LOG"; echo "$last" | grep -oE '[0-9a-f-]{36}' | head -1; return; fi
  while inflight; do sleep 60; done
  echo "$(date -u +%FT%TZ) launching $1 ($e)" >> "$LOG"
  local out; out=$(orx exp run $e --backend local 2>&1); echo "$out" | grep -E "run  |rror" >> "$LOG"
  local rid; rid=$(echo "$out" | grep -oE 'run  [0-9a-f-]{36}' | awk '{print $2}')
  until ! orx exp status $e 2>/dev/null | grep -q "last run: —"; do sleep 10; done
  echo "$rid"
}
wait_run() { while orx runs $P 2>/dev/null | awk -v r="$1" '$1 == r && $2 !~ /^(done|failed|cancelled|canceled)$/' | grep -q .; do sleep 60; done; }
for k in A1 A2 B9 B10 B11; do run_node $k > /dev/null; sleep 30; done
while inflight; do sleep 60; done
echo "$(date -u +%FT%TZ) Parts A and B finished; starting Part C calibration" >> "$LOG"
for cand in KeyCorridorS3R1 UnlockPickup KeyCorridorS3R2; do
  for budget in 2M 5M; do
    rid=$(run_node "cal-$cand-$budget"); wait_run "$rid"
    n=$(python3 - "$rid" <<'PYEOF'
import json, sys, glob, os
base = os.path.expanduser(f"~/.local/share/openresearch/local-runs/{sys.argv[1]}/repo/results")
k = 0
for f in glob.glob(base + "/seed*/metrics.jsonl"):
    rows = [json.loads(l) for l in open(f)]
    last = rows[-max(1, len(rows) // 10):]
    k += (sum(r.get("train/success", 0.0) for r in last) / len(last)) >= 0.9
print(k)
PYEOF
)
    echo "$(date -u +%FT%TZ) calibration $cand $budget run $rid: $n/5 seeds solve" >> "$LOG"
    if [ "$n" -ge 4 ]; then
      echo "{\"env\": \"MiniGrid-$cand-v0\", \"budget\": \"$budget\", \"run\": \"$rid\", \"solves\": $n, \"time\": \"$(date -u +%FT%TZ)\"}" > "$DIR/calibration-selection.json"
      echo "$(date -u +%FT%TZ) SELECTED $cand $budget; stop. Next: second lock (amendment), then C1-C6." >> "$LOG"; exit 0
    fi
  done
done
echo "{\"env\": null, \"note\": \"no candidate qualified; Part C runs skipped\", \"time\": \"$(date -u +%FT%TZ)\"}" > "$DIR/calibration-selection.json"
echo "$(date -u +%FT%TZ) no candidate qualified; Part C test runs skipped" >> "$LOG"
