#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/78c44406-6e63-466f-b309-8dfb82bfe663' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/78c44406-6e63-466f-b309-8dfb82bfe663/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/e4fc38797095d2a07359f8be933d2a60826f06e4bca183a39e46de5ba1628970.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
