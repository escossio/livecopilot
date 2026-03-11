#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.ingestion import normalize_input
from app.services.knowledge_imports import normalize_filename
from app.services.knowledge_ingest import process_knowledge_base
from app.services.semantic_min_api import ingest_min_document

BASE_DIR = ROOT_DIR
GAPS_FILE = BASE_DIR / "data" / "knowledge_gaps.ndjson"
GAPS_RAW_DIR = BASE_DIR / "data" / "knowledge_raw" / "gaps"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_gap_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _write_gap_entries(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(item, ensure_ascii=False) for item in entries]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _entry_status(entry: dict[str, Any]) -> str:
    return str(entry.get("status", "open")).strip().lower() or "open"


def _entry_key(entry: dict[str, Any]) -> str:
    timestamp = str(entry.get("timestamp", "")).strip()
    query = str(entry.get("query", "")).strip()
    source = str(entry.get("source", "")).strip()
    digest = hashlib.sha1(f"{timestamp}|{query}|{source}".encode("utf-8")).hexdigest()
    return digest[:12]


def _to_markdown(entry: dict[str, Any]) -> str:
    query = normalize_input(str(entry.get("query", "")))
    source = str(entry.get("source", "")).strip() or "project_brain_query"
    context = entry.get("context", {})
    return "\n".join(
        [
            "# Knowledge Gap",
            "",
            f"- timestamp: {entry.get('timestamp', '')}",
            f"- source: {source}",
            f"- status: {_entry_status(entry)}",
            "",
            "## Query",
            "",
            query,
            "",
            "## Context",
            "",
            "```json",
            json.dumps(context, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )


def _gap_doc_path(entry: dict[str, Any]) -> Path:
    timestamp = str(entry.get("timestamp", "")).replace(":", "").replace("+", "").replace("-", "")
    query = normalize_input(str(entry.get("query", ""))) or "knowledge_gap"
    key = _entry_key(entry)
    base_name = normalize_filename(f"gap_{timestamp}_{key}_{query}.md")
    return GAPS_RAW_DIR / base_name


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestao de knowledge gaps para base local e banco vetorial.")
    parser.add_argument("--limit", type=int, default=20, help="maximo de gaps abertos processados na rodada")
    parser.add_argument("--chunk-size", type=int, default=1200, help="chunk size para process_knowledge_base")
    parser.add_argument("--overlap", type=int, default=180, help="overlap para process_knowledge_base")
    parser.add_argument("--max-chunks", type=int, default=5, help="max chunks por gap na ingestao vetorial")
    args = parser.parse_args()

    entries = _load_gap_entries(GAPS_FILE)
    open_indexes = [idx for idx, item in enumerate(entries) if _entry_status(item) == "open"]
    open_indexes = open_indexes[: max(1, int(args.limit))]

    GAPS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    generated_docs: list[tuple[int, Path]] = []
    for idx in open_indexes:
        entry = entries[idx]
        path = _gap_doc_path(entry)
        path.write_text(_to_markdown(entry), encoding="utf-8")
        generated_docs.append((idx, path))

    ingest_summary = process_knowledge_base(chunk_size=max(1, args.chunk_size), overlap=max(0, args.overlap))

    resolved = 0
    failed = 0
    vector_docs = 0
    vector_chunks = 0
    errors: list[dict[str, Any]] = []
    for idx, path in generated_docs:
        entry = entries[idx]
        try:
            result = ingest_min_document(
                file_path=str(path),
                text=None,
                source_file=f"knowledge-gap::{path.name}",
                title=f"Knowledge Gap: {normalize_input(str(entry.get('query', '')) or 'sem query')[:100]}",
                max_chunks=max(1, args.max_chunks),
            )
            entry["status"] = "resolved"
            entry["resolved_at"] = _now_iso()
            entry["resolution"] = {
                "document_id": result.get("document", {}).get("document_id"),
                "source_file": result.get("document", {}).get("source_file"),
                "chunk_count": result.get("document", {}).get("chunk_count"),
            }
            resolved += 1
            vector_docs += 1
            vector_chunks += int(result.get("document", {}).get("chunk_count", 0) or 0)
        except Exception as exc:
            failed += 1
            errors.append({"query": str(entry.get("query", "")), "error": str(exc), "doc_path": str(path)})

    _write_gap_entries(GAPS_FILE, entries)

    summary = {
        "status": "ok",
        "gaps_total": len(entries),
        "gaps_open_before": len(open_indexes),
        "docs_generated": len(generated_docs),
        "resolved": resolved,
        "failed": failed,
        "vector_docs": vector_docs,
        "vector_chunks": vector_chunks,
        "knowledge_ingest_summary": ingest_summary,
        "errors": errors,
        "gaps_file": str(GAPS_FILE),
        "gaps_raw_dir": str(GAPS_RAW_DIR),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
