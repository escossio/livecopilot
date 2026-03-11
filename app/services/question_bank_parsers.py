import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional

from app.core.logging import get_logger
from app.services.knowledge_tags import infer_tags

logger = get_logger(__name__)

QUESTION_BANK_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "question_bank_raw"
QUESTION_BANK_PARSED_DIR = Path(__file__).resolve().parents[2] / "data" / "question_bank_parsed"
QUESTION_BANK_ITEMS_DIR = Path(__file__).resolve().parents[2] / "data" / "question_bank_items"

SUPPORTED_TYPES = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}
PARSED_STATUS_OK = "parsed"
PARSED_STATUS_ERROR = "error"
PARSED_STATUS_UNSUPPORTED = "unsupported"
PDF_EXTRACT_TIMEOUT_SECONDS = 45
PDF_FALLBACK_PAGE_LIMIT = 250
BACKUP_FILENAME_MARKERS = (".backup.", ".pre-", ".bak", ".backup")


def ensure_question_bank_dirs() -> None:
    QUESTION_BANK_RAW_DIR.mkdir(parents=True, exist_ok=True)
    QUESTION_BANK_PARSED_DIR.mkdir(parents=True, exist_ok=True)
    QUESTION_BANK_ITEMS_DIR.mkdir(parents=True, exist_ok=True)


def _is_operational_backup_file(path: Path) -> bool:
    lowered_name = path.name.lower()
    return any(marker in lowered_name for marker in BACKUP_FILENAME_MARKERS)


def list_question_bank_raw_files() -> list[Path]:
    ensure_question_bank_dirs()
    return sorted(path for path in QUESTION_BANK_RAW_DIR.rglob("*") if path.is_file() and not _is_operational_backup_file(path))


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
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    body = soup.body or soup
    text = body.get_text("\n", strip=True)
    return f"{title}\n\n{text}".strip() if title and title not in text else text


def _read_pdf_file(path: Path) -> str:
    pdftotext_path = shutil.which("pdftotext")
    if pdftotext_path:
        completed = subprocess.run(
            [pdftotext_path, "-layout", "-nopgbrk", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=PDF_EXTRACT_TIMEOUT_SECONDS,
        )
        return completed.stdout

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


PARSERS: Dict[str, Callable[[Path], str]] = {
    ".txt": _read_text_file,
    ".md": _read_markdown_file,
    ".pdf": _read_pdf_file,
    ".docx": _read_docx_file,
    ".html": _read_html_file,
    ".htm": _read_html_file,
}


def parsed_output_path(source_path: Path) -> Path:
    relative = source_path.relative_to(QUESTION_BANK_RAW_DIR)
    target_name = "__".join(relative.parts) + ".json"
    return QUESTION_BANK_PARSED_DIR / target_name


def parse_question_bank_file(source_path: Path) -> dict:
    ensure_question_bank_dirs()
    suffix = source_path.suffix.lower()
    sha256 = compute_sha256(source_path)
    relative_source = str(source_path.relative_to(QUESTION_BANK_RAW_DIR))
    title = infer_title(source_path)
    payload = {
        "source_file": relative_source,
        "file_type": suffix.lstrip("."),
        "title": title,
        "content": "",
        "tags": infer_tags(
            source_file=relative_source,
            title=title,
            content="",
            path_hint=str(source_path.parent.relative_to(QUESTION_BANK_RAW_DIR)) if source_path.parent != QUESTION_BANK_RAW_DIR else "",
        ),
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256,
        "status": PARSED_STATUS_OK,
        "pipeline": "question_bank",
    }

    parser = PARSERS.get(suffix)
    if parser is None:
        payload["status"] = PARSED_STATUS_UNSUPPORTED
        payload["error"] = f"Unsupported file type: {suffix}"
        return payload

    try:
        content = normalize_content(parser(source_path))
        if not content:
            payload["status"] = PARSED_STATUS_ERROR
            payload["error"] = "No textual content extracted"
        else:
            payload["content"] = content
            payload["tags"] = infer_tags(
                source_file=relative_source,
                title=title,
                content=content,
                path_hint=str(source_path.parent.relative_to(QUESTION_BANK_RAW_DIR)) if source_path.parent != QUESTION_BANK_RAW_DIR else "",
            )
    except Exception as exc:
        logger.exception(
            "question_bank_parse_error",
            extra={"event": "question_bank_parse_error", "source_file": relative_source, "file_type": payload["file_type"]},
        )
        payload["status"] = PARSED_STATUS_ERROR
        payload["error"] = str(exc)
    return payload


def write_parsed_payload(payload: dict) -> Path:
    output_path = parsed_output_path(QUESTION_BANK_RAW_DIR / payload["source_file"])
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
