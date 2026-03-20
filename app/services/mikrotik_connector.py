import base64
import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.services.operational_memory import append_event


FALSE_ENV_VALUES = {"0", "false", "no", "off"}
TRUE_ENV_VALUES = {"1", "true", "yes", "on"}
SUPPORTED_OPERATIONS = {"list_dhcp_leases"}


def _clean_base_url(value: str) -> str:
    return str(value or "").strip().rstrip("/")


def _sanitize_base_url(value: str) -> str:
    parsed = urllib.parse.urlparse(_clean_base_url(value))
    if not parsed.scheme or not parsed.netloc:
        return _clean_base_url(value)
    hostname = parsed.hostname or parsed.netloc
    port = f":{parsed.port}" if parsed.port else ""
    path = parsed.path or ""
    return f"{parsed.scheme}://{hostname}{port}{path}"


def _parse_verify_tls(value: str) -> bool | str:
    raw = str(value or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    if lowered in FALSE_ENV_VALUES:
        return False
    if lowered in TRUE_ENV_VALUES:
        return True
    return raw


def _parse_routeros_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raw = str(value or "").strip().lower()
    if not raw:
        return False
    if raw in TRUE_ENV_VALUES:
        return True
    if raw in FALSE_ENV_VALUES:
        return False
    return bool(value)


def load_mikrotik_config() -> dict[str, Any]:
    base_url = _clean_base_url(os.getenv("MIKROTIK_BASE_URL", ""))
    username = str(os.getenv("MIKROTIK_USERNAME", "") or "").strip()
    password = str(os.getenv("MIKROTIK_PASSWORD", "") or "")
    timeout_raw = str(os.getenv("MIKROTIK_TIMEOUT", "5") or "5").strip()
    try:
        timeout = max(float(timeout_raw), 1.0)
    except Exception:
        timeout = 5.0
    verify_tls = _parse_verify_tls(os.getenv("MIKROTIK_VERIFY_TLS", ""))
    return {
        "configured": bool(base_url and username and password),
        "base_url": base_url,
        "base_url_sanitized": _sanitize_base_url(base_url),
        "username": username,
        "password": password,
        "timeout": timeout,
        "verify_tls": verify_tls,
    }


def _build_ssl_context(verify_tls: bool | str) -> ssl.SSLContext:
    if verify_tls is False:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    context = ssl.create_default_context()
    if isinstance(verify_tls, str) and verify_tls.strip():
        context.load_verify_locations(cafile=verify_tls.strip())
    return context


def _build_rest_request(url: str, username: str, password: str) -> urllib.request.Request:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {token}",
        },
        method="GET",
    )


def _fetch_rest_rows(path: str) -> dict[str, Any]:
    config = load_mikrotik_config()
    if not config["configured"]:
        return {
            "status": "warn",
            "reason": "mikrotik_config_missing",
            "latency_ms": 0,
            "rows": [],
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
        }

    started = time.monotonic()
    url = f"{config['base_url']}/{path.lstrip('/')}"
    request = _build_rest_request(url, config["username"], config["password"])
    ssl_context = _build_ssl_context(config["verify_tls"])

    try:
        with urllib.request.urlopen(request, timeout=config["timeout"], context=ssl_context) as response:
            payload = json.loads(response.read().decode("utf-8") or "[]")
        rows = payload if isinstance(payload, list) else []
        return {
            "status": "ok",
            "reason": "mikrotik_rest_ok",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "rows": rows,
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
        }
    except urllib.error.HTTPError as exc:
        reason = "mikrotik_http_error"
        if exc.code in {401, 403}:
            reason = "mikrotik_auth_failed"
        return {
            "status": "fail",
            "reason": reason,
            "http_status": exc.code,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "rows": [],
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
            "error": str(exc).strip()[:180],
        }
    except urllib.error.URLError as exc:
        root = getattr(exc, "reason", exc)
        reason = "mikrotik_connect_failed"
        if isinstance(root, socket.timeout):
            reason = "mikrotik_timeout"
        return {
            "status": "fail",
            "reason": reason,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "rows": [],
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
            "error": str(root).strip()[:180],
        }
    except TimeoutError as exc:
        return {
            "status": "fail",
            "reason": "mikrotik_timeout",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "rows": [],
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
            "error": str(exc).strip()[:180],
        }
    except Exception as exc:
        return {
            "status": "fail",
            "reason": "mikrotik_unexpected_error",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "rows": [],
            "base_url": config["base_url_sanitized"],
            "verify_tls": config["verify_tls"],
            "error": str(exc).strip()[:180],
        }


