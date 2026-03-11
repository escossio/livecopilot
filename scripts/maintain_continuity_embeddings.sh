#!/usr/bin/env bash
set -euo pipefail

PROJECT="livecopilot"
LIMIT="200"
BATCH_SIZE="10"
MODEL="${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}"
DRY_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --limit) LIMIT="${2:-}"; shift 2 ;;
    --batch-size) BATCH_SIZE="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --dry-run-only) DRY_ONLY=1; shift ;;
    *)
      echo "Argumento invalido: $1" >&2
      echo "Uso: $0 [--project livecopilot] [--limit 200] [--batch-size 10] [--model text-embedding-3-small] [--dry-run-only]" >&2
      exit 1
      ;;
  esac
done

if [[ ! -r /etc/livecopilot-semantic.env ]]; then
  echo "ERRO: sem acesso a /etc/livecopilot-semantic.env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source /etc/livecopilot-semantic.env
set +a

EMBED_MODEL="${MODEL:-${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}}"
PG_DSN="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "$PG_DSN" ]]; then
  echo "ERRO: DATABASE_URL ausente em /etc/livecopilot-semantic.env" >&2
  exit 1
fi
export DATABASE_URL="$PG_DSN"
export SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-$PG_DSN}"
export LIVECOPILOT_DB_DSN="${LIVECOPILOT_DB_DSN:-$PG_DSN}"

run_backfill() {
  local extra_flag="${1:-}"
  env \
    OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    SEMANTIC_EMBED_MODEL="$EMBED_MODEL" \
    DATABASE_URL="$PG_DSN" \
    SEMANTIC_PG_DSN="$PG_DSN" \
    ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
    --project "$PROJECT" \
    --limit "$LIMIT" \
    --batch-size "$BATCH_SIZE" \
    --format text \
    ${extra_flag}
}

echo "[maintain-embeddings] dry-run inicial"
run_backfill "--dry-run"

if [[ "$DRY_ONLY" -eq 1 ]]; then
  exit 0
fi

echo "[maintain-embeddings] preenchimento incremental"
run_backfill ""

echo "[maintain-embeddings] contagem final"
psql "$PG_DSN" -c "SELECT COUNT(*) AS total_chunks, COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS with_embedding, COUNT(*) FILTER (WHERE embedding IS NULL) AS missing_embedding FROM project_memory_chunks;"
