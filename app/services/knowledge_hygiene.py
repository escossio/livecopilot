import argparse
import hashlib
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from app.services.knowledge_parsers import PARSED_DIR, RAW_DIR, load_parsed_payload, parsed_output_path

LOW_VALUE_CONTENT_LENGTH = 1500
LOW_VALUE_CHUNK_COUNT = 2
LOW_VALUE_UNIQUE_WORDS = 120
NEAR_DUPLICATE_THRESHOLD = 0.97
EXTENSION_COMPATIBILITY = {
    "pdf": {"pdf"},
    "html": {"html", "text"},
    "htm": {"html", "text"},
    "md": {"text"},
    "txt": {"text"},
    "docx": {"zip_container"},
    "epub": {"zip_container"},
}
FLAG_PENALTIES = {
    "mismatched_file_type": 0.45,
    "exact_duplicate": 0.35,
    "near_duplicate": 0.25,
    "low_value_document": 0.15,
}


def _detect_actual_type(path: Path) -> dict[str, str]:
    try:
        head = path.read_bytes()[:1024]
    except Exception:
        return {"actual_type": "unknown", "reason": "read_error"}

    lowered = head.lstrip().lower()
    if lowered.startswith(b"%pdf-"):
        return {"actual_type": "pdf", "reason": "pdf_header"}
    if lowered.startswith(b"<!doctype html") or lowered.startswith(b"<html") or b"<html" in lowered:
        return {"actual_type": "html", "reason": "html_header"}
    if lowered.startswith(b"pk\x03\x04"):
        return {"actual_type": "zip_container", "reason": "zip_header"}
    if b"\x00" in head:
        return {"actual_type": "binary", "reason": "binary_null_byte"}
    return {"actual_type": "text", "reason": "plain_text_fallback"}


