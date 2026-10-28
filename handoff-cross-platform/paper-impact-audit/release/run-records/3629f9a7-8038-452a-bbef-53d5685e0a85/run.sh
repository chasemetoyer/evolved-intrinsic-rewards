#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/3629f9a7-8038-452a-bbef-53d5685e0a85' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/3629f9a7-8038-452a-bbef-53d5685e0a85/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/ece5e846c1c82238b5376c985f598099bc45ffb04a4c41cad247a274dc4dc005.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
