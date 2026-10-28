#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/35c840cd-2776-4817-9ac0-1f21f93c5e4d' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/35c840cd-2776-4817-9ac0-1f21f93c5e4d/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/17a5e423d95f6421e4c50e69a7bee92d84edb3b231beb7b85b2b684b96786ec0.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
