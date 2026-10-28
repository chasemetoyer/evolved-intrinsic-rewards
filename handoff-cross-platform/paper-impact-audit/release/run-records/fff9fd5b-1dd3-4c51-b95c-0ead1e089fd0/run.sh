#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/fff9fd5b-1dd3-4c51-b95c-0ead1e089fd0' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/fff9fd5b-1dd3-4c51-b95c-0ead1e089fd0/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/18c34c024507d2d9296ba4a2dff130cb0861a75376bf5056e683d46a52163b78.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
