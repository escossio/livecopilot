#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT_DIR"

printf 'Listeners em 8000/8090:\n'
ss -tulnp | grep -E '8000|8090' || true

printf '\nProcessos relevantes:\n'
ps -eo pid,cmd | grep 'uvicorn app.main:app' | grep -v grep || true
ps -eo pid,cmd | grep 'http.server 8090' | grep -v grep || true

printf '\nValidações rápidas:\n'
echo -n 'API (127.0.0.1:8000/api/runs) -> '
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/runs

echo -n 'UI (127.0.0.1:8090) -> '
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090
