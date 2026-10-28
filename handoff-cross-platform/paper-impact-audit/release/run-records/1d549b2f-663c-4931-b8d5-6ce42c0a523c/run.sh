#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/1d549b2f-663c-4931-b8d5-6ce42c0a523c' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/1d549b2f-663c-4931-b8d5-6ce42c0a523c/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/fac079f4af0025cf6a3d4fd507ca1f661114fb6adf03b5421cf1575564e36b44.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
