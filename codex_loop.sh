#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUEUE_DIR="$ROOT_DIR/queue"
ARCHIVE_DIR="$QUEUE_DIR/archive"
REJECTED_DIR="$QUEUE_DIR/rejected"
RESULTS_DIR="$ROOT_DIR/results"
STATE_DIR="$ROOT_DIR/state"
LOGS_DIR="$ROOT_DIR/logs"

AGENTS_FILE="$ROOT_DIR/AGENTS.md"
PROJECT_STATE_FILE="$ROOT_DIR/project_state.md"
TASK_FILE="$QUEUE_DIR/next.md"
LAST_PROMPT_FILE="$STATE_DIR/last_prompt.md"
LAST_RESULT_FILE="$STATE_DIR/last_result.md"
LAST_RESULT_JSON_FILE="$STATE_DIR/last_result.json"
APPROVAL_FLAG_FILE="$STATE_DIR/needs_approval.flag"
LOOP_STATUS_FILE="$STATE_DIR/loop_status.json"
LAST_RUN_LOG_FILE="$STATE_DIR/last_run.log"
LOCK_FILE="$STATE_DIR/loop.lock"

DRY_RUN=0
SHOW_STATUS=0
LAST_SUMMARY_ONLY=0
LAST_RESULT_JSON_ONLY=0
NEXT_ACTION_ONLY=0
RUN_NEXT_ONLY=0
RESET_TRANSIENT_STATE_ONLY=0
SUBMIT_REQUESTED=0
SUBMIT_FILE_REQUESTED=0
APPROVE_ONLY=0
REJECT_ONLY=0
TAIL_LOG_ONLY=0
DRAIN_MODE=0
PEEK_QUEUE_ONLY=0
JSON_OUTPUT=0
ENQUEUE_TEXT=""
ENQUEUE_FILE=""
SUBMIT_TEXT=""
SUBMIT_FILE=""
ENQUEUE_REQUESTED=0
ENQUEUE_FILE_REQUESTED=0
SIMULATE_OUTPUT=""
SIMULATE_OUTPUT_FILE=""
CODEX_TIMEOUT_SECONDS="${CODEX_TIMEOUT_SECONDS:-900}"
CODEX_MODEL="${CODEX_MODEL:-gpt-5.1-codex-mini}"
CODEX_CALL_PAUSE_SECONDS="${CODEX_CALL_PAUSE_SECONDS:-2}"
CODEX_MAX_RETRIES="${CODEX_MAX_RETRIES:-5}"
LAST_CODEX_CALL_TS=0
SIMULATE_DELAY_SECONDS="${SIMULATE_DELAY_SECONDS:-0}"
SIMULATE_TIMEOUT="${SIMULATE_TIMEOUT:-0}"
LOCK_HELD=0
EXECUTION_FILE_MARKER=""

RISK_TERMS=(
  "DELETE"
  "DROP"
  "TRUNCATE"
  "rm -rf"
  "migration"
  "destructive"
  "overwrite"
  "conflict"
  "failing tests"
  "policy_denied"
  "not sure"
  "need approval"
  "ambiguous"
  "manual decision"
)

usage() {
  cat <<'EOF'
Uso:
  ./codex_loop.sh [--status|--last-summary|--last-result-json|--next-action|--peek-queue] [--json]
  ./codex_loop.sh [--run-next|--drain] [--dry-run] [--simulate-output "texto"] [--simulate-output-file arquivo]
  ./codex_loop.sh [--submit "texto" | --submit-file /caminho/arquivo.md] [--dry-run]
  ./codex_loop.sh [--enqueue "texto" | --enqueue-file /caminho/arquivo.md]
  ./codex_loop.sh [--approve|--reject|--tail-log|--reset-transient-state]
  ./codex_loop.sh [--dry-run] [--simulate-output "texto"] [--simulate-output-file arquivo]

Opcoes:
  --status               Mostra o ultimo estado do loop e sai
  --last-summary         Mostra um resumo curto da ultima execucao e sai
  --last-result-json     Mostra o ultimo resultado estruturado em JSON e sai
  --next-action          Mostra a proxima acao operacional recomendada e sai
  --run-next             Executa exatamente uma proxima tarefa pendente e sai
  --submit               Enfileira uma tarefa inline e executa a proxima
  --submit-file          Enfileira de um arquivo e executa a proxima
  --reset-transient-state Limpa needs_approval.flag e stale lock orfao
  --enqueue              Enfileira uma tarefa inline em queue/next.md
  --enqueue-file         Enfileira uma tarefa a partir de um arquivo
  --approve              Remove needs_approval.flag e sai
  --reject               Move a tarefa atual para queue/rejected/ e limpa approval
  --tail-log             Mostra o caminho do ultimo log bruto salvo
  --peek-queue           Mostra um preview da fila atual sem executar nada
  --drain                Processa varias tarefas em sequencia ate parar por fila vazia ou bloqueio
  --json                 Em comandos de leitura, imprime JSON quando suportado
  --dry-run              Monta prompt e simula execucao sem chamar o Codex
  --simulate-output      Texto bruto usado na simulacao do dry-run
  --simulate-output-file Arquivo com texto bruto usado na simulacao do dry-run
  -h, --help             Mostra esta ajuda

Exemplos:
  ./codex_loop.sh --enqueue "Corrigir bug X"
  ./codex_loop.sh --peek-queue
  ./codex_loop.sh --run-next --dry-run
  ./codex_loop.sh --submit "Corrigir bug X" --dry-run
  ./codex_loop.sh --drain --dry-run
  ./codex_loop.sh --status --json
  ./codex_loop.sh --next-action
  ./codex_loop.sh --approve
  ./codex_loop.sh --reset-transient-state
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status)
        SHOW_STATUS=1
        shift
        ;;
      --last-summary)
        LAST_SUMMARY_ONLY=1
        shift
        ;;
      --last-result-json)
        LAST_RESULT_JSON_ONLY=1
        shift
        ;;
      --next-action)
        NEXT_ACTION_ONLY=1
        shift
        ;;
      --run-next)
        RUN_NEXT_ONLY=1
        shift
        ;;
      --submit)
        SUBMIT_REQUESTED=1
        SUBMIT_TEXT="${2:-}"
        shift 2
        ;;
      --submit-file)
        SUBMIT_FILE_REQUESTED=1
        SUBMIT_FILE="${2:-}"
        shift 2
        ;;
      --reset-transient-state)
        RESET_TRANSIENT_STATE_ONLY=1
        shift
        ;;
      --enqueue)
        ENQUEUE_REQUESTED=1
        ENQUEUE_TEXT="${2:-}"
        shift 2
        ;;
      --enqueue-file)
        ENQUEUE_FILE_REQUESTED=1
        ENQUEUE_FILE="${2:-}"
        shift 2
        ;;
      --approve)
        APPROVE_ONLY=1
        shift
        ;;
      --reject)
        REJECT_ONLY=1
        shift
        ;;
      --tail-log)
        TAIL_LOG_ONLY=1
        shift
        ;;
      --peek-queue)
        PEEK_QUEUE_ONLY=1
        shift
        ;;
      --drain)
        DRAIN_MODE=1
        shift
        ;;
      --json)
        JSON_OUTPUT=1
        shift
        ;;
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --simulate-output)
        SIMULATE_OUTPUT="${2:-}"
        shift 2
        ;;
      --simulate-output-file)
        SIMULATE_OUTPUT_FILE="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "[erro] opcao desconhecida: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done
}

