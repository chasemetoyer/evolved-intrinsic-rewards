#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a3199664-35fd-4cc1-a784-9a1a1df9ef4e' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a3199664-35fd-4cc1-a784-9a1a1df9ef4e/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/53d7c5cca204a8066f5ebdadc10b161f7659c8d8c029df563aa310c1a1489e68.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
