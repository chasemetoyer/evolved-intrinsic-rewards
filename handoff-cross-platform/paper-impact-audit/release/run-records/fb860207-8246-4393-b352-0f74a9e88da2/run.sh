#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/fb860207-8246-4393-b352-0f74a9e88da2' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/fb860207-8246-4393-b352-0f74a9e88da2/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/510f58e631a695513259233088b9947b7a963e31117f436f507d35ed0a520366.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
