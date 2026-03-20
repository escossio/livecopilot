import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.logging import get_logger


VOICE_OBSERVABILITY_DIR = Path("/lab/projects/livecopilot/var/voice_observability")
VOICE_EVENTS_FILE = VOICE_OBSERVABILITY_DIR / "voice_events.ndjson"
VOICE_SESSION_ROOT = Path("/lab/projects/livecopilot/logs/voice_sessions")
VOICE_SESSION_INDEX_FILE = VOICE_SESSION_ROOT / "session_index.json"
VOICE_EVENTS_RETENTION_DAYS = 7

logger = get_logger(__name__)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize_text(value: Any, limit: int = 160) -> str:
    text = " ".join(str(value or "").strip().split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].strip() + "..."


def _safe_session_id(value: Any) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return text or "anonymous"


def _dir_stamp(ts: str) -> str:
    text = str(ts or now_iso()).strip()
    text = text.replace("+00:00", "Z")
    text = text.replace(":", "").replace("-", "")
    text = text.replace(".", "")
    text = text.replace("T", "T")
    return text[:16] if len(text) >= 16 else now_iso().replace(":", "").replace("-", "")[:16]


def _ensure_base_dirs() -> None:
    VOICE_OBSERVABILITY_DIR.mkdir(parents=True, exist_ok=True)
    VOICE_SESSION_ROOT.mkdir(parents=True, exist_ok=True)


