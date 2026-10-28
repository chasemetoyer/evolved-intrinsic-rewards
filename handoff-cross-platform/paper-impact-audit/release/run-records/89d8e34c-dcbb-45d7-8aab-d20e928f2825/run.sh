#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/89d8e34c-dcbb-45d7-8aab-d20e928f2825' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/89d8e34c-dcbb-45d7-8aab-d20e928f2825/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/ba14b214ff997c3308e51a0e4a159b1536bcefd5223b6dd447d1917e6de87fd1.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
