import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.services.knowledge_parsers import PARSED_DIR
from app.services.knowledge_hygiene import build_knowledge_hygiene_index_for_manifest
from app.services.knowledge_tags import TAG_PIPELINE_VERSION, infer_tags, merge_tags

CHUNKS_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_chunks"
INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_index"

DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 180
EPUB_STRUCTURED_CHUNK_SIZE = 2800
EPUB_STRUCTURED_OVERLAP = 240
EPUB_CHUNK_PIPELINE_VERSION = 5

EPUB_EDITORIAL_SECTION_TITLES = {
    "cover",
    "contents",
    "table of contents",
    "foreword",
    "forward",
    "preface",
    "acknowledgments",
    "acknowledgements",
    "contributors",
    "about the author",
    "about the reviewers",
    "copyright",
    "dedication",
}

TOPIC_STOPWORDS = {
    "a",
    "o",
    "e",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "em",
    "para",
    "por",
    "com",
    "sem",
    "na",
    "no",
    "nas",
    "nos",
    "um",
    "uma",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
}


def ensure_chunk_dirs() -> None:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def chunk_output_path(source_file: str) -> Path:
    relative = Path(source_file)
    target_name = "__".join(relative.parts) + ".chunks.json"
    return CHUNKS_DIR / target_name


