#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/2aa5ebb2-1b41-406b-8829-376d79dafec7' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/2aa5ebb2-1b41-406b-8829-376d79dafec7/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/474696c3e666da5afcdb3c769f190fb268db9e5fa1a16ab2c8b4da076b76c710.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
