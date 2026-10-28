#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/022a3e90-09c1-43dc-8c4e-3a266d1ee5d0' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/022a3e90-09c1-43dc-8c4e-3a266d1ee5d0/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/4910b59a04eea49172af02a14bf536d7507ff60d1e87f56494cd62ef30c8344f.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
