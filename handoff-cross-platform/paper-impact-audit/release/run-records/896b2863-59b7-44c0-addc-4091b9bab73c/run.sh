#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/896b2863-59b7-44c0-addc-4091b9bab73c' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/896b2863-59b7-44c0-addc-4091b9bab73c/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/a249ef36f2c54df8d45ec087896153879d5732660b3b60b6ff4a384b4c460599.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
