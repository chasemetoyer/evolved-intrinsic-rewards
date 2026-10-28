#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/af4373da-8be6-4a69-aa61-404ce37103d1' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/af4373da-8be6-4a69-aa61-404ce37103d1/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/7fa254dfeaf78392f4a64c1145d2f15572d510586a61d67c9e301fdad1d978e9.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
