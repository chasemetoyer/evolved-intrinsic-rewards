#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/18023803-f34a-4d1a-883b-d6e5d0d92e15' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/18023803-f34a-4d1a-883b-d6e5d0d92e15/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/8320d5de23ad7c94309b0681ee4125cb271d27420f3692ccb2a73769c59b8630.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
