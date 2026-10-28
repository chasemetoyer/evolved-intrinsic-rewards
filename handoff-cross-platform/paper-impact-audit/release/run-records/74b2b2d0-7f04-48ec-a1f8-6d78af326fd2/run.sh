#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/74b2b2d0-7f04-48ec-a1f8-6d78af326fd2' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/74b2b2d0-7f04-48ec-a1f8-6d78af326fd2/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/c0602746276466602abbe6da106ac08ac519b52c1aac10553a1ca8c5b14ac6f1.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
