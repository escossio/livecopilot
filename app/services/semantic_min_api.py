import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

from app.services.markdown_chunker import split_markdown_by_sections


def _to_vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vec) + "]"


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


def _parse_vector_literal(raw: str) -> list[float]:
    text = (raw or "").strip()
    if not text.startswith("[") or not text.endswith("]"):
        return []
    body = text[1:-1].strip()
    if not body:
        return []
    return [float(item.strip()) for item in body.split(",") if item.strip()]


def _normalize_source_file(file_path: Optional[str], explicit_source: Optional[str]) -> str:
    if explicit_source:
        return explicit_source
    if file_path:
        return file_path
    return "__inline_semantic_min__.txt"


def _build_chunks(text: str, max_chunks: int) -> list[dict[str, Any]]:
    lines = [line.rstrip() for line in text.splitlines()]

    numbered_blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if re.match(r"^\d+\.\s", line):
            if current:
                numbered_blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        numbered_blocks.append(current)

    chunks: list[dict[str, Any]] = []
    if numbered_blocks:
        for idx, block in enumerate(numbered_blocks[:max_chunks], start=1):
            content = "\n".join([x for x in block if x.strip()]).strip()
            if not content:
                continue
            first_line = block[0]
            chunks.append(
                {
                    "sequence": idx,
                    "title": first_line[:100],
                    "content": content,
                    "trecho_relevante": first_line,
                }
            )
    else:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for idx, paragraph in enumerate(paragraphs[:max_chunks], start=1):
            title = paragraph.splitlines()[0][:100]
            chunks.append(
                {
                    "sequence": idx,
                    "title": title,
                    "content": paragraph,
                    "trecho_relevante": title,
                }
            )

    if not chunks and text.strip():
        first = text.strip().splitlines()[0][:100]
        chunks.append(
            {
                "sequence": 1,
                "title": first,
                "content": text.strip(),
                "trecho_relevante": first,
            }
        )

    return chunks


def _count_markdown_headings(text: str) -> int:
    return len(re.findall(r"(?m)^#{1,3}\s+\S+", text or ""))


def _build_chunks_with_markdown_sections(
    *,
    text: str,
    max_chunks: int,
    resolved_file_path: Optional[str],
) -> list[dict[str, Any]]:
    is_markdown = bool(resolved_file_path and Path(resolved_file_path).suffix.lower() in {".md", ".markdown"})
    if not is_markdown:
        return _build_chunks(text, max_chunks=max_chunks)

    if _count_markdown_headings(text) < 3:
        return _build_chunks(text, max_chunks=max_chunks)

    try:
        section_chunks = split_markdown_by_sections(text)
        if not section_chunks:
            return _build_chunks(text, max_chunks=max_chunks)
        if len(section_chunks) > max_chunks:
            major_sections = [chunk for chunk in section_chunks if int(chunk.get("heading_level", 3) or 3) <= 2]
            if major_sections:
                section_chunks = major_sections
        chunks: list[dict[str, Any]] = []
        for idx, chunk in enumerate(section_chunks[:max_chunks], start=1):
            title = str(chunk.get("title", "")).strip() or f"Section {idx}"
            content = str(chunk.get("content", "")).strip()
            if not content:
                continue
            chunks.append(
                {
                    "sequence": idx,
                    "title": title[:100],
                    "content": content,
                    "trecho_relevante": title[:180],
                }
            )
        if chunks:
            return chunks
    except Exception:
        # Fallback obrigatório para manter compatibilidade do fluxo atual.
        pass

    return _build_chunks(text, max_chunks=max_chunks)


def _load_text(file_path: Optional[str], text: Optional[str]) -> tuple[str, Optional[str]]:
    if file_path:
        p = Path(file_path).expanduser()
        raw = p.read_text(encoding="utf-8")
        return raw, str(p)
    return (text or ""), None


def _get_clients() -> tuple[Any, str, str]:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY ausente")

    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise ValueError("DSN ausente: configure DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    model = os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small")
    return OpenAI(api_key=api_key), dsn, model


