#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
ENV_FILE="/etc/livecopilot-semantic.env"

if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "Nenhum interpretador Python compativel encontrado." >&2
    exit 1
  fi
fi

if [[ ! -r "$ENV_FILE" ]]; then
  echo "ERRO: sem acesso a $ENV_FILE (necessario para semantic/hybrid com OPENAI_API_KEY)." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

export SEMANTIC_EMBED_MODEL="${SEMANTIC_EMBED_MODEL:-${OPENAI_EMBED_MODEL:-text-embedding-3-small}}"
export DATABASE_URL="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "${DATABASE_URL}" ]]; then
  echo "ERRO: DATABASE_URL ausente em $ENV_FILE." >&2
  exit 1
fi
export SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-${DATABASE_URL}}"
export LIVECOPILOT_DB_DSN="${LIVECOPILOT_DB_DSN:-${DATABASE_URL}}"

cd "$PROJECT_ROOT"

exec "$PYTHON_BIN" scripts/project_brain_query.py "$@"
