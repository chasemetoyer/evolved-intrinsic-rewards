#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/1c7b2eda-0224-4a90-9755-26051f89f3f0' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/1c7b2eda-0224-4a90-9755-26051f89f3f0/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/3d47f6bb94c5c665cd3d35a24b84aa530ba5dd1d1e27f59728caa61822aa4725.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
