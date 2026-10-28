#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/07653362-50c4-4b7a-9506-2c0428496fba' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/07653362-50c4-4b7a-9506-2c0428496fba/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/4b441a0639ecf50058d87c110383915577851b33c9e2f7ce7b2de57765a48208.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
