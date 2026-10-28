#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/ff8134b3-6be3-4be1-af8d-93025bacc3ff' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/ff8134b3-6be3-4be1-af8d-93025bacc3ff/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/b5294dc9c31920477e1960e88708fd85c12ed008eb4b94baffe459439fbfa490.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
