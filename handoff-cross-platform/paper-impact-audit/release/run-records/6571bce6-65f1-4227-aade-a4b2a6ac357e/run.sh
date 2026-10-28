#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/6571bce6-65f1-4227-aade-a4b2a6ac357e' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/6571bce6-65f1-4227-aade-a4b2a6ac357e/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/c174e102bed7a80f4e2e9f34175fb72ab6d25fe4959d284663bd4e680b6bc421.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
