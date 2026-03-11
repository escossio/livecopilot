import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import get_logger
from app.services.question_bank_items import items_output_path, load_items_payload, write_items_payload, extract_question_items
from app.services.question_bank_parsers import (
    PARSED_STATUS_OK,
    QUESTION_BANK_ITEMS_DIR,
    QUESTION_BANK_PARSED_DIR,
    QUESTION_BANK_RAW_DIR,
    SUPPORTED_TYPES,
    compute_sha256,
    ensure_question_bank_dirs,
    list_question_bank_raw_files,
    load_parsed_payload,
    parse_question_bank_file,
    parsed_output_path,
    write_parsed_payload,
)

logger = get_logger(__name__)

STATE_PATH = QUESTION_BANK_ITEMS_DIR / "question_bank_state.json"
MANIFEST_PATH = QUESTION_BANK_ITEMS_DIR / "question_bank_manifest.json"
PIPELINE_VERSION = 8


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
    ensure_question_bank_dirs()
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return STATE_PATH


def write_manifest(records: list[dict]) -> Path:
    payload = {
        "pipeline": "question_bank",
        "document_count": len(records),
        "pipeline_version": PIPELINE_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "documents": records,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return MANIFEST_PATH


def _has_item_payload(payload: dict | None) -> bool:
    if not isinstance(payload, dict):
        return False
    items = payload.get("items")
    return isinstance(items, list)


def _needs_processing(source_path: Path, state: dict) -> tuple[bool, str]:
    relative = str(source_path.relative_to(QUESTION_BANK_RAW_DIR))
    sha256 = compute_sha256(source_path)
    record = state.get("files", {}).get(relative)
    parsed_path = parsed_output_path(source_path)
    item_path = items_output_path(relative)
    if not record:
        return True, sha256
    if int(record.get("pipeline_version", 0) or 0) != PIPELINE_VERSION:
        return True, sha256
    if record.get("sha256") != sha256:
        return True, sha256
    if not parsed_path.exists() or not item_path.exists():
        return True, sha256
    if not load_parsed_payload(parsed_path):
        return True, sha256
    if not _has_item_payload(load_items_payload(item_path)):
        return True, sha256
    return False, sha256


def process_question_bank() -> dict:
    ensure_question_bank_dirs()
    state = load_state()
    raw_files = list_question_bank_raw_files()
    active_sources = {str(path.relative_to(QUESTION_BANK_RAW_DIR)) for path in raw_files}

    stale_sources = [source_key for source_key in state.get("files", {}) if source_key not in active_sources]
    for source_key in stale_sources:
        record = state["files"].pop(source_key, {})
        for path_key in ("parsed_path", "items_path"):
            raw_path = record.get(path_key)
            if raw_path and Path(str(raw_path)).exists():
                Path(str(raw_path)).unlink()

    expected_parsed_paths = {parsed_output_path(path) for path in raw_files}
    expected_item_paths = {items_output_path(str(path.relative_to(QUESTION_BANK_RAW_DIR))) for path in raw_files}
    for artifact in QUESTION_BANK_PARSED_DIR.glob("*.json"):
        if artifact not in expected_parsed_paths:
            artifact.unlink()
    for artifact in QUESTION_BANK_ITEMS_DIR.glob("*.items.json"):
        if artifact not in expected_item_paths:
            artifact.unlink()

    total_found = len(raw_files)
    processed = 0
    skipped = 0
    failures = 0
    items_extracted = 0
    candidates_seen = 0
    dropped_by_cleaning = 0
    format_successes: set[str] = set()

    for source_path in raw_files:
        should_process, sha256 = _needs_processing(source_path, state)
        source_key = str(source_path.relative_to(QUESTION_BANK_RAW_DIR))
        if not should_process:
            skipped += 1
            existing_items = load_items_payload(items_output_path(source_key))
            if existing_items:
                items_extracted += int(existing_items.get("item_count", 0) or 0)
                filter_debug = existing_items.get("filter_debug", {})
                candidates_seen += int(filter_debug.get("candidate_count", 0) or 0)
                dropped_by_cleaning += int(filter_debug.get("dropped_count", 0) or 0)
                format_successes.add(source_path.suffix.lower())
            continue

        parsed_payload = parse_question_bank_file(source_path)
        parsed_path = write_parsed_payload(parsed_payload)
        processed += 1

        state.setdefault("files", {})[source_key] = {
            "sha256": sha256,
            "pipeline_version": PIPELINE_VERSION,
            "parsed_path": str(parsed_path),
            "items_path": str(items_output_path(source_key)),
            "status": parsed_payload.get("status", ""),
            "file_type": parsed_payload.get("file_type", ""),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        if source_path.suffix.lower() not in SUPPORTED_TYPES:
            failures += 1
            continue

        if parsed_payload.get("status") != PARSED_STATUS_OK:
            failures += 1
            continue

        items_payload = extract_question_items(parsed_payload)
        items_path = write_items_payload(items_payload)
        state["files"][source_key]["items_path"] = str(items_path)
        state["files"][source_key]["item_count"] = int(items_payload.get("item_count", 0) or 0)
        filter_debug = items_payload.get("filter_debug", {})
        state["files"][source_key]["candidate_count"] = int(filter_debug.get("candidate_count", 0) or 0)
        state["files"][source_key]["dropped_count"] = int(filter_debug.get("dropped_count", 0) or 0)
        items_extracted += int(items_payload.get("item_count", 0) or 0)
        candidates_seen += int(filter_debug.get("candidate_count", 0) or 0)
        dropped_by_cleaning += int(filter_debug.get("dropped_count", 0) or 0)
        format_successes.add(source_path.suffix.lower())

        logger.info(
            "question_bank_file_processed",
            extra={
                "event": "question_bank_file_processed",
                "source_file": source_key,
                "status": parsed_payload.get("status", ""),
                "item_count": items_payload.get("item_count", 0),
            },
        )

    records = []
    for source_key, record in sorted(state.get("files", {}).items()):
        records.append(
            {
                "source_file": source_key,
                "file_type": record.get("file_type", ""),
                "status": record.get("status", ""),
                "item_count": int(record.get("item_count", 0) or 0),
                "candidate_count": int(record.get("candidate_count", 0) or 0),
                "dropped_count": int(record.get("dropped_count", 0) or 0),
                "pipeline_version": int(record.get("pipeline_version", 0) or 0),
                "parsed_path": record.get("parsed_path", ""),
                "items_path": record.get("items_path", ""),
                "processed_at": record.get("processed_at", ""),
            }
        )

    write_state(state)
    write_manifest(records)

    return {
        "total_found": total_found,
        "processed": processed,
        "skipped": skipped,
        "failures": failures,
        "items_extracted": items_extracted,
        "candidates_seen": candidates_seen,
        "dropped_by_cleaning": dropped_by_cleaning,
        "formats_worked": sorted(ext.lstrip(".") for ext in format_successes),
        "state_path": str(STATE_PATH),
        "manifest_path": str(MANIFEST_PATH),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestao local da trilha question_bank.")
    parser.parse_args()
    summary = process_question_bank()
    print(f"Arquivos encontrados: {summary['total_found']}")
    print(f"Arquivos processados: {summary['processed']}")
    print(f"Arquivos ignorados: {summary['skipped']}")
    print(f"Falhas: {summary['failures']}")
    print(f"Candidatos avaliados: {summary['candidates_seen']}")
    print(f"Itens descartados por limpeza: {summary['dropped_by_cleaning']}")
    print(f"Itens extraidos: {summary['items_extracted']}")
    print(f"Formatos que funcionaram: {', '.join(summary['formats_worked']) if summary['formats_worked'] else '-'}")
    print(f"Manifesto: {summary['manifest_path']}")
    print(f"Estado: {summary['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
