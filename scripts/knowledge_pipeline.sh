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

MODE=""
ROUND_ID=""
ARTIFACT_DIR="docs/coverage"
STRICT=0
SEMANTIC_EMBEDDING_MODE="auto"
SEMANTIC_LIMIT_DOCS=""
SEMANTIC_MAX_CHUNKS_PER_DOC="8"
SEMANTIC_QUERYSET_FILE=""
SOURCE_PREFIXES=()

usage() {
  cat <<'EOF'
Uso:
  scripts/knowledge_pipeline.sh \
    --mode plan|run|validate \
    --source-prefix PREFIX [--source-prefix PREFIX ...] \
    [--strict-source-prefix] \
    [--round-id ROUND_ID] \
    [--artifact-dir DIR] \
    [--semantic-embedding-mode auto|openai|mock] \
    [--semantic-limit-docs N] \
    [--semantic-max-chunks-per-doc N] \
    [--semantic-queryset-file FILE]

Descricao:
  Pipeline operacional V1 para rodadas controladas de ingestao de conhecimento.
  Reaproveita:
  - scripts/round_plan.sh
  - app.services.knowledge_ingest
  - scripts/utf8_hygiene_scan.sh
  - scripts/knowledge_pipeline_semantic_validate.py

Modos:
  plan      Consolida preview da rodada sem alterar estado
  run       Executa ingestao seletiva + persistencia semantica seletiva
  validate  Valida artefatos/resultados da rodada e roda scanner UTF-8
  semantic-validate  Roda smoke semantico auditavel para a rodada/prefixo

Observacoes:
  - V1 exige pelo menos um --source-prefix explicito para evitar escopo amplo inesperado.
  - Para ligar plan/run/validate na mesma rodada, reuse o mesmo --round-id.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
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
    --round-id)
      ROUND_ID="${2:-}"
      shift 2
      ;;
    --artifact-dir)
      ARTIFACT_DIR="${2:-}"
      shift 2
      ;;
    --semantic-embedding-mode)
      SEMANTIC_EMBEDDING_MODE="${2:-}"
      shift 2
      ;;
    --semantic-limit-docs)
      SEMANTIC_LIMIT_DOCS="${2:-}"
      shift 2
      ;;
    --semantic-max-chunks-per-doc)
      SEMANTIC_MAX_CHUNKS_PER_DOC="${2:-}"
      shift 2
      ;;
    --semantic-queryset-file)
      SEMANTIC_QUERYSET_FILE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento invalido: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$MODE" ]]; then
  echo "Erro: --mode e obrigatorio" >&2
  exit 1
fi

case "$MODE" in
  plan|run|validate|semantic-validate) ;;
  *)
    echo "Erro: --mode deve ser plan, run, validate ou semantic-validate" >&2
    exit 1
    ;;
esac

if [[ "${#SOURCE_PREFIXES[@]}" -eq 0 ]]; then
  echo "Erro: V1 exige pelo menos um --source-prefix explicito." >&2
  exit 1
fi

if [[ "$MODE" == "semantic-validate" && -z "$ROUND_ID" ]]; then
  echo "Erro: --round-id e obrigatorio em semantic-validate" >&2
  exit 1
fi

if [[ -z "$ROUND_ID" ]]; then
  ROUND_ID="$(date -u +%Y%m%dT%H%M%SZ)"
fi

mkdir -p "$ARTIFACT_DIR"

COMMON_ARGS=()
for prefix in "${SOURCE_PREFIXES[@]}"; do
  COMMON_ARGS+=(--source-prefix "$prefix")
done
if [[ "$STRICT" == "1" ]]; then
  COMMON_ARGS+=(--strict-source-prefix)
fi

