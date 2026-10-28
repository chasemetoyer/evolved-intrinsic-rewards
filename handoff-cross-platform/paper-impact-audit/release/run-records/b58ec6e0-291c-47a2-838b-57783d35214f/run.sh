#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/b58ec6e0-291c-47a2-838b-57783d35214f' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/b58ec6e0-291c-47a2-838b-57783d35214f/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/95713250136d454fdb96f1216bed8d387bd8741bd565eaef44f17bfcb3ee438c.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
