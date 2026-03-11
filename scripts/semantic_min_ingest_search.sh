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
  echo "ERRO: DATABASE_URL/SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN ausente"
  exit 1
fi

DOC_PATH="data/question_bank_raw/sample_assessment.md"
QUERY_TEXT="componente que controla regras de entrada e saida na instancia na VPC AWS"

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "ERRO: OPENAI_API_KEY ausente"
  exit 1
fi

if [ ! -f "$DOC_PATH" ]; then
  echo "ERRO: documento nao encontrado: $DOC_PATH"
  exit 1
fi

if [ ! -x ./.venv/bin/python ]; then
  echo "ERRO: venv nao encontrado em /lab/projects/livecopilot/.venv"
  exit 1
fi

./.venv/bin/pip install -q openai 'psycopg[binary]'

env OPENAI_API_KEY="${OPENAI_API_KEY}" DATABASE_URL="${DB_DSN}" DOC_PATH="${DOC_PATH}" QUERY_TEXT="${QUERY_TEXT}" ./.venv/bin/python - <<'PY'
import hashlib
import json
import os
import re
from pathlib import Path

import psycopg
from openai import OpenAI


def to_vector_literal(vec):
    return "[" + ",".join(str(x) for x in vec) + "]"


doc_path = Path(os.environ["DOC_PATH"])
query_text = os.environ["QUERY_TEXT"]
raw = doc_path.read_text(encoding="utf-8")
checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()

lines = [line.rstrip() for line in raw.splitlines()]
title = next((line[2:].strip() for line in lines if line.startswith("# ")), doc_path.stem)

question_blocks = []
current = []
for line in lines:
    if re.match(r"^\d+\.\s", line):
        if current:
            question_blocks.append(current)
        current = [line]
    elif current:
        current.append(line)
if current:
    question_blocks.append(current)

chunks = []
for i, block in enumerate(question_blocks[:5], start=1):
    content = "\n".join([x for x in block if x.strip()]).strip()
    first_line = block[0] if block else f"Pergunta {i}"
    chunk_title = first_line[:80]
    chunks.append(
        {
            "chunk_id": f"semantic-min-{checksum[:8]}-{i}",
            "sequence": i,
            "title": chunk_title,
            "content": content,
            "trecho_relevante": first_line,
            "tags": ["semantic-min", "real-doc", "question-bank"],
            "metadata": {"source": "minimal-semantic-ingest", "question_index": i},
        }
    )

if not chunks:
    raise SystemExit("Nenhum chunk foi gerado")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

for c in chunks:
    emb = client.embeddings.create(model="text-embedding-3-small", input=c["content"]).data[0].embedding
    if len(emb) != 1536:
        raise SystemExit(f"Dimensao inesperada para {c['chunk_id']}: {len(emb)}")
    c["embedding"] = emb

query_emb = client.embeddings.create(model="text-embedding-3-small", input=query_text).data[0].embedding
if len(query_emb) != 1536:
    raise SystemExit(f"Dimensao inesperada da query: {len(query_emb)}")

conn = psycopg.connect(os.environ["DATABASE_URL"])
with conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM documents
            WHERE source_file = %s AND checksum = %s
            """,
            (str(doc_path), checksum),
        )

        cur.execute(
            """
            INSERT INTO documents (source_file, title, doc_type, checksum, metadata_json)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            RETURNING id
            """,
            (
                str(doc_path),
                title,
                "question-bank",
                checksum,
                json.dumps({"ingest_mode": "minimal-semantic", "chunk_count": len(chunks)}),
            ),
        )
        document_id = cur.fetchone()[0]

        for c in chunks:
            cur.execute(
                """
                INSERT INTO chunks (
                    document_id, chunk_id, sequence, title, content,
                    trecho_relevante, tags, embedding, metadata_json
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s::jsonb, %s::vector, %s::jsonb
                )
                """,
                (
                    document_id,
                    c["chunk_id"],
                    c["sequence"],
                    c["title"],
                    c["content"],
                    c["trecho_relevante"],
                    json.dumps(c["tags"]),
                    to_vector_literal(c["embedding"]),
                    json.dumps(c["metadata"]),
                ),
            )

        cur.execute(
            """
            SELECT chunk_id, sequence, title, char_length(content) AS content_len,
                   embedding IS NOT NULL AS embedding_ok
            FROM chunks
            WHERE document_id = %s
            ORDER BY sequence
            """,
            (document_id,),
        )
        chunk_rows = cur.fetchall()

        qvec = to_vector_literal(query_emb)
        cur.execute(
            """
            SELECT c.chunk_id,
                   c.sequence,
                   c.title,
                   LEFT(c.content, 140) AS excerpt,
                   ROUND((1 - (c.embedding <=> %s::vector))::numeric, 6) AS similarity
            FROM chunks c
            WHERE c.document_id = %s
            ORDER BY c.embedding <=> %s::vector ASC
            LIMIT 3
            """,
            (qvec, document_id, qvec),
        )
        search_rows = cur.fetchall()

print("DOCUMENT_INGESTED:")
print(
    json.dumps(
        {
            "source_file": str(doc_path),
            "title": title,
            "checksum": checksum,
            "chunk_count": len(chunks),
            "query": query_text,
        },
        ensure_ascii=False,
    )
)

print("CHUNKS_CREATED:")
for row in chunk_rows:
    print(row)

print("VECTOR_SEARCH_RESULTS:")
for row in search_rows:
    print(row)
PY
