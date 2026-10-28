#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/a97113a1-8de5-4940-a548-26275a829e4f' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/a97113a1-8de5-4940-a548-26275a829e4f/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/5c70bf56cb7ea5364a5d9400b983b7303a9aeb540a3eb7b2d8fd6871d2da2aef.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