PLAN_ARTIFACT="$ARTIFACT_DIR/knowledge_pipeline_plan_${ROUND_ID}.json"
RUN_ARTIFACT="$ARTIFACT_DIR/knowledge_pipeline_run_${ROUND_ID}.json"
VALIDATE_ARTIFACT="$ARTIFACT_DIR/knowledge_pipeline_validate_${ROUND_ID}.json"
UTF8_ARTIFACT="$ARTIFACT_DIR/knowledge_pipeline_validate_utf8_${ROUND_ID}.json"

run_round_plan_json() {
  "$PROJECT_ROOT/scripts/round_plan.sh" "${COMMON_ARGS[@]}" --json
}

wrap_plan_artifact() {
  local plan_json_path="$1"
  local output_path="$2"
  "$PYTHON_BIN" - "$plan_json_path" "$output_path" "$ROUND_ID" "$MODE" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

plan_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
round_id = sys.argv[3]
mode = sys.argv[4]

plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
artifact = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "pipeline": "knowledge_pipeline_v1",
    "mode": mode,
    "round_id": round_id,
    "side_effects_expected": False,
    "artifacts": {
        "plan_artifact": str(output_path),
    },
    "plan": plan_payload,
}
output_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(artifact, ensure_ascii=False, indent=2))
PY
}

if [[ "$MODE" == "plan" ]]; then
  PLAN_TMP="$(mktemp)"
  trap 'rm -f "$PLAN_TMP"' EXIT
  run_round_plan_json >"$PLAN_TMP"
  wrap_plan_artifact "$PLAN_TMP" "$PLAN_ARTIFACT"
  exit 0
fi

if [[ "$MODE" == "run" ]]; then
  PLAN_TMP="$(mktemp)"
  INGEST_OUT="$(mktemp)"
  SEM_OUT="$(mktemp)"
  trap 'rm -f "$PLAN_TMP" "$INGEST_OUT" "$SEM_OUT"' EXIT

  run_round_plan_json >"$PLAN_TMP"

  if [[ -n "$SEMANTIC_LIMIT_DOCS" ]]; then
    EFFECTIVE_LIMIT_DOCS="$SEMANTIC_LIMIT_DOCS"
  else
    EFFECTIVE_LIMIT_DOCS="$("$PYTHON_BIN" - "$PLAN_TMP" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
total = int(payload.get("totals", {}).get("semantic_total_source_files", 0) or 0)
print(total if total > 0 else 1)
PY
)"
  fi

  "$PROJECT_ROOT/scripts/ingest_knowledge.sh" "${COMMON_ARGS[@]}" >"$INGEST_OUT" 2>&1
  "$PROJECT_ROOT/scripts/with-semantic-env.sh" "$PYTHON_BIN" -m app.services.knowledge_ingest \
    "${COMMON_ARGS[@]}" \
    --semantic-persist \
    --semantic-embedding-mode "$SEMANTIC_EMBEDDING_MODE" \
    --semantic-limit-docs "$EFFECTIVE_LIMIT_DOCS" \
    --semantic-max-chunks-per-doc "$SEMANTIC_MAX_CHUNKS_PER_DOC" >"$SEM_OUT" 2>&1

  "$PYTHON_BIN" - "$PLAN_TMP" "$INGEST_OUT" "$SEM_OUT" "$RUN_ARTIFACT" "$ROUND_ID" "$SEMANTIC_EMBEDDING_MODE" "$EFFECTIVE_LIMIT_DOCS" "$SEMANTIC_MAX_CHUNKS_PER_DOC" "$STRICT" <<'PY'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

plan_path = Path(sys.argv[1])
ingest_path = Path(sys.argv[2])
semantic_path = Path(sys.argv[3])
run_artifact = Path(sys.argv[4])
round_id = sys.argv[5]
embedding_mode = sys.argv[6]
semantic_limit_docs = int(sys.argv[7])
semantic_max_chunks_per_doc = int(sys.argv[8])
strict_source_prefix = bool(int(sys.argv[9]))

plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
ingest_text = ingest_path.read_text(encoding="utf-8", errors="replace")
semantic_text = semantic_path.read_text(encoding="utf-8", errors="replace")

