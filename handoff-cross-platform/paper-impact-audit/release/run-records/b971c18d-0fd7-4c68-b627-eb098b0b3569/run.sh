#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/b971c18d-0fd7-4c68-b627-eb098b0b3569' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/b971c18d-0fd7-4c68-b627-eb098b0b3569/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/ad2b6f18564ebc5843189fb773febb22256c0d1cef858b8740183c2150c4d0d8.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