ensure_layout() {
  mkdir -p "$QUEUE_DIR" "$ARCHIVE_DIR" "$REJECTED_DIR" "$RESULTS_DIR" "$STATE_DIR" "$LOGS_DIR"
  [[ -f "$TASK_FILE" ]] || : > "$TASK_FILE"
  [[ -f "$LAST_PROMPT_FILE" ]] || : > "$LAST_PROMPT_FILE"
  [[ -f "$LAST_RESULT_FILE" ]] || : > "$LAST_RESULT_FILE"
  [[ -f "$LAST_RUN_LOG_FILE" ]] || : > "$LAST_RUN_LOG_FILE"
  if [[ ! -f "$LOOP_STATUS_FILE" ]]; then
    write_loop_status "idle" "false" "" ""
  fi
}

current_mode_label() {
  if [[ "$RUN_NEXT_ONLY" -eq 1 ]]; then
    echo "run-next"
  elif [[ "$DRAIN_MODE" -eq 1 ]]; then
    echo "drain"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    echo "dry-run"
  else
    echo "single"
  fi
}

cleanup() {
  if [[ "$LOCK_HELD" -eq 1 ]]; then
    rm -f "$LOCK_FILE"
    LOCK_HELD=0
  fi
}

read_lock_pid() {
  if [[ ! -f "$LOCK_FILE" ]]; then
    printf ''
    return 0
  fi

  python3 - "$LOCK_FILE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8").strip() if path.exists() else ""
pid = ""
for line in text.splitlines():
    if line.startswith("pid="):
        pid = line.split("=", 1)[1].strip()
        break
if not pid and text and "\n" not in text and text.isdigit():
    pid = text
print(pid, end="")
PY
}

acquire_lock() {
  if [[ -f "$LOCK_FILE" ]]; then
    local locked_pid
    locked_pid="$(read_lock_pid)"
    if [[ -n "$locked_pid" ]] && kill -0 "$locked_pid" 2>/dev/null; then
      echo "[erro] loop ja esta em execucao (pid $locked_pid)." >&2
      exit 1
    fi
    echo "stale_lock_detected=true"
    echo "stale_pid=${locked_pid:-none}"
    echo "stale_lock_removed=true"
    rm -f "$LOCK_FILE"
  fi

  cat > "$LOCK_FILE" <<EOF
pid=$$
created_at=$(iso_timestamp)
EOF
  LOCK_HELD=1
  trap cleanup EXIT
}

iso_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

file_timestamp() {
  date -u +"%Y%m%dT%H%M%S%N"
}

trimmed_file_content() {
  local file="$1"
  python3 - "$file" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
if not path.exists():
    print("", end="")
else:
    print(path.read_text(encoding="utf-8").strip(), end="")
PY
}

previous_result_excerpt() {
  python3 - "$LAST_RESULT_FILE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
if not path.exists():
    print("", end="")
    raise SystemExit(0)

try:
    lines = path.read_text(encoding="utf-8").splitlines()
except Exception:
    print("", end="")
    raise SystemExit(0)

priority_prefixes = [
    "- status final:",
    "- comandos executados:",
    "- arquivos tocados:",
    "- o que foi alterado:",
    "- o que falta:",
    "- se precisa aprovação:",
    "- se precisa aprovacao:",
    "- se houve erro:",
]

normalized = [line.strip() for line in lines if line.strip()]
selected = []
for prefix in priority_prefixes:
    for line in normalized:
        if line.lower().startswith(prefix.lower()):
            selected.append(line)
            break

if selected:
    print("\n".join(selected[:12]), end="")
    raise SystemExit(0)

useful = []
for stripped in normalized:
    if stripped in {"# Resultado do loop", "## Saida final do Codex"}:
        continue
    if stripped.lower().startswith("- log bruto:"):
        continue
    useful.append(stripped)
    if len(useful) >= 12:
        break

print("\n".join(useful), end="")
PY
}

previous_operational_status_excerpt() {
  python3 - "$LOOP_STATUS_FILE" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
if not path.exists():
    print("", end="")
    raise SystemExit(0)

try:
    raw = path.read_text(encoding="utf-8")
except Exception:
    print("", end="")
    raise SystemExit(0)

if not raw.strip():
    print("", end="")
    raise SystemExit(0)

try:
    data = json.loads(raw)
except Exception:
    print("", end="")
    raise SystemExit(0)

if not isinstance(data, dict):
    print("", end="")
    raise SystemExit(0)

def value(name):
    raw_value = data.get(name, "none")
    if raw_value in ("", None):
        return "none"
    if isinstance(raw_value, bool):
        return str(raw_value).lower()
    return str(raw_value)

lines = [
    f"- last_run_at: {value('last_run_at')}",
    f"- last_status: {value('last_status')}",
    f"- needs_approval: {value('needs_approval')}",
    f"- current_task_file: {value('current_task_file')}",
    f"- last_result_file: {value('last_result_file')}",
]
print("\n".join(lines), end="")
PY
}

build_prompt() {
  local task_content="$1"
  local previous_result
  local previous_operational_status
  previous_result="$(previous_result_excerpt)"
  previous_operational_status="$(previous_operational_status_excerpt)"
  cat > "$LAST_PROMPT_FILE" <<EOF
# Contexto persistente

## Regras fixas
$(cat "$AGENTS_FILE")

## Estado atual
$(cat "$PROJECT_STATE_FILE")

$(if [[ -n "$previous_result" ]]; then printf '## Resultado anterior\n%s\n\n' "$previous_result"; fi)
$(if [[ -n "$previous_operational_status" ]]; then printf '## Estado operacional anterior\n%s\n\n' "$previous_operational_status"; fi)

## Tarefa ativa
${task_content}

## Instrucoes de resposta
- Execute a tarefa com a menor mudanca util e segura.
- Se houver risco, ambiguidade ou necessidade de decisao humana, pare e diga explicitamente.
- Responda ao final de forma curta e auditavel, incluindo:
  - status final
  - comandos executados
  - arquivos tocados
  - o que foi alterado
  - o que falta
  - se precisa aprovacao
  - se houve erro
EOF
}

