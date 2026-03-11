#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH=.

python3 -m app.services.gap_priority_cli "$@"
