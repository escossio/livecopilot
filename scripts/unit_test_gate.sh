#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
export PYTHONPATH=.

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Nenhum interpretador Python compativel encontrado." >&2
  exit 1
fi

"$PYTHON_BIN" -m unittest -v \
  tests/test_curated_sources_validation.py \
  tests/test_knowledge_ingest_cli_modes.py \
  tests/test_livecopilot_interface_api.py \
  tests/test_knowledge_pipeline_cli_contract.py \
  tests/test_knowledge_pipeline_semantic_validate.py \
  tests/test_question_bank_items.py \
  tests/test_question_bank_metadata.py \
  tests/test_source_prefix_resolution.py \
  tests/test_transcription_routing.py
