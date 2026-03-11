#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=.venv/bin/python
else
  echo "Nenhum interpretador Python compatível encontrado." >&2
  exit 1
fi

"$PYTHON_BIN" -m app.services.curated_sources "$@"