def split_into_paragraphs(content: str) -> list[str]:
    content = content.strip()
    if not content:
        return []
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", content) if paragraph.strip()]
    if paragraphs:
        return paragraphs
    return [line.strip() for line in content.splitlines() if line.strip()]


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _is_epub_internal_marker_line(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    return bool(re.fullmatch(r"[A-Z]\d+(?:_[A-Za-z0-9]+)+", candidate))


def _clean_epub_chunk_text(text: str) -> str:
    cleaned_lines = [line for line in text.splitlines() if not _is_epub_internal_marker_line(line)]
    cleaned = "\n".join(cleaned_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _resolve_epub_chunk_label(section_title: str, chunk_text: str) -> str:
    if section_title and not _is_epub_internal_marker_line(section_title):
        return section_title
    for line in chunk_text.splitlines():
        candidate = line.strip()
        if not candidate or _is_epub_internal_marker_line(candidate):
            continue
        return candidate[:180]
    return section_title


def _is_epub_list_line(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    return bool(
        re.match(r"^(?:[-*•▪◦]|(?:\d+|[A-Za-z]|[ivxlcdm]+)[.)])\s+", candidate, flags=re.IGNORECASE)
    )


def _is_epub_heading_line(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    lowered = candidate.lower()
    if lowered in {"cover", "contents", "table of contents", "preface", "foreword", "introduction", "summary"}:
        return True
    if re.fullmatch(r"(?:chapter|part)\s+\d+(?::.*)?", lowered):
        return True
    if re.fullmatch(r"(?:appendix|section)\s+[a-z0-9]+(?::.*)?", lowered):
        return True
    if re.fullmatch(r"\d+|[ivxlcdm]+", candidate, flags=re.IGNORECASE):
        return True
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", candidate)
    if not words or len(words) > 14 or len(candidate) > 120:
        return False
    if re.search(r"[.!?]$", candidate):
        return False
    capitalized_words = sum(1 for word in words if word[:1].isupper() or word.isupper() or word.isdigit())
    return capitalized_words >= max(1, int(len(words) * 0.7))


def _looks_like_epub_continuation(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    if candidate[0].islower() or candidate[0].isdigit() or candidate[0] in ",.;:)]}%":
        return True
    if re.match(
        r"^(?:and|or|but|for|nor|so|yet|to|of|in|on|at|by|with|without|from|into|over|under|the|a|an)\b",
        candidate,
        flags=re.IGNORECASE,
    ):
        return True
    if len(candidate) <= 24:
        return True
    return False


def _looks_like_epub_paragraph_start(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    if _is_epub_heading_line(candidate) or _is_epub_list_line(candidate):
        return False
    if candidate[0].islower() or candidate[0] in ",.;:)]}%":
        return False
    return True


def _join_epub_lines(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left
    if left.endswith(("(", "/", "-", "“", '"')) or right.startswith((",", ".", ";", ":", ")", "]", "%", "”", '"')):
        separator = ""
    else:
        separator = " "
    return f"{left}{separator}{right}".strip()


def _should_break_epub_paragraph(current: str, next_line: str) -> bool:
    if not current or not next_line:
        return False
    if _is_epub_heading_line(next_line) or _is_epub_list_line(next_line):
        return True
    current_length = len(current)
    if not re.search(r'[.!?]["\')\]]*$', current.strip()):
        return False
    if not _looks_like_epub_paragraph_start(next_line):
        return False
    if current_length >= 280:
        return True
    return current_length >= 180 and len(next_line.strip()) >= 70


def _normalize_epub_section_content(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    paragraphs: list[str] = []
    current = ""

    for line in lines:
        if not line:
            if current:
                paragraphs.append(current.strip())
                current = ""
            continue
        if _is_epub_internal_marker_line(line):
            continue
        if _is_epub_heading_line(line) or _is_epub_list_line(line):
            if current:
                paragraphs.append(current.strip())
                current = ""
            paragraphs.append(line)
            continue
        if not current:
            current = line
            continue
        if current.endswith((",", ";", ":", "(", "/", "-")) or _looks_like_epub_continuation(line):
            current = _join_epub_lines(current, line)
            continue
        if _should_break_epub_paragraph(current, line):
            paragraphs.append(current.strip())
            current = line
            continue
        current = _join_epub_lines(current, line)

    if current:
        paragraphs.append(current.strip())

    cleaned = "\n\n".join(paragraph for paragraph in paragraphs if paragraph).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def _is_epub_editorial_section(section: dict) -> bool:
    title = _normalize_whitespace(str(section.get("title", "")).strip()).lower()
    if title in EPUB_EDITORIAL_SECTION_TITLES:
        return True
    if title.startswith("table of contents"):
        return True
    return False


def _resolve_epub_chunk_title(document_title: str, chapter_title: str, section_hint: str) -> str:
    normalized_document_title = _normalize_whitespace(document_title)
    candidates = [candidate.strip() for candidate in (chapter_title, section_hint) if candidate and candidate.strip()]
    for candidate in candidates:
        normalized_candidate = _normalize_whitespace(candidate)
        if not normalized_candidate:
            continue
        if normalized_candidate != normalized_document_title:
            return candidate
    return document_title


def _resolve_epub_estimated_topic(chunk_title: str, chapter_title: str, section_hint: str, chunk_text: str) -> str:
    for candidate in (chapter_title, section_hint, chunk_title):
        normalized_candidate = _normalize_whitespace(candidate)
        if normalized_candidate:
            return candidate.strip()
    return estimate_topic(chunk_title, chunk_text)


def estimate_topic(title: str, content: str) -> str:
    title = _normalize_whitespace(title)
    if title:
        return title
    tokens = re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9._/-]{2,}", content.lower())
    counts = Counter(token for token in tokens if token not in TOPIC_STOPWORDS)
    if not counts:
        return "general"
    return ", ".join(token for token, _ in counts.most_common(3))


def build_chunks(content: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[str]:
    paragraphs = split_into_paragraphs(content)
    if not paragraphs:
        return []

    chunks: list[str] = []
    current_parts: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)
        if current_parts and current_length + paragraph_length + 2 > chunk_size:
            chunk_text = "\n\n".join(current_parts).strip()
            if chunk_text:
                chunks.append(chunk_text)

            overlap_parts: list[str] = []
            overlap_length = 0
            for previous in reversed(current_parts):
                previous_length = len(previous)
                if overlap_parts and overlap_length + previous_length + 2 > overlap:
                    break
                overlap_parts.insert(0, previous)
                overlap_length += previous_length + (2 if overlap_parts else 0)

            current_parts = overlap_parts[:]
            current_length = sum(len(part) for part in current_parts) + max(0, len(current_parts) - 1) * 2

        if paragraph_length > chunk_size and not current_parts:
            start = 0
            step = max(1, chunk_size - overlap)
            while start < paragraph_length:
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
                start += step
            current_parts = []
            current_length = 0
            continue

        current_parts.append(paragraph)
        current_length += paragraph_length + (2 if len(current_parts) > 1 else 0)

    final_chunk = "\n\n".join(current_parts).strip()
    if final_chunk:
        chunks.append(final_chunk)
    return chunks


def _structured_epub_sections(parsed_payload: dict) -> list[dict]:
    if str(parsed_payload.get("file_type", "")).lower() != "epub":
        return []
    sections = parsed_payload.get("sections")
    if not isinstance(sections, list):
        return []

    normalized_sections = []
    for item in sections:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        content = str(item.get("content", "")).strip()
        if not content:
            continue
        normalized_sections.append(
            {
                "doc_path": str(item.get("doc_path", "")).strip(),
                "title": title,
                "content": content,
            }
        )

    titled_sections = sum(1 for item in normalized_sections if item["title"])
    if len(normalized_sections) < 3 or titled_sections < max(2, len(normalized_sections) // 2):
        return []
    return normalized_sections


def build_chunk_payload(parsed_payload: dict, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> dict:
    ensure_chunk_dirs()
    source_file = str(parsed_payload.get("source_file", ""))
    title = str(parsed_payload.get("title", "") or Path(source_file).stem)
    content = str(parsed_payload.get("content", ""))
    inherited_tags = parsed_payload.get("tags") if isinstance(parsed_payload.get("tags"), dict) else {}
    document_tags = merge_tags(
        inherited_tags,
        infer_tags(
            source_file=source_file,
            title=title,
            content=content,
            path_hint=str(Path(source_file).parent) if Path(source_file).parent != Path(".") else "",
        ),
    )

    chunk_records: list[dict] = []
    structured_sections = _structured_epub_sections(parsed_payload)
    effective_chunk_size = chunk_size
    effective_overlap = overlap
    editorial_sections_skipped: list[str] = []
    if structured_sections:
        chunk_sections = structured_sections
        if str(parsed_payload.get("file_type", "")).lower() == "epub":
            effective_chunk_size = max(chunk_size, EPUB_STRUCTURED_CHUNK_SIZE)
            effective_overlap = max(0, min(overlap, EPUB_STRUCTURED_OVERLAP))
            filtered_sections = []
            for section in structured_sections:
                if _is_epub_editorial_section(section):
                    skipped_title = str(section.get("title", "")).strip()
                    if skipped_title:
                        editorial_sections_skipped.append(skipped_title)
                    continue
                filtered_sections.append(section)
            if filtered_sections:
                chunk_sections = filtered_sections
        for section in chunk_sections:
            section_title = str(section.get("title", "")).strip()
            section_content = str(section.get("content", "")).strip()
            if str(parsed_payload.get("file_type", "")).lower() == "epub":
                section_content = _normalize_epub_section_content(section_content)
            for section_index, chunk_text in enumerate(
                build_chunks(section_content, chunk_size=effective_chunk_size, overlap=effective_overlap),
                start=1,
            ):
                cleaned_chunk_text = _clean_epub_chunk_text(chunk_text)
                if not cleaned_chunk_text:
                    continue
                effective_title = _resolve_epub_chunk_label(section_title, cleaned_chunk_text)
                chunk_records.append(
                    {
                        "content": cleaned_chunk_text,
                        "chapter_title": effective_title,
                        "section_hint": effective_title,
                        "section_path": str(section.get("doc_path", "")).strip(),
                        "section_chunk_index": section_index,
                    }
                )
    else:
        for chunk_text in build_chunks(content, chunk_size=chunk_size, overlap=overlap):
            chunk_records.append({"content": chunk_text})

    chunks = []
    for sequence, chunk_record in enumerate(chunk_records, start=1):
        chunk_text = str(chunk_record.get("content", "")).strip()
        if not chunk_text:
            continue
        chunk_hash = hashlib.sha256(f"{source_file}:{sequence}:{chunk_text}".encode("utf-8")).hexdigest()[:16]
        chapter_title = str(chunk_record.get("chapter_title", "")).strip()
        section_hint = str(chunk_record.get("section_hint", "")).strip()
        chunk_title = title
        if str(parsed_payload.get("file_type", "")).lower() == "epub" and (chapter_title or section_hint):
            chunk_title = _resolve_epub_chunk_title(title, chapter_title, section_hint)
        chunk_tags = merge_tags(
            document_tags,
            infer_tags(
                source_file=source_file,
                title=chunk_title,
                content=chunk_text,
                path_hint=str(Path(source_file).parent) if Path(source_file).parent != Path(".") else "",
            ),
        )
        chunk_payload = {
            "chunk_id": f"{Path(source_file).stem}-{sequence:04d}-{chunk_hash}",
            "source_file": source_file,
            "title": chunk_title,
            "sequence": sequence,
            "content": chunk_text,
            "estimated_topic": (
                _resolve_epub_estimated_topic(chunk_title, chapter_title, section_hint, chunk_text)
                if str(parsed_payload.get("file_type", "")).lower() == "epub" and (chapter_title or section_hint)
                else estimate_topic(chunk_title, chunk_text)
            ),
            "tags": chunk_tags,
        }
        if chapter_title:
            chunk_payload["chapter_title"] = chapter_title
        if section_hint:
            chunk_payload["section_hint"] = section_hint
        section_path = str(chunk_record.get("section_path", "")).strip()
        if section_path:
            chunk_payload["section_path"] = section_path
        section_chunk_index = chunk_record.get("section_chunk_index")
        if isinstance(section_chunk_index, int):
            chunk_payload["section_chunk_index"] = section_chunk_index
        chunks.append(chunk_payload)

    return {
        "source_file": source_file,
        "title": title,
        "tags": document_tags,
        "tag_pipeline_version": TAG_PIPELINE_VERSION,
        "sha256": parsed_payload.get("sha256", ""),
        "parsed_at": parsed_payload.get("parsed_at", ""),
        "chunked_at": datetime.now(timezone.utc).isoformat(),
        "status": "chunked" if chunks else "empty",
        "chunk_size": chunk_size,
        "overlap": overlap,
        **(
            {
                "effective_chunk_size": effective_chunk_size,
                "effective_overlap": effective_overlap,
            }
            if effective_chunk_size != chunk_size or effective_overlap != overlap
            else {}
        ),
        **(
            {"editorial_sections_skipped": editorial_sections_skipped}
            if editorial_sections_skipped
            else {}
        ),
        **({"epub_chunk_pipeline_version": EPUB_CHUNK_PIPELINE_VERSION} if str(parsed_payload.get("file_type", "")).lower() == "epub" else {}),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


def write_chunk_payload(payload: dict) -> Path:
    output_path = chunk_output_path(str(payload["source_file"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def load_chunk_payload(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(loaded, dict):
        return loaded
    return None


def write_index_manifest(documents: list[dict], chunk_documents: list[dict]) -> Path:
    ensure_chunk_dirs()
    manifest_documents = [
        {
            "source_file": item.get("source_file", ""),
            "title": item.get("title", ""),
            "sha256": item.get("sha256", ""),
            "status": item.get("status", ""),
            "tag_pipeline_version": item.get("tag_pipeline_version", ""),
            "tags": item.get("tags", {}),
            "parsed_path": str(PARSED_DIR / ("__".join(Path(str(item.get("source_file", ""))).parts) + ".json")),
            "chunk_path": str(chunk_output_path(str(item.get("source_file", "")))),
            "chunk_count": next(
                (int(chunk_doc.get("chunk_count", 0) or 0) for chunk_doc in chunk_documents if chunk_doc.get("source_file") == item.get("source_file")),
                0,
            ),
        }
        for item in documents
    ]
    hygiene_index = build_knowledge_hygiene_index_for_manifest(manifest_documents)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "document_count": len(documents),
        "chunk_document_count": len(chunk_documents),
        "chunk_count": sum(int(item.get("chunk_count", 0) or 0) for item in chunk_documents),
        "embedding_status": "pending",
        "vector_store_status": "not_built",
        "documents": [
            {
                **document,
                "hygiene_flags": hygiene_index.get(document["source_file"], {}).get("hygiene_flags", []),
                "hygiene_score": hygiene_index.get(document["source_file"], {}).get("hygiene_score", 1.0),
                "hygiene_notes": hygiene_index.get(document["source_file"], {}).get("hygiene_notes", []),
            }
            for document in manifest_documents
        ],
    }
    output_path = INDEX_DIR / "knowledge_manifest.json"
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
