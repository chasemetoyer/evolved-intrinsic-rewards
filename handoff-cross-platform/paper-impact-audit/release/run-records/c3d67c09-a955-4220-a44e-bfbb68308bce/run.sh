#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/c3d67c09-a955-4220-a44e-bfbb68308bce' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/c3d67c09-a955-4220-a44e-bfbb68308bce/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/5a9db1cfeeba4379792ca1aa7a44ff6537a6f6b58dffa5e3a87074d9761a8a30.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
