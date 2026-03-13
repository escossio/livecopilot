"""Executable local wrapper for SupervisorGptAdapter."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .api_client import SupervisorApiClient
from .gpt_adapter import SupervisorGptAdapter


class _JsonOnlyArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _parse_args() -> argparse.Namespace:
    parser = _JsonOnlyArgumentParser(
        description="Local tool host wrapper for supervisor GPT adapter"
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8787")
    parser.add_argument(
        "--token",
        default=None,
        help="Bearer token opcional; se omitido usa SUPERVISOR_API_TOKEN do ambiente.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--force-mode", choices=["run_once", "continue_run"])
    parser.add_argument("--target-project-path")
    parser.add_argument("--session-id")
    return parser.parse_args()


def _resolve_token(cli_token: str | None) -> str | None:
    if cli_token is not None:
        return cli_token
    env_token = os.getenv("SUPERVISOR_API_TOKEN")
    return env_token or None


def _fatal_payload(message: str, *, kind: str = "host_error") -> dict[str, Any]:
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
            "details": {},
        },
    }


def main() -> int:
    try:
        args = _parse_args()
        client = SupervisorApiClient(
            base_url=args.base_url,
            token=_resolve_token(args.token),
            timeout=args.timeout,
        )
        adapter = SupervisorGptAdapter(client=client)
        payload = adapter.decide_and_execute(
            force_mode=args.force_mode,
            target_project_path=args.target_project_path,
            session_id=args.session_id,
        )
    except Exception as exc:
        payload = _fatal_payload(str(exc))

    sys.stdout.write(json.dumps(payload, ensure_ascii=True))
    sys.stdout.write("\n")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
