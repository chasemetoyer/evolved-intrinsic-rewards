#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/135d1475-e4cf-4a4f-8ca2-be0d84c1d409' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/135d1475-e4cf-4a4f-8ca2-be0d84c1d409/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/7ea6759c6ef64839acd167486f0b7a8d5b74a3587a197bccdfab55904a6c53f8.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
