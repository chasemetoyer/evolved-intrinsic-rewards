#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/4cac9e0a-5ab1-442f-9d25-62d625570ee0' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/4cac9e0a-5ab1-442f-9d25-62d625570ee0/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/45458c26beb98ccc7f234ffb4e8a58dae735e113ab5cabcdf9da7df5ed922065.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
