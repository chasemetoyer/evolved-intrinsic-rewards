#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/06112c45-bbb1-483d-b67f-8d5f101f9548' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/06112c45-bbb1-483d-b67f-8d5f101f9548/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/c2ae5388be569872806c0a7edf5d5936573f02e4bc5d931328c35fce4c2e0b98.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
