#!/usr/bin/env bash
set -euo pipefail

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=.venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

ENV_FILE="/etc/livecopilot-semantic.env"
if [[ -r "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

DATABASE_URL="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "$DATABASE_URL" ]]; then
  echo "ERRO: DSN ausente. Defina DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)." >&2
  exit 1
fi
export DATABASE_URL
export SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-$DATABASE_URL}"
export LIVECOPILOT_DB_DSN="${LIVECOPILOT_DB_DSN:-$DATABASE_URL}"

BUILD_ARGS=()
INGEST_ARGS=()
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --facts-file)
      if [[ $# -lt 2 ]]; then
        echo "--facts-file exige caminho de arquivo JSON" >&2
        exit 1
      fi
      BUILD_ARGS+=("--facts-file" "$2")
      shift 2
      ;;
    --fact-inline)
      if [[ $# -lt 2 ]]; then
        echo "--fact-inline exige valor" >&2
        exit 1
      fi
      BUILD_ARGS+=("--fact-inline" "$2")
      shift 2
      ;;
    --enable-embeddings)
      INGEST_ARGS+=("--enable-embeddings")
      shift
      ;;
    --embed-model)
      if [[ $# -lt 2 ]]; then
        echo "--embed-model exige valor" >&2
        exit 1
      fi
      INGEST_ARGS+=("--embed-model" "$2")
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      BUILD_ARGS+=("$1")
      shift
      ;;
  esac
done

PAYLOAD_PATH="$($PYTHON_BIN scripts/continuity_build_payload.py "${BUILD_ARGS[@]}" --output-path-only)"

echo "[continuity] payload gerado: ${PAYLOAD_PATH}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[continuity] dry-run ativo; ingestao nao executada"
  exit 0
fi

$PYTHON_BIN scripts/continuity_ingest.py --input "$PAYLOAD_PATH" "${INGEST_ARGS[@]}"