def ingest_min_document(
    *,
    file_path: Optional[str],
    text: Optional[str],
    source_file: Optional[str],
    title: Optional[str],
    max_chunks: int,
) -> dict[str, Any]:
    import psycopg

    raw_text, resolved_file_path = _load_text(file_path=file_path, text=text)
    if not raw_text.strip():
        raise ValueError("conteudo vazio para ingestao")

    chunks = _build_chunks_with_markdown_sections(
        text=raw_text,
        max_chunks=max_chunks,
        resolved_file_path=resolved_file_path,
    )
    if not chunks:
        raise ValueError("nenhum chunk gerado")

    checksum = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    chosen_source_file = _normalize_source_file(resolved_file_path, source_file)

    if not title:
        first_line = raw_text.strip().splitlines()[0]
        title = first_line.lstrip("# ").strip()[:120]

    client, dsn, model = _get_clients()

    for chunk in chunks:
        resp = client.embeddings.create(model=model, input=chunk["content"])
        vec = resp.data[0].embedding
        if len(vec) != 1536:
            raise ValueError(f"dimensao inesperada: {len(vec)}")
        chunk["embedding"] = vec
        chunk["chunk_id"] = f"semantic-api-{checksum[:8]}-{chunk['sequence']}"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM documents
                WHERE source_file = %s AND checksum = %s
                """,
                (chosen_source_file, checksum),
            )

            cur.execute(
                """
                INSERT INTO documents (source_file, title, doc_type, checksum, metadata_json)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                RETURNING id
                """,
                (
                    chosen_source_file,
                    title,
                    "semantic-min",
                    checksum,
                    json.dumps({"ingest_mode": "api-min", "chunk_count": len(chunks)}),
                ),
            )
            document_id = cur.fetchone()[0]

            for chunk in chunks:
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
                        chunk["chunk_id"],
                        chunk["sequence"],
                        chunk["title"],
                        chunk["content"],
                        chunk["trecho_relevante"],
                        json.dumps(["semantic-api", "semantic-min"]),
                        _to_vector_literal(chunk["embedding"]),
                        json.dumps({"model": model}),
                    ),
                )

            cur.execute(
                """
                SELECT chunk_id, sequence, title, embedding IS NOT NULL AS embedding_ok
                FROM chunks
                WHERE document_id = %s
                ORDER BY sequence
                """,
                (document_id,),
            )
            rows = cur.fetchall()
            cur.execute("DELETE FROM semantic_search_cache")
            response_cache_cleared = int(cur.rowcount or 0)

    return {
        "document": {
            "document_id": document_id,
            "source_file": chosen_source_file,
            "title": title,
            "checksum": checksum,
            "chunk_count": len(chunks),
        },
        "chunks": [
            {
                "chunk_id": row[0],
                "sequence": row[1],
                "title": row[2],
                "embedding_ok": bool(row[3]),
            }
            for row in rows
        ],
        "cache_invalidation": {
            "semantic_search_cache_entries_cleared": response_cache_cleared,
        },
    }


def semantic_search(*, query: str, limit: int, source_file: Optional[str] = None) -> dict[str, Any]:
    import psycopg

    q = query.strip()
    if not q:
        raise ValueError("query vazia")

    client, dsn, model = _get_clients()
    q_norm = normalize_query(q)
    relevance_floor = 0.0
    qvec: list[float] = []
    search_cache_hit = False
    embedding_cache_hit = False
    openai_called = False
    started_at = time.monotonic()

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            if not source_file:
                cur.execute(
                    """
                    SELECT response_json
                    FROM semantic_search_cache
                    WHERE query_normalized = %s
                      AND embed_model = %s
                      AND limit_n = %s
                      AND relevance_floor = %s
                    """,
                    (q_norm, model, int(limit), relevance_floor),
                )
                cached_response = cur.fetchone()
                if cached_response and cached_response[0]:
                    search_cache_hit = True
                    cur.execute(
                        """
                        UPDATE semantic_search_cache
                        SET last_used_at = NOW(), hit_count = hit_count + 1
                        WHERE query_normalized = %s
                          AND embed_model = %s
                          AND limit_n = %s
                          AND relevance_floor = %s
                        """,
                        (q_norm, model, int(limit), relevance_floor),
                    )
                    payload = cached_response[0]
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if not isinstance(payload, dict):
                        payload = {}
                    return {
                        "query": payload.get("query", q),
                        "query_normalized": payload.get("query_normalized", q_norm),
                        "model": payload.get("model", model),
                        "count": int(payload.get("count", 0)),
                        "search_cache_hit": True,
                        "embedding_cache_hit": False,
                        "openai_called": False,
                        "semantic_path": "response_cache",
                        "semantic_duration_ms": int((time.monotonic() - started_at) * 1000),
                        "results": payload.get("results", []),
                    }

            cur.execute(
                """
                SELECT embedding::text
                FROM query_embedding_cache
                WHERE query_normalized = %s AND embed_model = %s
                """,
                (q_norm, model),
            )
            cached = cur.fetchone()
            if cached and cached[0]:
                qvec = _parse_vector_literal(cached[0])
                embedding_cache_hit = True
                cur.execute(
                    """
                    UPDATE query_embedding_cache
                    SET last_used_at = NOW(), hit_count = hit_count + 1
                    WHERE query_normalized = %s AND embed_model = %s
                    """,
                    (q_norm, model),
                )
            else:
                openai_called = True
                qvec = client.embeddings.create(model=model, input=q).data[0].embedding
                if len(qvec) != 1536:
                    raise ValueError(f"dimensao inesperada da query: {len(qvec)}")
                cur.execute(
                    """
                    INSERT INTO query_embedding_cache (
                        query_raw, query_normalized, embed_model, embedding, created_at, last_used_at, hit_count
                    )
                    VALUES (%s, %s, %s, %s::vector, NOW(), NOW(), 1)
                    ON CONFLICT (query_normalized, embed_model)
                    DO UPDATE SET
                        query_raw = EXCLUDED.query_raw,
                        embedding = EXCLUDED.embedding,
                        last_used_at = NOW(),
                        hit_count = query_embedding_cache.hit_count + 1
                    """,
                    (q, q_norm, model, _to_vector_literal(qvec)),
                )

            if len(qvec) != 1536:
                raise ValueError(f"dimensao inesperada da query: {len(qvec)}")

            qvec_literal = _to_vector_literal(qvec)
            sql = """
                SELECT
                    d.source_file,
                    c.chunk_id,
                    c.title,
                    ROUND((1 - (c.embedding <=> %s::vector))::numeric, 6) AS similarity,
                    LEFT(c.content, 180) AS snippet
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.embedding IS NOT NULL
            """
            params: list[Any] = [qvec_literal]
            if source_file:
                sql += " AND d.source_file = %s"
                params.append(source_file)
            sql += " ORDER BY c.embedding <=> %s::vector ASC LIMIT %s"
            params.extend([qvec_literal, limit])
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()

            results = [
                {
                    "source_file": row[0],
                    "chunk_id": row[1],
                    "title": row[2],
                    "similarity": float(row[3]),
                    "snippet": row[4],
                }
                for row in rows
            ]
            if not source_file:
                cur.execute(
                    """
                    INSERT INTO semantic_search_cache (
                        query_normalized, embed_model, limit_n, relevance_floor,
                        response_json, created_at, last_used_at, hit_count
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW(), 1)
                    ON CONFLICT (query_normalized, embed_model, limit_n, relevance_floor)
                    DO UPDATE SET
                        response_json = EXCLUDED.response_json,
                        last_used_at = NOW(),
                        hit_count = semantic_search_cache.hit_count + 1
                    """,
                    (
                        q_norm,
                        model,
                        int(limit),
                        relevance_floor,
                        json.dumps(
                            {
                                "query": q,
                                "query_normalized": q_norm,
                                "model": model,
                                "count": len(results),
                                "results": results,
                            }
                        ),
                    ),
                )

    semantic_path = "embedding_cache" if embedding_cache_hit else "openai_fresh"
    return {
        "query": q,
        "query_normalized": q_norm,
        "model": model,
        "count": len(results),
        "search_cache_hit": search_cache_hit,
        "embedding_cache_hit": embedding_cache_hit,
        "openai_called": openai_called,
        "semantic_path": semantic_path,
        "semantic_duration_ms": int((time.monotonic() - started_at) * 1000),
        "results": results,
    }
