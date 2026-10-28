#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/224a7d96-a57b-451d-b33e-1e156bf74fbe' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/224a7d96-a57b-451d-b33e-1e156bf74fbe/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/4213bb16325ab6d4701f0d378947f6873b8e1db9b4f2245080eb5e12bdf3e146.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
