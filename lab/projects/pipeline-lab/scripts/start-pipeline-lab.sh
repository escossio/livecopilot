#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT_DIR"

if [ ! -d .venv ]; then
  echo "venv não encontrado em $ROOT_DIR/.venv. Execute python3 -m venv .venv antes." >&2
  exit 1
fi

# activate the venv for uvicorn
# shellcheck source=/dev/null
source .venv/bin/activate

API_LOG=/tmp/pipeline-lab-api.log
UI_LOG=/tmp/pipeline-lab-ui.log

API_CMD=".venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
UI_CMD=".venv/bin/python3 -m http.server 8090 --bind 0.0.0.0 --directory web"

setsid $API_CMD >"$API_LOG" 2>&1 &
API_PID=$!
setsid $UI_CMD >"$UI_LOG" 2>&1 &
UI_PID=$!

cat <<MSG
API iniciado (PID $API_PID) > http://10.45.0.3:8000/api  log em $API_LOG
UI iniciado  (PID $UI_PID) > http://10.45.0.3:8090/ log em $UI_LOG
MSG
