#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Any

import psycopg


def _dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise RuntimeError("DSN ausente: defina DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    return dsn


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vec) + "]"


def _maybe_embed_query(query: str, model: str) -> list[float] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(model=model, input=query)
        vec = resp.data[0].embedding
        if len(vec) != 1536:
            raise ValueError(f"dimensao inesperada: {len(vec)}")
        return vec
    except Exception as exc:
        print(f"WARN: sem embedding de query, fallback textual: {exc}", file=sys.stderr)
        return None


def _fetch_latest_runs(cur, project: str, limit: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT id, session_id, actor, run_type, summary_short, checkpoint_path, created_at
        FROM project_runs
        WHERE project_name = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (project, limit),
    )
    rows = cur.fetchall()
    return [
        {
            "id": int(row[0]),
            "session_id": row[1],
            "actor": row[2],
            "run_type": row[3],
            "summary_short": row[4],
            "checkpoint_path": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        }
        for row in rows
    ]


def _fetch_active_facts(cur, project: str, limit: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT f.id, f.run_id, f.fact_type, f.fact_status, f.title, f.component, f.priority, f.created_at
        FROM project_facts f
        JOIN project_runs r ON r.id = f.run_id
        WHERE r.project_name = %s
          AND f.fact_status = 'active'
        ORDER BY f.created_at DESC
        LIMIT %s
        """,
        (project, limit),
    )
    rows = cur.fetchall()
    return [
        {
            "id": int(row[0]),
            "run_id": int(row[1]),
            "fact_type": row[2],
            "fact_status": row[3],
            "title": row[4],
            "component": row[5],
            "priority": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
        }
        for row in rows
    ]


def _search_textual(cur, project: str, query: str, limit: int) -> list[dict[str, Any]]:
    like = f"%{query}%"
    cur.execute(
        """
        SELECT
            'run' AS hit_type,
            r.id AS run_id,
            NULL::bigint AS fact_id,
            r.summary_short AS title,
            r.summary_full AS excerpt,
            r.created_at
        FROM project_runs r
        WHERE r.project_name = %s
          AND (r.summary_short ILIKE %s OR r.summary_full ILIKE %s)

        UNION ALL

        SELECT
            'fact' AS hit_type,
            f.run_id,
            f.id AS fact_id,
            f.title,
            LEFT(f.body, 300) AS excerpt,
            f.created_at
        FROM project_facts f
        JOIN project_runs r ON r.id = f.run_id
        WHERE r.project_name = %s
          AND (f.title ILIKE %s OR f.body ILIKE %s)

        UNION ALL

        SELECT
            'memory_chunk' AS hit_type,
            m.run_id,
            m.fact_id,
            LEFT(m.content, 120) AS title,
            LEFT(m.content, 300) AS excerpt,
            m.created_at
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE r.project_name = %s
          AND m.content ILIKE %s

        ORDER BY created_at DESC
        LIMIT %s
        """,
        (project, like, like, project, like, like, project, like, limit),
    )
    rows = cur.fetchall()
    return [
        {
            "hit_type": row[0],
            "run_id": int(row[1]) if row[1] is not None else None,
            "fact_id": int(row[2]) if row[2] is not None else None,
            "title": row[3],
            "excerpt": row[4],
            "created_at": row[5].isoformat() if row[5] else None,
        }
        for row in rows
    ]


def _search_semantic(cur, project: str, query: str, query_vec: list[float], limit: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            m.run_id,
            m.fact_id,
            LEFT(m.content, 220) AS excerpt,
            ROUND((1 - (m.embedding <=> %s::vector))::numeric, 6) AS similarity,
            m.source_type,
            m.source_path,
            m.created_at
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE r.project_name = %s
          AND m.embedding IS NOT NULL
        ORDER BY m.embedding <=> %s::vector ASC
        LIMIT %s
        """,
        (_vector_literal(query_vec), project, _vector_literal(query_vec), limit),
    )
    rows = cur.fetchall()
    return [
        {
            "run_id": int(row[0]) if row[0] is not None else None,
            "fact_id": int(row[1]) if row[1] is not None else None,
            "excerpt": row[2],
            "similarity": float(row[3]),
            "source_type": row[4],
            "source_path": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        }
        for row in rows
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Recall de continuidade operacional")
    parser.add_argument("--project", default="livecopilot", help="nome do projeto")
    parser.add_argument("--runs", type=int, default=5, help="quantidade de runs recentes")
    parser.add_argument("--facts", type=int, default=10, help="quantidade de fatos ativos")
    parser.add_argument("--search", default=None, help="busca textual")
    parser.add_argument("--search-limit", type=int, default=10, help="limite de hits da busca")
    parser.add_argument("--semantic", action="store_true", help="ativa busca semantica de chunks")
    parser.add_argument(
        "--embed-model",
        default=os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small"),
        help="modelo de embedding para busca semantica",
    )
    parser.add_argument("--json", action="store_true", help="saida JSON")
    args = parser.parse_args()

    try:
        with psycopg.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                runs = _fetch_latest_runs(cur, args.project, max(1, args.runs))
                facts = _fetch_active_facts(cur, args.project, max(1, args.facts))

                text_hits: list[dict[str, Any]] = []
                semantic_hits: list[dict[str, Any]] = []

                if args.search:
                    text_hits = _search_textual(cur, args.project, args.search, max(1, args.search_limit))
                    if args.semantic:
                        query_vec = _maybe_embed_query(args.search, args.embed_model)
                        if query_vec is not None:
                            semantic_hits = _search_semantic(cur, args.project, args.search, query_vec, max(1, args.search_limit))

        payload = {
            "status": "ok",
            "project": args.project,
            "latest_runs": runs,
            "active_facts": facts,
            "text_hits": text_hits,
            "semantic_hits": semantic_hits,
        }

        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        print(f"project: {args.project}")
        print(f"latest_runs: {len(runs)}")
        for run in runs:
            print(
                f"  - run_id={run['id']} created_at={run['created_at']} "
                f"type={run['run_type']} actor={run['actor']} summary={run['summary_short']}"
            )

        print(f"active_facts: {len(facts)}")
        for fact in facts:
            print(
                f"  - fact_id={fact['id']} run_id={fact['run_id']} type={fact['fact_type']} "
                f"priority={fact['priority']} title={fact['title']}"
            )

        if args.search:
            print(f"text_hits: {len(text_hits)}")
            for hit in text_hits:
                print(
                    f"  - [{hit['hit_type']}] run_id={hit['run_id']} fact_id={hit['fact_id']} "
                    f"title={hit['title']}"
                )

            if args.semantic:
                print(f"semantic_hits: {len(semantic_hits)}")
                for hit in semantic_hits:
                    print(
                        f"  - run_id={hit['run_id']} fact_id={hit['fact_id']} "
                        f"sim={hit['similarity']} source={hit['source_type']} excerpt={hit['excerpt']}"
                    )

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