print_status() {
  python3 - "$LOOP_STATUS_FILE" "$JSON_OUTPUT" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
json_mode = sys.argv[2] == "1"
if not path.exists():
    data = {
        "last_run_at": "",
        "last_status": "",
        "needs_approval": False,
        "current_task_file": "",
        "last_result_file": "",
        "mode": "",
        "stopped_reason": "",
        "tasks_processed": 0,
        "dry_run": False,
    }
    if json_mode:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("last_run_at=")
        print("last_status=")
        print("needs_approval=false")
        print("current_task_file=")
        print("last_result_file=")
        print("mode=")
        print("stopped_reason=")
        print("tasks_processed=0")
        print("dry_run=false")
    raise SystemExit(0)

try:
    data = json.loads(path.read_text(encoding="utf-8") or "{}")
except Exception:
    data = {}

payload = {
    "last_run_at": data.get("last_run_at", ""),
    "last_status": data.get("last_status", ""),
    "needs_approval": bool(data.get("needs_approval", False)),
    "current_task_file": data.get("current_task_file", ""),
    "last_result_file": data.get("last_result_file", ""),
    "mode": data.get("mode", ""),
    "stopped_reason": data.get("stopped_reason", ""),
    "tasks_processed": int(data.get("tasks_processed", 0) or 0),
    "dry_run": bool(data.get("dry_run", False)),
}

if json_mode:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
else:
    print(f"last_run_at={payload['last_run_at']}")
    print(f"last_status={payload['last_status']}")
    print(f"needs_approval={str(payload['needs_approval']).lower()}")
    print(f"current_task_file={payload['current_task_file']}")
    print(f"last_result_file={payload['last_result_file']}")
    print(f"mode={payload['mode']}")
    print(f"stopped_reason={payload['stopped_reason']}")
    print(f"tasks_processed={payload['tasks_processed']}")
    print(f"dry_run={str(payload['dry_run']).lower()}")
PY
}

