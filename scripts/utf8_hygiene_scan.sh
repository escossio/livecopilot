#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT_DIR/scripts/with-semantic-env.sh" "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/utf8_hygiene_scan.py" "$@"
