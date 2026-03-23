#!/bin/bash
set -euo pipefail

ROOT_DIR="/lab/projects/livecopilot"
SUGGESTIONS_JSON="$ROOT_DIR/var/usage/fix_suggestions.json"
STATUS_FILE="$ROOT_DIR/STATUS.md"
ROUTES_FILE="$ROOT_DIR/app/api/routes.py"
GUARDRAIL_SCRIPT="$ROOT_DIR/scripts/run_with_guardrail.sh"
AUTO_LOOP_LOG="$ROOT_DIR/var/auto_loop/auto_loop_events.jsonl"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="/tmp/livecopilot_backup_${TS}"

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$AUTO_LOOP_LOG")"

suggestion_json="$(
python3 - "$SUGGESTIONS_JSON" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
for item in data.get("suggestions", []):
    if not isinstance(item, dict):
        continue
    if str(item.get("prioridade", "")).strip().lower() == "alta":
        print(json.dumps(item, ensure_ascii=False))
        raise SystemExit(0)
raise SystemExit(1)
PY
)" || {
  echo "nenhuma sugestao HIGH encontrada" >&2
  exit 1
}

python3 - "$BACKUP_DIR" "$ROUTES_FILE" "$STATUS_FILE" <<'PY'
import shutil
import sys
from pathlib import Path

backup_dir = Path(sys.argv[1])
routes = Path(sys.argv[2])
status = Path(sys.argv[3])

backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(routes, backup_dir / routes.name)
shutil.copy2(status, backup_dir / status.name)
PY

suggestion_id="$(python3 - <<'PY' "$suggestion_json"
import json
import sys
item = json.loads(sys.argv[1])
print(item.get("pattern_id", "").strip())
PY
)"

apply_patch_for_suggestion() {
python3 - "$ROUTES_FILE" "$suggestion_id" <<'PY'
import sys
from pathlib import Path

routes_path = Path(sys.argv[1])
pattern_id = sys.argv[2]
text = routes_path.read_text(encoding="utf-8")

if pattern_id != "fallback_short_new_topic":
    raise SystemExit(f"pattern_id nao suportado: {pattern_id}")

old = """    elif new_topic_short_prompt:\n        topic_answer = _topic_short_answer(_detect_topic(effective_input_text))\n        if topic_answer is not None:\n            answer, bullets = topic_answer\n            snapshot[\"suggestions\"] = [answer, *bullets]\n            knowledge_context[\"reason\"] = \"short_new_topic_specific_answer\"\n            backend = \"topic_short_answer\"\n"""

new = """    elif new_topic_short_prompt:\n        topic_answer = _topic_short_answer(_detect_topic(effective_input_text))\n        if topic_answer is not None:\n            answer, bullets = topic_answer\n        else:\n            answer, bullets = _safe_final_answer_for_query(effective_input_text)\n        snapshot[\"suggestions\"] = [answer, *bullets]\n        knowledge_context[\"reason\"] = \"short_new_topic_specific_answer\"\n        backend = \"topic_short_answer\"\n"""

if old not in text:
    raise SystemExit("trecho alvo nao encontrado para fallback_short_new_topic")

routes_path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
}

restore_backup() {
python3 - "$BACKUP_DIR" "$ROUTES_FILE" "$STATUS_FILE" <<'PY'
import shutil
import sys
from pathlib import Path

backup_dir = Path(sys.argv[1])
routes = Path(sys.argv[2])
status = Path(sys.argv[3])

shutil.copy2(backup_dir / routes.name, routes)
shutil.copy2(backup_dir / status.name, status)
PY
}

update_json_state() {
  local applied="$1"
  local failed="$2"
  local guardrail_result="$3"
  local rollback="$4"
  python3 - "$SUGGESTIONS_JSON" "$suggestion_id" "$applied" "$failed" "$guardrail_result" "$rollback" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
suggestion_id = sys.argv[2]
applied = sys.argv[3].lower() == "true"
failed = sys.argv[4].lower() == "true"
guardrail_result = sys.argv[5]
rollback = sys.argv[6].lower() == "true"

data = json.loads(path.read_text(encoding="utf-8"))
for item in data.get("suggestions", []):
    if isinstance(item, dict) and str(item.get("pattern_id", "")).strip() == suggestion_id:
        item["applied"] = applied
        item["failed"] = failed
        item["guardrail_result"] = guardrail_result
        item["rollback"] = rollback
        item["updated_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
        break
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
PY
}

write_loop_log() {
  local applied="$1"
  local guardrail_result="$2"
  local rollback="$3"
  python3 - "$AUTO_LOOP_LOG" "$suggestion_id" "$applied" "$guardrail_result" "$rollback" "$TS" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
row = {
    "ts": sys.argv[6],
    "suggestion_id": sys.argv[2],
    "applied": sys.argv[3].lower() == "true",
    "guardrail_result": sys.argv[4],
    "rollback": sys.argv[5].lower() == "true",
}
path.parent.mkdir(parents=True, exist_ok=True)
with path.open("a", encoding="utf-8") as fp:
    fp.write(json.dumps(row, ensure_ascii=False) + "\n")
PY
}

append_status_success() {
python3 - "$STATUS_FILE" "$suggestion_id" "$guardrail_result" <<'PY'
import sys
from pathlib import Path

status_path = Path(sys.argv[1])
suggestion_id = sys.argv[2]
guardrail_result = sys.argv[3]
text = status_path.read_text(encoding="utf-8")
entry = f"""## Checkpoint {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')}: auto-loop de sugestao HIGH aplicado\n- Sugestao aplicada:\n  - `{suggestion_id}`\n- Resultado do guardrail:\n  - `GUARDRAIL_RESULT={guardrail_result}`\n- Rollover/rollback:\n  - `rollback = false`\n- Impacto observado:\n  - ajuste minimo aplicado e mantido apos validacao protegida\n  - apenas uma sugestao foi processada nesta rodada\n\n"""
status_path.write_text(entry + text, encoding="utf-8")
PY
}

append_status_failure() {
python3 - "$STATUS_FILE" "$suggestion_id" "$guardrail_result" <<'PY'
import sys
from pathlib import Path

status_path = Path(sys.argv[1])
suggestion_id = sys.argv[2]
guardrail_result = sys.argv[3]
text = status_path.read_text(encoding="utf-8")
entry = f"""## Checkpoint {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')}: auto-loop de sugestao HIGH revertido\n- Sugestao tentada:\n  - `{suggestion_id}`\n- Resultado do guardrail:\n  - `GUARDRAIL_RESULT={guardrail_result}`\n- Rollover/rollback:\n  - `rollback = true`\n- Impacto observado:\n  - codigo restaurado do backup local\n  - nenhuma alteracao foi mantida apos falha do guardrail\n\n"""
status_path.write_text(entry + text, encoding="utf-8")
PY
}

apply_patch_for_suggestion

set +e
guardrail_output="$(bash "$GUARDRAIL_SCRIPT")"
guardrail_status=$?
set -e
printf '%s\n' "$guardrail_output"

guardrail_result="FAIL"
if printf '%s\n' "$guardrail_output" | rg -q '^GUARDRAIL_RESULT=PASS$'; then
  guardrail_result="PASS"
fi

if [[ "$guardrail_result" == "PASS" && "$guardrail_status" -eq 0 ]]; then
  update_json_state true false "$guardrail_result" false
  write_loop_log true "$guardrail_result" false
  append_status_success
  exit 0
fi

restore_backup
update_json_state false true "$guardrail_result" true
write_loop_log false "$guardrail_result" true
append_status_failure
exit 2
