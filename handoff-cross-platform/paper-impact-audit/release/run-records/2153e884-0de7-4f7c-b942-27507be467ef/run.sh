#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/2153e884-0de7-4f7c-b942-27507be467ef' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/2153e884-0de7-4f7c-b942-27507be467ef/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/cfd81e72050cbe711cb6203a7a7e60080f73fc6cbba75d16e237f0a05ba054cd.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
