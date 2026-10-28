#!/usr/bin/env bash
cd '~/.local/share/openresearch/local-runs/6518a3c8-0446-45de-805c-5f5e8aa3258e' || exit 97
(
trap 'exit 143' TERM
trap 'code=$?; wait; echo "$code" > '\''~/.local/share/openresearch/local-runs/6518a3c8-0446-45de-805c-5f5e8aa3258e/exit_code'\''; exit "$code"' EXIT
set -eo pipefail; mkdir -p repo; tar -xf '~/.local/share/openresearch/source-snapshots/3a65ae5f6e513cce023adb3c4ae93d1851f5085a6c22ff66e5e21c48111dacf5.tar' -C repo; cd repo; ./run.sh
) > log 2>&1