line_patterns = {
    "total_found": r"^Arquivos encontrados:\s*(\d+)\s*$",
    "processed": r"^Arquivos processados:\s*(\d+)\s*$",
    "skipped": r"^Arquivos ignorados:\s*(\d+)\s*$",
    "errors": r"^Erros de parsing:\s*(\d+)\s*$",
    "unsupported": r"^Arquivos não suportados:\s*(\d+)\s*$",
    "chunk_total": r"^Chunks gerados:\s*(\d+)\s*$",
}

ingest_summary = {
    "selection_mode": plan_payload.get("ingest_dry_run", {}).get("selection_mode", ""),
    "source_prefixes": plan_payload.get("source_prefixes", []),
    "files_found_by_prefix": plan_payload.get("ingest_dry_run", {}).get("files_found_by_prefix", {}),
    "selected_targets_sample": plan_payload.get("ingest_dry_run", {}).get("targets_sample", []),
}
for key, pattern in line_patterns.items():
    match = re.search(pattern, ingest_text, flags=re.MULTILINE)
    ingest_summary[key] = int(match.group(1)) if match else 0

semantic_marker = "Persistência semântica:"
if semantic_marker not in semantic_text:
    raise SystemExit("Resumo semântico nao encontrado na execucao de run.")
semantic_json = semantic_text.split(semantic_marker, 1)[1]
start = semantic_json.find("{")
if start < 0:
    raise SystemExit("JSON semântico ausente na execucao de run.")
semantic_summary = json.loads(semantic_json[start:].strip())

artifact = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "pipeline": "knowledge_pipeline_v1",
    "mode": "run",
    "round_id": round_id,
    "side_effects_expected": True,
    "artifacts": {
        "run_artifact": str(run_artifact),
    },
    "config": {
        "source_prefixes": plan_payload.get("source_prefixes", []),
        "strict_source_prefix": strict_source_prefix,
        "semantic_embedding_mode": embedding_mode,
        "semantic_limit_docs": semantic_limit_docs,
        "semantic_max_chunks_per_doc": semantic_max_chunks_per_doc,
    },
    "pre_run_plan": plan_payload,
    "ingest": ingest_summary,
    "semantic": semantic_summary,
}

run_artifact.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(artifact, ensure_ascii=False, indent=2))
PY
  exit 0
fi

if [[ "$MODE" == "semantic-validate" ]]; then
  SEMANTIC_VALIDATE_CMD=(
    "$PYTHON_BIN"
    "$PROJECT_ROOT/scripts/knowledge_pipeline_semantic_validate.py"
    --round-id "$ROUND_ID"
    --artifact-dir "$ARTIFACT_DIR"
  )
  for prefix in "${SOURCE_PREFIXES[@]}"; do
    SEMANTIC_VALIDATE_CMD+=(--source-prefix "$prefix")
  done
  if [[ -n "$SEMANTIC_QUERYSET_FILE" ]]; then
    SEMANTIC_VALIDATE_CMD+=(--queryset-file "$SEMANTIC_QUERYSET_FILE")
  fi
  exec "$PROJECT_ROOT/scripts/with-semantic-env.sh" "${SEMANTIC_VALIDATE_CMD[@]}"
fi

if [[ ! -f "$RUN_ARTIFACT" ]]; then
  echo "Erro: artefato de run nao encontrado para round-id ${ROUND_ID}: $RUN_ARTIFACT" >&2
  exit 1
fi

PLAN_TMP="$(mktemp)"
trap 'rm -f "$PLAN_TMP"' EXIT
run_round_plan_json >"$PLAN_TMP"
"$PROJECT_ROOT/scripts/utf8_hygiene_scan.sh" --output "$UTF8_ARTIFACT" --pretty >/dev/null

