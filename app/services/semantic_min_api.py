import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.services.markdown_chunker import split_markdown_by_sections

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_INDEX_DIR = PROJECT_ROOT / "data" / "knowledge_index"
KNOWLEDGE_STATE_PATH = KNOWLEDGE_INDEX_DIR / "knowledge_state.json"
KNOWLEDGE_MANIFEST_PATH = KNOWLEDGE_INDEX_DIR / "knowledge_manifest.json"


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


def _get_dsn_and_model() -> tuple[str, str]:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise ValueError("DSN ausente: configure DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    model = os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small")
    return dsn, model


def _get_search_runtime(embedding_mode: str) -> tuple[Any | None, str, str, bool]:
    mode = (embedding_mode or "openai").strip().lower()
    if mode not in {"auto", "openai", "mock"}:
        raise ValueError("embedding_mode invalido: use auto|openai|mock")

    dsn, model = _get_dsn_and_model()
    if mode == "mock":
        return None, dsn, "mock-embedding-v1", False

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if mode == "auto" and not api_key:
        return None, dsn, "mock-embedding-v1", False
    if not api_key:
        raise ValueError("OPENAI_API_KEY ausente")

    from openai import OpenAI

    return OpenAI(api_key=api_key), dsn, model, True


def _normalize_doc_key(source_file: str, sha256_hex: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._/-]+", "-", source_file).strip("-")
    return f"doc::{normalized}::{sha256_hex[:12]}"


def _mock_embedding(text: str, dim: int = 1536) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
    values: list[float] = []
    seed = digest
    while len(values) < dim:
        for byte in seed:
            # Range [-1, 1], deterministico e estavel para execucao sem credenciais.
            values.append((byte / 127.5) - 1.0)
            if len(values) >= dim:
                break
        seed = hashlib.sha256(seed).digest()
    return values


def _build_canonical_chunk_id(doc_key: str, sequence: int, content: str) -> str:
    content_hash = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()[:8]
    return f"chunk::{doc_key}::{int(sequence):04d}::{content_hash}"


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {}


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_knowledge_state_files() -> tuple[dict[str, Any], dict[str, Any]]:
    state = _load_json_file(KNOWLEDGE_STATE_PATH)
    if not isinstance(state.get("files"), dict):
        state["files"] = {}
    manifest = _load_json_file(KNOWLEDGE_MANIFEST_PATH)
    if not isinstance(manifest.get("documents"), list):
        manifest["documents"] = []
    return state, manifest


def _resolve_docs_from_state(
    state: dict[str, Any],
    *,
    limit_docs: int,
    source_files: Optional[list[str]] = None,
) -> list[tuple[str, dict[str, Any]]]:
    files = state.get("files", {})
    if not isinstance(files, dict):
        return []
    selected: list[tuple[str, dict[str, Any]]] = []
    source_filter = {item.strip() for item in (source_files or []) if item and item.strip()}
    for source_file in sorted(files.keys()):
        record = files.get(source_file, {})
        if not isinstance(record, dict):
            continue
        if source_filter and source_file not in source_filter:
            continue
        chunk_path = Path(str(record.get("chunk_path", "")))
        status = str(record.get("status", "")).strip().lower()
        chunk_count = int(record.get("chunk_count", 0) or 0)
        if status != "parsed" or chunk_count <= 0:
            continue
        if not chunk_path.exists():
            continue
        selected.append((source_file, record))
        if len(selected) >= max(limit_docs, 1):
            break
    return selected


