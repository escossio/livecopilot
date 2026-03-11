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


def _build_where(
    *,
    project: str,
    only_missing: bool,
    run_id: int | None,
    chunk_id: int | None,
) -> tuple[str, list[Any]]:
    filters = ["r.project_name = %s"]
    params: list[Any] = [project]

    if only_missing:
        filters.append("m.embedding IS NULL")
    if run_id is not None:
        filters.append("m.run_id = %s")
        params.append(int(run_id))
    if chunk_id is not None:
        filters.append("m.id = %s")
        params.append(int(chunk_id))

    where_sql = " AND ".join(filters)
    return where_sql, params


def _fetch_candidates(
    cur: Any,
    *,
    project: str,
    only_missing: bool,
    run_id: int | None,
    chunk_id: int | None,
    limit: int,
) -> tuple[int, list[dict[str, Any]]]:
    where_sql, params = _build_where(
        project=project,
        only_missing=only_missing,
        run_id=run_id,
        chunk_id=chunk_id,
    )

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE {where_sql}
        """,
        tuple(params),
    )
    total = int(cur.fetchone()[0])

    cur.execute(
        f"""
        SELECT m.id, m.run_id, r.run_key, m.content
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE {where_sql}
        ORDER BY m.created_at ASC, m.id ASC
        LIMIT %s
        """,
        tuple(params + [max(1, limit)]),
    )
    rows = cur.fetchall()

    candidates = [
        {
            "id": int(row[0]),
            "run_id": int(row[1]),
            "run_key": row[2],
            "content": row[3],
        }
        for row in rows
    ]
    return total, candidates


def _embed_text(client: Any, model: str, text: str) -> list[float]:
    resp = client.embeddings.create(model=model, input=text)
    vec = resp.data[0].embedding
    if len(vec) != 1536:
        raise ValueError(f"embedding com dimensao inesperada: {len(vec)}")
    return vec


def backfill_embeddings(
    *,
    project: str,
    limit: int,
    dry_run: bool,
    only_missing: bool,
    model: str,
    run_id: int | None,
    chunk_id: int | None,
    batch_size: int,
) -> dict[str, Any]:
    if limit <= 0:
        raise ValueError("--limit deve ser > 0")
    if batch_size <= 0:
        raise ValueError("--batch-size deve ser > 0")

    with psycopg.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            total_found, candidates = _fetch_candidates(
                cur,
                project=project,
                only_missing=only_missing,
                run_id=run_id,
                chunk_id=chunk_id,
                limit=limit,
            )

            selected = len(candidates)
            result = {
                "status": "ok",
                "project": project,
                "model": model,
                "only_missing": only_missing,
                "run_id": run_id,
                "chunk_id": chunk_id,
                "total_candidates": total_found,
                "selected_by_limit": selected,
                "processed": 0,
                "updated": 0,
                "failed": 0,
                "dry_run": dry_run,
                "failures": [],
            }

            if dry_run or selected == 0:
                return result

            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY ausente; nao foi possivel executar backfill real")

            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            for start in range(0, selected, batch_size):
                batch = candidates[start : start + batch_size]
                for item in batch:
                    result["processed"] += 1
                    chunk_pk = int(item["id"])
                    content = str(item["content"] or "").strip()
                    if not content:
                        result["failed"] += 1
                        result["failures"].append(
                            {
                                "chunk_id": chunk_pk,
                                "error": "content vazio",
                            }
                        )
                        continue

                    try:
                        vec = _embed_text(client=client, model=model, text=content)
                        if only_missing:
                            cur.execute(
                                """
                                UPDATE project_memory_chunks
                                SET embedding = %s::vector
                                WHERE id = %s
                                  AND embedding IS NULL
                                """,
                                (_vector_literal(vec), chunk_pk),
                            )
                        else:
                            cur.execute(
                                """
                                UPDATE project_memory_chunks
                                SET embedding = %s::vector
                                WHERE id = %s
                                """,
                                (_vector_literal(vec), chunk_pk),
                            )
                        if int(cur.rowcount or 0) > 0:
                            result["updated"] += 1
                    except Exception as exc:
                        result["failed"] += 1
                        result["failures"].append(
                            {
                                "chunk_id": chunk_pk,
                                "error": str(exc),
                            }
                        )
                conn.commit()

            return result


def _render_text(payload: dict[str, Any]) -> str:
    lines = [
        "CONTINUITY EMBEDDING BACKFILL RESULT",
        f"project: {payload['project']}",
        f"model: {payload['model']}",
        f"only_missing: {payload['only_missing']}",
        f"dry_run: {payload['dry_run']}",
        f"total_candidates: {payload['total_candidates']}",
        f"selected_by_limit: {payload['selected_by_limit']}",
        f"processed: {payload['processed']}",
        f"updated: {payload['updated']}",
        f"failed: {payload['failed']}",
    ]
    failures = payload.get("failures") or []
    if failures:
        lines.append("failures:")
        for item in failures[:10]:
            lines.append(f"- chunk_id={item.get('chunk_id')} error={item.get('error')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill incremental de embeddings para project_memory_chunks")
    parser.add_argument("--project", default="livecopilot", help="nome do projeto")
    parser.add_argument("--limit", type=int, default=50, help="maximo de chunks por execucao")
    parser.add_argument("--dry-run", action="store_true", help="nao grava, so mostra contagem")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        default=True,
        help="processa apenas embedding IS NULL (padrao)",
    )
    parser.add_argument(
        "--include-filled",
        action="store_true",
        help="permite reprocessar chunks ja preenchidos (desativa only-missing)",
    )
    parser.add_argument("--run-id", type=int, default=None, help="filtra por run_id")
    parser.add_argument("--chunk-id", type=int, default=None, help="filtra por id do chunk")
    parser.add_argument("--batch-size", type=int, default=10, help="tamanho do lote")
    parser.add_argument(
        "--model",
        default=os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small"),
        help="modelo de embedding",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text", help="formato da saida")
    args = parser.parse_args()

    try:
        payload = backfill_embeddings(
            project=str(args.project).strip() or "livecopilot",
            limit=int(args.limit),
            dry_run=bool(args.dry_run),
            only_missing=False if args.include_filled else bool(args.only_missing),
            model=str(args.model).strip() or "text-embedding-3-small",
            run_id=args.run_id,
            chunk_id=args.chunk_id,
            batch_size=int(args.batch_size),
        )
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(_render_text(payload))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
