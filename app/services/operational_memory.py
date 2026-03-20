import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OPERATIONAL_MEMORY_FILE = Path("/lab/projects/livecopilot/data/operational_memory.jsonl")
VALID_EVENT_KINDS = {"infra_check", "project_event", "mapping_change", "voice_runtime_event"}
VALID_STATUSES = {"ok", "warn", "fail", "info"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_operational_event(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("evento de operational_memory deve ser objeto")
    timestamp = str(payload.get("timestamp", "")).strip()
    kind = str(payload.get("kind", "")).strip()
    target_type = str(payload.get("target_type", "")).strip()
    target_name = str(payload.get("target_name", "")).strip()
    status = str(payload.get("status", "")).strip()
    summary = str(payload.get("summary", "")).strip()
    source = str(payload.get("source", "")).strip()

    if not timestamp:
        raise ValueError("evento sem timestamp")
    if kind not in VALID_EVENT_KINDS:
        raise ValueError(f"kind invalido: {kind}")
    if not target_type:
        raise ValueError("evento sem target_type")
    if not target_name:
        raise ValueError("evento sem target_name")
    if status not in VALID_STATUSES:
        raise ValueError(f"status invalido: {status}")
    if not summary:
        raise ValueError("evento sem summary")
    if not source:
        raise ValueError("evento sem source")

    return {
        "timestamp": timestamp,
        "kind": kind,
        "target_type": target_type,
        "target_name": target_name,
        "status": status,
        "summary": summary,
        "source": source,
    }


def append_event(
    *,
    kind: str,
    target_type: str,
    target_name: str,
    status: str,
    summary: str,
    source: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    event = validate_operational_event(
        {
            "timestamp": str(timestamp or _now_iso()).strip(),
            "kind": kind,
            "target_type": target_type,
            "target_name": target_name,
            "status": status,
            "summary": summary,
            "source": source,
        }
    )
    OPERATIONAL_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OPERATIONAL_MEMORY_FILE.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def read_recent_events(limit: int = 20) -> list[dict[str, Any]]:
    if limit <= 0 or not OPERATIONAL_MEMORY_FILE.exists():
        return []
    rows: list[dict[str, Any]] = []
    with OPERATIONAL_MEMORY_FILE.open("r", encoding="utf-8") as fp:
        for line in fp:
            raw = str(line or "").strip()
            if not raw:
                continue
            try:
                rows.append(validate_operational_event(json.loads(raw)))
            except Exception:
                continue
    return rows[-limit:]


def get_last_event_for_target(*, kind: str, target_type: str, target_name: str) -> dict[str, Any] | None:
    for event in reversed(read_recent_events(limit=500)):
        if event["kind"] != kind:
            continue
        if event["target_type"] != target_type:
            continue
        if event["target_name"] != target_name:
            continue
        return event
    return None


def compare_with_last_event(current_event: dict[str, Any], last_event: dict[str, Any] | None) -> dict[str, Any]:
    current = validate_operational_event(current_event)
    if not last_event:
        return {
            "has_previous": False,
            "changed": False,
            "previous_status": "",
            "current_status": current["status"],
            "message": "",
        }

    previous = validate_operational_event(last_event)
    previous_status = previous["status"]
    current_status = current["status"]
    if previous_status == current_status:
        message = (
            "ultima verificacao tambem estava saudavel"
            if current_status == "ok"
            else "sem mudanca relevante desde a ultima verificacao"
        )
        return {
            "has_previous": True,
            "changed": False,
            "previous_status": previous_status,
            "current_status": current_status,
            "message": message,
        }

    return {
        "has_previous": True,
        "changed": True,
        "previous_status": previous_status,
        "current_status": current_status,
        "message": f"mudou de {previous_status} para {current_status}",
    }
