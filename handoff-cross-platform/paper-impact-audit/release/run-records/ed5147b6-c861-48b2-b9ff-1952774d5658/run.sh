#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/ed5147b6-c861-48b2-b9ff-1952774d5658' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/ed5147b6-c861-48b2-b9ff-1952774d5658/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/73b5b4a9023b310abd7a40c3e5ea5765c20368b8ed7e18d214d02b8627d0b7fc.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
