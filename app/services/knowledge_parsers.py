import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from xml.etree import ElementTree as ET

from app.core.logging import get_logger
from app.services.knowledge_tags import TAG_PIPELINE_VERSION, infer_tags

logger = get_logger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_raw"
PARSED_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_parsed"

SUPPORTED_TYPES = {".txt", ".md", ".pdf", ".docx", ".html", ".htm", ".epub"}
PARSED_STATUS_OK = "parsed"
PARSED_STATUS_ERROR = "error"
PARSED_STATUS_UNSUPPORTED = "unsupported"
PDF_EXTRACT_TIMEOUT_SECONDS = 45
PDF_FALLBACK_PAGE_LIMIT = 250


def ensure_knowledge_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)


def list_raw_files() -> list[Path]:
    ensure_knowledge_dirs()
    return sorted(path for path in RAW_DIR.rglob("*") if path.is_file())


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_title(path: Path) -> str:
    return re.sub(r"[_\-]+", " ", path.stem).strip() or path.name


def normalize_content(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_markdown_file(path: Path) -> str:
    return _read_text_file(path)


def _read_html_file(path: Path) -> str:
    from bs4 import BeautifulSoup

    raw = path.read_text(encoding="utf-8", errors="ignore")
    return _extract_html_text(raw)


def _extract_html_text(raw: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    for tag in soup.find_all(["nav", "aside"]):
        epub_type = str(tag.attrs.get("epub:type", "") or tag.attrs.get("role", "")).lower()
        classes = " ".join(str(item) for item in tag.attrs.get("class", [])).lower()
        if "toc" in epub_type or "navigation" in epub_type or "toc" in classes or "nav" in classes:
            tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    body = soup.body or soup
    text = body.get_text("\n", strip=True)
    return f"{title}\n\n{text}".strip() if title and title not in text else text


def _extract_epub_html_text(raw: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    for tag in soup.find_all(["nav", "aside"]):
        epub_type = str(tag.attrs.get("epub:type", "") or tag.attrs.get("role", "")).lower()
        classes = " ".join(str(item) for item in tag.attrs.get("class", [])).lower()
        if "toc" in epub_type or "navigation" in epub_type or "toc" in classes or "nav" in classes:
            tag.decompose()

    body = soup.body or soup
    block_tags = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "li",
        "blockquote",
        "pre",
        "dt",
        "dd",
        "figcaption",
        "caption",
        "td",
        "th",
    }
    container_tags = {"div", "section", "article"}
    selector = list(block_tags | container_tags)
    extracted_blocks: list[tuple[str, str]] = []

    for tag in body.find_all(selector):
        if tag.find_parent(list(block_tags)):
            continue
        if tag.name in container_tags and tag.find(list(block_tags)):
            continue
        if tag.name == "pre":
            text = normalize_content(tag.get_text("\n", strip=True))
        else:
            text = normalize_content(tag.get_text(" ", strip=True)).replace("\n", " ")
        if not text:
            continue
        if tag.name == "li" and not re.match(r"^(?:[-*•▪◦]|\d+[.)])\s+", text):
            text = f"- {text}"
        if tag.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            extracted_blocks.append(("heading", text))
        elif tag.name == "li":
            extracted_blocks.append(("list", text))
        elif tag.name == "pre":
            extracted_blocks.append(("pre", text))
        else:
            extracted_blocks.append(("paragraph", text))

    if extracted_blocks:
        compacted_blocks: list[str] = []
        prose_parts: list[str] = []
        prose_length = 0
        list_parts: list[str] = []

        def flush_prose() -> None:
            nonlocal prose_parts, prose_length
            if prose_parts:
                compacted_blocks.append(" ".join(prose_parts).strip())
                prose_parts = []
                prose_length = 0

        def flush_list() -> None:
            nonlocal list_parts
            if list_parts:
                compacted_blocks.append("\n".join(list_parts).strip())
                list_parts = []

        for kind, text in extracted_blocks:
            if kind == "paragraph":
                flush_list()
                projected_length = prose_length + len(text) + (1 if prose_parts else 0)
                if prose_parts and projected_length > 900:
                    flush_prose()
                prose_parts.append(text)
                prose_length += len(text) + (1 if prose_parts else 0)
                continue
            flush_prose()
            if kind == "list":
                list_parts.append(text)
                continue
            flush_list()
            compacted_blocks.append(text)

        flush_prose()
        flush_list()
        return "\n\n".join(block for block in compacted_blocks if block.strip()).strip()
    return _extract_html_text(raw)


def _looks_like_html_file(path: Path) -> bool:
    try:
        head = path.read_bytes()[:512]
    except Exception:
        return False
    lowered = head.lstrip().lower()
    return lowered.startswith(b"<!doctype html") or lowered.startswith(b"<html") or b"<html" in lowered


def _read_pdf_file(path: Path) -> str:
    if _looks_like_html_file(path):
        raw = path.read_text(encoding="utf-8", errors="ignore")
        return _extract_html_text(raw)

    pdftotext_path = shutil.which("pdftotext")
    if pdftotext_path:
        try:
            completed = subprocess.run(
                [pdftotext_path, "-layout", "-nopgbrk", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
                timeout=PDF_EXTRACT_TIMEOUT_SECONDS,
            )
            if completed.stdout.strip():
                return completed.stdout
        except subprocess.SubprocessError:
            logger.info(
                "knowledge_pdf_pdftotext_fallback",
                extra={"event": "knowledge_pdf_pdftotext_fallback", "source_file": path.name},
            )

    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages):
        if index >= PDF_FALLBACK_PAGE_LIMIT:
            raise RuntimeError(f"PDF exceeded fallback page limit ({PDF_FALLBACK_PAGE_LIMIT} pages) without pdftotext installed")
        extracted = page.extract_text() or ""
        if extracted.strip():
            pages.append(extracted)
    return "\n\n".join(pages)


def _read_docx_file(path: Path) -> str:
    from docx import Document

    document = Document(str(path))
    blocks = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            blocks.append(text)
    return "\n\n".join(blocks)


def _decode_epub_text(blob: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "utf-16le", "utf-16be", "latin-1"):
        try:
            return blob.decode(encoding)
        except UnicodeDecodeError:
            continue
    return blob.decode("utf-8", errors="ignore")


def _epub_zip_path(path: str) -> str:
    return path.lstrip("./")


def _is_epub_content_doc(name: str, media_type: str = "") -> bool:
    lowered = name.lower()
    return lowered.endswith((".xhtml", ".html", ".htm", ".xml")) or media_type in {
        "application/xhtml+xml",
        "text/html",
        "application/xml",
    }


def _resolve_epub_href(base_path: str, href: str) -> str:
    href_path = Path(href.split("#", 1)[0])
    if not str(href_path):
        return ""
    return _epub_zip_path(str((Path(base_path).parent / href_path).as_posix()))


def _clean_epub_toc_label(label: str) -> str:
    cleaned = normalize_content(label).replace("\n", " ").strip(" .:-")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _is_noise_epub_toc_label(label: str, book_title: str = "") -> bool:
    lowered = label.lower()
    if not lowered:
        return True
    if book_title and lowered == book_title.lower():
        return True
    if lowered in {"cover", "contents", "table of contents"}:
        return True
    return bool(re.fullmatch(r"[a-z]\d+(?:_[a-z0-9]+)+", lowered))


def _is_editorial_epub_preview_label(label: str) -> bool:
    lowered = label.lower().strip()
    if not lowered:
        return True
    editorial_labels = {
        "foreword",
        "preface",
        "acknowledgments",
        "acknowledgements",
        "contributors",
        "about the author",
        "about the reviewers",
        "introduction",
        "copyright",
        "dedication",
        "appendix",
        "index",
    }
    return lowered in editorial_labels


def _build_epub_toc_hint_preview(toc_entries: list[str], limit: int = 8) -> list[str]:
    technical_entries = [entry for entry in toc_entries if not _is_editorial_epub_preview_label(entry)]
    preview = technical_entries[:limit]
    if len(preview) >= limit:
        return preview

    for entry in toc_entries:
        if entry in preview:
            continue
        preview.append(entry)
        if len(preview) >= limit:
            break
    return preview


def _build_epub_section_record(
    doc_path: str,
    title: str,
    text: str,
) -> dict[str, str]:
    return {
        "doc_path": doc_path,
        "title": _clean_epub_toc_label(title),
        "content": text.strip(),
    }


def _is_epub_internal_marker_line(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    return bool(re.fullmatch(r"[A-Z]\d+(?:_[A-Za-z0-9]+)+", candidate))


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
    if not words or len(words) > 12 or len(candidate) > 100:
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
    if re.match(r"^(?:and|or|but|for|nor|so|yet|to|of|in|on|at|by|with|without|from|into|over|under|the|a|an)\b", candidate, flags=re.IGNORECASE):
        return True
    if len(candidate) <= 40 and not re.search(r"[.!?]$", candidate):
        return True
    return False


def _join_epub_lines(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left
    separator = ""
    if left.endswith(("(", "/", "-")) or right.startswith((",", ".", ";", ":", ")", "]", "%")):
        separator = ""
    else:
        separator = " "
    return f"{left}{separator}{right}".strip()


def _should_unwrap_epub_lines(current: str, next_line: str) -> bool:
    if not current or not next_line:
        return False
    if _is_epub_list_line(current) or _is_epub_list_line(next_line):
        return False
    if _is_epub_heading_line(current) or _is_epub_heading_line(next_line):
        return False
    if re.search(r'[.!?]["\')\]]*$', current):
        return False
    if current.endswith(":") and (_is_epub_list_line(next_line) or _is_epub_heading_line(next_line)):
        return False
    if current.endswith((",", ";", ":", "(", "/", "-")):
        return True
    if _looks_like_epub_continuation(next_line):
        return True
    current_words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", current)
    next_words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", next_line)
    if len(current_words) <= 8 or len(next_words) <= 5:
        return True
    return False


def _unwrap_epub_paragraphs(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    paragraphs: list[str] = []
    current = ""

    for line in lines:
        if not line:
            if current:
                paragraphs.append(current.strip())
                current = ""
            continue
        if not current:
            current = line
            continue
        if _should_unwrap_epub_lines(current, line):
            current = _join_epub_lines(current, line)
            continue
        paragraphs.append(current.strip())
        current = line

    if current:
        paragraphs.append(current.strip())
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph).strip()


def _clean_epub_section_text(text: str) -> str:
    cleaned_lines = [
        line
        for line in text.splitlines()
        if not _is_epub_internal_marker_line(line)
    ]
    normalized = normalize_content("\n".join(cleaned_lines))
    return _unwrap_epub_paragraphs(normalized)


def _score_epub_toc_label(label: str, book_title: str = "") -> int:
    lowered = label.lower()
    if not lowered:
        return -1
    if _is_noise_epub_toc_label(label, book_title=book_title):
        return 0

    score = 1
    if re.search(r"\bchapter\s+\d+\b", lowered):
        score += 10
    elif re.search(r"\bpart\s+\d+\b", lowered):
        score += 8
    elif lowered in {"preface", "introduction", "foreword", "appendix"}:
        score += 6

    if len(label) >= 12:
        score += 2
    if re.fullmatch(r"\d+", lowered):
        score -= 6
    if re.fullmatch(r"[a-z]\d+(?:_[a-z0-9]+)*", lowered):
        score -= 8
    if re.search(r"\b(id|toc|fm|part|chapter)?[_-]?\d+\b", lowered) and "chapter" not in lowered and "part" not in lowered:
        score -= 4
    return score


def _register_epub_toc_entry(
    toc_map: dict[str, tuple[int, str]],
    doc_path: str,
    label: str,
    *,
    book_title: str = "",
) -> None:
    cleaned = _clean_epub_toc_label(label)
    if not cleaned or not doc_path:
        return

    score = _score_epub_toc_label(cleaned, book_title=book_title)
    current = toc_map.get(doc_path)
    if current is None or score > current[0]:
        toc_map[doc_path] = (score, cleaned)


def _extract_epub_nav_toc_map(raw: str, base_path: str, *, book_title: str = "") -> dict[str, tuple[int, str]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw, "html.parser")
    toc_map: dict[str, tuple[int, str]] = {}
    for anchor in soup.select("nav a[href], [epub\\:type='toc'] a[href], a[href]"):
        href = str(anchor.get("href", "")).strip()
        doc_path = _resolve_epub_href(base_path, href)
        if not doc_path:
            continue
        label = anchor.get_text(" ", strip=True)
        _register_epub_toc_entry(toc_map, doc_path, label, book_title=book_title)
    return toc_map


def _extract_epub_ncx_toc_map(raw: str, base_path: str, *, book_title: str = "") -> dict[str, tuple[int, str]]:
    toc_map: dict[str, tuple[int, str]] = {}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return toc_map

    for nav_point in root.findall(".//{*}navPoint"):
        label = nav_point.findtext(".//{*}navLabel/{*}text", default="").strip()
        content = nav_point.find(".//{*}content")
        href = content.attrib.get("src", "").strip() if content is not None else ""
        doc_path = _resolve_epub_href(base_path, href)
        _register_epub_toc_entry(toc_map, doc_path, label, book_title=book_title)
    return toc_map


def _extract_epub_toc_map(
    archive: zipfile.ZipFile,
    manifest_items: dict[str, dict[str, str]],
    package_path: str,
    *,
    book_title: str = "",
) -> dict[str, str]:
    toc_candidates: list[str] = []
    for item in manifest_items.values():
        href = item.get("href", "")
        media_type = item.get("media_type", "")
        properties = item.get("properties", "")
        if not href:
            continue
        lowered = href.lower()
        if "nav" in properties or media_type == "application/x-dtbncx+xml" or lowered.endswith(("toc.ncx", "toc.xhtml", "toc.html")):
            toc_candidates.append(href)

    if not toc_candidates:
        toc_candidates = [
            _resolve_epub_href(package_path, candidate)
            for candidate in ("toc.xhtml", "toc.html", "toc.ncx")
        ]

    merged_map: dict[str, tuple[int, str]] = {}
    for toc_path in dict.fromkeys(candidate for candidate in toc_candidates if candidate):
        try:
            raw = _decode_epub_text(archive.read(toc_path))
        except KeyError:
            continue
        if toc_path.lower().endswith(".ncx"):
            candidate_map = _extract_epub_ncx_toc_map(raw, toc_path, book_title=book_title)
        else:
            candidate_map = _extract_epub_nav_toc_map(raw, toc_path, book_title=book_title)
        for doc_path, candidate in candidate_map.items():
            current = merged_map.get(doc_path)
            if current is None or candidate[0] > current[0]:
                merged_map[doc_path] = candidate

    return {
        doc_path: label
        for doc_path, (score, label) in merged_map.items()
        if score > 0 and label
    }


def _read_epub_file(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        if "mimetype" not in archive.namelist():
            raise RuntimeError("EPUB missing mimetype entry")

        try:
            mimetype = archive.read("mimetype").decode("utf-8", errors="ignore").strip()
        except KeyError as exc:
            raise RuntimeError("EPUB missing mimetype entry") from exc
        if mimetype != "application/epub+zip":
            raise RuntimeError(f"Unsupported EPUB mimetype: {mimetype or 'unknown'}")

        package_path = ""
        try:
            container_root = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = container_root.find(".//{*}rootfile")
            if rootfile is not None:
                package_path = _epub_zip_path(rootfile.attrib.get("full-path", ""))
        except KeyError:
            package_path = ""
        except ET.ParseError as exc:
            raise RuntimeError("EPUB container.xml is malformed") from exc

        if not package_path:
            opf_candidates = sorted(name for name in archive.namelist() if name.lower().endswith(".opf"))
            if not opf_candidates:
                raise RuntimeError("EPUB package document (.opf) not found")
            package_path = _epub_zip_path(opf_candidates[0])

        try:
            package_root = ET.fromstring(archive.read(package_path))
        except KeyError as exc:
            raise RuntimeError(f"EPUB package document not found: {package_path}") from exc
        except ET.ParseError as exc:
            raise RuntimeError("EPUB package document is malformed") from exc

        metadata_title = package_root.findtext(".//{*}metadata/{*}title", default="").strip()

        manifest_items: dict[str, dict[str, str]] = {}
        for item in package_root.findall(".//{*}manifest/{*}item"):
            item_id = item.attrib.get("id", "").strip()
            if not item_id:
                continue
            manifest_items[item_id] = {
                "href": _resolve_epub_href(package_path, item.attrib.get("href", "")),
                "media_type": item.attrib.get("media-type", "").strip(),
                "properties": item.attrib.get("properties", "").strip(),
            }

        spine_paths: list[str] = []
        toc_entries: list[str] = []
        for itemref in package_root.findall(".//{*}spine/{*}itemref"):
            item_id = itemref.attrib.get("idref", "").strip()
            item = manifest_items.get(item_id, {})
            href = item.get("href", "")
            if not href or not _is_epub_content_doc(href, item.get("media_type", "")):
                continue
            if "nav" in item.get("properties", ""):
                continue
            spine_paths.append(href)

        if not spine_paths:
            for item in manifest_items.values():
                href = item.get("href", "")
                if href and _is_epub_content_doc(href, item.get("media_type", "")) and "nav" not in item.get("properties", ""):
                    spine_paths.append(href)

        if not spine_paths:
            raise RuntimeError("EPUB does not contain readable HTML/XHTML sections")

        toc_map = _extract_epub_toc_map(
            archive,
            manifest_items,
            package_path,
            book_title=metadata_title,
        )
        sections: list[str] = []
        section_records: list[dict[str, str]] = []
        toc_entries_seen: set[str] = set()
        for doc_path in spine_paths:
            try:
                raw = _decode_epub_text(archive.read(doc_path))
            except KeyError:
                continue
            section_text = _clean_epub_section_text(normalize_content(_extract_epub_html_text(raw)))
            if not section_text:
                continue

            lines = [line.strip() for line in section_text.splitlines() if line.strip()]
            fallback_heading = lines[0] if lines else ""
            toc_heading = toc_map.get(doc_path, fallback_heading)
            cleaned_heading = _clean_epub_toc_label(toc_heading)
            if (
                cleaned_heading
                and not _is_noise_epub_toc_label(cleaned_heading, book_title=metadata_title)
                and cleaned_heading not in toc_entries_seen
            ):
                toc_entries_seen.add(cleaned_heading)
                toc_entries.append(cleaned_heading)
            if fallback_heading:
                sections.append(f"{fallback_heading}\n\n{section_text}")
                section_records.append(_build_epub_section_record(doc_path, cleaned_heading or fallback_heading, section_text))
            else:
                sections.append(section_text)
                if cleaned_heading:
                    section_records.append(_build_epub_section_record(doc_path, cleaned_heading, section_text))

        content = "\n\n".join(section for section in sections if section.strip()).strip()
        if not content:
            raise RuntimeError("No textual content extracted from EPUB sections")

        return {
            "content": content,
            "title": metadata_title,
            "chapter_count": len(sections),
            "toc_hint": _build_epub_toc_hint_preview(toc_entries),
            "sections": section_records,
        }


PARSERS: Dict[str, Callable[[Path], str | dict[str, Any]]] = {
    ".txt": _read_text_file,
    ".md": _read_markdown_file,
    ".pdf": _read_pdf_file,
    ".docx": _read_docx_file,
    ".html": _read_html_file,
    ".htm": _read_html_file,
    ".epub": _read_epub_file,
}


def parsed_output_path(source_path: Path) -> Path:
    relative = source_path.relative_to(RAW_DIR)
    target_name = "__".join(relative.parts) + ".json"
    return PARSED_DIR / target_name


def parse_file(source_path: Path) -> dict:
    ensure_knowledge_dirs()
    suffix = source_path.suffix.lower()
    sha256 = compute_sha256(source_path)
    title = infer_title(source_path)
    payload = {
        "source_file": str(source_path.relative_to(RAW_DIR)),
        "file_type": suffix.lstrip("."),
        "title": title,
        "content": "",
        "tags": infer_tags(
            source_file=str(source_path.relative_to(RAW_DIR)),
            title=title,
            content="",
            path_hint=str(source_path.parent.relative_to(RAW_DIR)) if source_path.parent != RAW_DIR else "",
        ),
        "tag_pipeline_version": TAG_PIPELINE_VERSION,
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256,
        "status": PARSED_STATUS_OK,
    }

    parser = PARSERS.get(suffix)
    if parser is None:
        payload["status"] = PARSED_STATUS_UNSUPPORTED
        payload["error"] = f"Unsupported file type: {suffix}"
        return payload

    try:
        parsed_result = parser(source_path)
        metadata = parsed_result if isinstance(parsed_result, dict) else {"content": parsed_result}
        if metadata.get("title"):
            payload["title"] = str(metadata["title"]).strip() or title
        content = normalize_content(str(metadata.get("content", "")))
        if not content:
            payload["status"] = PARSED_STATUS_ERROR
            payload["error"] = "No textual content extracted"
        else:
            payload["content"] = content
            if "chapter_count" in metadata:
                payload["chapter_count"] = int(metadata.get("chapter_count", 0) or 0)
            if "toc_hint" in metadata:
                toc_hint = metadata.get("toc_hint", [])
                if isinstance(toc_hint, list):
                    payload["toc_hint"] = [str(item) for item in toc_hint if str(item).strip()][:8]
            if "sections" in metadata:
                sections = metadata.get("sections", [])
                if isinstance(sections, list):
                    payload["sections"] = [
                        {
                            "doc_path": str(item.get("doc_path", "")).strip(),
                            "title": str(item.get("title", "")).strip(),
                            "content": str(item.get("content", "")).strip(),
                        }
                        for item in sections
                        if isinstance(item, dict)
                        and str(item.get("content", "")).strip()
                    ]
            payload["tags"] = infer_tags(
                source_file=payload["source_file"],
                title=payload["title"],
                content=content,
                path_hint=str(source_path.parent.relative_to(RAW_DIR)) if source_path.parent != RAW_DIR else "",
            )
            payload["tag_pipeline_version"] = TAG_PIPELINE_VERSION
    except Exception as exc:
        logger.exception(
            "knowledge_parse_error",
            extra={"event": "knowledge_parse_error", "source_file": payload["source_file"], "file_type": payload["file_type"]},
        )
        payload["status"] = PARSED_STATUS_ERROR
        payload["error"] = str(exc)
    return payload


def write_parsed_payload(payload: dict) -> Path:
    output_path = parsed_output_path(RAW_DIR / payload["source_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def load_parsed_payload(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(loaded, dict):
        return loaded
    return None
