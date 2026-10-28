#!/bin/sh
# Fixed tracked run contract. The controller is local; every training job is a
# separate Modal Function. Credentials must already be configured externally.
set -eu
test -n "${ORX_RUN_ID:-}" || { echo 'Start through the project experiment runner.' >&2; exit 2; }
test -n "${ORX_COMMIT:-}" || { echo 'A recorded source commit is required.' >&2; exit 2; }
uv run --locked python -m stage1.modal_app
