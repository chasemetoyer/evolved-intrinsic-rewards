#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a8f5efc4-63e7-4a55-8020-08f7e7cff7bb' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a8f5efc4-63e7-4a55-8020-08f7e7cff7bb/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/fa5eda1e2bbdc5a73564d85fc7823d5ca9fef8315b50017c1d77e6a4f89b314a.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