def _normalize_dhcp_lease(raw: dict[str, Any]) -> dict[str, Any]:
    active_address = str(raw.get("active-address") or "").strip()
    configured_address = str(raw.get("address") or raw.get("ip-address") or "").strip()
    active_mac = str(raw.get("active-mac-address") or "").strip()
    configured_mac = str(raw.get("mac-address") or raw.get("mac_address") or "").strip()
    status = str(raw.get("status") or "").strip().lower()
    if not status:
        status = "bound" if active_address else "waiting"
    host_name = str(raw.get("host-name") or raw.get("host_name") or "").strip()
    server = str(raw.get("server") or raw.get("dhcp-server") or "").strip()
    last_seen = str(raw.get("last-seen") or "").strip()
    expires_after = str(raw.get("expires-after") or "").strip()
    dynamic = _parse_routeros_bool(raw.get("dynamic", False))
    blocked = _parse_routeros_bool(raw.get("blocked", False))
    disabled = _parse_routeros_bool(raw.get("disabled", False))
    return {
        "ip": active_address or configured_address,
        "configured_ip": configured_address,
        "mac_address": active_mac or configured_mac,
        "configured_mac_address": configured_mac,
        "host_name": host_name,
        "status": status,
        "last_seen": last_seen,
        "expires_after": expires_after,
        "server": server,
        "dynamic": dynamic,
        "blocked": blocked,
        "disabled": disabled,
    }


def list_dhcp_leases() -> dict[str, Any]:
    runtime = _fetch_rest_rows("ip/dhcp-server/lease")
    rows = runtime.get("rows") or []
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in rows:
        if not isinstance(item, dict):
            continue
        lease = _normalize_dhcp_lease(item)
        if lease["disabled"] or lease["blocked"]:
            continue
        if lease["status"] not in {"bound", "offered"} and not lease["ip"]:
            continue
        if not any((lease["ip"], lease["mac_address"], lease["host_name"])):
            continue
        key = (str(lease["ip"]), str(lease["mac_address"]), str(lease["host_name"]).lower())
        if key in seen:
            continue
        seen.add(key)
        normalized.append(lease)
    runtime["leases"] = normalized
    runtime["client_count"] = len(normalized)
    if runtime["status"] == "ok":
        runtime["reason"] = "mikrotik_dhcp_leases_ok"
    return runtime


def _build_operational_summary(status: str, client_count: int) -> str:
    return f"consulta dhcp mikrotik: status {status} | client_count {client_count}"


