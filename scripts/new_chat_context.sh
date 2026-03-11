#!/usr/bin/env bash
set -euo pipefail

PROJECT="livecopilot"
FORMAT="txt"
OUTPUT="docs/continuity/opening_context/latest_new_chat_context.txt"
SNAPSHOT_OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT="${2:-}"
      shift 2
      ;;
    --snapshot-output)
      SNAPSHOT_OUTPUT="${2:-}"
      shift 2
      ;;
    --format)
      FORMAT="${2:-}"
      shift 2
      ;;
    *)
      echo "Argumento invalido: $1" >&2
      echo "Uso: $0 [--project <name>] [--output <path>] [--snapshot-output <path>] [--format txt|json]" >&2
      exit 1
      ;;
  esac
done

case "$FORMAT" in
  txt) BOOTSTRAP_FORMAT="text" ;;
  json) BOOTSTRAP_FORMAT="json" ;;
  *)
    echo "--format invalido: $FORMAT (use txt ou json)" >&2
    exit 1
    ;;
esac

if [[ -z "$SNAPSHOT_OUTPUT" ]]; then
  if [[ "$FORMAT" == "json" ]]; then
    SNAPSHOT_OUTPUT="docs/continuity/bootstrap/latest_snapshot.json"
  else
    SNAPSHOT_OUTPUT="docs/continuity/bootstrap/latest_snapshot.txt"
  fi
fi

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

ENV_FILE="/etc/livecopilot-semantic.env"
if [[ ! -r "$ENV_FILE" ]]; then
  echo "ERRO: sem acesso a $ENV_FILE (necessario para DSN canônico)." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

export DATABASE_URL="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "${DATABASE_URL}" ]]; then
  echo "ERRO: DATABASE_URL ausente em $ENV_FILE." >&2
  exit 1
fi
export SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-${DATABASE_URL}}"
export LIVECOPILOT_DB_DSN="${LIVECOPILOT_DB_DSN:-${DATABASE_URL}}"

snapshot_err_file="$(mktemp)"
cleanup() {
  rm -f "$snapshot_err_file"
}
trap cleanup EXIT

snapshot_cmd=("$PYTHON_BIN" "scripts/continuity_bootstrap_context.py" "--project" "$PROJECT" "--format" "$BOOTSTRAP_FORMAT")

SNAPSHOT_CONTENT=""
if ! SNAPSHOT_CONTENT="$(${snapshot_cmd[@]} 2>"$snapshot_err_file")"; then
  echo "Falha ao gerar snapshot." >&2
  cat "$snapshot_err_file" >&2 || true
  exit 1
fi

mkdir -p "$(dirname "$SNAPSHOT_OUTPUT")"
printf "%s\n" "$SNAPSHOT_CONTENT" > "$SNAPSHOT_OUTPUT"

mkdir -p "$(dirname "$OUTPUT")"

if [[ "$FORMAT" == "json" ]]; then
  if ! CONTEXT_SNAPSHOT_BLOCK="$("$PYTHON_BIN" "scripts/continuity_bootstrap_context.py" --project "$PROJECT" --format text 2>"$snapshot_err_file")"; then
    echo "Falha ao gerar contexto acionavel em texto." >&2
    cat "$snapshot_err_file" >&2 || true
    exit 1
  fi
else
  CONTEXT_SNAPSHOT_BLOCK="$SNAPSHOT_CONTENT"
fi

cat > "$OUTPUT" <<CONTEXT_EOF
CONTEXTO DE CONTINUIDADE DO PROJETO LIVECOPILOT

Projeto:
$PROJECT

Objetivo deste contexto:
Fornecer estado atual resumido do projeto para continuacao em novo chat, com base na camada de continuidade persistida.

Snapshot atual:
$CONTEXT_SNAPSHOT_BLOCK

Instrução operacional:
Continuar a partir deste estado, preservando decisoes ativas, pendencias abertas, riscos ativos e milestones recentes.
CONTEXT_EOF

echo "[new-chat-context] snapshot: $SNAPSHOT_OUTPUT"
echo "[new-chat-context] contexto final: $OUTPUT"
