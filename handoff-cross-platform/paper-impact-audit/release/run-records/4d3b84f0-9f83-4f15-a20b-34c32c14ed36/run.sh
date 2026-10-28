#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/4d3b84f0-9f83-4f15-a20b-34c32c14ed36' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/4d3b84f0-9f83-4f15-a20b-34c32c14ed36/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/44f7ea8daafe479d2a24b06aff227cbb22a2afcbe3c968a4e4ea5f036554fb20.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
