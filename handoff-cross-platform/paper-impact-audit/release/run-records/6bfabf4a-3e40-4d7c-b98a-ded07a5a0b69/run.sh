#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/6bfabf4a-3e40-4d7c-b98a-ded07a5a0b69/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/097330db2d056a9dc4a0bfd7cb8722d0395b5c5afafa74624dbe90c95b7a02cd.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
