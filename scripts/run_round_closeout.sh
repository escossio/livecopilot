#!/usr/bin/env bash
set -euo pipefail

PROJECT="livecopilot"
SESSION_ID=""
ACTOR="codex"
RUN_TYPE="implementation"
SUMMARY_SHORT=""
SUMMARY_FULL=""
CHECKPOINT_PATH=""
FACTS_FILE=""

ENABLE_HOOK="${LIVECOPILOT_CONTINUITY_HOOK:-0}"
FORCE_DISABLE=0
ENABLE_EMBEDDING_MAINTENANCE="${LIVECOPILOT_CONTINUITY_EMBEDDING_MAINTENANCE:-0}"
FORCE_DISABLE_EMBEDDING_MAINTENANCE=0
EMBEDDING_MAINT_LIMIT="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_LIMIT:-200}"
EMBEDDING_MAINT_BATCH_SIZE="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_BATCH_SIZE:-10}"
EMBEDDING_MAINT_MODEL="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_MODEL:-${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}}"

SNAPSHOT_TXT="docs/continuity/bootstrap/latest_snapshot.txt"
SNAPSHOT_JSON="docs/continuity/bootstrap/latest_snapshot.json"
FINAL_CONTEXT="docs/continuity/opening_context/latest_new_chat_context.txt"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --session-id) SESSION_ID="${2:-}"; shift 2 ;;
    --actor) ACTOR="${2:-}"; shift 2 ;;
    --run-type) RUN_TYPE="${2:-}"; shift 2 ;;
    --summary-short) SUMMARY_SHORT="${2:-}"; shift 2 ;;
    --summary-full) SUMMARY_FULL="${2:-}"; shift 2 ;;
    --checkpoint-path) CHECKPOINT_PATH="${2:-}"; shift 2 ;;
    --facts-file) FACTS_FILE="${2:-}"; shift 2 ;;
    --enable-continuity-hook) ENABLE_HOOK=1; shift ;;
    --disable-continuity-hook) FORCE_DISABLE=1; shift ;;
    --enable-embedding-maintenance) ENABLE_EMBEDDING_MAINTENANCE=1; shift ;;
    --disable-embedding-maintenance) FORCE_DISABLE_EMBEDDING_MAINTENANCE=1; shift ;;
    --embedding-maintenance-limit) EMBEDDING_MAINT_LIMIT="${2:-}"; shift 2 ;;
    --embedding-maintenance-batch-size) EMBEDDING_MAINT_BATCH_SIZE="${2:-}"; shift 2 ;;
    --embedding-maintenance-model) EMBEDDING_MAINT_MODEL="${2:-}"; shift 2 ;;
    *)
      echo "Argumento invalido: $1" >&2
      echo "Uso: $0 [--enable-continuity-hook] [--disable-continuity-hook] [--enable-embedding-maintenance] [--disable-embedding-maintenance] [--embedding-maintenance-limit N] [--embedding-maintenance-batch-size N] [--embedding-maintenance-model MODEL] --session-id ... --summary-short ... --summary-full ... --checkpoint-path ... [--facts-file ...]" >&2
      exit 1
      ;;
  esac
done

if [[ "$FORCE_DISABLE" -eq 1 ]]; then
  ENABLE_HOOK=0
fi
if [[ "$FORCE_DISABLE_EMBEDDING_MAINTENANCE" -eq 1 ]]; then
  ENABLE_EMBEDDING_MAINTENANCE=0
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$ENABLE_HOOK" != "1" ]]; then
  echo "[round-closeout] continuity hook desabilitado; encerramento sem cadeia de continuidade."
  exit 0
fi

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

if [[ -z "$SESSION_ID" || -z "$SUMMARY_SHORT" || -z "$SUMMARY_FULL" || -z "$CHECKPOINT_PATH" ]]; then
  echo "Com hook habilitado, informe: --session-id --summary-short --summary-full --checkpoint-path" >&2
  exit 1
fi

capture_cmd=(
  ./scripts/run_continuity_capture.sh
  --session-id "$SESSION_ID"
  --actor "$ACTOR"
  --run-type "$RUN_TYPE"
  --summary-short "$SUMMARY_SHORT"
  --summary-full "$SUMMARY_FULL"
  --checkpoint-path "$CHECKPOINT_PATH"
)

if [[ -n "$FACTS_FILE" ]]; then
  capture_cmd+=(--facts-file "$FACTS_FILE")
fi

run_direct_postgres_ingest() {
  # Build local + ingest direto via DSN explícito.
  local -a build_cmd=(
    "$PYTHON_BIN" scripts/continuity_build_payload.py
    --project-name "$PROJECT"
    --session-id "$SESSION_ID"
    --actor "$ACTOR"
    --run-type "$RUN_TYPE"
    --summary-short "$SUMMARY_SHORT"
    --summary-full "$SUMMARY_FULL"
    --checkpoint-path "$CHECKPOINT_PATH"
    --output-path-only
  )
  if [[ -n "$FACTS_FILE" ]]; then
    build_cmd+=(--facts-file "$FACTS_FILE")
  fi

  local payload_path
  if ! payload_path="$("${build_cmd[@]}")"; then
    echo "Falha ao gerar payload canônico para ingest direto postgres" >&2
    return 1
  fi

  local -a ingest_cmd=("$PYTHON_BIN" scripts/continuity_ingest.py --input "$payload_path")
  if ! (cd "$PROJECT_ROOT" && "${ingest_cmd[@]}"); then
    echo "Falha ao ingerir continuidade com DSN explícito" >&2
    return 1
  fi
  echo "[round-closeout] ingest direto com DSN explicito aplicado."
}

if ! "${capture_cmd[@]}"; then
  echo "Falha ao executar run_continuity_capture.sh" >&2
  exit 1
fi

# Atualiza snapshot JSON (artefato bruto estruturado)
if ! ./scripts/new_chat_context.sh \
  --project "$PROJECT" \
  --format json \
  --snapshot-output "$SNAPSHOT_JSON" \
  --output /tmp/livecopilot_new_chat_context_json.tmp; then
  echo "Falha ao gerar snapshot JSON no encerramento" >&2
  exit 1
fi

# Atualiza snapshot TXT e contexto final (artefato humano)
if ! ./scripts/new_chat_context.sh \
  --project "$PROJECT" \
  --format txt \
  --snapshot-output "$SNAPSHOT_TXT" \
  --output "$FINAL_CONTEXT"; then
  echo "Falha ao gerar contexto final de novo chat no encerramento" >&2
  exit 1
fi

echo "[round-closeout] continuidade persistida e contexto de novo chat atualizado."
echo "[round-closeout] payloads: docs/continuity/payloads/"
echo "[round-closeout] snapshots: $SNAPSHOT_TXT | $SNAPSHOT_JSON"
echo "[round-closeout] contexto final: $FINAL_CONTEXT"

if [[ "$ENABLE_EMBEDDING_MAINTENANCE" == "1" ]]; then
  echo "[round-closeout] embedding maintenance habilitada; executando manutencao incremental..."
  if ! ./scripts/maintain_continuity_embeddings.sh \
    --project "$PROJECT" \
    --limit "$EMBEDDING_MAINT_LIMIT" \
    --batch-size "$EMBEDDING_MAINT_BATCH_SIZE" \
    --model "$EMBEDDING_MAINT_MODEL"; then
    echo "Falha na manutencao de embeddings da continuidade" >&2
    exit 1
  fi
else
  echo "[round-closeout] embedding maintenance desabilitada; sem manutencao automatica."
fi
