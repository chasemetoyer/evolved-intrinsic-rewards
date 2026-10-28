#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a6e11900-bf82-4dd1-8f07-48a8f55cffbc' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a6e11900-bf82-4dd1-8f07-48a8f55cffbc/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/7da6364b5ee95d94216cf141b75db60654f95d463fa6d34464a1eac88a7917c7.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