def resolve_mikrotik_query(query: str, operation: str) -> dict[str, Any]:
    clean_operation = str(operation or "").strip()
    if clean_operation not in SUPPORTED_OPERATIONS:
        return {
            "matched": True,
            "intent": "network_device_count",
            "status": "warn",
            "answer": "O conector MikroTik foi acionado, mas a operacao solicitada nao e suportada nesta integracao.",
            "bullets": [
                f"operacao_solicitada: {clean_operation or 'n/a'}.",
                "operacoes_permitidas: list_dhcp_leases.",
            ],
            "knowledge_context": {
                "query": str(query or "").strip(),
                "used_search": False,
                "search_backend": "mikrotik_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 0,
                "context": "conector MikroTik REST API read-only com lista fixa de operacoes suportadas",
                "sources": [{"title": "mikrotik_rest_connector", "source_file": "internal://mikrotik/rest/ip/dhcp-server/lease"}],
                "connector": "mikrotik_connector",
                "intent": "network_device_count",
                "target": "mikrotik",
                "status": "warn",
                "reason": "unsupported_operation",
                "operation": clean_operation,
            },
        }

    leases_runtime = list_dhcp_leases()
    client_count = int(leases_runtime.get("client_count", 0) or 0)
    top_clients = [
        {
            "ip": str(item.get("ip", "")).strip(),
            "mac_address": str(item.get("mac_address", "")).strip(),
            "host_name": str(item.get("host_name", "")).strip(),
            "status": str(item.get("status", "")).strip(),
            "last_seen": str(item.get("last_seen", "")).strip(),
            "expires_after": str(item.get("expires_after", "")).strip(),
        }
        for item in (leases_runtime.get("leases") or [])[:5]
        if isinstance(item, dict)
    ]
    status = str(leases_runtime.get("status", "warn") or "warn")
    reason = str(leases_runtime.get("reason", "") or "").strip()

    try:
        append_event(
            kind="infra_check",
            target_type="mikrotik",
            target_name="dhcp_leases",
            status=status if status in {"ok", "warn", "fail"} else "warn",
            summary=_build_operational_summary(status, client_count),
            source="mikrotik_connector",
        )
    except Exception:
        pass

    if status == "ok" and client_count == 0:
        answer = "A REST API do MikroTik respondeu, mas nao encontrei leases uteis no servidor DHCP neste momento."
    elif status == "ok":
        answer = f"Encontrei {client_count} cliente(s) ativo(s) ou utilmente identificados no servidor DHCP da sua rede."
    elif reason == "mikrotik_config_missing":
        answer = "A skill do MikroTik foi acionada, mas o conector REST API ainda nao esta configurado no ambiente."
    else:
        answer = "Nao consegui ler os leases do DHCP no MikroTik pela REST API read-only neste momento."

    bullets = [
        f"status: {status} | operacao: list_dhcp_leases.",
        f"client_count: {client_count} | latency_ms: {leases_runtime.get('latency_ms', 'n/a')}.",
    ]
    if top_clients:
        bullets.extend(
            [
                "principais_clientes: "
                + "; ".join(
                    (
                        f"{item['host_name'] or item['ip'] or 'n/a'} "
                        f"(ip={item['ip'] or 'n/a'} mac={item['mac_address'] or 'n/a'} "
                        f"status={item['status'] or 'n/a'}"
                        f"{' last_seen=' + item['last_seen'] if item['last_seen'] else ''}"
                        f"{' expires_after=' + item['expires_after'] if item['expires_after'] else ''})"
                    )
                    for item in top_clients
                )
            ]
        )
    elif status == "ok":
        bullets.append("principais_clientes: nenhum lease util retornado pelo DHCP.")
    else:
        bullets.append(
            "envs_necessarios: MIKROTIK_BASE_URL, MIKROTIK_USERNAME, MIKROTIK_PASSWORD, "
            "MIKROTIK_VERIFY_TLS, MIKROTIK_TIMEOUT."
        )

    error_message = str(leases_runtime.get("error", "")).strip()
    if error_message:
        bullets.append(f"erro: {error_message}.")

    return {
        "matched": True,
        "intent": "network_device_count",
        "status": status,
        "answer": answer,
        "bullets": bullets[:5],
        "knowledge_context": {
            "query": str(query or "").strip(),
            "used_search": False,
            "search_backend": "mikrotik_connector",
            "context_used": False,
            "fallback_used": False,
            "semantic_api_ok": False,
            "semantic_duration_ms": 0,
            "result_count": client_count,
            "context": "consulta read-only de leases do DHCP via MikroTik RouterOS REST API /ip/dhcp-server/lease",
            "sources": [{"title": "mikrotik_rest_dhcp_leases", "source_file": "internal://mikrotik/rest/ip/dhcp-server/lease"}],
            "connector": "mikrotik_connector",
            "intent": "network_device_count",
            "target": "mikrotik",
            "status": status,
            "reason": reason,
            "operation": clean_operation,
            "client_count": client_count,
            "top_clients": top_clients,
            "latency_ms": leases_runtime.get("latency_ms"),
            "base_url": leases_runtime.get("base_url", ""),
            "verify_tls": leases_runtime.get("verify_tls"),
        },
    }
