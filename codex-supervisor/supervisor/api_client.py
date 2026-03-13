"""Small Python client for codex-supervisor local HTTP API."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


@dataclass(slots=True)
class SupervisorApiClient:
    base_url: str = "http://127.0.0.1:8787"
    token: str | None = None
    timeout: float = 30.0

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def get_status(self) -> dict[str, Any]:
        return self._request_json("GET", "/status")

    def get_last_action(self) -> dict[str, Any]:
        return self._request_json("GET", "/last-action")

    def get_next_step(self) -> str:
        payload = self._request_json("GET", "/next-step")
        next_step = payload.get("next_step")
        if isinstance(next_step, str):
            return next_step
        raise SupervisorApiClientError("Invalid response from /next-step: missing next_step.")

    def get_audit_tail(self, limit: int = 10) -> dict[str, Any]:
        safe_limit = min(max(int(limit), 1), 50)
        query = parse.urlencode({"limit": safe_limit})
        return self._request_json("GET", f"/audit-tail?{query}")

    def run_once(
        self,
        *,
        target_project_path: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, str] = {}
        if target_project_path:
            payload["target_project_path"] = target_project_path
        if session_id:
            payload["session_id"] = session_id
        return self._request_json("POST", "/run-once", payload=payload if payload else None)

    def continue_run(self) -> dict[str, Any]:
        return self._request_json("POST", "/continue-run")

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: bytes | None = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = request.Request(
            url=f"{self.base_url}{path}",
            data=body,
            method=method,
            headers=headers,
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise SupervisorApiHttpError(
                f"HTTP {exc.code} for {method} {path}: {error_body[:500]}",
                status_code=exc.code,
                response_body=error_body,
            ) from exc
        except error.URLError as exc:
            raise SupervisorApiClientError(
                f"Request failed for {method} {path}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise SupervisorApiClientError(
                f"Request timed out for {method} {path} after {self.timeout}s"
            ) from exc

        try:
            parsed = json.loads(raw_body)
        except Exception as exc:
            raise SupervisorApiClientError(
                f"Invalid JSON from {method} {path}: {raw_body[:500]}"
            ) from exc

        if not isinstance(parsed, dict):
            raise SupervisorApiClientError(f"Invalid JSON shape from {method} {path}.")
        return parsed


class SupervisorApiClientError(RuntimeError):
    """Base client exception."""


class SupervisorApiHttpError(SupervisorApiClientError):
    """HTTP error with status/body details."""

    def __init__(self, message: str, *, status_code: int, response_body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal client for codex-supervisor API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8787")
    parser.add_argument("--token")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--limit", type=int, default=10, help="Used by --audit-tail")
    parser.add_argument("--target-project-path", type=str, help="Used by --run-once")
    parser.add_argument("--session-id", type=str, help="Used by --run-once")

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--status", action="store_true")
    actions.add_argument("--last-action", action="store_true")
    actions.add_argument("--next-step", action="store_true")
    actions.add_argument("--audit-tail", action="store_true")
    actions.add_argument("--run-once", action="store_true")
    actions.add_argument("--continue-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    client = SupervisorApiClient(
        base_url=args.base_url,
        token=args.token,
        timeout=args.timeout,
    )
    try:
        if args.status:
            output: Any = client.get_status()
        elif args.last_action:
            output = client.get_last_action()
        elif args.next_step:
            output = {"next_step": client.get_next_step()}
        elif args.audit_tail:
            output = client.get_audit_tail(limit=args.limit)
        elif args.run_once:
            output = client.run_once(
                target_project_path=args.target_project_path,
                session_id=args.session_id,
            )
        else:
            output = client.continue_run()
    except SupervisorApiClientError as exc:
        print(f"Error: {exc}")
        return 1

    print(json.dumps(output, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
