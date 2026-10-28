#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/fe575571-c9c9-4359-9601-01357806f84e' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/fe575571-c9c9-4359-9601-01357806f84e/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/07a4ab719c43149a53bd2ecb13763ff0ddf45b25b1c3e9fc4a0e0a8c03ec9213.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
