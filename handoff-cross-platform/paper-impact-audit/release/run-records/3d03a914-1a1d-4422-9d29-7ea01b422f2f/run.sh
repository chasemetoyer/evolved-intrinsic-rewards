#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/3d03a914-1a1d-4422-9d29-7ea01b422f2f' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/3d03a914-1a1d-4422-9d29-7ea01b422f2f/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/7eca3d0f1caa1ea5bcebace28cbc4d18ea9a3567f5687dadcf2eab237dd618b0.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
