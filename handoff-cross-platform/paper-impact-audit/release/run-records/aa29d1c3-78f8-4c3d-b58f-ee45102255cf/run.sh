#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/aa29d1c3-78f8-4c3d-b58f-ee45102255cf' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/aa29d1c3-78f8-4c3d-b58f-ee45102255cf/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/afc19419916ecf562f4ae963b453545a5cae96cb9cce244a344ce8556c7ce5b2.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
