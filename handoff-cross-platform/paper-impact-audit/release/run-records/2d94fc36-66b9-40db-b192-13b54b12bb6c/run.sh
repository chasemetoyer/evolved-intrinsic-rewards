#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/2d94fc36-66b9-40db-b192-13b54b12bb6c' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/2d94fc36-66b9-40db-b192-13b54b12bb6c/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/f20dcce163e205245ab97cfce35eb12ec1c032f3b8fc85473a876f82e58af51e.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
