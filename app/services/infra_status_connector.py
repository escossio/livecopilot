import json
import os
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.request
from typing import Any

from fastapi import Request

from app.core.config import settings
from app.services.operational_memory import append_event, compare_with_last_event, get_last_event_for_target
from app.services.realtime_openai import get_realtime_runtime
from app.services.transcription import get_transcription_runtime
from app.services.voice_output import get_voice_output_runtime

SERVER_HOST_ENDPOINTS: dict[str, dict[str, str]] = {
    "agt01": {
        "health_url": "http://agt01:8000/health",
        "status_url": "http://agt01:8000/status",
    },
}
SERVER_TARGET_ALIASES = {"agt01", "debian2-1", "llm"}


def _normalize(text: str) -> str:
    lowered = str(text or "").strip().lower()
    ascii_text = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def _build_operational_memory_summary(target_type: str, target_name: str, status: str) -> str:
    if target_type == "postgresql":
        return f"check curto de PostgreSQL em {target_name}: status {status}"
    if target_type == "server":
        return f"check curto de servidor em {target_name}: status {status}"
    if target_type == "backend":
        return f"check curto do backend em {target_name}: status {status}"
    return f"evento operacional em {target_name}: status {status}"


def _build_operational_memory_note(target_type: str, target_name: str, status: str) -> dict[str, Any]:
    current_event = {
        "timestamp": "1970-01-01T00:00:00Z",
        "kind": "infra_check",
        "target_type": target_type,
        "target_name": target_name,
        "status": status,
        "summary": _build_operational_memory_summary(target_type, target_name, status),
        "source": "infra_status_connector",
    }
    last_event = get_last_event_for_target(kind="infra_check", target_type=target_type, target_name=target_name)
    comparison = compare_with_last_event(current_event, last_event)
    append_event(
        kind="infra_check",
        target_type=target_type,
        target_name=target_name,
        status=status,
        summary=current_event["summary"],
        source="infra_status_connector",
    )
    return comparison


def _looks_like_infra_query(query: str) -> bool:
    normalized = _normalize(query)
    if not normalized:
        return False
    if "terraform" in normalized and "backend" in normalized:
        return False
    return any(
        token in normalized
        for token in (
            "backend",
            "servidor",
            "server",
            "load",
            "carga",
            "uptime",
            "memoria",
            "saudavel",
            "saudavel?",
            "health",
            "status do servico",
            "servico principal",
            "postgres",
            "postgresql",
            "infra",
        )
    )


def _looks_like_postgres_query(query: str) -> bool:
    normalized = _normalize(query)
    if not normalized:
        return False
    if "postgres" in normalized or "postgresql" in normalized:
        return True
    banco_tokens = ("banco", "database", "db")
    status_tokens = ("saudavel", "de pe", "em pe", "disponivel", "saude", "health", "status")
    return any(token in normalized for token in banco_tokens) and any(token in normalized for token in status_tokens)


def _looks_like_server_query(query: str) -> bool:
    normalized = _normalize(query)
    if not normalized:
        return False
    server_tokens = ("servidor", "server", "hostname", "host")
    metric_tokens = ("saudavel", "de pe", "em pe", "load", "carga", "uptime", "memoria", "memory", "health", "status", "como esta")
    explicit_host_mentioned = any(token in normalized.split() for token in SERVER_TARGET_ALIASES)
    return (any(token in normalized for token in server_tokens) or explicit_host_mentioned) and any(
        token in normalized for token in metric_tokens
    )


def _extract_server_target(query: str) -> str:
    normalized = _normalize(query)
    stopwords = {"esta", "esta?", "saudavel", "de", "em", "funcionando", "carga", "status"}
    tokens = normalized.split()
    for token in tokens:
        candidate = str(token or "").strip(" ?!.,;:")
        if candidate in SERVER_TARGET_ALIASES:
            return candidate
    for idx, token in enumerate(tokens[:-1]):
        if token not in {"servidor", "server", "host"}:
            continue
        candidate = str(tokens[idx + 1] or "").strip(" ?!.,;:")
        if candidate and candidate not in stopwords:
            return candidate
    return ""


def _postgres_dsn() -> str:
    return (
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SEMANTIC_PG_DSN", "").strip()
        or os.getenv("LIVECOPILOT_DB_DSN", "").strip()
    )


