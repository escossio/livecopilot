import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

KNOWLEDGE_GAPS_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_gaps.ndjson"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_context(context: Any) -> Any:
    if isinstance(context, (dict, list, str, int, float, bool)) or context is None:
        return context
    return str(context)


def log_knowledge_gap(query: str, reason: str, context: Any, source: str = "project_brain_query") -> bool:
    payload = {
        "timestamp": _now_iso(),
        "query": str(query or "").strip(),
        "context": {
            "reason": str(reason or "").strip() or "unspecified",
            "details": _safe_context(context),
        },
        "source": str(source or "project_brain_query").strip() or "project_brain_query",
        "status": "open",
    }
    if not payload["query"]:
        return False

    try:
        KNOWLEDGE_GAPS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with KNOWLEDGE_GAPS_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        logger.info(
            "knowledge_gap_logged",
            extra={
                "event": "knowledge_gap_logged",
                "query": payload["query"],
                "reason": payload["context"]["reason"],
                "source": payload["source"],
            },
        )
        return True
    except Exception as exc:
        logger.warning(
            "knowledge_gap_log_failed",
            extra={
                "event": "knowledge_gap_log_failed",
                "query": payload["query"],
                "reason": payload["context"]["reason"],
                "error": str(exc),
            },
        )
        return False
