"""CLI entrypoint for local supervisor skeleton."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from .config import SupervisorConfig
from .workflow import SupervisorWorkflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Supervisor (Agents SDK + MCP)")
    parser.add_argument(
        "--target-project",
        type=Path,
        help="Absolute/relative path to the external target project.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Stable agent session identifier for SQLiteSession (Agents SDK).",
    )
    parser.add_argument(
        "--init-state",
        action="store_true",
        help="Initialize state files and directories.",
    )
    run_mode_group = parser.add_mutually_exclusive_group()
    run_mode_group.add_argument(
        "--run-once",
        action="store_true",
        help="Run one new supervisor cycle with Agents SDK + Codex MCP server.",
    )
    run_mode_group.add_argument(
        "--continue-run",
        action="store_true",
        help="Continue an existing run using persisted state/last_action.json.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    try:
        config = SupervisorConfig.from_env()
        if args.target_project is not None:
            config = config.with_target(args.target_project)
        if args.session_id:
            config = config.with_session_id(args.session_id)

        workflow = SupervisorWorkflow(config)

        if args.init_state:
            workflow.initialize()

        if args.run_once:
            action = asyncio.run(workflow.run_once())
            print(json.dumps(asdict(action), indent=2, ensure_ascii=True))
        elif args.continue_run:
            action = asyncio.run(workflow.continue_run())
            print(json.dumps(asdict(action), indent=2, ensure_ascii=True))

        if not args.init_state and not args.run_once and not args.continue_run:
            print("No action selected. Use --init-state, --run-once, or --continue-run.")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