def _check_postgres_runtime() -> dict[str, Any]:
    dsn = _postgres_dsn()
    if not dsn:
        return {
            "status": "warn",
            "reason": "database_url_missing",
            "latency_ms": None,
            "database": "",
            "server_version": "",
            "select_1_ok": False,
            "dsn_present": False,
        }

    started = time.monotonic()
    try:
        import psycopg

        with psycopg.connect(dsn, connect_timeout=2) as conn:
            conn.autocommit = True
            try:
                conn.read_only = True
            except Exception:
                pass
            with conn.cursor() as cur:
                cur.execute("select 1")
                select_1_row = cur.fetchone() or [None]
                cur.execute("select current_database(), version()")
                info_row = cur.fetchone() or ["", ""]
        latency_ms = int((time.monotonic() - started) * 1000)
        version_prefix = str(info_row[1] or "").split(",")[0].strip()
        return {
            "status": "ok" if select_1_row[0] == 1 else "warn",
            "reason": "" if select_1_row[0] == 1 else "postgres_select_1_unexpected",
            "latency_ms": latency_ms,
            "database": str(info_row[0] or "").strip(),
            "server_version": version_prefix,
            "select_1_ok": bool(select_1_row[0] == 1),
            "dsn_present": True,
        }
    except Exception as exc:
        return {
            "status": "fail",
            "reason": "postgres_connect_failed",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "database": "",
            "server_version": "",
            "select_1_ok": False,
            "dsn_present": True,
            "error": str(exc).strip()[:180],
        }


def _read_proc_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fp:
            return fp.read().strip()
    except Exception:
        return ""


def _fetch_json_http(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=2) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body or "{}")


def _check_local_server_metrics(
    hostname: str,
    requested_target: str = "",
    started: float | None = None,
    check_mode: str = "local_read_only_metrics",
) -> dict[str, Any]:
    started_at = started if started is not None else time.monotonic()
    uptime_text = _read_proc_text("/proc/uptime")
    load_text = _read_proc_text("/proc/loadavg")
    meminfo_text = _read_proc_text("/proc/meminfo")

    uptime_seconds = None
    if uptime_text:
        try:
            uptime_seconds = int(float(uptime_text.split()[0]))
        except Exception:
            uptime_seconds = None

    load_average: list[float] = []
    if load_text:
        try:
            load_average = [round(float(part), 2) for part in load_text.split()[:3]]
        except Exception:
            load_average = []

    memory_total_mb = None
    memory_available_mb = None
    memory_available_pct = None
    if meminfo_text:
        meminfo: dict[str, int] = {}
        for line in meminfo_text.splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            match = re.search(r"(\d+)", raw_value)
            if match:
                meminfo[key.strip()] = int(match.group(1))
        total_kb = int(meminfo.get("MemTotal", 0) or 0)
        available_kb = int(meminfo.get("MemAvailable", 0) or 0)
        if total_kb > 0:
            memory_total_mb = int(total_kb / 1024)
            memory_available_mb = int(available_kb / 1024)
            memory_available_pct = round((available_kb / total_kb) * 100, 1)

    cpu_count = int(os.cpu_count() or 1)
    load_warn = bool(load_average and load_average[0] > (cpu_count * 1.5))
    memory_warn = bool(memory_available_pct is not None and memory_available_pct < 15.0)
    status = "warn" if load_warn or memory_warn else "ok"
    if uptime_seconds is None or not load_average or memory_total_mb is None:
        status = "warn"

    return {
        "status": status,
        "reason": "server_metrics_read" if status == "ok" else "server_metrics_warn",
        "requested_target": requested_target or hostname,
        "checked_host": hostname,
        "reachable": True,
        "uptime_seconds": uptime_seconds,
        "load_average": load_average,
        "memory_total_mb": memory_total_mb,
        "memory_available_mb": memory_available_mb,
        "memory_available_pct": memory_available_pct,
        "latency_ms": int((time.monotonic() - started_at) * 1000),
        "check_mode": check_mode,
    }