def ingest_knowledge_base_min(
    *,
    limit_docs: int = 1,
    max_chunks_per_doc: int = 8,
    source_files: Optional[list[str]] = None,
    embedding_mode: str = "auto",
) -> dict[str, Any]:
    import psycopg

    dsn, model = _get_dsn_and_model()
    mode = (embedding_mode or "auto").strip().lower()
    if mode not in {"auto", "openai", "mock"}:
        raise ValueError("embedding_mode invalido: use auto|openai|mock")

    use_openai = mode == "openai" or (mode == "auto" and bool(os.getenv("OPENAI_API_KEY", "").strip()))
    client = None
    if use_openai:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            if mode == "openai":
                raise ValueError("OPENAI_API_KEY ausente para embedding_mode=openai")
            use_openai = False
        else:
            client = OpenAI(api_key=api_key)

    state, manifest = _load_knowledge_state_files()
    selected_docs = _resolve_docs_from_state(state, limit_docs=limit_docs, source_files=source_files)
    started_at = datetime.now(timezone.utc).isoformat()
    results: list[dict[str, Any]] = []

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            for source_file, record in selected_docs:
                states = ["discovered", "extracted", "chunked"]
                chunk_path = Path(str(record.get("chunk_path", "")))
                parsed_path = Path(str(record.get("parsed_path", "")))
                sha256_hex = str(record.get("sha256", "") or "")
                doc_result: dict[str, Any] = {
                    "source_file": source_file,
                    "states": states[:],
                    "status": "failed",
                    "error": "",
                    "document_id": None,
                    "chunks_persisted": 0,
                    "embedding_mode_used": "openai" if use_openai else "mock",
                }
                try:
                    chunk_payload = _load_json_file(chunk_path)
                    chunks = chunk_payload.get("chunks", [])
                    if not isinstance(chunks, list) or not chunks:
                        raise ValueError("chunk payload sem chunks")

                    max_chunks = max(1, int(max_chunks_per_doc))
                    chunks = chunks[:max_chunks]
                    title = str(chunk_payload.get("title", "") or source_file)
                    doc_checksum = sha256_hex or hashlib.sha256((source_file + str(chunks)).encode("utf-8")).hexdigest()
                    doc_key = _normalize_doc_key(source_file, doc_checksum)

                    cur.execute(
                        "DELETE FROM documents WHERE source_file = %s AND checksum = %s",
                        (source_file, doc_checksum),
                    )
                    dedup_deleted = int(cur.rowcount or 0)

                    cur.execute(
                        """
                        INSERT INTO documents (source_file, title, doc_type, checksum, metadata_json)
                        VALUES (%s, %s, %s, %s, %s::jsonb)
                        RETURNING id
                        """,
                        (
                            source_file,
                            title,
                            "knowledge",
                            doc_checksum,
                            json.dumps(
                                {
                                    "ingest_mode": "knowledge-base-min",
                                    "document_key": doc_key,
                                    "chunk_path": str(chunk_path),
                                    "parsed_path": str(parsed_path),
                                    "embedding_model": model if use_openai else "mock-embedding-v1",
                                    "dedup_deleted_documents": dedup_deleted,
                                }
                            ),
                        ),
                    )
                    document_id = int(cur.fetchone()[0])

                    embedded_count = 0
                    for chunk in chunks:
                        content = str(chunk.get("content", "") or "").strip()
                        if not content:
                            continue
                        sequence = int(chunk.get("sequence", 0) or 0)
                        if sequence <= 0:
                            sequence = embedded_count + 1
                        chunk_id = _build_canonical_chunk_id(doc_key, sequence, content)
                        trecho = str(chunk.get("trecho_relevante", "") or content[:180])
                        tags = chunk.get("tags", {})
                        if not isinstance(tags, dict):
                            tags = {"all": []}
                        if use_openai and client is not None:
                            vec = client.embeddings.create(model=model, input=content).data[0].embedding
                            embedding_status = "ok"
                        else:
                            vec = _mock_embedding(content)
                            embedding_status = "mock"
                        if len(vec) != 1536:
                            raise ValueError(f"dimensao inesperada no chunk {sequence}: {len(vec)}")
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
                                chunk_id,
                                sequence,
                                str(chunk.get("title", "") or title)[:200],
                                content,
                                trecho[:500],
                                json.dumps(tags),
                                _to_vector_literal(vec),
                                json.dumps(
                                    {
                                        "model": model if use_openai else "mock-embedding-v1",
                                        "embedding_status": embedding_status,
                                        "document_key": doc_key,
                                        "source_chunk_id": str(chunk.get("chunk_id", "")),
                                    }
                                ),
                            ),
                        )
                        embedded_count += 1

                    states.append("embedded")

                    cur.execute(
                        "SELECT COUNT(*) FROM chunks WHERE document_id = %s",
                        (document_id,),
                    )
                    persisted_chunks = int(cur.fetchone()[0] or 0)
                    if persisted_chunks <= 0:
                        raise ValueError("persistencia sem chunks")
                    states.append("persisted")
                    states.append("validated")

                    record["semantic_document_id"] = document_id
                    record["semantic_checksum"] = doc_checksum
                    record["semantic_status"] = "validated"
                    record["semantic_last_ingested_at"] = datetime.now(timezone.utc).isoformat()
                    record["semantic_chunk_count"] = persisted_chunks
                    record["semantic_embedding_model"] = model if use_openai else "mock-embedding-v1"
                    record["semantic_states"] = states
                    record.pop("semantic_last_error", None)

                    doc_result.update(
                        {
                            "states": states,
                            "status": "validated",
                            "document_id": document_id,
                            "chunks_persisted": persisted_chunks,
                        }
                    )
                except Exception as exc:
                    failure_reason = str(exc)
                    record["semantic_status"] = "failed"
                    record["semantic_last_error"] = failure_reason
                    record["semantic_last_ingested_at"] = datetime.now(timezone.utc).isoformat()
                    states.append("failed")
                    doc_result.update({"states": states, "error": failure_reason, "status": "failed"})
                results.append(doc_result)

            try:
                cur.execute("DELETE FROM semantic_search_cache")
                search_cache_cleared = int(cur.rowcount or 0)
            except Exception:
                search_cache_cleared = 0
            try:
                cur.execute("DELETE FROM query_embedding_cache")
                embedding_cache_cleared = int(cur.rowcount or 0)
            except Exception:
                embedding_cache_cleared = 0

    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_json_file(KNOWLEDGE_STATE_PATH, state)

    manifest_docs = manifest.get("documents", [])
    if not isinstance(manifest_docs, list):
        manifest_docs = []
    manifest_by_source = {str(item.get("source_file", "")): item for item in manifest_docs if isinstance(item, dict)}
    for item in results:
        source_file = item.get("source_file", "")
        doc_meta = manifest_by_source.get(source_file)
        if not doc_meta:
            continue
        doc_meta["semantic_status"] = item.get("status")
        doc_meta["semantic_document_id"] = item.get("document_id")
        doc_meta["semantic_chunk_count"] = item.get("chunks_persisted", 0)
        if item.get("status") != "failed":
            doc_meta.pop("semantic_last_error", None)
        else:
            doc_meta["semantic_last_error"] = item.get("error", "")
    manifest["documents"] = list(manifest_by_source.values())
    manifest["embedding_status"] = "ready" if all(item.get("status") == "validated" for item in results) and results else "partial"
    manifest["vector_store_status"] = "built" if any(item.get("status") == "validated" for item in results) else "not_built"
    manifest["semantic_last_ingestion"] = {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "documents_selected": len(selected_docs),
        "documents_validated": sum(1 for item in results if item.get("status") == "validated"),
        "documents_failed": sum(1 for item in results if item.get("status") == "failed"),
        "chunks_persisted": sum(int(item.get("chunks_persisted", 0) or 0) for item in results),
        "embedding_mode": "openai" if use_openai else "mock",
    }
    _write_json_file(KNOWLEDGE_MANIFEST_PATH, manifest)

    return {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "documents_selected": len(selected_docs),
        "documents_processed": len(results),
        "documents_validated": sum(1 for item in results if item.get("status") == "validated"),
        "documents_failed": sum(1 for item in results if item.get("status") == "failed"),
        "chunks_persisted": sum(int(item.get("chunks_persisted", 0) or 0) for item in results),
        "states_final": sorted({str(item.get("status", "")) for item in results if str(item.get("status", ""))}),
        "results": results,
        "embedding_mode_used": "openai" if use_openai else "mock",
        "manifest_path": str(KNOWLEDGE_MANIFEST_PATH),
        "state_path": str(KNOWLEDGE_STATE_PATH),
        "cache_invalidation": {
            "semantic_search_cache_entries_cleared": search_cache_cleared,
            "query_embedding_cache_entries_cleared": embedding_cache_cleared,
        },
    }


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


