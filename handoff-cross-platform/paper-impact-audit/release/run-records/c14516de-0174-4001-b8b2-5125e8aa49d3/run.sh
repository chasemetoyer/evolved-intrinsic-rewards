#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/c14516de-0174-4001-b8b2-5125e8aa49d3' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/c14516de-0174-4001-b8b2-5125e8aa49d3/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/fff36592465eb3ae237837a7096a2871eef3fa0ea474ee7d10d89885e1081990.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
