import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS_FILE = PROJECT_ROOT / "logs" / "search_metrics.jsonl"


def _is_enabled() -> bool:
    raw = str(os.getenv("LIVECOPILOT_SEARCH_METRICS", "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _metrics_file() -> Path:
    configured = str(os.getenv("LIVECOPILOT_SEARCH_METRICS_FILE", "")).strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_METRICS_FILE


def _topk_to_log() -> int:
    raw = str(os.getenv("LIVECOPILOT_SEARCH_METRICS_TOPK", "3")).strip()
    try:
        value = int(raw)
    except ValueError:
        value = 3
    return max(1, min(20, value))


def _extract_item_summary(result: dict[str, Any], rank: int) -> dict[str, Any]:
    tags = result.get("tags") if isinstance(result.get("tags"), dict) else {}
    return {
        "rank": rank,
        "source_file": str(result.get("source_file", "")),
        "question_id": str(result.get("question_id", "")),
        "score": float(result.get("score", 0.0) or 0.0),
        "base_score": float(result.get("base_score", 0.0) or 0.0),
        "practicality_bonus": float(result.get("practicality_bonus", 0.0) or 0.0),
        "practicality_signals": [str(signal) for signal in result.get("practicality_signals", []) if str(signal).strip()],
        "matched_tags": [str(tag) for tag in result.get("matched_tags", []) if str(tag).strip()],
        "inferred_domain": str(result.get("inferred_domain", "")),
        "inferred_subtheme": str(result.get("inferred_subtheme", "")),
        "tag_domains": [str(tag) for tag in tags.get("domain", []) if str(tag).strip()],
        "tag_subthemes": [str(tag) for tag in tags.get("subtheme", []) if str(tag).strip()],
    }


def log_search_metrics(
    *,
    search_type: str,
    query: str,
    limit: int,
    elapsed_ms: float,
    results: list[dict[str, Any]],
) -> None:
    if not _is_enabled():
        return

    try:
        topk = _topk_to_log()
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "search_type": str(search_type),
            "query": str(query),
            "limit": int(limit),
            "total_results": len(results),
            "response_time_ms": round(float(elapsed_ms), 3),
            "topk_logged": min(topk, len(results)),
            "topk": [
                _extract_item_summary(result, index)
                for index, result in enumerate(results[:topk], start=1)
                if isinstance(result, dict)
            ],
        }
        target = _metrics_file()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Metrics must never interfere with search behavior.
        return