"$PYTHON_BIN" - "$RUN_ARTIFACT" "$PLAN_TMP" "$UTF8_ARTIFACT" "$VALIDATE_ARTIFACT" "$ROUND_ID" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.services.knowledge_chunks import chunk_output_path
from app.services.knowledge_ingest import STATE_PATH, load_state
from app.services.knowledge_parsers import PARSED_DIR
from app.services.source_prefix_resolution import resolve_source_files_from_prefixes

run_artifact_path = Path(sys.argv[1])
plan_path = Path(sys.argv[2])
utf8_path = Path(sys.argv[3])
validate_path = Path(sys.argv[4])
round_id = sys.argv[5]

run_payload = json.loads(run_artifact_path.read_text(encoding="utf-8"))
plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
utf8_payload = json.loads(utf8_path.read_text(encoding="utf-8"))

state = load_state()
prefixes = list(run_payload.get("config", {}).get("source_prefixes", []))
resolved_sources, resolved_counts = resolve_source_files_from_prefixes(state, prefixes)

missing_parsed = []
missing_chunks = []
for source_file in resolved_sources:
    record = state.get("files", {}).get(source_file, {})
    parsed_path = Path(str(record.get("parsed_path", ""))) if record.get("parsed_path") else None
    chunk_path = chunk_output_path(source_file)
    if not parsed_path or not parsed_path.exists():
        missing_parsed.append(source_file)
    if not chunk_path.exists():
        missing_chunks.append(source_file)

semantic = run_payload.get("semantic", {})
ingest = run_payload.get("ingest", {})

checks = {
    "run_artifact_present": run_artifact_path.exists(),
    "run_prefixes_match_validate_prefixes": prefixes == plan_payload.get("source_prefixes", []),
    "plan_vs_run_ingest_total_match": int(plan_payload.get("totals", {}).get("ingest_total_found", 0) or 0) == int(ingest.get("total_found", 0) or 0),
    "plan_vs_run_semantic_total_match": int(plan_payload.get("totals", {}).get("semantic_total_source_files", 0) or 0) == int(semantic.get("source_files_resolved_total", 0) or 0),
    "state_resolved_total_match_run": len(resolved_sources) == int(semantic.get("source_files_resolved_total", 0) or 0),
    "parsed_artifacts_present_for_scope": not missing_parsed,
    "chunk_artifacts_present_for_scope": not missing_chunks,
    "utf8_scan_clean": int(utf8_payload.get("bad_chunks_count", 0) or 0) == 0,
}

artifact = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "pipeline": "knowledge_pipeline_v1",
    "mode": "validate",
    "round_id": round_id,
    "side_effects_expected": False,
    "artifacts": {
        "run_artifact": str(run_artifact_path),
        "validate_artifact": str(validate_path),
        "utf8_artifact": str(utf8_path),
        "state_path": str(STATE_PATH),
    },
    "scope": {
        "source_prefixes": prefixes,
        "resolved_sources_total": len(resolved_sources),
        "resolved_sources_by_prefix": resolved_counts,
        "resolved_sources_sample": resolved_sources[:20],
    },
    "run_summary": {
        "ingest_total_found": int(ingest.get("total_found", 0) or 0),
        "ingest_processed": int(ingest.get("processed", 0) or 0),
        "documents_selected": int(semantic.get("documents_selected", 0) or 0),
        "documents_processed": int(semantic.get("documents_processed", 0) or 0),
        "chunks_persisted": int(semantic.get("chunks_persisted", 0) or 0),
    },
    "checks": checks,
    "missing": {
        "parsed_source_files": missing_parsed[:20],
        "chunk_source_files": missing_chunks[:20],
    },
    "utf8_summary": {
        "total_chunks_scanned": int(utf8_payload.get("total_chunks_scanned", 0) or 0),
        "bad_chunks_count": int(utf8_payload.get("bad_chunks_count", 0) or 0),
        "affected_source_files_count": int(utf8_payload.get("affected_source_files_count", 0) or 0),
    },
}

artifact["validation_passed"] = all(checks.values())
validate_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(artifact, ensure_ascii=False, indent=2))
PY
