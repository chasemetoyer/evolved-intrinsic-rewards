#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/bced806e-eccb-434b-be50-ad91f57a9dfb' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/bced806e-eccb-434b-be50-ad91f57a9dfb/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/1bf37e014e2104dfc5dbed127ee73816ef5f2d2068ea3eeb03a4aa4c6814c82d.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
