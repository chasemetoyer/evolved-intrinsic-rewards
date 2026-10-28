#!/bin/sh
# Isolated user-approved read-only diagnosis. The registered search branch is unchanged.
set -eu
test -n "${ORX_RUN_ID:-}" || { echo 'Use tracked diagnostic run' >&2; exit 2; }
test -n "${ORX_COMMIT:-}" || { echo 'Recorded diagnostic source required' >&2; exit 2; }
if [ "$(uname -s)" = Linux ]; then export STAGE2_CLOUD_CONTROLLER=1; fi
uv run --locked --default-index https://pypi.org/simple python diagnostics/spec_dump.py
