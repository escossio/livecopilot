#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/lab/projects/livecopilot"
cd "$PROJECT_ROOT"

HYBRID_JSON="$(mktemp)"
SEMANTIC_JSON="$(mktemp)"
cleanup() {
  rm -f "$HYBRID_JSON" "$SEMANTIC_JSON"
}
trap cleanup EXIT

./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "continuidade" \
  --mode hybrid \
  --facts-limit 6 \
  --memory-limit 5 \
  --format json > "$HYBRID_JSON"

./scripts/project_brain_query.sh \
  --project livecopilot \
  --query "realtime" \
  --mode semantic \
  --memory-limit 5 \
  --format json > "$SEMANTIC_JSON"

./.venv/bin/python - "$HYBRID_JSON" "$SEMANTIC_JSON" <<'PY'
import json
import sys
from pathlib import Path

hybrid_path = Path(sys.argv[1])
semantic_path = Path(sys.argv[2])

def parse_last_json(path: Path) -> dict:
    # Some commands can emit structured logs before the final payload.
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Try single-line JSON first (fast path).
    for raw in reversed(lines):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and "status" in parsed:
                return parsed
        except Exception:
            continue
    # Fallback: try parsing from each line start to EOF (supports pretty JSON payload).
    for idx in range(len(lines)):
        blob = "\n".join(lines[idx:])
        try:
            parsed = json.loads(blob)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue
    raise ValueError(f"sem JSON valido em {path}")

hybrid = parse_last_json(hybrid_path)
semantic = parse_last_json(semantic_path)

def fail(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)

hybrid_warn = hybrid.get("semantic_warning")
semantic_warn = semantic.get("semantic_warning")
hybrid_hits = hybrid.get("semantic_hits") or []
semantic_hits = semantic.get("semantic_hits") or []
hybrid_status = str(hybrid.get("status") or "").strip().lower()
semantic_status = str(semantic.get("status") or "").strip().lower()

if hybrid_warn is not None:
    fail(
        "wrapper retornou semantic_warning em modo hybrid: "
        f"{hybrid_warn}. Caminho recomendado: scripts/project_brain_query.sh com /etc/livecopilot-semantic.env valido."
    )
if semantic_warn is not None:
    fail(
        "wrapper retornou semantic_warning em modo semantic: "
        f"{semantic_warn}. Caminho recomendado: validar OPENAI_API_KEY e embeddings via scripts/maintain_continuity_embeddings.sh."
    )

if hybrid_status != "ok":
    fail(f"modo hybrid retornou status invalido: {hybrid.get('status')}")
if semantic_status != "ok":
    fail(f"modo semantic retornou status invalido: {semantic.get('status')}")

print("SMOKE PROJECT BRAIN WRAPPER: OK")
print(f"hybrid_semantic_hits={len(hybrid_hits)}")
print(f"semantic_hits={len(semantic_hits)}")
print("semantic_warning_hybrid=null")
print("semantic_warning_semantic=null")
PY