def _check_mapped_server_runtime(requested_target: str) -> dict[str, Any]:
    started = time.monotonic()
    requested = _normalize(requested_target)
    endpoints = SERVER_HOST_ENDPOINTS.get(requested)
    if not endpoints:
        return {
            "status": "warn",
            "reason": "server_target_not_mapped",
            "requested_target": requested,
            "checked_host": "",
            "reachable": False,
            "latency_ms": 0,
            "check_mode": "whitelist_http_health_status",
        }

    local_hostname = _normalize(socket.gethostname().strip())
    if requested == local_hostname:
        return _check_local_server_metrics(
            hostname=socket.gethostname().strip(),
            requested_target=requested,
            started=started,
            check_mode="whitelist_local_read_only_metrics",
        )

    try:
        health_payload = _fetch_json_http(endpoints["health_url"])
        status_payload = _fetch_json_http(endpoints["status_url"])
        health_ok = str(health_payload.get("status", "")).strip().lower() == "ok"
        checked_host = requested
        app_status = status_payload.get("status") if isinstance(status_payload, dict) else None
        backend_ok = str(app_status or "").strip().lower() in {"ok", "healthy", "ready"}
        status = "ok" if health_ok and backend_ok else "warn"
        return {
            "status": status,
            "reason": "server_http_runtime_ok" if status == "ok" else "server_http_runtime_warn",
            "requested_target": requested,
            "checked_host": checked_host,
            "reachable": bool(health_ok),
            "latency_ms": int((time.monotonic() - started) * 1000),
            "check_mode": "whitelist_http_health_status",
            "health_ok": health_ok,
            "app_status": str(app_status or "").strip(),
            "capture_mode": str(status_payload.get("capture_mode") or "").strip(),
            "ws_enabled": bool(status_payload.get("ws_enabled", False)),
            "realtime_api_enabled": bool(status_payload.get("realtime_api_enabled", False)),
            "source_urls": [endpoints["health_url"], endpoints["status_url"]],
        }
    except Exception as exc:
        return {
            "status": "fail",
            "reason": "server_http_check_failed",
            "requested_target": requested,
            "checked_host": requested,
            "reachable": False,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "check_mode": "whitelist_http_health_status",
            "error": str(exc).strip()[:180],
            "source_urls": [endpoints["health_url"], endpoints["status_url"]],
        }


def _check_server_runtime(requested_target: str = "") -> dict[str, Any]:
    hostname = socket.gethostname().strip()
    requested = str(requested_target or "").strip()
    started = time.monotonic()
    normalized_hostname = _normalize(hostname)
    normalized_requested = _normalize(requested)

    if normalized_requested:
        if normalized_requested in SERVER_HOST_ENDPOINTS:
            return _check_mapped_server_runtime(normalized_requested)
        return {
            "status": "warn",
            "reason": "server_target_not_mapped",
            "requested_target": normalized_requested,
            "checked_host": hostname,
            "reachable": False,
            "uptime_seconds": None,
            "load_average": [],
            "memory_total_mb": None,
            "memory_available_mb": None,
            "memory_available_pct": None,
            "latency_ms": 0,
            "check_mode": "whitelist_http_health_status",
        }

    if normalized_hostname in SERVER_HOST_ENDPOINTS:
        return _check_mapped_server_runtime(normalized_hostname)
    return _check_local_server_metrics(hostname=hostname, requested_target=requested or hostname, started=started)


