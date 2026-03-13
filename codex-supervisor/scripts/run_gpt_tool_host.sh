#!/usr/bin/env bash
set -euo pipefail

# Credencial recomendada: export SUPERVISOR_API_TOKEN no ambiente chamador.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

exec python3 -m supervisor.gpt_tool_host "$@"