def _load_index() -> dict[str, dict[str, str]]:
    try:
        if not VOICE_SESSION_INDEX_FILE.exists():
            return {}
        raw = json.loads(VOICE_SESSION_INDEX_FILE.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _write_index(payload: dict[str, dict[str, str]]) -> None:
    _ensure_base_dirs()
    tmp_path = VOICE_SESSION_INDEX_FILE.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(VOICE_SESSION_INDEX_FILE)


def _session_dir_for(session_id: str, started_at: str) -> Path:
    _ensure_base_dirs()
    safe_session_id = _safe_session_id(session_id)
    index = _load_index()
    row = index.get(safe_session_id, {})
    dir_name = str(row.get("dir_name", "")).strip()
    if dir_name:
        return VOICE_SESSION_ROOT / dir_name
    dir_name = f"{_dir_stamp(started_at)}_{safe_session_id}"
    index[safe_session_id] = {
        "dir_name": dir_name,
        "started_at": str(started_at or now_iso()),
    }
    _write_index(index)
    return VOICE_SESSION_ROOT / dir_name


def _session_file(session_dir: Path, filename: str) -> Path:
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / filename


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
    except Exception:
        return []
    return rows


def _build_summary(session_dir: Path, meta: dict[str, Any]) -> str:
    frontend_events = _read_jsonl(session_dir / "frontend_events.jsonl")
    backend_events = _read_jsonl(session_dir / "backend_events.jsonl")
    responses = _read_jsonl(session_dir / "responses.jsonl")
    errors = _read_jsonl(session_dir / "errors.jsonl")
    transcripts = _read_jsonl(session_dir / "transcripts.jsonl")

    all_events = frontend_events + backend_events
    all_events.sort(key=lambda item: str(item.get("ts", "")))
    last_success = ""
    for item in reversed(all_events):
        name = str(item.get("event", "")).strip()
        if name and "failed" not in name and "error" not in name:
            last_success = name
            break

    first_failure = ""
    first_failure_detail = ""
    if errors:
        first_failure = str(errors[0].get("event", "voice_error")).strip() or "voice_error"
        first_failure_detail = summarize_text(errors[0].get("message", "") or errors[0].get("error_message", ""), limit=180)

    hypothesis = "fluxo ainda sem evidencia suficiente"
    if transcripts and not backend_events:
        hypothesis = "a transcricao final foi capturada, mas nao ha evidencia de envio ao backend"
    elif backend_events and not responses and not errors:
        hypothesis = "o backend recebeu a consulta, mas nao ha resposta registrada; verificar status HTTP e excecoes"
    elif responses and not any(str(item.get("event", "")).strip() == "voice_backend_response_rendered" for item in frontend_events):
        hypothesis = "a resposta chegou do backend, mas nao ha evidencia de renderizacao na UI"
    elif errors:
        hypothesis = f"falha registrada: {first_failure_detail or first_failure}"

    lines = [
        "# Voice Session Summary",
        "",
        f"- session_id: `{meta.get('session_id', '')}`",
        f"- started_at: `{meta.get('started_at', '')}`",
        f"- session_dir: `{session_dir}`",
        f"- transport: `{meta.get('transport', '')}`",
        f"- model: `{meta.get('model', '')}`",
        f"- voice: `{meta.get('voice', '')}`",
        f"- frontend_events: `{len(frontend_events)}`",
        f"- backend_events: `{len(backend_events)}`",
        f"- transcripts: `{len(transcripts)}`",
        f"- responses: `{len(responses)}`",
        f"- errors: `{len(errors)}`",
        "",
        f"- ultimo evento bem-sucedido: `{last_success or 'n/a'}`",
        f"- primeiro ponto de falha ou silencio: `{first_failure or 'n/a'}`",
        f"- hipotese principal: {hypothesis}",
    ]
    if first_failure_detail:
        lines.append(f"- detalhe da falha: {first_failure_detail}")
    return "\n".join(lines) + "\n"


def _update_session_meta(session_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    meta_path = _session_file(session_dir, "session_meta.json")
    current = _read_json(meta_path)
    current.update({k: v for k, v in payload.items() if v not in (None, "")})
    current["session_id"] = str(payload.get("session_id", current.get("session_id", ""))).strip()
    current["started_at"] = str(payload.get("started_at", current.get("started_at", now_iso()))).strip()
    current["last_event"] = str(payload.get("event", current.get("last_event", ""))).strip()
    current["updated_at"] = now_iso()
    _write_json(meta_path, current)
    return current


def get_latest_voice_session_dir() -> str:
    _ensure_base_dirs()
    entries = [item for item in VOICE_SESSION_ROOT.iterdir() if item.is_dir()]
    if not entries:
        return ""
    latest = sorted(entries, key=lambda item: item.name)[-1]
    return str(latest)


def record_voice_event(event: str, **payload: Any) -> str:
    try:
        _ensure_base_dirs()
        ts = str(payload.get("ts", "") or now_iso()).strip()
        source = str(payload.get("source", "") or "frontend").strip() or "frontend"
        session_id = str(payload.get("session_id", "") or payload.get("conversation_id", "") or "anonymous").strip()
        conversation_id = str(payload.get("conversation_id", "") or session_id).strip()
        session_dir = _session_dir_for(session_id, payload.get("started_at", "") or ts)
        row = {
            "ts": ts,
            "event": str(event or "").strip(),
            **payload,
            "session_id": session_id,
            "conversation_id": conversation_id,
            "source": source,
            "session_dir": str(session_dir),
        }

        _append_jsonl(VOICE_EVENTS_FILE, row)

        if source == "backend":
            _append_jsonl(_session_file(session_dir, "backend_events.jsonl"), row)
        else:
            _append_jsonl(_session_file(session_dir, "frontend_events.jsonl"), row)

        transcript_excerpt = summarize_text(payload.get("transcript_excerpt", ""), limit=240)
        if event == "transcription_completed" and transcript_excerpt:
            _append_jsonl(
                _session_file(session_dir, "transcripts.jsonl"),
                {
                    "ts": ts,
                    "session_id": session_id,
                    "conversation_id": conversation_id,
                    "text": transcript_excerpt,
                },
            )

        response_summary = summarize_text(payload.get("response_summary", ""), limit=240)
        if event in {"voice_backend_response_received", "voice_backend_response_rendered", "voice_backend_response_completed"} and response_summary:
            _append_jsonl(
                _session_file(session_dir, "responses.jsonl"),
                {
                    "ts": ts,
                    "session_id": session_id,
                    "conversation_id": conversation_id,
                    "answer": response_summary,
                    "backend": str(payload.get("backend", "")).strip(),
                    "connector": str(payload.get("backend", "")).strip(),
                    "http_status": payload.get("http_status"),
                    "event": event,
                },
            )

        error_message = summarize_text(payload.get("error_message", ""), limit=240)
        if error_message or "failed" in event or event == "voice_error":
            _append_jsonl(
                _session_file(session_dir, "errors.jsonl"),
                {
                    "ts": ts,
                    "session_id": session_id,
                    "conversation_id": conversation_id,
                    "side": source,
                    "event": event,
                    "http_status": payload.get("http_status"),
                    "message": error_message or summarize_text(payload.get("response_summary", ""), limit=240),
                },
            )

        meta = _update_session_meta(
            session_dir,
            {
                "session_id": session_id,
                "conversation_id": conversation_id,
                "started_at": str(payload.get("started_at", "") or ts).strip(),
                "url": str(payload.get("url", "")).strip(),
                "transport": str(payload.get("transport", "")).strip(),
                "model": str(payload.get("model", "")).strip(),
                "voice": str(payload.get("voice", "")).strip(),
                "secure_context": payload.get("secure_context"),
                "media_devices": payload.get("media_devices"),
                "get_user_media": payload.get("get_user_media"),
                "user_agent": str(payload.get("user_agent", "")).strip(),
                "provider_event_type": str(payload.get("provider_event_type", "")).strip(),
                "event": str(event or "").strip(),
            },
        )
        _session_file(session_dir, "summary.md").write_text(_build_summary(session_dir, meta), encoding="utf-8")

        logger.info(
            "voice_event",
            extra={
                "event": row["event"],
                "session_id": session_id,
                "conversation_id": conversation_id,
                "source": source,
                "session_dir": str(session_dir),
                "http_status": payload.get("http_status"),
                "backend": str(payload.get("backend", "")).strip(),
            },
        )
        return str(session_dir)
    except Exception:
        # Observabilidade nao deve quebrar a trilha principal.
        return ""
