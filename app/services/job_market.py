import json
import threading
import unicodedata
from pathlib import Path
from typing import List, Dict, Any

_lock = threading.Lock()
_cache: List[Dict[str, Any]] | None = None

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "job_market_seed.json"


def normalize_text(text: str) -> str:
    lowered = text.lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = []
    for ch in normalized:
        if ch.isalnum() or ch in {"+", "#", " ", "."}:
            cleaned.append(ch)
        else:
            cleaned.append(" ")
    return " ".join("".join(cleaned).split())


def load_job_market_seed() -> List[Dict[str, Any]]:
    global _cache
    if _cache is not None:
        return _cache
    with _lock:
        if _cache is not None:
            return _cache
        if not DATA_PATH.exists():
            _cache = []
            return _cache
        try:
            payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                _cache = payload
            else:
                _cache = []
        except Exception:
            _cache = []
    return _cache


def match_terms(text: str, limit: int = 3) -> List[str]:
    if not text:
        return []
    normalized = f" {normalize_text(text)} "
    matches = []
    for item in load_job_market_seed():
        term = str(item.get("termo", "") or item.get("term", "")).strip()
        if not term:
            continue
        aliases = item.get("aliases")
        if isinstance(aliases, list):
            candidates = [term, *[str(alias) for alias in aliases if isinstance(alias, str)]]
        else:
            candidates = [term]
        if any(f" {normalize_text(candidate)} " in normalized for candidate in candidates if candidate.strip()):
            matches.append(item)

    if not matches:
        return []

    specific_matches = []
    generic_categories = {
        str(item.get("categoria", "") or item.get("category", ""))
        for item in matches
        if not bool(item.get("generic")) and str(item.get("subcategoria", "") or item.get("subcategory", "")) not in {"", "geral", "genérico"}
    }
    specific_subcategories = {
        str(item.get("subcategoria", "") or item.get("subcategory", ""))
        for item in matches
        if not bool(item.get("generic")) and str(item.get("subcategoria", "") or item.get("subcategory", "")) not in {"", "geral", "genérico"}
    }
    for item in matches:
        category = str(item.get("categoria", "") or item.get("category", ""))
        subcategory = str(item.get("subcategoria", "") or item.get("subcategory", ""))
        is_generic = bool(item.get("generic"))
        if is_generic and category in generic_categories:
            continue
        if is_generic and subcategory in specific_subcategories:
            continue
        specific_matches.append(item)

    specific_matches.sort(
        key=lambda item: (
            -len(normalize_text(str(item.get("termo", "") or item.get("term", ""))).split()),
            -int(item.get("frequencia", item.get("frequency", 0)) or 0),
            str(item.get("termo", "") or item.get("term", "")),
        )
    )
    return [str(item.get("termo", "") or item.get("term", "")).strip() for item in specific_matches[:limit]]
