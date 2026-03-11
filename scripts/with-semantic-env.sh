#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=/etc/livecopilot-semantic.env
if [ ! -r "$ENV_FILE" ]; then
  echo "ERRO: sem permissao de leitura em $ENV_FILE (use sudo/root)" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# Compatibilidade com nomes usados internamente pela API
export SEMANTIC_EMBED_MODEL="${SEMANTIC_EMBED_MODEL:-${OPENAI_EMBED_MODEL:-text-embedding-3-small}}"
export DATABASE_URL="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "${DATABASE_URL}" ]]; then
  echo "ERRO: DSN ausente no ambiente canônico (${ENV_FILE}). Defina DATABASE_URL." >&2
  exit 1
fi
export SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-${DATABASE_URL}}"
export LIVECOPILOT_DB_DSN="${LIVECOPILOT_DB_DSN:-${DATABASE_URL}}"

if [ "$#" -eq 0 ]; then
  env | rg '^(OPENAI_API_KEY|OPENAI_EMBED_MODEL|DATABASE_URL|LIVECOPILOT_DB_DSN|SEMANTIC_EMBED_MODEL|SEMANTIC_PG_DSN)=' | sed -E 's/^OPENAI_API_KEY=.*/OPENAI_API_KEY=<redacted>/; s#^(DATABASE_URL=postgresql://[^:]+:)[^@]+(.*)$#\\1<redacted>\\2#'
  exit 0
fi

exec "$@"
