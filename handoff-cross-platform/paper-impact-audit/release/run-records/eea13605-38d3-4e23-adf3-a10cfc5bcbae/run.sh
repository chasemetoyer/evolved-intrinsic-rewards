#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/eea13605-38d3-4e23-adf3-a10cfc5bcbae' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/eea13605-38d3-4e23-adf3-a10cfc5bcbae/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/9ad9383df4db2507b0597cd2492ac58a811b2ea965c3b501481be8a75420b105.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