print_last_summary() {
  python3 - "$LOOP_STATUS_FILE" "$LAST_RESULT_FILE" "$LAST_RUN_LOG_FILE" "$JSON_OUTPUT" <<'PY'
from pathlib import Path
import json
import sys

status_path = Path(sys.argv[1])
result_path = Path(sys.argv[2])
log_path = Path(sys.argv[3])
json_mode = sys.argv[4] == "1"

status = {}
if status_path.exists():
    try:
        status = json.loads(status_path.read_text(encoding="utf-8") or "{}")
    except Exception:
        status = {}

def value(name):
    raw = status.get(name, "none")
    if raw == "":
        return "none"
    if isinstance(raw, bool):
        return str(raw).lower()
    return str(raw)

def raw_value(name, default):
    raw = status.get(name, default)
    if raw in ("", None):
        return default
    return raw

last_log_file = "none"
if log_path.exists():
    content = log_path.read_text(encoding="utf-8").strip()
    if content:
        last_log_file = content

excerpt = "none"
if result_path.exists():
    useful = []
    for line in result_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped == "# Resultado do loop":
            continue
        useful.append(stripped)
        if len(useful) >= 4:
            break
    if useful:
        excerpt = " | ".join(useful)
        if len(excerpt) > 220:
            excerpt = excerpt[:217] + "..."

if json_mode:
    payload = {
        "last_run_at": value('last_run_at'),
        "last_status": value('last_status'),
        "needs_approval": bool(raw_value('needs_approval', False)),
        "current_task_file": value('current_task_file'),
        "last_result_file": value('last_result_file'),
        "last_log_file": last_log_file,
        "result_excerpt": excerpt,
        "mode": value('mode'),
        "stopped_reason": value('stopped_reason'),
        "tasks_processed": int(raw_value('tasks_processed', 0)),
        "dry_run": bool(raw_value('dry_run', False)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0)
print(f"last_run_at={value('last_run_at')}")
print(f"last_status={value('last_status')}")
print(f"needs_approval={value('needs_approval')}")
print(f"current_task_file={value('current_task_file')}")
print(f"last_result_file={value('last_result_file')}")
print(f"last_log_file={last_log_file}")
print(f"result_excerpt={excerpt}")
print(f"mode={value('mode')}")
print(f"stopped_reason={value('stopped_reason')}")
print(f"tasks_processed={value('tasks_processed')}")
print(f"dry_run={value('dry_run')}")
PY
}

print_last_result_json() {
  if [[ -f "$LAST_RESULT_JSON_FILE" ]]; then
    cat "$LAST_RESULT_JSON_FILE"
    printf '\n'
  else
    printf '%s\n' '{"exists":false}'
  fi
}

next_action_value() {
  python3 - "$LOOP_STATUS_FILE" "$LAST_RESULT_JSON_FILE" "$TASK_FILE" <<'PY'
from pathlib import Path
import json
import sys

status_path = Path(sys.argv[1])
last_result_path = Path(sys.argv[2])
queue_path = Path(sys.argv[3])

if not status_path.exists():
    print("idle")
    raise SystemExit(0)

try:
    raw_status = status_path.read_text(encoding="utf-8")
except Exception:
    raw_status = ""

status = {}
if raw_status.strip():
    try:
        parsed = json.loads(raw_status)
        if isinstance(parsed, dict):
            status = parsed
    except Exception:
        status = {}

try:
    raw_last_result = last_result_path.read_text(encoding="utf-8") if last_result_path.exists() else ""
    if raw_last_result.strip():
        parsed_last_result = json.loads(raw_last_result)
        if not isinstance(parsed_last_result, dict):
            parsed_last_result = {}
except Exception:
    parsed_last_result = {}

needs_approval = status.get("needs_approval")
if needs_approval is True:
    print("needs_approval")
    raise SystemExit(0)

last_status = str(status.get("last_status", "")).strip().lower()
if last_status == "rejected":
    print("rejected")
    raise SystemExit(0)
if last_status in {"timeout", "error", "failed"}:
    print("retry")
    raise SystemExit(0)

try:
    text = queue_path.read_text(encoding="utf-8") if queue_path.exists() else ""
    parts = []
    current = []
    for line in text.splitlines():
        if line.strip() == "---":
            block = "\n".join(current).strip()
            if block:
                parts.append(block)
            current = []
        else:
            current.append(line)
    block = "\n".join(current).strip()
    if block:
        parts.append(block)
    queue_has_content = bool(parts)
except Exception:
    queue_has_content = False

if queue_has_content:
    print("continue")
else:
    print("idle")
PY
}

print_next_action() {
  local action
  action="$(next_action_value)"
  if [[ "$JSON_OUTPUT" -eq 1 ]]; then
    python3 - "$action" <<'PY'
import json
import sys
print(json.dumps({"next_action": sys.argv[1]}, ensure_ascii=False, indent=2))
PY
  else
    printf '%s\n' "$action"
  fi
}

tail_last_log() {
  if [[ -s "$LAST_RUN_LOG_FILE" ]]; then
    cat "$LAST_RUN_LOG_FILE"
  else
    echo "[info] nenhum log bruto registrado ainda."
  fi
}

load_loop_field() {
  local field="$1"
  python3 - "$LOOP_STATUS_FILE" "$field" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
field = sys.argv[2]
if not path.exists():
    print("", end="")
    raise SystemExit(0)
data = json.loads(path.read_text(encoding="utf-8") or "{}")
value = data.get(field, "")
if isinstance(value, bool):
    print(str(value).lower(), end="")
else:
    print(value, end="")
PY
}

queue_operation() {
  local mode="$1"
  python3 - "$TASK_FILE" "$mode" "$JSON_OUTPUT" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
mode = sys.argv[2]
json_mode = sys.argv[3] == "1"
text = path.read_text(encoding="utf-8") if path.exists() else ""

parts = []
current = []
for line in text.splitlines():
    if line.strip() == "---":
        block = "\n".join(current).strip()
        if block:
            parts.append(block)
        current = []
    else:
        current.append(line)
block = "\n".join(current).strip()
if block:
    parts.append(block)

if mode == "count":
    print(len(parts))
    raise SystemExit(0)

if mode == "prepare":
    if not parts:
        path.write_text("", encoding="utf-8")
        print("empty")
        raise SystemExit(0)
    current_task = parts[0]
    remaining = "\n\n---\n\n".join(parts[1:])
    path.write_text(current_task, encoding="utf-8")
    print("prepared")
    if remaining:
        print(remaining)
    raise SystemExit(0)

if mode == "peek":
    if json_mode:
        payload = {
            "tasks_found": len(parts),
            "queue_empty": len(parts) == 0,
            "tasks": [],
        }
        for index, part in enumerate(parts, start=1):
            lines = [line.rstrip() for line in part.splitlines()]
            non_empty = [line.strip() for line in lines if line.strip()]
            first_line = non_empty[0] if non_empty else ""
            if len(first_line) > 100:
                first_line = first_line[:97] + "..."
            payload["tasks"].append(
                {
                    "index": index,
                    "first_line": first_line,
                    "line_count": len(lines),
                }
            )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise SystemExit(0)
    if not parts:
        print("tasks_found=0")
        print("queue_empty=true")
        raise SystemExit(0)
    print(f"tasks_found={len(parts)}")
    print("queue_empty=false")
    for index, part in enumerate(parts, start=1):
        lines = [line.rstrip() for line in part.splitlines()]
        non_empty = [line.strip() for line in lines if line.strip()]
        first_line = non_empty[0] if non_empty else ""
        if len(first_line) > 100:
            first_line = first_line[:97] + "..."
        print(f"task_{index}_index={index}")
        print(f"task_{index}_first_line={first_line}")
        print(f"task_{index}_line_count={len(lines)}")
    raise SystemExit(0)
PY
}

prepare_drain_task() {
  queue_operation "prepare"
}

peek_queue() {
  queue_operation "peek"
}

queue_task_count() {
  queue_operation "count"
}

enqueue_task_content() {
  local source="$1"
  local task_content="$2"
  local appended="false"
  local tasks_found_after

  if [[ -z "$task_content" ]]; then
    echo "[erro] tarefa vazia; nada foi enfileirado." >&2
    return 1
  fi

  if [[ "$(queue_task_count)" -gt 0 ]]; then
    appended="true"
    printf '\n\n---\n\n%s\n' "$task_content" >> "$TASK_FILE"
  else
    printf '%s\n' "$task_content" > "$TASK_FILE"
  fi

  tasks_found_after="$(queue_task_count)"
  echo "enqueued=true"
  echo "queue_file=$TASK_FILE"
  echo "tasks_found_after=$tasks_found_after"
  echo "appended=$appended"
  echo "source=$source"
}

enqueue_inline_task() {
  local task_text="${1:-$ENQUEUE_TEXT}"
  if [[ -z "$task_text" ]]; then
    echo "[erro] texto vazio em --enqueue; nada foi alterado." >&2
    return 1
  fi
  enqueue_task_content "inline" "$task_text"
}

enqueue_file_task() {
  local file_path="${1:-$ENQUEUE_FILE}"
  local file_content

  if [[ -z "$file_path" ]]; then
    echo "[erro] caminho vazio em --enqueue-file; nada foi alterado." >&2
    return 1
  fi
  if [[ ! -f "$file_path" ]]; then
    echo "[erro] arquivo de enqueue nao encontrado: $file_path" >&2
    return 1
  fi

  file_content="$(trimmed_file_content "$file_path")"
  if [[ -z "$file_content" ]]; then
    echo "[erro] arquivo de enqueue vazio; nada foi alterado." >&2
    return 1
  fi

  enqueue_task_content "file" "$file_content"
}

approve_current_pause() {
  rm -f "$APPROVAL_FLAG_FILE"
  echo "[ok] approval liberado."
}

reset_transient_state() {
  local approval_cleared="false"
  local stale_lock_removed="false"
  local lock_preserved="false"
  local locked_pid=""

  if [[ -f "$APPROVAL_FLAG_FILE" ]]; then
    rm -f "$APPROVAL_FLAG_FILE"
    approval_cleared="true"
  fi

  if [[ -f "$LOCK_FILE" ]]; then
    locked_pid="$(read_lock_pid)"
    if [[ -n "$locked_pid" ]] && kill -0 "$locked_pid" 2>/dev/null; then
      lock_preserved="true"
    else
      rm -f "$LOCK_FILE"
      stale_lock_removed="true"
    fi
  fi

  echo "approval_cleared=$approval_cleared"
  echo "stale_lock_removed=$stale_lock_removed"
  echo "lock_preserved=$lock_preserved"
}

reject_current_task() {
  local stamp rejected_file
  stamp="$(file_timestamp)"
  rejected_file="$REJECTED_DIR/${stamp}.md"

  if [[ -s "$TASK_FILE" ]]; then
    mv "$TASK_FILE" "$rejected_file"
    : > "$TASK_FILE"
  fi

  rm -f "$APPROVAL_FLAG_FILE"
  write_loop_status "rejected" "false" "" "" "single" "rejected" "0"
  echo "[ok] tarefa rejeitada."
  if [[ -f "$rejected_file" ]]; then
    echo "[ok] tarefa movida para ${rejected_file#$ROOT_DIR/}"
  fi
}

run_codex_exec() {
  local raw_log_file="$1"
  local result_capture_file="$2"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    local simulated=""
    if [[ -n "$SIMULATE_OUTPUT_FILE" && -f "$SIMULATE_OUTPUT_FILE" ]]; then
      simulated="$(cat "$SIMULATE_OUTPUT_FILE")"
    elif [[ -n "$SIMULATE_OUTPUT" ]]; then
      simulated="$SIMULATE_OUTPUT"
    else
      simulated=$'status final: dry-run\ncomandos executados: nenhum\narquivos tocados: nenhum\no que foi alterado: simulacao de fluxo\no que falta: executar sem dry-run\nse precisa aprovacao: nao\nse houve erro: nao'
    fi
    if [[ "$SIMULATE_TIMEOUT" == "1" && "$SIMULATE_DELAY_SECONDS" -lt "$((CODEX_TIMEOUT_SECONDS + 1))" ]]; then
      SIMULATE_DELAY_SECONDS="$((CODEX_TIMEOUT_SECONDS + 1))"
    fi

    timeout "${CODEX_TIMEOUT_SECONDS}s" env \
      RAW_LOG_FILE="$raw_log_file" \
      RESULT_CAPTURE_FILE="$result_capture_file" \
      SIMULATED_OUTPUT="$simulated" \
      SIMULATE_DELAY_SECONDS="$SIMULATE_DELAY_SECONDS" \
      bash -c 'sleep "$SIMULATE_DELAY_SECONDS"; printf "%s\n" "$SIMULATED_OUTPUT" > "$RAW_LOG_FILE"; printf "%s\n" "$SIMULATED_OUTPUT" > "$RESULT_CAPTURE_FILE"'
    return $?
  fi

  if ! command -v codex >/dev/null 2>&1; then
    printf '%s\n' "status final: erro
comandos executados: nenhum
arquivos tocados: nenhum
o que foi alterado: nada
o que falta: instalar ou expor o binario codex
se precisa aprovacao: nao
se houve erro: codex nao encontrado" > "$result_capture_file"
    printf '%s\n' "codex binary not found" > "$raw_log_file"
    return 127
  fi

  timeout "${CODEX_TIMEOUT_SECONDS}s" codex exec \
    --skip-git-repo-check \
    --model "$CODEX_MODEL" \
    --cd "$ROOT_DIR" \
    --output-last-message "$result_capture_file" \
    - < "$LAST_PROMPT_FILE" >"$raw_log_file" 2>&1
}

ensure_codex_call_spacing() {
  if [[ "${CODEX_CALL_PAUSE_SECONDS:-0}" -le 0 ]]; then
    return 0
  fi
  if [[ "$LAST_CODEX_CALL_TS" -le 0 ]]; then
    return 0
  fi

  local now elapsed wait
  now="$(date +%s)"
  elapsed=$(( now - LAST_CODEX_CALL_TS ))
  wait=$(( CODEX_CALL_PAUSE_SECONDS - elapsed ))
  if (( wait > 0 )); then
    sleep "$wait"
  fi
}

should_retry_codex_failure() {
  local rc="$1"
  local raw_log_file="$2"
  if [[ "$rc" -eq 0 || "$rc" -eq 124 || "$rc" -eq 127 ]]; then
    return 1
  fi
  if [[ ! -f "$raw_log_file" ]]; then
    return 1
  fi

  local content
  content="$(tr '[:upper:]' '[:lower:]' < "$raw_log_file" 2>/dev/null || true)"
  local patterns=("rate limit" "too many requests" "429" "retry after" "retry later" "request was rejected" "throttl" "quota exceeded")
  for pattern in "${patterns[@]}"; do
    if [[ "$content" == *"$pattern"* ]]; then
      return 0
    fi
  done
  return 1
}

execute_codex_with_backoff() {
  local raw_log_file="$1"
  local result_capture_file="$2"
  local attempt=1
  local backoff_delay=2
  local run_rc=0

  while true; do
    ensure_codex_call_spacing
    run_codex_exec "$raw_log_file" "$result_capture_file"
    run_rc=$?
    LAST_CODEX_CALL_TS="$(date +%s)"
    if [[ "$run_rc" -eq 0 ]]; then
      break
    fi
    if (( attempt >= CODEX_MAX_RETRIES )); then
      break
    fi
    if ! should_retry_codex_failure "$run_rc" "$raw_log_file"; then
      break
    fi
    printf '%s\n' "[retry] codex exec failed (rc=$run_rc); waiting ${backoff_delay}s before attempt $((attempt + 1))"
    sleep "$backoff_delay"
    backoff_delay=$(( backoff_delay < 8 ? backoff_delay * 2 : 8 ))
    attempt=$((attempt + 1))
  done

  return "$run_rc"
}

contains_risk_signal() {
  local text_file="$1"
  python3 - "$text_file" "${RISK_TERMS[@]}" <<'PY'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text(encoding="utf-8").lower() if Path(sys.argv[1]).exists() else ""
terms = [term.lower() for term in sys.argv[2:]]
print("true" if any(term in text for term in terms) else "false")
PY
}

extract_field_block() {
  local label="$1"
  local source_file="$2"
  python3 - "$label" "$source_file" <<'PY'
from pathlib import Path
import re
import sys

label = sys.argv[1].strip().lower()
text = Path(sys.argv[2]).read_text(encoding="utf-8") if Path(sys.argv[2]).exists() else ""
lines = text.splitlines()
pattern = re.compile(r"^\s*" + re.escape(label) + r"\s*[:\-]\s*(.*)\s*$", re.IGNORECASE)
for idx, line in enumerate(lines):
    match = pattern.match(line)
    if not match:
        continue
    value = match.group(1).strip()
    if value:
        print(value)
        raise SystemExit(0)
    collected = []
    for follow in lines[idx + 1:]:
        if re.match(r"^\s*[A-Za-zÀ-ÿ0-9 _/-]+\s*[:\-]\s*", follow):
            break
        if follow.strip():
            collected.append(follow.strip())
    print(" | ".join(collected))
    raise SystemExit(0)
print("", end="")
PY
}

build_result_summary() {
  local timestamp="$1"
  local task_content="$2"
  local exec_status="$3"
  local raw_log_file="$4"
  local result_capture_file="$5"
  local result_file="$6"
  local risk_detected="$7"

  local status_final commands_executed files_touched changed missing needs_approval had_error
  status_final="$(extract_field_block "status final" "$result_capture_file")"
  commands_executed="$(extract_field_block "comandos executados" "$result_capture_file")"
  files_touched="$(extract_field_block "arquivos tocados" "$result_capture_file")"
  changed="$(extract_field_block "o que foi alterado" "$result_capture_file")"
  missing="$(extract_field_block "o que falta" "$result_capture_file")"
  needs_approval="$(extract_field_block "se precisa aprovacao" "$result_capture_file")"
  had_error="$(extract_field_block "se houve erro" "$result_capture_file")"

  [[ -n "$status_final" ]] || status_final="$exec_status"
  [[ -n "$commands_executed" ]] || commands_executed="nao identificado automaticamente"
  [[ -n "$files_touched" ]] || files_touched="nao identificado automaticamente"
  [[ -n "$changed" ]] || changed="nao identificado automaticamente"
  [[ -n "$missing" ]] || missing="nao identificado automaticamente"
  [[ -n "$needs_approval" ]] || needs_approval="$risk_detected"
  [[ -n "$had_error" ]] || had_error="$([[ "$exec_status" == "success" || "$exec_status" == "dry-run" ]] && echo "nao" || echo "sim")"

  cat > "$result_file" <<EOF
# Resultado do loop

- timestamp: $timestamp
- tarefa executada: $(printf '%s' "$task_content" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | cut -c1-220)
- status final: $status_final
- comandos executados: $commands_executed
- arquivos tocados: $files_touched
- o que foi alterado: $changed
- o que falta: $missing
- se precisa aprovação: $needs_approval
- se houve erro: $had_error
- log bruto: $(basename "$raw_log_file")

## Saida final do Codex

$(cat "$result_capture_file")
EOF
}

write_last_result_json() {
  local source_file="$1"
  python3 - "$source_file" "$LAST_RESULT_JSON_FILE" <<'PY'
from pathlib import Path
import json
import re
import sys

source_path = Path(sys.argv[1])
target_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
lines = text.splitlines()

fields = {
    "timestamp": "",
    "task_excerpt": "",
    "status_final": "",
    "comandos_executados": "",
    "arquivos_tocados": "",
    "o_que_foi_alterado": "",
    "o_que_falta": "",
    "se_precisa_aprovacao": "",
    "se_houve_erro": "",
    "log_file": "",
}

label_map = {
    "timestamp": "timestamp",
    "tarefa executada": "task_excerpt",
    "status final": "status_final",
    "comandos executados": "comandos_executados",
    "arquivos tocados": "arquivos_tocados",
    "o que foi alterado": "o_que_foi_alterado",
    "o que falta": "o_que_falta",
    "se precisa aprovação": "se_precisa_aprovacao",
    "se precisa aprovacao": "se_precisa_aprovacao",
    "se houve erro": "se_houve_erro",
    "log bruto": "log_file",
}

for line in lines:
    match = re.match(r"^\s*-\s*([^:]+):\s*(.*)\s*$", line)
    if not match:
      continue
    label = match.group(1).strip().lower()
    key = label_map.get(label)
    if key is None:
      continue
    fields[key] = match.group(2).strip()

target_path.write_text(json.dumps(fields, ensure_ascii=False, indent=2), encoding="utf-8")
PY
}

write_loop_status() {
  local last_status="$1"
  local needs_approval="$2"
  local current_task_file="$3"
  local last_result_file="$4"
  local mode="${5:-$(current_mode_label)}"
  local stopped_reason="${6:-}"
  local tasks_processed="${7:-0}"
  local dry_run="${8:-$([[ "$DRY_RUN" -eq 1 ]] && echo "true" || echo "false")}"
  python3 - "$LOOP_STATUS_FILE" "$last_status" "$needs_approval" "$current_task_file" "$last_result_file" "$mode" "$stopped_reason" "$tasks_processed" "$dry_run" <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import json
import sys

path = Path(sys.argv[1])
payload = {
    "last_run_at": datetime.now(timezone.utc).isoformat(),
    "last_status": sys.argv[2],
    "needs_approval": sys.argv[3].lower() == "true",
    "current_task_file": sys.argv[4],
    "last_result_file": sys.argv[5],
    "mode": sys.argv[6],
    "stopped_reason": sys.argv[7],
    "tasks_processed": int(sys.argv[8]),
    "dry_run": sys.argv[9].lower() == "true",
}
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
PY
}

print_terminal_execution_summary() {
  local mode="$1"
  local marker="${2:-}"
  python3 - "$LOOP_STATUS_FILE" "$LAST_RESULT_JSON_FILE" "$LAST_RUN_LOG_FILE" "$RESULTS_DIR" "$LOGS_DIR" "$mode" "$marker" <<'PY'
from pathlib import Path
import json
import sys

status_path = Path(sys.argv[1])
last_result_json_path = Path(sys.argv[2])
last_run_log_path = Path(sys.argv[3])
results_dir = Path(sys.argv[4])
logs_dir = Path(sys.argv[5])
mode = sys.argv[6]
marker = sys.argv[7].strip()

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

def read_last_log_file(path: Path) -> str:
    if not path.exists():
        return "none"
    try:
        content = path.read_text(encoding="utf-8").strip()
    except Exception:
        return "none"
    return content or "none"

def build_result_excerpt(result_file: str) -> str:
    if not result_file or result_file == "none":
        return "none"
    path = Path(result_file)
    if not path.exists():
        return "none"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return "none"
    useful = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped in {"# Resultado do loop", "## Saida final do Codex"}:
            continue
        if stripped.lower().startswith("- log bruto:"):
            continue
        useful.append(stripped)
        if len(useful) >= 4:
            break
    if not useful:
        return "none"
    excerpt = " | ".join(useful)
    return excerpt if len(excerpt) <= 220 else excerpt[:217] + "..."

def created_files(path: Path, suffix: str, marker_value: str) -> list[str]:
    if not marker_value or not path.exists():
        return []
    output = []
    for candidate in sorted(path.glob(f"*{suffix}")):
        stem = candidate.name[:-len(suffix)] if suffix and candidate.name.endswith(suffix) else candidate.stem
        if stem >= marker_value:
            output.append(candidate.name)
    return output

status = load_json(status_path)
_ = load_json(last_result_json_path)
last_status = str(status.get("last_status", "") or "none")
stopped_reason = str(status.get("stopped_reason", "") or "none")
tasks_processed = int(status.get("tasks_processed", 0) or 0)
last_result_file = str(status.get("last_result_file", "") or "none")
last_log_file = read_last_log_file(last_run_log_path)
result_excerpt = build_result_excerpt(last_result_file)

print("summary_last_status=" + last_status)
print("summary_stopped_reason=" + stopped_reason)
print("summary_tasks_processed=" + str(tasks_processed))
print("summary_last_result_file=" + last_result_file)
print("summary_last_log_file=" + last_log_file)
print("summary_result_excerpt=" + result_excerpt)

if mode == "drain":
    result_files = created_files(results_dir, ".md", marker)
    log_files = created_files(logs_dir, ".log", marker)
    print("summary_created_result_files=" + (",".join(result_files) if result_files else "none"))
    print("summary_created_log_files=" + (",".join(log_files) if log_files else "none"))
PY
}

archive_task() {
  local stamp="$1"
  local archive_file="$ARCHIVE_DIR/${stamp}.md"
  mv "$TASK_FILE" "$archive_file"
  : > "$TASK_FILE"
  printf '%s\n' "$archive_file"
}

run_single_iteration() {
  local task_content
  task_content="$(trimmed_file_content "$TASK_FILE")"
  if [[ -z "$task_content" ]]; then
    echo "[idle] queue/next.md vazio ou ausente; nada para executar."
    write_loop_status "idle" "false" "" "" "$(current_mode_label)" "empty_queue" "0"
    return 10
  fi

  local ts stamp raw_log_file result_capture_file result_file exec_status risk_result risk_detected archived_task run_rc
  ts="$(iso_timestamp)"
  stamp="$(file_timestamp)"
  raw_log_file="$LOGS_DIR/${stamp}.log"
  result_capture_file="$STATE_DIR/.last_codex_message_${stamp}.tmp"
  result_file="$RESULTS_DIR/${stamp}.md"
  exec_status="success"
  printf '%s\n' "$raw_log_file" > "$LAST_RUN_LOG_FILE"

  build_prompt "$task_content"
  echo "[run] tarefa carregada de queue/next.md"
  echo "[run] prompt consolidado salvo em state/last_prompt.md"

  run_rc=0
  execute_codex_with_backoff "$raw_log_file" "$result_capture_file" || run_rc=$?
  if [[ "$run_rc" -ne 0 ]]; then
    if [[ "$run_rc" -eq 124 ]]; then
      exec_status="timeout"
      printf '%s\n' "codex exec timed out after ${CODEX_TIMEOUT_SECONDS}s" >> "$raw_log_file"
      cat > "$result_capture_file" <<EOF
status final: timeout
comandos executados: codex exec
arquivos tocados: nenhum
o que foi alterado: nada
o que falta: revisar a tarefa e decidir se deve retentar
se precisa aprovacao: sim
se houve erro: timeout apos ${CODEX_TIMEOUT_SECONDS}s
EOF
    else
      exec_status="failed"
    fi
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    exec_status="dry-run"
  fi

  risk_result="$(contains_risk_signal "$result_capture_file")"
  risk_detected="false"
  if [[ "$risk_result" == "true" ]]; then
    risk_detected="true"
  fi
  if [[ "$exec_status" == "timeout" ]]; then
    risk_detected="true"
  fi

  build_result_summary "$ts" "$task_content" "$exec_status" "$raw_log_file" "$result_capture_file" "$result_file" "$risk_detected"
  cp "$result_file" "$LAST_RESULT_FILE"
  write_last_result_json "$result_file"

  if [[ "$risk_detected" == "true" ]]; then
    : > "$APPROVAL_FLAG_FILE"
    if [[ "$exec_status" == "timeout" ]]; then
      write_loop_status "${exec_status}" "true" "$TASK_FILE" "$result_file" "$(current_mode_label)" "timeout" "0"
    else
      write_loop_status "${exec_status}" "true" "$TASK_FILE" "$result_file" "$(current_mode_label)" "approval_required" "0"
    fi
    echo "[pause] risco detectado; revisao humana necessaria."
    echo "[pause] tarefa mantida em queue/next.md"
    rm -f "$result_capture_file"
    return 20
  fi

  rm -f "$APPROVAL_FLAG_FILE"

  if [[ "$exec_status" == "success" || "$exec_status" == "dry-run" ]]; then
    archived_task="$(archive_task "$stamp")"
    write_loop_status "$exec_status" "false" "" "$result_file" "$(current_mode_label)" "completed" "1"
    echo "[ok] execucao concluida sem risco."
    echo "[ok] tarefa arquivada em ${archived_task#$ROOT_DIR/}"
    rm -f "$result_capture_file"
    return 0
  fi

  write_loop_status "$exec_status" "false" "$TASK_FILE" "$result_file" "$(current_mode_label)" "error" "0"
  echo "[erro] execucao falhou; tarefa mantida para revisao."
  rm -f "$result_capture_file"
  return 30
}

run_drain_mode() {
  local tasks_processed=0
  local stopped_reason="empty_queue"
  local prepared_output prepare_state remaining task_status needs_approval

  while true; do
    prepared_output="$(prepare_drain_task)"
    prepare_state="$(printf '%s\n' "$prepared_output" | sed -n '1p')"
    remaining="$(printf '%s\n' "$prepared_output" | sed -n '2,$p')"

    if [[ "$prepare_state" == "empty" ]]; then
      if [[ "$tasks_processed" -eq 0 ]]; then
        write_loop_status "idle" "false" "" "$(load_loop_field last_result_file)" "drain" "empty_queue" "0"
      fi
      stopped_reason="empty_queue"
      break
    fi

    run_single_iteration || true
    task_status="$(load_loop_field last_status)"
    needs_approval="$(load_loop_field needs_approval)"

    if [[ "$needs_approval" == "true" ]]; then
      if [[ -n "$remaining" ]]; then
        current_task="$(trimmed_file_content "$TASK_FILE")"
        if [[ -n "$current_task" ]]; then
          printf '%s\n\n---\n\n%s\n' "$current_task" "$remaining" > "$TASK_FILE"
        else
          printf '%s\n' "$remaining" > "$TASK_FILE"
        fi
      fi
      if [[ "$task_status" == "timeout" ]]; then
        stopped_reason="timeout"
      else
        stopped_reason="approval_required"
      fi
      break
    fi

    if [[ "$task_status" == "success" || "$task_status" == "dry-run" ]]; then
      tasks_processed=$((tasks_processed + 1))
      if [[ -n "$remaining" ]]; then
        printf '%s\n' "$remaining" > "$TASK_FILE"
      else
        : > "$TASK_FILE"
      fi
      continue
    fi

    if [[ -n "$remaining" ]]; then
      current_task="$(trimmed_file_content "$TASK_FILE")"
      if [[ -n "$current_task" ]]; then
        printf '%s\n\n---\n\n%s\n' "$current_task" "$remaining" > "$TASK_FILE"
      else
        printf '%s\n' "$remaining" > "$TASK_FILE"
      fi
    fi

    stopped_reason="error"
    break
  done

  write_loop_status "$(load_loop_field last_status)" "$(load_loop_field needs_approval)" "$(load_loop_field current_task_file)" "$(load_loop_field last_result_file)" "drain" "$stopped_reason" "$tasks_processed"
  echo "tasks_processed=$tasks_processed"
  echo "last_status=$(load_loop_field last_status)"
  echo "stopped_reason=$stopped_reason"
}

submit_and_run_next() {
  local enqueue_output="" run_output="" submit_enqueued="false" submit_executed="false" run_executed="false"

  if [[ "$SUBMIT_REQUESTED" -eq 1 && "$SUBMIT_FILE_REQUESTED" -eq 1 ]]; then
    echo "[erro] use apenas um entre --submit e --submit-file." >&2
    return 2
  fi

  if [[ "$SUBMIT_REQUESTED" -eq 1 ]]; then
    if ! enqueue_output="$(enqueue_inline_task "$SUBMIT_TEXT")"; then
      printf '%s\n' "submit_enqueued=false" "submit_executed=false" "last_status=$(load_loop_field last_status)" "needs_approval=$(load_loop_field needs_approval)" "next_action=$(next_action_value)" "last_result_file=$(load_loop_field last_result_file)"
      return 1
    fi
  else
    if ! enqueue_output="$(enqueue_file_task "$SUBMIT_FILE")"; then
      printf '%s\n' "submit_enqueued=false" "submit_executed=false" "last_status=$(load_loop_field last_status)" "needs_approval=$(load_loop_field needs_approval)" "next_action=$(next_action_value)" "last_result_file=$(load_loop_field last_result_file)"
      return 1
    fi
  fi

  if [[ "$enqueue_output" == *"enqueued=true"* ]]; then
    submit_enqueued="true"
  fi

  run_output="$(run_next_once)"
  if [[ "$run_output" == *"run_next_executed=true"* ]]; then
    run_executed="true"
  fi
  if [[ "$run_output" == *"run_next_executed=false"* ]]; then
    run_executed="false"
  fi
  submit_executed="$run_executed"

  printf '%s\n' \
    "submit_enqueued=$submit_enqueued" \
    "submit_executed=$submit_executed" \
    "last_status=$(load_loop_field last_status)" \
    "needs_approval=$(load_loop_field needs_approval)" \
    "next_action=$(next_action_value)" \
    "last_result_file=$(load_loop_field last_result_file)"
}

run_next_once() {
  local prepared_output prepare_state remaining task_status needs_approval current_task stopped_reason="completed" tasks_processed="0"

  if [[ -f "$APPROVAL_FLAG_FILE" ]]; then
    write_loop_status "$(load_loop_field last_status)" "true" "$TASK_FILE" "$(load_loop_field last_result_file)" "run-next" "needs_approval" "0"
    echo "run_next_executed=false"
    echo "reason=needs_approval"
    echo "task_consumed=false"
    echo "tasks_processed=0"
    return 0
  fi

  acquire_lock

  prepared_output="$(prepare_drain_task)"
  prepare_state="$(printf '%s\n' "$prepared_output" | sed -n '1p')"
  remaining="$(printf '%s\n' "$prepared_output" | sed -n '2,$p')"

  if [[ "$prepare_state" == "empty" ]]; then
    write_loop_status "idle" "false" "" "$(load_loop_field last_result_file)" "run-next" "empty_queue" "0"
    echo "run_next_executed=false"
    echo "reason=empty_queue"
    echo "task_consumed=false"
    echo "tasks_processed=0"
    return 0
  fi

  run_single_iteration || true
  task_status="$(load_loop_field last_status)"
  needs_approval="$(load_loop_field needs_approval)"

  if [[ "$needs_approval" == "true" ]]; then
    if [[ "$task_status" == "timeout" ]]; then
      stopped_reason="timeout"
    else
      stopped_reason="approval_required"
    fi
    if [[ -n "$remaining" ]]; then
      current_task="$(trimmed_file_content "$TASK_FILE")"
      if [[ -n "$current_task" ]]; then
        printf '%s\n\n---\n\n%s\n' "$current_task" "$remaining" > "$TASK_FILE"
      else
        printf '%s\n' "$remaining" > "$TASK_FILE"
      fi
    fi
  elif [[ "$task_status" == "success" || "$task_status" == "dry-run" ]]; then
    tasks_processed="1"
    if [[ -n "$remaining" ]]; then
      printf '%s\n' "$remaining" > "$TASK_FILE"
    else
      : > "$TASK_FILE"
    fi
  elif [[ -n "$remaining" ]]; then
    stopped_reason="error"
    current_task="$(trimmed_file_content "$TASK_FILE")"
    if [[ -n "$current_task" ]]; then
      printf '%s\n\n---\n\n%s\n' "$current_task" "$remaining" > "$TASK_FILE"
    else
      printf '%s\n' "$remaining" > "$TASK_FILE"
    fi
  fi

  write_loop_status "$task_status" "$needs_approval" "$(load_loop_field current_task_file)" "$(load_loop_field last_result_file)" "run-next" "$stopped_reason" "$tasks_processed"
  echo "run_next_executed=true"
  echo "last_status=$task_status"
  if [[ "$task_status" == "success" || "$task_status" == "dry-run" ]]; then
    echo "task_consumed=true"
  else
    echo "task_consumed=false"
  fi
  echo "tasks_processed=$tasks_processed"
  echo "stopped_reason=$stopped_reason"
}

main() {
  parse_args "$@"
  if [[ "$NEXT_ACTION_ONLY" -eq 1 ]]; then
    print_next_action
    exit 0
  fi
  ensure_layout
  EXECUTION_FILE_MARKER="$(file_timestamp)"
  if [[ "$SHOW_STATUS" -eq 1 ]]; then
    print_status
    exit 0
  fi
  if [[ "$LAST_SUMMARY_ONLY" -eq 1 ]]; then
    print_last_summary
    exit 0
  fi
  if [[ "$LAST_RESULT_JSON_ONLY" -eq 1 ]]; then
    print_last_result_json
    exit 0
  fi
  if [[ "$SUBMIT_REQUESTED" -eq 1 || "$SUBMIT_FILE_REQUESTED" -eq 1 ]]; then
    submit_and_run_next
    local submit_rc=$?
    print_terminal_execution_summary "run-next" "$EXECUTION_FILE_MARKER"
    exit $submit_rc
  fi
  if [[ "$ENQUEUE_REQUESTED" -eq 1 || "$ENQUEUE_FILE_REQUESTED" -eq 1 ]]; then
    if [[ "$ENQUEUE_REQUESTED" -eq 1 && "$ENQUEUE_FILE_REQUESTED" -eq 1 ]]; then
      echo "[erro] use apenas um entre --enqueue e --enqueue-file." >&2
      exit 2
    fi
    if [[ "$ENQUEUE_REQUESTED" -eq 1 ]]; then
      enqueue_inline_task
      exit $?
    fi
    enqueue_file_task
    exit $?
  fi
  if [[ "$TAIL_LOG_ONLY" -eq 1 ]]; then
    tail_last_log
    exit 0
  fi
  if [[ "$PEEK_QUEUE_ONLY" -eq 1 ]]; then
    peek_queue
    exit 0
  fi
  if [[ "$APPROVE_ONLY" -eq 1 ]]; then
    approve_current_pause
    exit 0
  fi
  if [[ "$REJECT_ONLY" -eq 1 ]]; then
    reject_current_task
    exit 0
  fi
  if [[ "$RESET_TRANSIENT_STATE_ONLY" -eq 1 ]]; then
    reset_transient_state
    exit 0
  fi
  if [[ "$RUN_NEXT_ONLY" -eq 1 ]]; then
    run_next_once
    local run_next_rc=$?
    print_terminal_execution_summary "run-next" "$EXECUTION_FILE_MARKER"
    exit $run_next_rc
  fi

  acquire_lock

  if [[ "$DRAIN_MODE" -eq 1 ]]; then
    run_drain_mode
    local drain_rc=$?
    print_terminal_execution_summary "drain" "$EXECUTION_FILE_MARKER"
    exit $drain_rc
  fi
  run_single_iteration || true
  print_terminal_execution_summary "single" "$EXECUTION_FILE_MARKER"
}

main "$@"
