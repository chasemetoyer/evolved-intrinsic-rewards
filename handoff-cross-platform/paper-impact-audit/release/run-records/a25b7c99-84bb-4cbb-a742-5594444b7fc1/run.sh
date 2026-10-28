#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a25b7c99-84bb-4cbb-a742-5594444b7fc1' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a25b7c99-84bb-4cbb-a742-5594444b7fc1/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/b07214e7a812ffc44f083af94669cadf13eb563d18c8068e1d688f14d1e330b2.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