def semantic_search_with_mode(
    *,
    query: str,
    limit: int,
    source_file: Optional[str] = None,
    embedding_mode: str = "auto",
) -> dict[str, Any]:
    import psycopg

    q = query.strip()
    if not q:
        raise ValueError("query vazia")

    client, dsn, model, use_openai = _get_search_runtime(embedding_mode)
    q_norm = normalize_query(q)
    relevance_floor = 0.0
    qvec: list[float] = []
    search_cache_hit = False
    embedding_cache_hit = False
    openai_called = False
    snippet_fallback_due_encoding = False
    snippet_fallback_error = ""
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
                        "snippet_fallback_due_encoding": bool(payload.get("snippet_fallback_due_encoding", False)),
                        "snippet_fallback_error": str(payload.get("snippet_fallback_error", "") or ""),
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
                if use_openai:
                    openai_called = True
                    qvec = client.embeddings.create(model=model, input=q).data[0].embedding
                else:
                    qvec = _mock_embedding(q)
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
                    {snippet_expr} AS snippet
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

            cur.execute("SAVEPOINT semantic_search_snippet")
            try:
                cur.execute(sql.format(snippet_expr="LEFT(c.content, 180)"), tuple(params))
                rows = cur.fetchall()
            except psycopg.errors.CharacterNotInRepertoire as exc:
                cur.execute("ROLLBACK TO SAVEPOINT semantic_search_snippet")
                snippet_fallback_due_encoding = True
                snippet_fallback_error = str(exc)
                cur.execute(sql.format(snippet_expr="LEFT(COALESCE(c.title, ''), 180)"), tuple(params))
                rows = cur.fetchall()
            finally:
                cur.execute("RELEASE SAVEPOINT semantic_search_snippet")

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
                                "snippet_fallback_due_encoding": snippet_fallback_due_encoding,
                                "snippet_fallback_error": snippet_fallback_error,
                                "results": results,
                            }
                        ),
                    ),
                )

    if embedding_cache_hit:
        semantic_path = "embedding_cache"
    elif use_openai:
        semantic_path = "openai_fresh"
    else:
        semantic_path = "mock_fresh"
    return {
        "query": q,
        "query_normalized": q_norm,
        "model": model,
        "count": len(results),
        "search_cache_hit": search_cache_hit,
        "embedding_cache_hit": embedding_cache_hit,
        "openai_called": openai_called,
        "semantic_path": semantic_path,
        "snippet_fallback_due_encoding": snippet_fallback_due_encoding,
        "snippet_fallback_error": snippet_fallback_error,
        "semantic_duration_ms": int((time.monotonic() - started_at) * 1000),
        "results": results,
    }


def semantic_search(*, query: str, limit: int, source_file: Optional[str] = None) -> dict[str, Any]:
    return semantic_search_with_mode(query=query, limit=limit, source_file=source_file, embedding_mode="openai")
