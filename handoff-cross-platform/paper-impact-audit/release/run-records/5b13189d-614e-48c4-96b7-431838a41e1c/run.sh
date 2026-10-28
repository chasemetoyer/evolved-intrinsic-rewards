#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/5b13189d-614e-48c4-96b7-431838a41e1c' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/5b13189d-614e-48c4-96b7-431838a41e1c/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/d6df19c6267bfba049f1565a048bd5e4d1ff9bcd4c37f8be478f45d3f1a611b4.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
