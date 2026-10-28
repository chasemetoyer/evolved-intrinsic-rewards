#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/44f45322-8c3b-4836-a7ec-fea842e96ef2' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/44f45322-8c3b-4836-a7ec-fea842e96ef2/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/5307563ec43591cec02384991c3dbca95566db85590d9893c144a8150420cb27.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
