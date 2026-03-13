"""Thin decision/orchestration adapter for GPT runtimes."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Literal

from .api_client import SupervisorApiClient, SupervisorApiClientError, SupervisorApiHttpError

ForceMode = Literal["run_once", "continue_run"]


@dataclass(slots=True)
class SupervisorGptAdapter:
    client: SupervisorApiClient

    def decide_and_execute(
        self,
        *,
        force_mode: ForceMode | None = None,
        target_project_path: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            status_snapshot = self.client.get_status()
            decision = self._decide_mode(status_snapshot, force_mode=force_mode)
            if decision == "continue_run":
                execution_result = self.client.continue_run()
            else:
                execution_result = self.client.run_once(
                    target_project_path=target_project_path,
                    session_id=session_id,
                )
            last_action = self.client.get_last_action()
            next_step = self.client.get_next_step()
            return {
                "ok": True,
                "decision": decision,
                "execution_result": execution_result,
                "last_action": last_action,
                "next_step": next_step,
                "status_snapshot": status_snapshot,
            }
        except SupervisorApiHttpError as exc:
            return self._error_payload(
                kind="http_error",
                message=str(exc),
                details={
                    "status_code": exc.status_code,
                    "response_body": exc.response_body[:500],
                },
            )
        except SupervisorApiClientError as exc:
            return self._error_payload(
                kind="client_error",
                message=str(exc),
                details={},
            )
        except Exception as exc:
            return self._error_payload(
                kind="unexpected_error",
                message=str(exc),
                details={},
            )

    @staticmethod
    def _decide_mode(
        status_snapshot: dict[str, Any],
        *,
        force_mode: ForceMode | None,
    ) -> ForceMode:
        if force_mode in {"run_once", "continue_run"}:
            return force_mode
        can_continue = bool(status_snapshot.get("can_continue"))
        has_thread = bool(status_snapshot.get("codex_thread_id"))
        return "continue_run" if can_continue and has_thread else "run_once"

    @staticmethod
    def _error_payload(
        *,
        kind: str,
        message: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "ok": False,
            "decision": None,
            "execution_result": None,
            "last_action": None,
            "next_step": None,
            "status_snapshot": None,
            "error": {
                "kind": kind,
                "message": message,
                "details": details,
            },
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Thin GPT adapter for codex-supervisor")
    parser.add_argument("--base-url", default="http://127.0.0.1:8787")
    parser.add_argument("--token")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--force-mode",
        choices=["run_once", "continue_run"],
        help="Optional override of automatic decision.",
    )
    parser.add_argument("--target-project-path")
    parser.add_argument("--session-id")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    client = SupervisorApiClient(
        base_url=args.base_url,
        token=args.token,
        timeout=args.timeout,
    )
    adapter = SupervisorGptAdapter(client=client)
    payload = adapter.decide_and_execute(
        force_mode=args.force_mode,
        target_project_path=args.target_project_path,
        session_id=args.session_id,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
