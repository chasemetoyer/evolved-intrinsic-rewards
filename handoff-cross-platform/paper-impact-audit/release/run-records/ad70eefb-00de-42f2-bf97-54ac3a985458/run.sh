#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/ad70eefb-00de-42f2-bf97-54ac3a985458' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/ad70eefb-00de-42f2-bf97-54ac3a985458/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/16d8ba37ce0221aa71ae0ac60a600b9b5b21b021b08f0237805203f39561732a.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
