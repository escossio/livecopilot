import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import get_logger
from app.services.knowledge_chunks import (
    CHUNKS_DIR,
    INDEX_DIR,
    EPUB_CHUNK_PIPELINE_VERSION,
    build_chunk_payload,
    chunk_output_path,
    load_chunk_payload,
    write_chunk_payload,
    write_index_manifest,
)
from app.services.knowledge_parsers import (
    PARSED_DIR,
    PARSED_STATUS_OK,
    RAW_DIR,
    SUPPORTED_TYPES,
    compute_sha256,
    ensure_knowledge_dirs,
    list_raw_files,
    load_parsed_payload,
    parse_file,
    parsed_output_path,
    write_parsed_payload,
)
from app.services.knowledge_tags import TAG_PIPELINE_VERSION

logger = get_logger(__name__)

STATE_PATH = INDEX_DIR / "knowledge_state.json"


def _has_tag_payload(payload: dict | None) -> bool:
    if not isinstance(payload, dict):
        return False
    tags = payload.get("tags")
    if not isinstance(tags, dict):
        return False
    all_tags = tags.get("all", [])
    return isinstance(all_tags, list)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"files": {}, "updated_at": None}
    try:
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}, "updated_at": None}
    if not isinstance(payload, dict):
        return {"files": {}, "updated_at": None}
    files = payload.get("files")
    if not isinstance(files, dict):
        payload["files"] = {}
    return payload


def write_state(state: dict) -> Path:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return STATE_PATH


def _needs_processing(source_path: Path, state: dict) -> tuple[bool, str]:
    relative = str(source_path.relative_to(RAW_DIR))
    sha256 = compute_sha256(source_path)
    record = state.get("files", {}).get(relative)
    parsed_path = parsed_output_path(source_path)
    chunk_path = chunk_output_path(relative)
    if not record:
        return True, sha256
    if record.get("sha256") != sha256:
        return True, sha256
    if record.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    if not parsed_path.exists() or not chunk_path.exists():
        return True, sha256
    parsed_payload = load_parsed_payload(parsed_path)
    if not _has_tag_payload(parsed_payload):
        return True, sha256
    if parsed_payload.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    chunk_payload = load_chunk_payload(chunk_path)
    if not _has_tag_payload(chunk_payload):
        return True, sha256
    if chunk_payload.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    if source_path.suffix.lower() == ".epub":
        if int(chunk_payload.get("epub_chunk_pipeline_version", 0) or 0) != EPUB_CHUNK_PIPELINE_VERSION:
            return True, sha256
    return False, sha256


def process_knowledge_base(chunk_size: int = 1200, overlap: int = 180) -> dict:
    ensure_knowledge_dirs()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    raw_files = list_raw_files()
    active_sources = {str(path.relative_to(RAW_DIR)) for path in raw_files}

    stale_sources = [source_key for source_key in state.get("files", {}) if source_key not in active_sources]
    for source_key in stale_sources:
        record = state["files"].pop(source_key, {})
        for path_key in ("parsed_path", "chunk_path"):
            raw_path = record.get(path_key)
            if not raw_path:
                continue
            path = Path(str(raw_path))
            if path.exists():
                path.unlink()

    expected_parsed_paths = {parsed_output_path(path) for path in raw_files}
    expected_chunk_paths = {chunk_output_path(str(path.relative_to(RAW_DIR))) for path in raw_files}
    for artifact in PARSED_DIR.glob("*.json"):
        if artifact not in expected_parsed_paths:
            artifact.unlink()
    for artifact in CHUNKS_DIR.glob("*.json"):
        if artifact not in expected_chunk_paths:
            artifact.unlink()

    total_found = len(raw_files)
    processed = 0
    skipped = 0
    errors = 0
    unsupported = 0
    chunk_total = 0

    for source_path in raw_files:
        should_process, sha256 = _needs_processing(source_path, state)
        source_key = str(source_path.relative_to(RAW_DIR))
        if not should_process:
            skipped += 1
            existing_chunk = load_chunk_payload(chunk_output_path(source_key))
            if existing_chunk:
                chunk_total += int(existing_chunk.get("chunk_count", 0) or 0)
            continue

        parsed_payload = parse_file(source_path)
        previous_record = state.setdefault("files", {}).get(source_key, {})
        new_parsed_path = parsed_output_path(source_path)
        new_chunk_path = chunk_output_path(source_key)
        for path_key, new_path in (("parsed_path", new_parsed_path), ("chunk_path", new_chunk_path)):
            raw_path = previous_record.get(path_key)
            if raw_path and Path(str(raw_path)) != new_path:
                old_path = Path(str(raw_path))
                if old_path.exists():
                    old_path.unlink()

        parsed_path = write_parsed_payload(parsed_payload)
        processed += 1

        state.setdefault("files", {})[source_key] = {
            "sha256": sha256,
            "tag_pipeline_version": TAG_PIPELINE_VERSION,
            "parsed_path": str(parsed_path),
            "chunk_path": str(new_chunk_path),
            "status": parsed_payload.get("status", ""),
            "file_type": parsed_payload.get("file_type", ""),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        if source_path.suffix.lower() not in SUPPORTED_TYPES:
            unsupported += 1
            continue

        if parsed_payload.get("status") != PARSED_STATUS_OK:
            errors += 1
            continue

        chunk_payload = build_chunk_payload(parsed_payload, chunk_size=chunk_size, overlap=overlap)
        write_chunk_payload(chunk_payload)
        state["files"][source_key]["chunk_count"] = int(chunk_payload.get("chunk_count", 0) or 0)
        chunk_total += int(chunk_payload.get("chunk_count", 0) or 0)

        logger.info(
            "knowledge_file_processed",
            extra={
                "event": "knowledge_file_processed",
                "source_file": source_key,
                "status": parsed_payload.get("status", ""),
                "chunk_count": chunk_payload.get("chunk_count", 0),
            },
        )

    documents = []
    chunk_documents = []
    for source_key, record in sorted(state.get("files", {}).items()):
        parsed_path = Path(str(record.get("parsed_path", "")))
        parsed_payload = load_parsed_payload(parsed_path)
        if parsed_payload:
            documents.append(parsed_payload)
        chunk_payload = load_chunk_payload(chunk_output_path(source_key))
        if chunk_payload:
            chunk_documents.append(chunk_payload)

    write_state(state)
    manifest_path = write_index_manifest(documents, chunk_documents)

    return {
        "total_found": total_found,
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
        "unsupported": unsupported,
        "chunk_total": chunk_total,
        "manifest_path": str(manifest_path),
        "state_path": str(STATE_PATH),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão local de base de conhecimento.")
    parser.add_argument("--chunk-size", type=int, default=1200, help="Tamanho alvo de cada chunk em caracteres.")
    parser.add_argument("--overlap", type=int, default=180, help="Sobreposição leve entre chunks em caracteres.")
    args = parser.parse_args()

    summary = process_knowledge_base(chunk_size=args.chunk_size, overlap=args.overlap)
    print(f"Arquivos encontrados: {summary['total_found']}")
    print(f"Arquivos processados: {summary['processed']}")
    print(f"Arquivos ignorados: {summary['skipped']}")
    print(f"Erros de parsing: {summary['errors']}")
    print(f"Arquivos não suportados: {summary['unsupported']}")
    print(f"Chunks gerados: {summary['chunk_total']}")
    print(f"Manifesto: {summary['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
