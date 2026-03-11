#!/usr/bin/env bash
set -euo pipefail

cd /lab/projects/livecopilot

if [ ! -r /etc/livecopilot-semantic.env ]; then
  echo "ERRO: sem acesso a /etc/livecopilot-semantic.env"
  exit 1
fi

set -a
# shellcheck disable=SC1091
source /etc/livecopilot-semantic.env
set +a

DB_DSN="${DATABASE_URL:-${SEMANTIC_PG_DSN:-${LIVECOPILOT_DB_DSN:-}}}"
if [ -z "${DB_DSN}" ]; then
  echo "ERRO: DATABASE_URL/SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN ausente" >&2
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "ERRO: OPENAI_API_KEY ausente"
  exit 1
fi

if [ ! -x ./.venv/bin/python ]; then
  echo "ERRO: venv não encontrado em /lab/projects/livecopilot/.venv"
  exit 1
fi

./.venv/bin/pip install -q openai 'psycopg[binary]'

env OPENAI_API_KEY="${OPENAI_API_KEY}" DATABASE_URL="${DB_DSN}" ./.venv/bin/python - <<'PY'
import os
import json
import psycopg
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

texts = [
    "liveness probe nginx example",
    "docker container healthcheck example",
]

vectors = []
for text in texts:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    vec = resp.data[0].embedding
    print(f"TEXT={text!r}")
    print(f"DIM={len(vec)}")
    print(f"HEAD={vec[:5]}")
    vectors.append(vec)

if len(vectors[0]) != 1536:
    raise SystemExit(f"Dimensão inesperada: {len(vectors[0])} (esperado 1536)")

conn = psycopg.connect(os.environ["DATABASE_URL"])
with conn:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO documents (source_file, title, doc_type, checksum, metadata_json)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            "__smoke_openai__.md",
            "Smoke OpenAI Embeddings",
            "smoke-test",
            "smoke-openai-001",
            json.dumps({"source": "manual-test"})
        ))
        document_id = cur.fetchone()[0]

        for i, (text, vec) in enumerate(zip(texts, vectors), start=1):
            cur.execute("""
                INSERT INTO chunks (
                    document_id, chunk_id, sequence, title, content,
                    trecho_relevante, tags, embedding, metadata_json
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s::jsonb, %s::vector, %s::jsonb
                )
            """, (
                document_id,
                f"smoke-openai-{i}",
                i,
                f"Smoke Chunk {i}",
                text,
                text,
                json.dumps(["smoke", "openai"]),
                "[" + ",".join(str(x) for x in vec) + "]",
                json.dumps({"model": "text-embedding-3-small"})
            ))

        cur.execute("""
            SELECT d.source_file,
                   c.chunk_id,
                   c.sequence,
                   c.title,
                   c.embedding IS NOT NULL AS embedding_ok
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.id = %s
            ORDER BY c.sequence
        """, (document_id,))
        rows = cur.fetchall()

print("ROWS:")
for row in rows:
    print(row)
PY

echo
echo "Validação extra no Postgres:"
psql "$DB_DSN" -c "
SELECT d.source_file, c.chunk_id, c.sequence, c.title, c.embedding IS NOT NULL AS embedding_ok
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE d.source_file = '__smoke_openai__.md'
ORDER BY c.sequence;
"
