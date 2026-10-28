#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a7cb164e-db25-4428-aa9f-165f0c285814' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a7cb164e-db25-4428-aa9f-165f0c285814/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/97cf0da326008c76c6a435572a1e82492394cd7533c69c2c04a76b87fc3881b7.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
