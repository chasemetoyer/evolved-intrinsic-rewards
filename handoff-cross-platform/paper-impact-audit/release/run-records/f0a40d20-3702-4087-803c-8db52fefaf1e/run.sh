#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/f0a40d20-3702-4087-803c-8db52fefaf1e' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/f0a40d20-3702-4087-803c-8db52fefaf1e/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/f4603c39424a7ed28a851902b5e4d572ebd9f98a1023040d86165b0badf1a40b.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
