#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg

FACT_TYPES = {
    "decision",
    "milestone",
    "issue",
    "fix",
    "pending",
    "insight",
    "risk",
    "checkpoint",
    "hypothesis",
    "abandoned_idea",
}

FACT_STATUSES = {"active", "historical", "partial", "abandoned", "superseded"}


def _dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise RuntimeError("DSN ausente: defina DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    return dsn


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vec) + "]"


def _json_hash(payload: Any) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _must_non_empty(payload: dict, key: str) -> str:
    value = str(payload.get(key, "")).strip()
    if not value:
        raise ValueError(f"campo obrigatorio ausente/vazio: {key}")
    return value


def _validate_payload(payload: dict[str, Any]) -> None:
    required = [
        "project_name",
        "session_id",
        "actor",
        "run_type",
        "summary_short",
        "summary_full",
        "status_md_path",
        "checkpoint_path",
    ]
    for key in required:
        _must_non_empty(payload, key)

    facts = payload.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError("campo obrigatorio facts deve ser lista nao vazia")

    for idx, fact in enumerate(facts, start=1):
        if not isinstance(fact, dict):
            raise ValueError(f"facts[{idx}] deve ser objeto")
        fact_type = _must_non_empty(fact, "fact_type")
        fact_status = _must_non_empty(fact, "fact_status")
        _must_non_empty(fact, "title")
        _must_non_empty(fact, "body")
        if fact_type not in FACT_TYPES:
            raise ValueError(f"facts[{idx}].fact_type invalido: {fact_type}")
        if fact_status not in FACT_STATUSES:
            raise ValueError(f"facts[{idx}].fact_status invalido: {fact_status}")


def _maybe_embed_texts(texts: list[str], model: str, enable_embedding: bool) -> list[list[float] | None]:
    if not enable_embedding:
        return [None for _ in texts]

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return [None for _ in texts]

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        vectors: list[list[float] | None] = []
        for text in texts:
            resp = client.embeddings.create(model=model, input=text)
            vec = resp.data[0].embedding
            if len(vec) != 1536:
                raise ValueError(f"embedding com dimensao inesperada: {len(vec)}")
            vectors.append(vec)
        return vectors
    except Exception as exc:
        print(f"WARN: falha ao gerar embeddings, fallback sem embedding: {exc}", file=sys.stderr)
        return [None for _ in texts]


def _run_chunk_content(run_payload: dict[str, Any]) -> str:
    return (
        f"Run summary ({run_payload['run_type']}): {run_payload['summary_short']}\n\n"
        f"{run_payload['summary_full']}"
    )


def _fact_chunk_content(fact: dict[str, Any]) -> str:
    return (
        f"Fact [{fact['fact_type']}/{fact['fact_status']}]: {fact['title']}\n"
        f"Component: {fact.get('component', '')} Priority: {fact.get('priority', '')}\n\n"
        f"{fact['body']}"
    ).strip()


