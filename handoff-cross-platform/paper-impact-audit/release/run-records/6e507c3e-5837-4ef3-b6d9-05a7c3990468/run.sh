#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/6e507c3e-5837-4ef3-b6d9-05a7c3990468' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/6e507c3e-5837-4ef3-b6d9-05a7c3990468/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/9053301615aed2bbef134e2b8d7e4cbb7e6c94edbf3a7af7835b70a1a8e4e18b.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
