#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/lab/projects/livecopilot"
cd "$PROJECT_ROOT"

if [ ! -r /etc/livecopilot-semantic.env ]; then
  echo "ERRO: sem acesso a /etc/livecopilot-semantic.env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source /etc/livecopilot-semantic.env
set +a

DB_DSN="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [[ -z "$DB_DSN" ]]; then
  echo "ERRO: DATABASE_URL ausente no ambiente canônico" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SESSION_ID="smoke-round-${STAMP}"
SUMMARY_SHORT="smoke-round-continuity-${STAMP}"
SUMMARY_FULL="Smoke curto para validar round padrao + closeout + continuidade + embedding maintenance."

./scripts/round \
  --from-last-action-only \
  --session-id "$SESSION_ID" \
  --run-type smoke \
  --actor smoke \
  --summary-short "$SUMMARY_SHORT" \
  --summary-full "$SUMMARY_FULL" \
  --checkpoint-path STATUS.md \
  --facts-file docs/continuity/examples/sample_facts.json

RUN_METRICS="$(
  DATABASE_URL="$DB_DSN" SEMANTIC_PG_DSN="$DB_DSN" ./.venv/bin/python - "$SUMMARY_SHORT" <<'PY'
import sys
import os
import psycopg

summary = sys.argv[1]
dsn = os.environ.get("DATABASE_URL") or os.environ.get("SEMANTIC_PG_DSN")
with psycopg.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, run_key
            FROM project_runs
            WHERE project_name = %s
              AND summary_short = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            ("livecopilot", summary),
        )
        row = cur.fetchone()
        if row is None:
            raise SystemExit("NOT_FOUND")
        run_id, run_key = int(row[0]), str(row[1])

        cur.execute("SELECT COUNT(*) FROM project_facts WHERE run_id = %s", (run_id,))
        facts_count = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM project_memory_chunks WHERE run_id = %s", (run_id,))
        chunks_count = int(cur.fetchone()[0])
        cur.execute(
            "SELECT COUNT(*) FROM project_memory_chunks WHERE run_id = %s AND embedding IS NULL",
            (run_id,),
        )
        missing_run = int(cur.fetchone()[0])

print(f"{run_id}|{run_key}|{facts_count}|{chunks_count}|{missing_run}")
PY
)"

if [[ "$RUN_METRICS" == "NOT_FOUND" || -z "$RUN_METRICS" ]]; then
  echo "ERRO: nao encontrou run persistido para summary_short=$SUMMARY_SHORT" >&2
  exit 1
fi

IFS='|' read -r RUN_ID RUN_KEY FACTS_COUNT CHUNKS_COUNT MISSING_RUN <<< "$RUN_METRICS"

if [[ "$FACTS_COUNT" -lt 1 ]]; then
  echo "ERRO: facts nao persistidos para run_id=${RUN_ID}" >&2
  exit 1
fi
if [[ "$CHUNKS_COUNT" -lt 1 ]]; then
  echo "ERRO: memory_chunks nao persistidos para run_id=${RUN_ID}" >&2
  exit 1
fi
if [[ "$MISSING_RUN" -ne 0 ]]; then
  echo "ERRO: run_id=${RUN_ID} ainda tem missing_embedding=${MISSING_RUN}" >&2
  exit 1
fi

for path in \
  docs/continuity/payloads \
  docs/continuity/bootstrap/latest_snapshot.txt \
  docs/continuity/bootstrap/latest_snapshot.json \
  docs/continuity/opening_context/latest_new_chat_context.txt
  do
  if [[ ! -e "$path" ]]; then
    echo "ERRO: artefato esperado ausente: $path" >&2
    exit 1
  fi
  if [[ -f "$path" && ! -s "$path" ]]; then
    echo "ERRO: artefato vazio: $path" >&2
    exit 1
  fi
done

echo "SMOKE ROUND CONTINUITY: OK"
echo "run_id=${RUN_ID}"
echo "run_key=${RUN_KEY}"
echo "facts=${FACTS_COUNT} chunks=${CHUNKS_COUNT} missing_embedding=${MISSING_RUN}"
echo "snapshot_txt=docs/continuity/bootstrap/latest_snapshot.txt"
echo "snapshot_json=docs/continuity/bootstrap/latest_snapshot.json"
echo "new_chat_context=docs/continuity/opening_context/latest_new_chat_context.txt"
