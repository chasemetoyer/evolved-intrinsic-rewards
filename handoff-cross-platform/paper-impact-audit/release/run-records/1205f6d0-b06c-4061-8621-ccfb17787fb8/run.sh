#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/1205f6d0-b06c-4061-8621-ccfb17787fb8' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/1205f6d0-b06c-4061-8621-ccfb17787fb8/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/e29bdfad8f2afb366671b612169bb36bb66464d2b14240634ea2a0af80f2bbe1.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
