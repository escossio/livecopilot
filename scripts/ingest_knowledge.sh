#!/usr/bin/env bash
set -euo pipefail

# Wrapper do pipeline canonico.
# Aceita argumentos do módulo Python, incluindo filtros seletivos:
#   --source-prefix continuity_docs_selected/
#   --source-prefix terraform_docs_selected_incremental/
#   --dry-run
#   --semantic-persist --list-targets

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=.venv/bin/python
else
  echo "Nenhum interpretador Python compatível encontrado." >&2
  exit 1
fi

"$PYTHON_BIN" -m app.services.knowledge_ingest "$@"