def _normalized_content(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip().lower()
    return normalized


def _content_hash(text: str) -> str:
    return hashlib.sha256(_normalized_content(text).encode("utf-8")).hexdigest()


def _word_count(text: str) -> int:
    return len(re.findall(r"[a-zA-ZÀ-ÿ0-9_/-]+", str(text or "")))


def _unique_word_count(text: str) -> int:
    return len(set(re.findall(r"[a-zA-ZÀ-ÿ0-9_/-]+", str(text or "").lower())))


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _chunk_payload_path(source_file: str) -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "knowledge_chunks" / ("__".join(Path(source_file).parts) + ".chunks.json")


def _build_hygiene_index(documents: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    parsed_records = []
    mismatch_records = []
    low_value_records = []
    duplicate_groups: list[dict[str, Any]] = []
    near_duplicate_groups: list[dict[str, Any]] = []
    index: dict[str, dict[str, Any]] = {}

    for document in documents:
        if not isinstance(document, dict):
            continue
        source_file = str(document.get("source_file", ""))
        raw_path = RAW_DIR / source_file
        parsed_payload = load_parsed_payload(Path(str(document.get("parsed_path", "")))) or {}
        chunk_payload = _load_json(Path(str(document.get("chunk_path", "")))) or _load_json(_chunk_payload_path(source_file)) or {}
        content = str(parsed_payload.get("content", ""))
        chunk_count = int(document.get("chunk_count", chunk_payload.get("chunk_count", 0)) or 0)
        content_length = len(content)
        unique_words = _unique_word_count(content)
        words = _word_count(content)

        actual = _detect_actual_type(raw_path) if raw_path.exists() else {"actual_type": "unknown", "reason": "missing_raw_file"}
        extension = raw_path.suffix.lower().lstrip(".") if raw_path.exists() else ""
        compatible_types = EXTENSION_COMPATIBILITY.get(extension, {extension, "text"})
        if extension and actual["actual_type"] not in compatible_types:
            mismatch_records.append(
                {
                    "source_file": source_file,
                    "extension": extension,
                    "actual_type": actual["actual_type"],
                    "reason": actual["reason"],
                    "status": parsed_payload.get("status", document.get("status", "")),
                }
            )

        if content:
            parsed_records.append(
                {
                    "source_file": source_file,
                    "content": content,
                    "normalized_hash": _content_hash(content),
                    "content_length": content_length,
                    "chunk_count": chunk_count,
                    "word_count": words,
                    "unique_word_count": unique_words,
                }
            )

        low_value_reasons = []
        if content_length and content_length < LOW_VALUE_CONTENT_LENGTH:
            low_value_reasons.append("short_content")
        if chunk_count <= LOW_VALUE_CHUNK_COUNT:
            low_value_reasons.append("few_chunks")
        if unique_words and unique_words < LOW_VALUE_UNIQUE_WORDS:
            low_value_reasons.append("low_unique_word_count")
        if low_value_reasons:
            low_value_records.append(
                {
                    "source_file": source_file,
                    "status": parsed_payload.get("status", document.get("status", "")),
                    "content_length": content_length,
                    "chunk_count": chunk_count,
                    "word_count": words,
                    "unique_word_count": unique_words,
                    "reasons": low_value_reasons,
                }
            )

    exact_duplicate_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in parsed_records:
        exact_duplicate_groups[record["normalized_hash"]].append(record)
    for content_hash, records in exact_duplicate_groups.items():
        if len(records) < 2:
            continue
        duplicate_groups.append(
            {
                "duplicate_type": "exact_content_hash",
                "content_hash": content_hash,
                "documents": [
                    {
                        "source_file": record["source_file"],
                        "content_length": record["content_length"],
                        "chunk_count": record["chunk_count"],
                    }
                    for record in records
                ],
            }
        )

    short_records = [record for record in parsed_records if record["content_length"] <= 5000]
    for idx, left in enumerate(short_records):
        for right in short_records[idx + 1 :]:
            if left["normalized_hash"] == right["normalized_hash"]:
                continue
            ratio = SequenceMatcher(None, _normalized_content(left["content"]), _normalized_content(right["content"])).ratio()
            if ratio >= NEAR_DUPLICATE_THRESHOLD:
                near_duplicate_groups.append(
                    {
                        "duplicate_type": "near_duplicate_similarity",
                        "similarity": round(ratio, 4),
                        "documents": [
                            {
                                "source_file": left["source_file"],
                                "content_length": left["content_length"],
                                "chunk_count": left["chunk_count"],
                            },
                            {
                                "source_file": right["source_file"],
                                "content_length": right["content_length"],
                                "chunk_count": right["chunk_count"],
                            },
                        ],
                    }
                )

    for record in mismatch_records:
        source_file = record["source_file"]
        bucket = index.setdefault(source_file, {"hygiene_flags": [], "hygiene_notes": []})
        bucket["hygiene_flags"].append("mismatched_file_type")
        bucket["hygiene_notes"].append(
            f"extension={record['extension']} actual_type={record['actual_type']} reason={record['reason']}"
        )

    for group in duplicate_groups:
        for record in group["documents"]:
            source_file = record["source_file"]
            bucket = index.setdefault(source_file, {"hygiene_flags": [], "hygiene_notes": []})
            bucket["hygiene_flags"].append("exact_duplicate")
            peers = [doc["source_file"] for doc in group["documents"] if doc["source_file"] != source_file]
            if peers:
                bucket["hygiene_notes"].append(f"exact duplicate of {', '.join(peers[:3])}")

    for group in near_duplicate_groups:
        for record in group["documents"]:
            source_file = record["source_file"]
            bucket = index.setdefault(source_file, {"hygiene_flags": [], "hygiene_notes": []})
            bucket["hygiene_flags"].append("near_duplicate")
            peers = [doc["source_file"] for doc in group["documents"] if doc["source_file"] != source_file]
            if peers:
                bucket["hygiene_notes"].append(f"near duplicate of {', '.join(peers[:3])}")

    for record in low_value_records:
        source_file = record["source_file"]
        bucket = index.setdefault(source_file, {"hygiene_flags": [], "hygiene_notes": []})
        bucket["hygiene_flags"].append("low_value_document")
        bucket["hygiene_notes"].append(f"low value signals: {', '.join(record['reasons'])}")

    for source_file, bucket in index.items():
        unique_flags = sorted(set(bucket["hygiene_flags"]))
        unique_notes = []
        for note in bucket["hygiene_notes"]:
            if note not in unique_notes:
                unique_notes.append(note)
        penalty = sum(FLAG_PENALTIES.get(flag, 0.0) for flag in unique_flags)
        bucket["hygiene_flags"] = unique_flags
        bucket["hygiene_notes"] = unique_notes[:6]
        bucket["hygiene_score"] = round(max(0.1, 1.0 - penalty), 3)

    return {
        "index": index,
        "mismatch_file_type": sorted(mismatch_records, key=lambda item: (item["actual_type"], item["source_file"])),
        "suspected_duplicates": sorted(
            duplicate_groups + near_duplicate_groups,
            key=lambda item: (-len(item["documents"]), item["documents"][0]["source_file"]),
        ),
        "low_value_documents": sorted(
            low_value_records,
            key=lambda item: (len(item["reasons"]) * -1, item["content_length"], item["source_file"]),
        ),
    }


def build_knowledge_hygiene_report(top: int = 20) -> dict[str, Any]:
    documents = []
    for raw_path in sorted(RAW_DIR.rglob("*")):
        if not raw_path.is_file():
            continue
        source_file = str(raw_path.relative_to(RAW_DIR))
        parsed_path = parsed_output_path(raw_path)
        documents.append(
            {
                "source_file": source_file,
                "parsed_path": str(parsed_path),
                "chunk_path": str(_chunk_payload_path(source_file)),
                "chunk_count": (_load_json(_chunk_payload_path(source_file)) or {}).get("chunk_count", 0),
                "status": (load_parsed_payload(parsed_path) or {}).get("status", ""),
            }
        )
    hygiene = _build_hygiene_index(documents)

    return {
        "raw_dir": str(RAW_DIR),
        "parsed_dir": str(PARSED_DIR),
        "mismatched_file_type": hygiene["mismatch_file_type"][:top],
        "suspected_duplicates": hygiene["suspected_duplicates"][:top],
        "low_value_documents": hygiene["low_value_documents"][:top],
        "document_hygiene": [
            {
                "source_file": source_file,
                **payload,
            }
            for source_file, payload in sorted(
                hygiene["index"].items(),
                key=lambda item: (float(item[1].get("hygiene_score", 1.0)), item[0]),
            )[:top]
        ],
        "summary": {
            "mismatched_file_type_count": len(hygiene["mismatch_file_type"]),
            "suspected_duplicates_count": len(hygiene["suspected_duplicates"]),
            "low_value_documents_count": len(hygiene["low_value_documents"]),
        },
    }


def build_knowledge_hygiene_index_for_manifest(documents: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    hygiene = _build_hygiene_index(documents)
    return hygiene["index"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostico de higiene do acervo knowledge")
    parser.add_argument("--top", type=int, default=20, help="Quantidade maxima por lista")
    parser.add_argument("--pretty", action="store_true", help="Renderiza JSON identado")
    args = parser.parse_args()

    payload = build_knowledge_hygiene_report(top=max(1, args.top))
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
