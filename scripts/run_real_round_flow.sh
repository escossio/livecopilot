#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/lab/projects/livecopilot"
SUPERVISOR_ROOT="/lab/projects/codex-supervisor"
LAST_ACTION_PATH=""
SESSION_ID=""
RUN_TYPE=""
ACTOR="codex-supervisor"
SUMMARY_SHORT=""
SUMMARY_FULL=""
CHECKPOINT_PATH=""
FACTS_FILE=""
FROM_LAST_ACTION_ONLY=0
MODE="run-once"

ENABLE_HOOK="${LIVECOPILOT_CONTINUITY_HOOK:-0}"
FORCE_DISABLE=0
ENABLE_EMBEDDING_MAINTENANCE="${LIVECOPILOT_CONTINUITY_EMBEDDING_MAINTENANCE:-0}"
FORCE_DISABLE_EMBEDDING_MAINTENANCE=0
EMBEDDING_MAINT_LIMIT="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_LIMIT:-200}"
EMBEDDING_MAINT_BATCH_SIZE="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_BATCH_SIZE:-10}"
EMBEDDING_MAINT_MODEL="${LIVECOPILOT_CONTINUITY_EMBED_MAINT_MODEL:-${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root) PROJECT_ROOT="${2:-}"; shift 2 ;;
    --supervisor-root) SUPERVISOR_ROOT="${2:-}"; shift 2 ;;
    --last-action-path) LAST_ACTION_PATH="${2:-}"; shift 2 ;;
    --from-last-action-only) FROM_LAST_ACTION_ONLY=1; shift ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --session-id) SESSION_ID="${2:-}"; shift 2 ;;
    --run-type) RUN_TYPE="${2:-}"; shift 2 ;;
    --actor) ACTOR="${2:-}"; shift 2 ;;
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
      echo "Uso: $0 [--mode run-once|continue-run] [--from-last-action-only] [--enable-continuity-hook] [--disable-continuity-hook] [--enable-embedding-maintenance] [--disable-embedding-maintenance] [--embedding-maintenance-limit N] [--embedding-maintenance-batch-size N] [--embedding-maintenance-model MODEL] [--summary-short ...] [--summary-full ...] [--facts-file ...]" >&2
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

if [[ "$MODE" != "run-once" && "$MODE" != "continue-run" ]]; then
  echo "--mode invalido: $MODE (use run-once ou continue-run)" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "project-root invalido: $PROJECT_ROOT" >&2
  exit 1
fi

if [[ -z "$LAST_ACTION_PATH" ]]; then
  LAST_ACTION_PATH="$SUPERVISOR_ROOT/state/last_action.json"
fi

if [[ ! -f "$LAST_ACTION_PATH" ]]; then
  echo "last-action nao encontrado: $LAST_ACTION_PATH" >&2
  exit 1
fi

if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  LOCAL_PY="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  LOCAL_PY="python3"
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

if [[ "$FROM_LAST_ACTION_ONLY" -eq 0 ]]; then
  if [[ -x "$SUPERVISOR_ROOT/.venv/bin/python" ]]; then
    SUP_PY="$SUPERVISOR_ROOT/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    SUP_PY="python3"
  else
    echo "Nenhum interpretador Python compativel para supervisor." >&2
    exit 1
  fi

  sup_cmd=("$SUP_PY" -m supervisor.main)
  if [[ "$MODE" == "run-once" ]]; then
    sup_cmd+=(--run-once --target-project "$PROJECT_ROOT")
  else
    sup_cmd+=(--continue-run)
  fi
  if [[ -n "$SESSION_ID" ]]; then
    sup_cmd+=(--session-id "$SESSION_ID")
  fi

  echo "[real-flow] executando supervisor (${MODE})..."
  (
    cd "$SUPERVISOR_ROOT"
    "${sup_cmd[@]}"
  )
fi

eval "$("$LOCAL_PY" - "$LAST_ACTION_PATH" "$SUMMARY_SHORT" "$SUMMARY_FULL" "$SESSION_ID" "$RUN_TYPE" "$CHECKPOINT_PATH" <<'PY'
import json
import re
import shlex
import sys
from pathlib import Path

last_action_path = Path(sys.argv[1])
summary_short_override = sys.argv[2]
summary_full_override = sys.argv[3]
session_id_override = sys.argv[4]
run_type_override = sys.argv[5]
checkpoint_override = sys.argv[6]

payload = json.loads(last_action_path.read_text(encoding="utf-8"))

final_output = str(payload.get("final_output", "") or "")
def first_meaningful_line(text: str) -> str:
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^\d+\)\s+", line):
            continue
        if line.startswith("- "):
            return line[2:].strip()
        return line
    return ""

derived_short = first_meaningful_line(final_output) or "Supervisor round closeout"
derived_short = re.sub(r"\s+", " ", derived_short).strip()[:140]
derived_full = final_output.strip() or "Rodada do supervisor concluida sem resumo detalhado."

session_id = session_id_override.strip() or str(payload.get("agent_session_id", "") or "").strip() or "agent-livecopilot"
route = str(payload.get("codex_continue_route", "") or "").strip().lower()
if route in {"continue-run", "continue_run"}:
    route = "continue_run"
elif route == "run_once":
    route = "run_once"
else:
    route = "run_once"
run_type = run_type_override.strip() or route
checkpoint_path = checkpoint_override.strip() or str(payload.get("project_journal_checkpoint_path", "") or "").strip() or "STATUS.md"
summary_short = summary_short_override.strip() or derived_short
summary_full = summary_full_override.strip() or derived_full

print(f"HOOK_SESSION_ID={shlex.quote(session_id)}")
print(f"HOOK_RUN_TYPE={shlex.quote(run_type)}")
print(f"HOOK_CHECKPOINT_PATH={shlex.quote(checkpoint_path)}")
print(f"HOOK_SUMMARY_SHORT={shlex.quote(summary_short)}")
print(f"HOOK_SUMMARY_FULL={shlex.quote(summary_full)}")
PY
)"

if [[ "$ENABLE_HOOK" != "1" ]]; then
  echo "[real-flow] rodada concluida; continuidade desabilitada (hook off)."
  exit 0
fi

closeout_cmd=(
  "$PROJECT_ROOT/scripts/run_round_closeout.sh"
  --enable-continuity-hook
  --project livecopilot
  --session-id "$HOOK_SESSION_ID"
  --actor "$ACTOR"
  --run-type "$HOOK_RUN_TYPE"
  --summary-short "$HOOK_SUMMARY_SHORT"
  --summary-full "$HOOK_SUMMARY_FULL"
  --checkpoint-path "$HOOK_CHECKPOINT_PATH"
)
if [[ -n "$FACTS_FILE" ]]; then
  closeout_cmd+=(--facts-file "$FACTS_FILE")
fi
if [[ "$ENABLE_EMBEDDING_MAINTENANCE" == "1" ]]; then
  closeout_cmd+=(
    --enable-embedding-maintenance
    --embedding-maintenance-limit "$EMBEDDING_MAINT_LIMIT"
    --embedding-maintenance-batch-size "$EMBEDDING_MAINT_BATCH_SIZE"
    --embedding-maintenance-model "$EMBEDDING_MAINT_MODEL"
  )
fi
if [[ "$FORCE_DISABLE_EMBEDDING_MAINTENANCE" -eq 1 ]]; then
  closeout_cmd+=(--disable-embedding-maintenance)
fi

echo "[real-flow] hook de continuidade habilitado; executando closeout..."
"${closeout_cmd[@]}"
