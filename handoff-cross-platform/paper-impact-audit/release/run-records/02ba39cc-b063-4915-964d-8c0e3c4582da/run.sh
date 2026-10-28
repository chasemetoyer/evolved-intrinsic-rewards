#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/02ba39cc-b063-4915-964d-8c0e3c4582da' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/02ba39cc-b063-4915-964d-8c0e3c4582da/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/1294638e55f651c94f775a19910f43b57d09c7b312c4b287908c7ae890707bbf.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