def ingest(payload: dict[str, Any], model: str, enable_embedding: bool) -> dict[str, Any]:
    _validate_payload(payload)

    run_payload = {
        "project_name": _must_non_empty(payload, "project_name"),
        "session_id": _must_non_empty(payload, "session_id"),
        "actor": _must_non_empty(payload, "actor"),
        "run_type": _must_non_empty(payload, "run_type"),
        "summary_short": _must_non_empty(payload, "summary_short"),
        "summary_full": _must_non_empty(payload, "summary_full"),
        "status_md_path": _must_non_empty(payload, "status_md_path"),
        "checkpoint_path": _must_non_empty(payload, "checkpoint_path"),
    }
    facts = payload["facts"]

    run_key = str(payload.get("run_key", "")).strip() or _json_hash(
        {
            "run": run_payload,
            "facts": facts,
        }
    )

    run_chunk = {
        "content": _run_chunk_content(run_payload),
        "source_type": "run_summary",
        "source_path": run_payload["checkpoint_path"],
        "semantic_layer": "run",
        "tags": ["run", run_payload["run_type"], run_payload["actor"]],
        "fact_idx": None,
    }

    fact_chunks: list[dict[str, Any]] = []
    for idx, fact in enumerate(facts):
        tags = [
            "fact",
            str(fact.get("fact_type", "")).strip(),
            str(fact.get("fact_status", "")).strip(),
            str(fact.get("component", "")).strip(),
        ]
        fact_chunks.append(
            {
                "content": _fact_chunk_content(fact),
                "source_type": "fact",
                "source_path": str(fact.get("source_path", "")).strip() or run_payload["status_md_path"],
                "semantic_layer": "fact",
                "tags": [tag for tag in tags if tag],
                "fact_idx": idx,
            }
        )

    all_chunks = [run_chunk] + fact_chunks
    vectors = _maybe_embed_texts([chunk["content"] for chunk in all_chunks], model, enable_embedding)

    with psycopg.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO project_runs (
                    project_name, session_id, actor, run_type,
                    summary_short, summary_full, status_md_path, checkpoint_path, run_key
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_key)
                DO UPDATE SET
                    summary_short = EXCLUDED.summary_short,
                    summary_full = EXCLUDED.summary_full,
                    status_md_path = EXCLUDED.status_md_path,
                    checkpoint_path = EXCLUDED.checkpoint_path
                RETURNING id
                """,
                (
                    run_payload["project_name"],
                    run_payload["session_id"],
                    run_payload["actor"],
                    run_payload["run_type"],
                    run_payload["summary_short"],
                    run_payload["summary_full"],
                    run_payload["status_md_path"],
                    run_payload["checkpoint_path"],
                    run_key,
                ),
            )
            run_id = int(cur.fetchone()[0])

            fact_ids: list[int] = []
            for idx, fact in enumerate(facts):
                fact_key = str(fact.get("fact_key", "")).strip() or _json_hash(
                    {
                        "title": fact.get("title"),
                        "body": fact.get("body"),
                        "fact_type": fact.get("fact_type"),
                        "fact_status": fact.get("fact_status"),
                        "idx": idx,
                    }
                )
                cur.execute(
                    """
                    INSERT INTO project_facts (
                        run_id, fact_type, title, body, fact_status,
                        component, priority, source_path, source_section, fact_key
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id, fact_key)
                    DO UPDATE SET
                        fact_type = EXCLUDED.fact_type,
                        title = EXCLUDED.title,
                        body = EXCLUDED.body,
                        fact_status = EXCLUDED.fact_status,
                        component = EXCLUDED.component,
                        priority = EXCLUDED.priority,
                        source_path = EXCLUDED.source_path,
                        source_section = EXCLUDED.source_section
                    RETURNING id
                    """,
                    (
                        run_id,
                        _must_non_empty(fact, "fact_type"),
                        _must_non_empty(fact, "title"),
                        _must_non_empty(fact, "body"),
                        _must_non_empty(fact, "fact_status"),
                        str(fact.get("component", "")).strip() or None,
                        str(fact.get("priority", "")).strip() or None,
                        str(fact.get("source_path", "")).strip() or None,
                        str(fact.get("source_section", "")).strip() or None,
                        fact_key,
                    ),
                )
                fact_ids.append(int(cur.fetchone()[0]))

            chunks_upserted = 0
            for idx, chunk in enumerate(all_chunks):
                linked_fact_id = None
                fact_idx = chunk["fact_idx"]
                if fact_idx is not None and 0 <= int(fact_idx) < len(fact_ids):
                    linked_fact_id = fact_ids[int(fact_idx)]

                chunk_key = _json_hash(
                    {
                        "source_type": chunk["source_type"],
                        "fact_idx": fact_idx,
                        "content": chunk["content"],
                    }
                )
                vector_value = vectors[idx]
                cur.execute(
                    """
                    INSERT INTO project_memory_chunks (
                        run_id, fact_id, content, embedding,
                        source_type, source_path, semantic_layer, tags, chunk_key
                    )
                    VALUES (%s, %s, %s, %s::vector, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (run_id, chunk_key)
                    DO UPDATE SET
                        fact_id = EXCLUDED.fact_id,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        source_type = EXCLUDED.source_type,
                        source_path = EXCLUDED.source_path,
                        semantic_layer = EXCLUDED.semantic_layer,
                        tags = EXCLUDED.tags
                    """,
                    (
                        run_id,
                        linked_fact_id,
                        chunk["content"],
                        _vector_literal(vector_value) if vector_value is not None else None,
                        chunk["source_type"],
                        chunk["source_path"],
                        chunk["semantic_layer"],
                        json.dumps(chunk["tags"], ensure_ascii=False),
                        chunk_key,
                    ),
                )
                chunks_upserted += 1

    return {
        "status": "ok",
        "run_id": run_id,
        "run_key": run_key,
        "facts_upserted": len(facts),
        "chunks_upserted": chunks_upserted,
        "embeddings_enabled": bool(enable_embedding),
        "embedding_model": model,
    }


def _load_payload(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise FileNotFoundError(f"arquivo de payload nao encontrado: {input_path}")
    raw = input_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("payload JSON deve ser objeto")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestao de continuidade operacional e semantica")
    parser.add_argument("--input", required=True, help="arquivo JSON com payload canonico")
    parser.add_argument(
        "--embed-model",
        default=os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small"),
        help="modelo de embedding",
    )
    parser.add_argument(
        "--enable-embeddings",
        action="store_true",
        help="ativa tentativa de embedding (fallback automatico para NULL em caso de falha)",
    )

    args = parser.parse_args()

    try:
        payload = _load_payload(Path(args.input))
        result = ingest(payload=payload, model=args.embed_model, enable_embedding=args.enable_embeddings)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
