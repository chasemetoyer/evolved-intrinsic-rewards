#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/eb8555bd-afbf-484d-b1fc-30faa29648b6' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/eb8555bd-afbf-484d-b1fc-30faa29648b6/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/33cab97e246211ac6413424e9b0e119097da78d62329ab17249437f61e78234d.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
