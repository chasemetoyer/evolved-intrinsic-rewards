#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/2ca77641-1a17-4073-aa84-0addd68ee6c3' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/2ca77641-1a17-4073-aa84-0addd68ee6c3/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/dd5d0c43402e2cc87e81761436f2655fc1b87cfb90658dcce8f6a9417e6b2cec.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
