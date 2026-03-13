"""Minimal HTTP API for codex-supervisor orchestration."""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv

from .config import SupervisorConfig
from .service import SupervisorService

LOGGER = logging.getLogger("codex_supervisor.http_api")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Supervisor HTTP API")
    parser.add_argument("--host", type=str, default=os.getenv("SUPERVISOR_API_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("SUPERVISOR_API_PORT", "8787"))
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("SUPERVISOR_API_TOKEN"),
        help="Optional bearer token for API authentication.",
    )
    parser.add_argument(
        "--target-project",
        type=Path,
        help="Optional override for TARGET_PROJECT_PATH.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Optional override for AGENT_SESSION_ID.",
    )
    parser.add_argument(
        "--init-state",
        action="store_true",
        help="Initialize state files before serving.",
    )
    return parser.parse_args()


class _ApiError(RuntimeError):
    pass


def _build_handler(service: SupervisorService, token: str | None) -> type[BaseHTTPRequestHandler]:
    class SupervisorHttpHandler(BaseHTTPRequestHandler):
        server_version = "CodexSupervisorHTTP/0.2"

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._dispatch("POST")

        def _dispatch(self, method: str) -> None:
            started = time.perf_counter()
            route = self.path
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            payload: dict[str, Any] = {"error": "Unexpected error."}

            try:
                self._authorize()
                url = urlsplit(self.path)
                route = url.path
                query = parse_qs(url.query)

                status, payload = self._route_request(method=method, route=route, query=query)
            except _ApiError as exc:
                status = HTTPStatus.UNAUTHORIZED
                payload = {"error": str(exc)}
            except ValueError as exc:
                status = HTTPStatus.BAD_REQUEST
                payload = {"error": str(exc)}
            except Exception as exc:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
                payload = {"error": str(exc)}
            finally:
                try:
                    self._write_json_response(status, payload)
                except BrokenPipeError:
                    LOGGER.warning("response_write_failed method=%s path=%s reason=broken_pipe", method, route)
                except Exception:
                    LOGGER.exception("response_write_failed method=%s path=%s", method, route)

                duration_ms = (time.perf_counter() - started) * 1000.0
                LOGGER.info(
                    "request method=%s path=%s status=%d duration_ms=%.2f",
                    method,
                    route,
                    int(status),
                    duration_ms,
                )

        def _route_request(
            self,
            *,
            method: str,
            route: str,
            query: dict[str, list[str]],
        ) -> tuple[HTTPStatus, dict[str, Any]]:
            if method == "GET" and route == "/status":
                return HTTPStatus.OK, service.get_status()

            if method == "GET" and route == "/last-action":
                return HTTPStatus.OK, service.get_last_action()

            if method == "GET" and route == "/next-step":
                return HTTPStatus.OK, {"next_step": service.get_next_step()}

            if method == "GET" and route == "/audit-tail":
                limit = self._safe_int(query.get("limit", ["20"])[0], default=20)
                return HTTPStatus.OK, service.get_audit_tail(limit=limit)

            if method == "POST" and route == "/run-once":
                payload = self._parse_json_body()
                return (
                    HTTPStatus.ACCEPTED,
                    service.enqueue_run_once(
                        target_project_path=self._safe_optional_str(payload.get("target_project_path")),
                        session_id=self._safe_optional_str(payload.get("session_id")),
                    ),
                )

            if method == "POST" and route == "/continue-run":
                return HTTPStatus.ACCEPTED, service.enqueue_continue_run()

            if method == "GET" and route == "/jobs":
                limit = self._safe_int(query.get("limit", ["20"])[0], default=20)
                return HTTPStatus.OK, service.list_jobs(limit=limit)

            path_parts = [part for part in route.split("/") if part]
            if method == "GET" and len(path_parts) == 2 and path_parts[0] == "jobs":
                job_payload = service.get_job(path_parts[1])
                if job_payload is None:
                    return HTTPStatus.NOT_FOUND, {"error": f"Job not found: {path_parts[1]}"}
                return HTTPStatus.OK, job_payload

            if (
                method == "GET"
                and len(path_parts) == 3
                and path_parts[0] == "jobs"
                and path_parts[2] == "result"
            ):
                job_result = service.get_job_result(path_parts[1])
                if job_result is None:
                    return HTTPStatus.NOT_FOUND, {"error": f"Job not found: {path_parts[1]}"}
                return HTTPStatus.OK, job_result

            return HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {method} {route}"}

        def _authorize(self) -> None:
            if not token:
                return
            auth_header = self.headers.get("Authorization", "")
            expected = f"Bearer {token}"
            if auth_header != expected:
                raise _ApiError("Invalid or missing bearer token.")

        def _parse_json_body(self) -> dict[str, Any]:
            content_length = self.headers.get("Content-Length")
            if not content_length:
                return {}
            size = self._safe_int(content_length, default=0)
            if size <= 0:
                return {}
            raw = self.rfile.read(size)
            if not raw:
                return {}
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except Exception as exc:
                raise ValueError(f"Invalid JSON body: {exc}") from exc
            if not isinstance(parsed, dict):
                raise ValueError("JSON body must be an object.")
            return parsed

        @staticmethod
        def _safe_optional_str(value: object) -> str | None:
            if value is None:
                return None
            if not isinstance(value, str):
                raise ValueError("Expected string fields in request body.")
            clean_value = value.strip()
            return clean_value if clean_value else None

        @staticmethod
        def _safe_int(value: str, *, default: int) -> int:
            try:
                return int(value)
            except Exception:
                return default

        def _write_json_response(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            safe_status = status
            safe_payload: dict[str, Any] = payload if isinstance(payload, dict) else {"error": "Invalid payload."}
            try:
                body = json.dumps(safe_payload, ensure_ascii=True, default=str).encode("utf-8")
            except Exception as exc:
                safe_status = HTTPStatus.INTERNAL_SERVER_ERROR
                body = json.dumps(
                    {"error": f"Failed to encode JSON response: {exc}"},
                    ensure_ascii=True,
                ).encode("utf-8")
            try:
                self.send_response(int(safe_status))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()
            finally:
                self.close_connection = True

        def log_message(self, format: str, *args: object) -> None:
            return

    return SupervisorHttpHandler


def main() -> int:
    load_dotenv()
    args = parse_args()

    config = SupervisorConfig.from_env()
    if args.target_project is not None:
        config = config.with_target(args.target_project)
    if args.session_id:
        config = config.with_session_id(args.session_id)

    level_name = str(config.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    service = SupervisorService(config)
    if args.init_state:
        service.initialize()

    handler_cls = _build_handler(service, args.token)
    server = ThreadingHTTPServer((args.host, args.port), handler_cls)
    print(
        json.dumps(
            {
                "service": "codex-supervisor-http-api",
                "host": args.host,
                "port": args.port,
                "token_enabled": bool(args.token),
            },
            ensure_ascii=True,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