def resolve_infra_status_query(req: Request, query: str) -> dict[str, Any]:
    if not _looks_like_infra_query(query):
        return {"matched": False}

    normalized = _normalize(query)
    if _looks_like_postgres_query(query):
        postgres_runtime = _check_postgres_runtime()
        postgres_status = str(postgres_runtime.get("status", "warn") or "warn")
        latency_ms = postgres_runtime.get("latency_ms")
        memory_note = _build_operational_memory_note("postgresql", postgres_runtime.get("database") or "livecopilot", postgres_status)
        answer = "O PostgreSQL do Livecopilot esta de pe e respondeu ao check read-only." if postgres_status == "ok" else (
            "O PostgreSQL do Livecopilot nao respondeu ao check read-only."
            if postgres_status == "fail"
            else "O PostgreSQL do Livecopilot ainda nao esta totalmente configurado para este check."
        )
        bullets = [
            f"status: {postgres_status}.",
            f"check: SELECT 1 read-only | latency_ms: {latency_ms if latency_ms is not None else 'n/a'}.",
            f"database: {postgres_runtime.get('database') or 'n/a'}.",
            f"server_version: {postgres_runtime.get('server_version') or 'n/a'}.",
        ]
        error_message = str(postgres_runtime.get("error", "")).strip()
        if error_message:
            bullets[-1] = f"erro: {error_message}."
        if memory_note["message"]:
            bullets.append(f"memoria_operacional: {memory_note['message']}.")
        return {
            "matched": True,
            "intent": "infra_status",
            "status": postgres_status,
            "answer": answer,
            "bullets": bullets,
            "knowledge_context": {
                "query": str(query or "").strip(),
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "check read-only de PostgreSQL via DATABASE_URL com SELECT 1 e metadado fixo de runtime",
                "sources": [{"title": "postgres_readonly_check", "source_file": "internal://postgresql/read_only_health"}],
                "connector": "infra_status_connector",
                "intent": "infra_status",
                "target": "postgresql",
                "status": postgres_status,
                "latency_ms": latency_ms,
                "database": postgres_runtime.get("database", ""),
                "server_version": postgres_runtime.get("server_version", ""),
                "dsn_present": bool(postgres_runtime.get("dsn_present", False)),
                "select_1_ok": bool(postgres_runtime.get("select_1_ok", False)),
                "check_mode": "read_only_fixed_query",
                "reason": postgres_runtime.get("reason", ""),
                "operational_memory": memory_note,
            },
        }
    if _looks_like_server_query(query):
        requested_target = _extract_server_target(query)
        server_runtime = _check_server_runtime(requested_target)
        server_status = str(server_runtime.get("status", "warn") or "warn")
        checked_host = str(server_runtime.get("checked_host", "") or "")
        requested_target = str(server_runtime.get("requested_target", "") or checked_host)
        check_mode = str(server_runtime.get("check_mode", "local_read_only_metrics") or "local_read_only_metrics")
        load_average = server_runtime.get("load_average") or []
        memory_target_name = checked_host or requested_target or "unknown_server"
        memory_note = _build_operational_memory_note("server", memory_target_name, server_status)
        if str(server_runtime.get("reason", "")) == "server_target_not_mapped":
            answer = f"O alvo de servidor `{requested_target}` nao esta mapeado neste conector; o host local disponivel e `{checked_host}`."
        elif str(server_runtime.get("reason", "")) == "server_http_check_failed":
            answer = f"O servidor `{checked_host}` esta mapeado, mas nao respondeu ao check read-only controlado."
        elif server_status == "ok":
            answer = (
                f"O servidor `{checked_host}` esta saudavel no check HTTP read-only controlado."
                if check_mode == "whitelist_http_health_status"
                else f"O servidor `{checked_host}` esta saudavel no check local read-only."
            )
        elif server_status == "fail":
            answer = (
                f"O servidor `{checked_host}` nao respondeu ao check HTTP read-only controlado."
                if check_mode == "whitelist_http_health_status"
                else f"O servidor `{checked_host}` nao respondeu ao check local read-only."
            )
        else:
            answer = (
                f"O servidor `{checked_host}` respondeu ao check controlado, mas ha sinal de atencao no runtime."
                if check_mode == "whitelist_http_health_status"
                else f"O servidor `{checked_host}` respondeu, mas ha sinal de atencao nas metricas basicas."
            )
        if check_mode == "whitelist_http_health_status":
            bullets = [
                f"status: {server_status} | host: {checked_host or 'n/a'}.",
                f"health_ok: {server_runtime.get('health_ok', False)} | app_status: {server_runtime.get('app_status') or 'n/a'}.",
                f"capture_mode: {server_runtime.get('capture_mode') or 'n/a'} | ws_enabled: {server_runtime.get('ws_enabled', False)} | realtime_api_enabled: {server_runtime.get('realtime_api_enabled', False)}.",
                f"check_mode: {check_mode} | latency_ms: {server_runtime.get('latency_ms', 'n/a')}.",
            ]
            error_message = str(server_runtime.get("error", "")).strip()
            if error_message:
                bullets[-1] = f"erro: {error_message}."
        else:
            bullets = [
                f"status: {server_status} | host: {checked_host or 'n/a'}.",
                f"load_avg(1m,5m,15m): {load_average if load_average else 'n/a'}.",
                f"uptime_s: {server_runtime.get('uptime_seconds') if server_runtime.get('uptime_seconds') is not None else 'n/a'} | latency_ms: {server_runtime.get('latency_ms', 'n/a')}.",
                f"mem_available_mb: {server_runtime.get('memory_available_mb') if server_runtime.get('memory_available_mb') is not None else 'n/a'} / {server_runtime.get('memory_total_mb') if server_runtime.get('memory_total_mb') is not None else 'n/a'} ({server_runtime.get('memory_available_pct') if server_runtime.get('memory_available_pct') is not None else 'n/a'}%).",
            ]
        if memory_note["message"]:
            bullets.append(f"memoria_operacional: {memory_note['message']}.")
        return {
            "matched": True,
            "intent": "infra_status",
            "status": server_status,
            "answer": answer,
            "bullets": bullets,
            "knowledge_context": {
                "query": str(query or "").strip(),
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": (
                    "check HTTP read-only controlado de host permitido via /health e /status"
                    if check_mode == "whitelist_http_health_status"
                    else "check local read-only de servidor com hostname, uptime, load average e memoria via procfs/stdlib"
                ),
                "sources": (
                    [{"title": "server_whitelist_http_check", "source_file": "internal://server/whitelist_health_status"}]
                    if check_mode == "whitelist_http_health_status"
                    else [{"title": "server_local_readonly_check", "source_file": "internal://server/local_read_only_health"}]
                ),
                "connector": "infra_status_connector",
                "intent": "infra_status",
                "target": "server",
                "status": server_status,
                "requested_target": requested_target,
                "checked_host": checked_host,
                "reachable": bool(server_runtime.get("reachable", False)),
                "load_average": load_average,
                "uptime_seconds": server_runtime.get("uptime_seconds"),
                "memory_total_mb": server_runtime.get("memory_total_mb"),
                "memory_available_mb": server_runtime.get("memory_available_mb"),
                "memory_available_pct": server_runtime.get("memory_available_pct"),
                "latency_ms": server_runtime.get("latency_ms"),
                "reason": server_runtime.get("reason", ""),
                "check_mode": check_mode,
                "health_ok": server_runtime.get("health_ok"),
                "app_status": server_runtime.get("app_status"),
                "capture_mode": server_runtime.get("capture_mode"),
                "ws_enabled": server_runtime.get("ws_enabled"),
                "realtime_api_enabled": server_runtime.get("realtime_api_enabled"),
                "source_urls": server_runtime.get("source_urls") or [],
                "operational_memory": memory_note,
            },
        }

    audio_capture = getattr(req.app.state, "audio_capture", None)
    transcription_runtime = get_transcription_runtime()
    voice_runtime = get_voice_output_runtime()
    realtime_runtime = get_realtime_runtime()

    health_ok = True
    capture_live = bool(audio_capture.is_live()) if audio_capture and hasattr(audio_capture, "is_live") else False
    ws_enabled = bool(settings.ws_enabled)
    realtime_enabled = bool(realtime_runtime.get("enabled", False))
    realtime_key_present = bool(realtime_runtime.get("api_key_present", False))
    transcription_provider = str(transcription_runtime.get("provider_selected") or transcription_runtime.get("provider") or "unknown")
    backend_status = "ok" if health_ok else "fail"
    memory_note = _build_operational_memory_note("backend", "livecopilot_backend", backend_status)

    answer = "O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente." if health_ok else "O backend principal do Livecopilot reportou anomalia."
    bullets = [
        f"ws_enabled: {str(ws_enabled)}.",
        f"capture_mode: {settings.capture_mode} | capture_live: {str(capture_live)}.",
        f"transcription_provider: {transcription_provider}.",
        f"realtime_enabled: {str(realtime_enabled)} | realtime_api_key_present: {str(realtime_key_present)}.",
    ]
    if voice_runtime.get("voice_output_control_policy"):
        bullets.append(f"voice_output_control_policy: {voice_runtime.get('voice_output_control_policy')}.")
    if memory_note["message"]:
        bullets.append(f"memoria_operacional: {memory_note['message']}.")

    return {
        "matched": True,
        "intent": "livecopilot_backend_status",
        "status": backend_status,
        "answer": answer,
        "bullets": bullets[:5],
        "knowledge_context": {
            "query": str(query or "").strip(),
            "used_search": False,
            "search_backend": "infra_status_connector",
            "context_used": False,
            "fallback_used": False,
            "semantic_api_ok": False,
            "semantic_duration_ms": 0,
            "result_count": 2,
            "context": "health/status internos do backend principal do Livecopilot",
            "sources": [
                {"title": "/health", "source_file": "internal://livecopilot/health"},
                {"title": "/status", "source_file": "internal://livecopilot/status"},
            ],
            "connector": "infra_status_connector",
            "intent": "livecopilot_backend_status",
            "target": "livecopilot_backend",
            "status": backend_status,
            "health_ok": health_ok,
            "ws_enabled": ws_enabled,
            "capture_live": capture_live,
            "realtime_enabled": realtime_enabled,
            "realtime_api_key_present": realtime_key_present,
            "operational_memory": memory_note,
        },
    }
