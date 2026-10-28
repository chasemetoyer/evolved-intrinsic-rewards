#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/ad87a02f-7353-4a64-8c32-e981408dd774' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/ad87a02f-7353-4a64-8c32-e981408dd774/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/d375ab511ca5e9d5bc7e67fb04dfcfa71276fadfbbb734eb5e90b0f8671171f6.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
