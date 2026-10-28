#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/bd005cb8-bad4-4321-a593-e4d3fc1a39fd' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/bd005cb8-bad4-4321-a593-e4d3fc1a39fd/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/bff24b7891adb91ee37658b92c05cc2d48e1478b59b7109d3b451adcac06e185.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
