#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

SOURCE_PREFIXES=()
STRICT=0
JSON_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-prefix)
      if [[ $# -lt 2 ]]; then
        echo "Uso invalido: --source-prefix requer valor" >&2
        exit 1
      fi
      SOURCE_PREFIXES+=("$2")
      shift 2
      ;;
    --strict-source-prefix)
      STRICT=1
      shift
      ;;
    --json)
      JSON_ONLY=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Uso:
  scripts/round_plan.sh [--source-prefix PREFIX ...] [--strict-source-prefix] [--json]

Descricao:
  Pre-visualiza uma rodada por prefixo sem alterar estado, consolidando:
  - ingestao em --dry-run
  - persistencia semantica em --semantic-persist --list-targets

Opcoes:
  --source-prefix PREFIX      Prefixo relativo a data/knowledge_raw (repetivel)
  --strict-source-prefix      Falha quando nenhum alvo e resolvido para os prefixos
  --json                      Emite apenas JSON consolidado
EOF
      exit 0
      ;;
    *)
      echo "Argumento invalido: $1" >&2
      echo "Use --help para ajuda." >&2
      exit 1
      ;;
  esac
done

COMMON_ARGS=()
for prefix in "${SOURCE_PREFIXES[@]}"; do
  COMMON_ARGS+=(--source-prefix "$prefix")
done
if [[ "$STRICT" == "1" ]]; then
  COMMON_ARGS+=(--strict-source-prefix)
fi

DRY_CMD=("$PYTHON_BIN" -m app.services.knowledge_ingest "${COMMON_ARGS[@]}" --dry-run)
SEM_CMD=("$PYTHON_BIN" -m app.services.knowledge_ingest "${COMMON_ARGS[@]}" --semantic-persist --list-targets)

DRY_OUT="$(mktemp)"
SEM_OUT="$(mktemp)"
cleanup() {
  rm -f "$DRY_OUT" "$SEM_OUT"
}
trap cleanup EXIT

set +e
"${DRY_CMD[@]}" >"$DRY_OUT" 2>&1
DRY_EXIT=$?
if [[ "$DRY_EXIT" -ne 0 ]]; then
  cat "$DRY_OUT"
  exit "$DRY_EXIT"
fi

"${SEM_CMD[@]}" >"$SEM_OUT" 2>&1
SEM_EXIT=$?
if [[ "$SEM_EXIT" -ne 0 ]]; then
  cat "$SEM_OUT"
  exit "$SEM_EXIT"
fi
set -e

PLAN_JSON="$($PYTHON_BIN - "$DRY_OUT" "$SEM_OUT" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_json_after_marker(text: str, marker: str) -> dict:
    if marker not in text:
        raise ValueError(f"marker ausente: {marker}")
    tail = text.split(marker, 1)[1]
    start = tail.find("{")
    if start < 0:
        raise ValueError(f"json ausente apos marker: {marker}")
    payload = tail[start:].strip()
    return json.loads(payload)


def extract_semantic_payload(text: str) -> tuple[dict, str]:
    if "Persistência semântica - list-targets:" in text:
        return parse_json_after_marker(text, "Persistência semântica - list-targets:"), "list_targets"
    if "Persistência semântica:" in text:
        return parse_json_after_marker(text, "Persistência semântica:"), "semantic_noop_summary"
    raise ValueError("payload semantico nao encontrado")


dry_text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
sem_text = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")

ingest = parse_json_after_marker(dry_text, "Ingestão - dry-run:")
semantic, semantic_payload_kind = extract_semantic_payload(sem_text)

ingest_targets = [str(item) for item in ingest.get("targets_sample", [])]
semantic_targets = [str(item) for item in semantic.get("source_files_sample", [])]
if not semantic_targets and isinstance(semantic.get("source_files_resolved_total"), int) and int(semantic.get("source_files_resolved_total", 0)) == 0:
    semantic_targets = []

ingest_set = set(ingest_targets)
semantic_set = set(semantic_targets)

divergence = {
    "ingest_only_count": len(ingest_set - semantic_set),
    "semantic_only_count": len(semantic_set - ingest_set),
    "ingest_only_sample": sorted(ingest_set - semantic_set)[:10],
    "semantic_only_sample": sorted(semantic_set - ingest_set)[:10],
    "has_divergence": bool((ingest_set - semantic_set) or (semantic_set - ingest_set)),
}

plan = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "plan_mode": "prefix_round_preview",
    "source_prefixes": ingest.get("source_prefixes", []),
    "ingest_dry_run": {
        "selection_mode": ingest.get("selection_mode", ""),
        "files_found_by_prefix": ingest.get("files_found_by_prefix", {}),
        "total_found": int(ingest.get("total_found", 0) or 0),
        "targets_sample": ingest.get("targets_sample", []),
        "targets_sample_size": int(ingest.get("targets_sample_size", 0) or 0),
        "targets_sample_truncated": bool(ingest.get("targets_sample_truncated", False)),
    },
    "semantic_list_targets": {
        "payload_kind": semantic_payload_kind,
        "selection_mode": semantic.get("selection_mode", ""),
        "source_files_resolved_by_prefix": semantic.get("source_files_resolved_by_prefix", {}),
        "source_files_resolved_total": int(semantic.get("source_files_resolved_total", 0) or 0),
        "source_files_sample": semantic.get("source_files_sample", []),
        "source_files_sample_size": int(semantic.get("source_files_sample_size", 0) or 0),
        "source_files_sample_truncated": bool(semantic.get("source_files_sample_truncated", False)),
        "note": semantic.get("note", ""),
    },
    "totals": {
        "ingest_total_found": int(ingest.get("total_found", 0) or 0),
        "semantic_total_source_files": int(semantic.get("source_files_resolved_total", 0) or 0),
    },
    "divergence": divergence,
}
print(json.dumps(plan, ensure_ascii=False, indent=2))
PY
)"

if [[ "$JSON_ONLY" == "1" ]]; then
  printf '%s\n' "$PLAN_JSON"
  exit 0
fi

printf '%s\n' "ROUND PLAN (prefix preview)"
printf '%s\n' "- Prefixos: $(printf '%s' "$PLAN_JSON" | $PYTHON_BIN -c 'import json,sys; p=json.load(sys.stdin); print(", ".join(p.get("source_prefixes", [])) or "(nenhum)")')"
printf '%s\n' "- Ingestão total encontrada: $(printf '%s' "$PLAN_JSON" | $PYTHON_BIN -c 'import json,sys; p=json.load(sys.stdin); print(p["totals"]["ingest_total_found"])')"
printf '%s\n' "- Persistência total resolvida: $(printf '%s' "$PLAN_JSON" | $PYTHON_BIN -c 'import json,sys; p=json.load(sys.stdin); print(p["totals"]["semantic_total_source_files"])')"
printf '%s\n' "- Divergência: $(printf '%s' "$PLAN_JSON" | $PYTHON_BIN -c 'import json,sys; p=json.load(sys.stdin); print("sim" if p["divergence"]["has_divergence"] else "nao")')"
printf '%s\n' ""
printf '%s\n' "$PLAN_JSON"
