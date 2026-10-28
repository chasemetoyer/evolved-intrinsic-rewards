#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/192da9b3-39e6-4c23-9acf-956034d5adce' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/192da9b3-39e6-4c23-9acf-956034d5adce/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/53e5ce2b6ab1489852981f03d2d27ed5dccfd74f377425c0fb48adcb54419a1e.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
