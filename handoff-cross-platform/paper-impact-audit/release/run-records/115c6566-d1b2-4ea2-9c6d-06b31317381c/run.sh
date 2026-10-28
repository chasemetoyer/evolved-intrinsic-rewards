#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/115c6566-d1b2-4ea2-9c6d-06b31317381c' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/115c6566-d1b2-4ea2-9c6d-06b31317381c/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/34f5e4b6acd5acb860d1f9fbb412c59c30d9eeb49b230cb02824f566e59ed952.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
