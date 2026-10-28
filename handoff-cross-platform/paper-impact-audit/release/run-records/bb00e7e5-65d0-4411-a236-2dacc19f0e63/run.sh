#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/bb00e7e5-65d0-4411-a236-2dacc19f0e63' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/bb00e7e5-65d0-4411-a236-2dacc19f0e63/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/d269dc1107f3c414e0a7299bf2547daeb9460f9ec52ca4f4acf3d5f1e229dd66.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
