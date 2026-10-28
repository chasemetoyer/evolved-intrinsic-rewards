#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/7a364fed-a875-4d3d-a366-21a162be994d' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/7a364fed-a875-4d3d-a366-21a162be994d/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/c61e9144cc4192d19e985656578c5f749b97f427a4977e1bf8a722ed96fdaefb.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
