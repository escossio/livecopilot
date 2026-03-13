"""Main orchestration flow for one real supervisor cycle."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from agents import Agent, Runner
from agents.memory.sqlite_session import SQLiteSession

from .codex_bridge import CodexBridge, CodexBridgeConfig, CodexContinueAttemptResult
from .config import SupervisorConfig
from .prompts import (
    build_agent_instructions,
    build_continuation_context as build_continuation_task,
    build_supervisor_task,
)
from .project_journal import append_project_checkpoint, update_or_create_status_md
from .state_store import ActionRecord, PersistedContinuationState, StateStore


class SupervisorWorkflow:
    """Coordinates local state with Agents SDK + Codex MCP server."""

    def __init__(self, config: SupervisorConfig) -> None:
        self.config = config
        self.state = StateStore(config)
        self._run_max_turns = self._load_run_max_turns()
        self.bridge = CodexBridge(
            CodexBridgeConfig(
                target_project_path=self.config.target_project_path,
                client_session_timeout_seconds=30.0,
                audit_log_path=self.config.logs_dir / "codex_mcp_audit.jsonl",
                audit_enabled=(
                    os.getenv("SUPERVISOR_MCP_AUDIT", "0") in {"1", "true", "TRUE"}
                ),
            )
        )

    def initialize(self) -> None:
        self.state.ensure_defaults()

    async def run_once(self) -> ActionRecord:
        self.config.validate()
        self.state.ensure_defaults()
        self._configure_bridge_for_target(self.config.target_project_path)
        self._validate_runtime_for_target(self.config.target_project_path)
        self.bridge.reset_observed_thread_hint()
        agent_session_id = self.config.resolved_agent_session_id()
        self.config.session_db_path.parent.mkdir(parents=True, exist_ok=True)

        mission = self.state.read_mission()
        next_step = self.state.read_next_step()
        instructions = build_agent_instructions(
            target_project=str(self.config.target_project_path),
            supervisor_home=str(self.config.supervisor_home),
        )
        task = build_supervisor_task(
            mission=mission,
            next_step=next_step,
            target_project=str(self.config.target_project_path),
        )
        task = self._append_readme_fallback_context(
            task=task,
            target_project_path=self.config.target_project_path,
        )

        try:
            session = SQLiteSession(
                session_id=agent_session_id,
                db_path=self.config.session_db_path,
            )
        except Exception as exc:
            error_text = f"Failed to initialize SQLiteSession: {exc}"
            failed_action = ActionRecord(
                timestamp=self.state._now_iso(),
                status="error",
                mode="agents_sdk_mcp",
                target_project_path=str(self.config.target_project_path),
                final_output=error_text,
                agent_session_id=agent_session_id,
                agent_session_backend="sqlite",
                codex_thread_id=None,
                codex_thread_id_status="pending_capture_from_mcp_tool_result",
                codex_thread_id_source=None,
                codex_continue_attempted=False,
                codex_continue_mode=None,
                codex_continue_status=None,
                codex_continue_route=None,
                codex_continue_tool_name=None,
                codex_continue_contract_mode=None,
                codex_continue_strict_mode=False,
            )
            self._persist_action_with_project_journal(
                failed_action,
                execution_mode="run-once",
                decision="run_once",
            )
            raise RuntimeError(error_text) from exc

        continue_attempt = CodexContinueAttemptResult(
            attempted=False,
            mode="not_applicable",
            status="not_applicable",
            route="run_once",
            tool_name=None,
            contract_mode="not_applicable",
            strict_mode=False,
            deploy_profile=self._deploy_profile(),
            contract_validated=False,
            contract_validation_reason=None,
        )
        try:
            async with self.bridge.codex_mcp_server() as codex_mcp_server:
                agent = Agent(
                    name="LocalCodexSupervisor",
                    instructions=instructions,
                    mcp_servers=[codex_mcp_server],
                )
                result = await Runner.run(
                    starting_agent=agent,
                    input=task,
                    max_turns=self._run_max_turns,
                    session=session,
                )
        except TimeoutError as exc:
            error_text = f"Agents SDK run timed out: {exc}"
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text[:500], "phase": "runner.run", "status": "timeout"},
            )
            self.state.write_next_step(
                "A rodada expirou (timeout). Reexecutar --run-once e validar saúde do MCP/SDK."
            )
            self._persist_terminal_action(
                status="timeout",
                final_output=error_text,
                agent_session_id=agent_session_id,
                new_items=[],
                target_project_path=str(self.config.target_project_path),
                continue_attempt=continue_attempt,
            )
            raise TimeoutError(error_text) from exc
        except asyncio.CancelledError as exc:
            error_text = "Agents SDK run interrupted by cancellation."
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text, "phase": "runner.run", "status": "interrupted"},
            )
            self.state.write_next_step(
                "A rodada foi interrompida. Retomar execução com --run-once ou futuro --continue-run."
            )
            self._persist_terminal_action(
                status="interrupted",
                final_output=error_text,
                agent_session_id=agent_session_id,
                new_items=[],
                target_project_path=str(self.config.target_project_path),
                continue_attempt=continue_attempt,
            )
            raise
        except KeyboardInterrupt as exc:
            error_text = "Agents SDK run interrupted by keyboard signal."
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text, "phase": "runner.run", "status": "interrupted"},
            )
            self.state.write_next_step(
                "A rodada foi interrompida. Retomar execução com --run-once ou futuro --continue-run."
            )
            self._persist_terminal_action(
                status="interrupted",
                final_output=error_text,
                agent_session_id=agent_session_id,
                new_items=[],
                target_project_path=str(self.config.target_project_path),
                continue_attempt=continue_attempt,
            )
            raise
        except Exception as exc:
            error_text = f"Agents SDK run failed: {exc}"
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text[:500], "phase": "runner.run", "status": "error"},
            )
            self.state.write_next_step(
                "Corrigir o erro da rodada (credenciais/configuração) e reexecutar --run-once."
            )
            self._persist_terminal_action(
                status="error",
                final_output=error_text,
                agent_session_id=agent_session_id,
                new_items=[],
                target_project_path=str(self.config.target_project_path),
                continue_attempt=continue_attempt,
            )
            raise

        final_output = self._final_output_text(result.final_output)
        next_step_summary = self._extract_next_step_summary(final_output)
        self.state.write_next_step(next_step_summary)

        new_items = getattr(result, "new_items", [])
        self.bridge.audit_event(
            "runner_new_items_summary",
            {"items": self._summarize_new_items_for_audit(new_items)},
        )
        self._debug_new_items(new_items)

        return self._persist_terminal_action(
            status="success",
            final_output=final_output,
            agent_session_id=agent_session_id,
            new_items=new_items,
            target_project_path=str(self.config.target_project_path),
            continue_attempt=continue_attempt,
        )

    async def continue_run(self) -> ActionRecord:
        self.state.ensure_defaults()
        continuation_state = self.state.load_last_action_for_continue()
        target_project_path = Path(continuation_state.target_project_path).expanduser().resolve()
        if self.config.target_project_configured and (
            self.config.target_project_path != target_project_path
        ):
            raise ValueError(
                "Cannot continue: --target-project differs from persisted "
                f"state target ({target_project_path})."
            )
        if self.config.agent_session_id and (
            self.config.agent_session_id != continuation_state.agent_session_id
        ):
            raise ValueError(
                "Cannot continue: --session-id differs from persisted agent_session_id "
                f"({continuation_state.agent_session_id})."
            )

        self._configure_bridge_for_target(target_project_path)
        self._validate_runtime_for_target(target_project_path)
        self.bridge.reset_observed_thread_hint()
        self.config.session_db_path.parent.mkdir(parents=True, exist_ok=True)

        mission = self.state.read_mission()
        next_step = self.state.read_next_step()
        instructions = build_agent_instructions(
            target_project=str(target_project_path),
            supervisor_home=str(self.config.supervisor_home),
        )
        task = build_continuation_task(
            mission=mission,
            next_step=next_step,
            target_project=str(target_project_path),
            agent_session_id=continuation_state.agent_session_id,
            codex_thread_id=continuation_state.codex_thread_id,
            codex_thread_id_status=continuation_state.codex_thread_id_status,
            codex_thread_id_source=continuation_state.codex_thread_id_source,
            explicit_continue_active=True,
            continue_contract_mode="deterministic_primary_with_heuristic_fallback",
        )
        task = self._append_readme_fallback_context(
            task=task,
            target_project_path=target_project_path,
        )

        self.bridge.audit_event(
            "continuation_resume_requested",
            {
                "agent_session_id": continuation_state.agent_session_id,
                "codex_thread_id": continuation_state.codex_thread_id,
                "codex_thread_id_status": continuation_state.codex_thread_id_status,
                "codex_thread_id_source": continuation_state.codex_thread_id_source,
            },
        )

        try:
            session = SQLiteSession(
                session_id=continuation_state.agent_session_id,
                db_path=self.config.session_db_path,
            )
        except Exception as exc:
            error_text = f"Failed to initialize SQLiteSession for continue-run: {exc}"
            failed_action = ActionRecord(
                timestamp=self.state._now_iso(),
                status="error",
                mode="agents_sdk_mcp",
                target_project_path=str(target_project_path),
                final_output=error_text,
                agent_session_id=continuation_state.agent_session_id,
                agent_session_backend="sqlite",
                codex_thread_id=continuation_state.codex_thread_id,
                codex_thread_id_status=continuation_state.codex_thread_id_status,
                codex_thread_id_source=continuation_state.codex_thread_id_source,
                codex_continue_attempted=False,
                codex_continue_mode="context_fallback",
                codex_continue_status="failed",
                codex_continue_route="not_attempted",
                codex_continue_tool_name=None,
                codex_continue_contract_mode="deterministic",
                codex_continue_strict_mode=(
                    self._continue_strict_enabled()
                ),
                codex_continue_deploy_profile=self._deploy_profile(),
                codex_continue_contract_validated=False,
                codex_continue_contract_validation_reason=error_text,
            )
            self._persist_action_with_project_journal(
                failed_action,
                execution_mode="continue-run",
                decision="continue_run",
            )
            raise RuntimeError(error_text) from exc

        continue_attempt = CodexContinueAttemptResult(
            attempted=False,
            mode="context_fallback",
            status="failed",
            route="not_attempted",
            tool_name=None,
            contract_mode="deterministic",
            strict_mode=(
                self._continue_strict_enabled()
            ),
            deploy_profile=self._deploy_profile(),
            contract_validated=False,
            contract_validation_reason="explicit continue not attempted",
            error="explicit continue not attempted",
        )
        try:
            async with self.bridge.codex_mcp_server() as codex_mcp_server:
                continue_attempt = await self.bridge.continue_with_thread(
                    server=codex_mcp_server,
                    codex_thread_id=continuation_state.codex_thread_id,
                    continuation_context=task,
                )
                if continue_attempt.status == "failed" and continue_attempt.contract_mode == "strict_blocked":
                    raise RuntimeError(
                        "Strict continue mode blocked fallback: "
                        f"{continue_attempt.error or 'codex-reply explicit continuation failed'}"
                    )
                if continue_attempt.status != "acknowledged":
                    self.bridge.audit_event(
                        "codex_continue_fallback",
                        {
                            "reason": continue_attempt.error
                            or "explicit continue not acknowledged",
                            "mode": "context_fallback",
                            "continue_mode": continue_attempt.mode,
                            "continue_route": continue_attempt.route,
                            "continue_tool_name": continue_attempt.tool_name,
                            "continue_contract_mode": continue_attempt.contract_mode,
                            "codex_thread_id": continuation_state.codex_thread_id,
                        },
                    )
                agent = Agent(
                    name="LocalCodexSupervisor",
                    instructions=instructions,
                    mcp_servers=[codex_mcp_server],
                )
                result = await Runner.run(
                    starting_agent=agent,
                    input=task,
                    max_turns=self._run_max_turns,
                    session=session,
                )
        except TimeoutError as exc:
            error_text = f"Continue-run timed out: {exc}"
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text[:500], "phase": "continue_run", "status": "timeout"},
            )
            self.state.write_next_step(
                "A continuidade expirou (timeout). Reexecutar --continue-run."
            )
            self._persist_terminal_action(
                status="timeout",
                final_output=error_text,
                agent_session_id=continuation_state.agent_session_id,
                new_items=[],
                target_project_path=str(target_project_path),
                fallback_state=continuation_state,
                continue_attempt=continue_attempt,
            )
            raise TimeoutError(error_text) from exc
        except asyncio.CancelledError:
            error_text = "Continue-run interrupted by cancellation."
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text, "phase": "continue_run", "status": "interrupted"},
            )
            self.state.write_next_step(
                "A continuidade foi interrompida. Retomar com --continue-run."
            )
            self._persist_terminal_action(
                status="interrupted",
                final_output=error_text,
                agent_session_id=continuation_state.agent_session_id,
                new_items=[],
                target_project_path=str(target_project_path),
                fallback_state=continuation_state,
                continue_attempt=continue_attempt,
            )
            raise
        except KeyboardInterrupt:
            error_text = "Continue-run interrupted by keyboard signal."
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text, "phase": "continue_run", "status": "interrupted"},
            )
            self.state.write_next_step(
                "A continuidade foi interrompida. Retomar com --continue-run."
            )
            self._persist_terminal_action(
                status="interrupted",
                final_output=error_text,
                agent_session_id=continuation_state.agent_session_id,
                new_items=[],
                target_project_path=str(target_project_path),
                fallback_state=continuation_state,
                continue_attempt=continue_attempt,
            )
            raise
        except Exception as exc:
            error_text = f"Continue-run failed: {exc}"
            self.bridge.audit_event(
                "runner_error",
                {"error": error_text[:500], "phase": "continue_run", "status": "error"},
            )
            self.state.write_next_step(
                "Corrigir o erro de continuidade e reexecutar --continue-run."
            )
            self._persist_terminal_action(
                status="error",
                final_output=error_text,
                agent_session_id=continuation_state.agent_session_id,
                new_items=[],
                target_project_path=str(target_project_path),
                fallback_state=continuation_state,
                continue_attempt=continue_attempt,
            )
            raise

        final_output = self._final_output_text(result.final_output)
        next_step_summary = self._extract_next_step_summary(final_output)
        self.state.write_next_step(next_step_summary)

        new_items = getattr(result, "new_items", [])
        self.bridge.audit_event(
            "runner_new_items_summary",
            {"items": self._summarize_new_items_for_audit(new_items)},
        )
        self._debug_new_items(new_items)

        return self._persist_terminal_action(
            status="success",
            final_output=final_output,
            agent_session_id=continuation_state.agent_session_id,
            new_items=new_items,
            target_project_path=str(target_project_path),
            fallback_state=continuation_state,
            continue_attempt=continue_attempt,
        )

    def _persist_terminal_action(
        self,
        *,
        status: str,
        final_output: str,
        agent_session_id: str,
        new_items: Sequence[Any],
        target_project_path: str,
        fallback_state: PersistedContinuationState | None = None,
        continue_attempt: CodexContinueAttemptResult | None = None,
    ) -> ActionRecord:
        execution_mode = "continue-run" if fallback_state is not None else "run-once"
        decision = "continue_run" if fallback_state is not None else "run_once"
        codex_thread_id, codex_thread_status, codex_thread_source = (
            self._resolve_codex_thread_metadata(new_items)
        )
        if (
            fallback_state is not None
            and not codex_thread_id
            and fallback_state.codex_thread_id
        ):
            codex_thread_id = fallback_state.codex_thread_id
            codex_thread_status = fallback_state.codex_thread_id_status
            codex_thread_source = fallback_state.codex_thread_id_source
        self.bridge.audit_event(
            "codex_thread_capture_result",
            {
                "captured": bool(codex_thread_id),
                "codex_thread_id_source": codex_thread_source,
                "codex_thread_id_status": codex_thread_status,
            },
        )
        action = ActionRecord(
            timestamp=self.state._now_iso(),
            status=status,
            mode="agents_sdk_mcp",
            target_project_path=target_project_path,
            final_output=final_output,
            agent_session_id=agent_session_id,
            agent_session_backend="sqlite",
            codex_thread_id=codex_thread_id,
            codex_thread_id_status=codex_thread_status,
            codex_thread_id_source=codex_thread_source,
            codex_continue_attempted=(
                continue_attempt.attempted if continue_attempt is not None else False
            ),
            codex_continue_mode=(
                continue_attempt.mode if continue_attempt is not None else None
            ),
            codex_continue_status=(
                continue_attempt.status if continue_attempt is not None else None
            ),
            codex_continue_route=(
                continue_attempt.route if continue_attempt is not None else None
            ),
            codex_continue_tool_name=(
                continue_attempt.tool_name if continue_attempt is not None else None
            ),
            codex_continue_contract_mode=(
                continue_attempt.contract_mode if continue_attempt is not None else None
            ),
            codex_continue_strict_mode=(
                continue_attempt.strict_mode if continue_attempt is not None else False
            ),
            codex_continue_deploy_profile=(
                continue_attempt.deploy_profile
                if continue_attempt is not None
                else self._deploy_profile()
            ),
            codex_continue_contract_validated=(
                continue_attempt.contract_validated if continue_attempt is not None else False
            ),
            codex_continue_contract_validation_reason=(
                continue_attempt.contract_validation_reason
                if continue_attempt is not None
                else None
            ),
        )
        self.bridge.audit_event(
            "continuation_context_ready",
            self.build_continuation_identifiers(action),
        )
        return self._persist_action_with_project_journal(
            action,
            execution_mode=execution_mode,
            decision=decision,
        )

    def _persist_action_with_project_journal(
        self,
        action: ActionRecord,
        *,
        execution_mode: str,
        decision: str,
    ) -> ActionRecord:
        self.state.write_last_action(action)
        supervisor_checkpoint_path = self.state.write_checkpoint(action)
        if not self._project_journal_enabled():
            updated = replace(
                action,
                project_journal_enabled=False,
                project_journal_written=False,
                project_journal_error="disabled_by_env",
            )
            self.state.write_last_action(updated)
            return updated

        journal_record = self._build_project_journal_record(
            action,
            execution_mode=execution_mode,
            decision=decision,
            supervisor_checkpoint_path=supervisor_checkpoint_path,
        )
        try:
            project_checkpoint_path = append_project_checkpoint(
                action.target_project_path,
                journal_record,
            )
            project_status_path = update_or_create_status_md(
                action.target_project_path,
                journal_record,
            )
            updated = replace(
                action,
                project_journal_enabled=True,
                project_journal_written=True,
                project_journal_checkpoint_path=str(project_checkpoint_path),
                project_journal_status_path=str(project_status_path),
                project_journal_error=None,
            )
            self.bridge.audit_event(
                "project_journal_write_ok",
                {
                    "status_path": str(project_status_path),
                    "checkpoint_path": str(project_checkpoint_path),
                    "mode": execution_mode,
                },
            )
        except Exception as exc:
            error_text = str(exc)[:500]
            updated = replace(
                action,
                project_journal_enabled=True,
                project_journal_written=False,
                project_journal_error=error_text,
            )
            self.bridge.audit_event(
                "project_journal_write_failed",
                {
                    "error": error_text,
                    "target_project_path": action.target_project_path,
                    "mode": execution_mode,
                },
            )

        self.state.write_last_action(updated)
        return updated

    def _build_project_journal_record(
        self,
        action: ActionRecord,
        *,
        execution_mode: str,
        decision: str,
        supervisor_checkpoint_path: Path,
    ) -> dict[str, str]:
        status_compact = "success" if action.status == "success" else "failed"
        return {
            "timestamp_utc": action.timestamp,
            "mode": execution_mode,
            "deploy_profile": action.codex_continue_deploy_profile or self._deploy_profile(),
            "decision": decision,
            "status": status_compact,
            "status_raw": action.status,
            "agent_session_id": action.agent_session_id,
            "codex_thread_id": action.codex_thread_id or "",
            "final_output": action.final_output,
            "next_step": self.state.read_next_step(),
            "supervisor_last_action_path": str(self.state.last_action_file),
            "supervisor_checkpoint_path": str(supervisor_checkpoint_path),
        }

    def build_continuation_identifiers(
        self, action: ActionRecord
    ) -> dict[str, str | None]:
        """Prepare identifiers for a future explicit continue-run entrypoint."""
        return {
            "agent_session_id": action.agent_session_id,
            "codex_thread_id": action.codex_thread_id,
            "codex_thread_id_status": action.codex_thread_id_status,
            "codex_thread_id_source": action.codex_thread_id_source,
            "codex_continue_mode": action.codex_continue_mode,
            "codex_continue_status": action.codex_continue_status,
            "codex_continue_route": action.codex_continue_route,
            "codex_continue_tool_name": action.codex_continue_tool_name,
            "codex_continue_contract_mode": action.codex_continue_contract_mode,
            "codex_continue_strict_mode": str(action.codex_continue_strict_mode),
            "codex_continue_deploy_profile": action.codex_continue_deploy_profile,
            "codex_continue_contract_validated": str(
                action.codex_continue_contract_validated
            ),
            "codex_continue_contract_validation_reason": (
                action.codex_continue_contract_validation_reason
            ),
        }

    def _validate_runtime_for_target(self, target_project_path: Path) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY is required for Agents SDK execution. "
                "Set it in .env or environment variables."
            )
        if not target_project_path.exists():
            raise FileNotFoundError(
                f"Target project path not found: {target_project_path}"
            )
        if not target_project_path.is_dir():
            raise NotADirectoryError(
                f"Target project path is not a directory: {target_project_path}"
            )

    def _configure_bridge_for_target(self, target_project_path: Path) -> None:
        self.bridge = CodexBridge(
            CodexBridgeConfig(
                target_project_path=target_project_path,
                client_session_timeout_seconds=30.0,
                audit_log_path=self.config.logs_dir / "codex_mcp_audit.jsonl",
                audit_enabled=(
                    os.getenv("SUPERVISOR_MCP_AUDIT", "0") in {"1", "true", "TRUE"}
                ),
                continue_strict=(
                    self._continue_strict_enabled()
                ),
                deploy_profile=self._deploy_profile(),
                continue_expected_tool="codex-reply",
                continue_expected_min_version=os.getenv(
                    "SUPERVISOR_CONTINUE_EXPECTED_MIN_VERSION"
                ),
            )
        )

    @staticmethod
    def _deploy_profile() -> str:
        profile = os.getenv("SUPERVISOR_DEPLOY_PROFILE", "compat").strip().lower()
        return profile if profile in {"compat", "production"} else "compat"

    def _continue_strict_enabled(self) -> bool:
        strict_env = os.getenv("SUPERVISOR_CONTINUE_STRICT", "0") in {"1", "true", "TRUE"}
        return strict_env or self._deploy_profile() == "production"

    @staticmethod
    def _load_run_max_turns() -> int:
        raw_value = os.getenv("SUPERVISOR_RUN_MAX_TURNS", "2").strip()
        try:
            parsed = int(raw_value)
        except Exception:
            parsed = 2
        return min(max(parsed, 1), 4)

    @staticmethod
    def _project_journal_enabled() -> bool:
        raw = os.getenv("SUPERVISOR_PROJECT_JOURNAL", "1").strip().lower()
        return raw not in {"0", "false", "no", "off"}

    @staticmethod
    def _final_output_text(final_output: Any) -> str:
        text = str(final_output).strip()
        return text if text else "(empty final output)"

    @staticmethod
    def _extract_next_step_summary(final_output: str) -> str:
        first_non_empty_line = next(
            (line.strip() for line in final_output.splitlines() if line.strip()),
            "",
        )
        if first_non_empty_line:
            return (
                "Próximo passo sugerido pelo agente: "
                f"{first_non_empty_line[:500]}"
            )
        return "Próximo passo sugerido pelo agente: revisar saída final da rodada."

    def _extract_codex_thread_metadata(
        self, new_items: Sequence[Any]
    ) -> tuple[str | None, str, str | None]:
        try:
            for candidate_source, payload in self._iter_tool_result_payloads(new_items):
                thread_id, path = self._find_thread_id_in_payload(payload)
                if thread_id:
                    return (
                        thread_id,
                        "captured_from_mcp_tool_result",
                        f"{candidate_source}.{path}",
                    )
        except Exception:
            return (None, "pending_capture_from_mcp_tool_result", None)
        return (None, "pending_capture_from_mcp_tool_result", None)

    def _append_readme_fallback_context(self, *, task: str, target_project_path: Path) -> str:
        try:
            readme_text, resolved_path, truncated = self.read_project_file_safe(
                target_project_path=target_project_path,
                rel_or_abs_path="README.md",
                max_bytes=200_000,
            )
        except FileNotFoundError:
            return task
        except Exception as exc:
            self.bridge.audit_event(
                "project_file_fallback_read_failed",
                {
                    "path": "README.md",
                    "error": str(exc)[:500],
                    "reason": "local_read_only_fallback",
                },
            )
            return task

        preview_lines = readme_text.splitlines()[:120]
        preview = "\n".join(preview_lines).strip()
        if len(preview) > 12_000:
            preview = preview[:12_000].rstrip()
            truncated = True

        self.bridge.audit_event(
            "project_file_fallback_read_ok",
            {
                "path": "README.md",
                "resolved_path": str(resolved_path),
                "bytes_preview": len(preview.encode("utf-8", errors="ignore")),
                "truncated": truncated,
                "reason": "local_read_only_fallback",
            },
        )
        if not preview:
            return task
        return (
            f"{task}\n\n"
            "README preview (fallback local, read-only):\n"
            "Use este trecho apenas como contexto auxiliar se a leitura via MCP falhar.\n"
            "```text\n"
            f"{preview}\n"
            "```"
        )

    @staticmethod
    def read_project_file_safe(
        *,
        target_project_path: Path,
        rel_or_abs_path: str,
        max_bytes: int = 200_000,
    ) -> tuple[str, Path, bool]:
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive.")
        if not rel_or_abs_path or not str(rel_or_abs_path).strip():
            raise ValueError("path is required.")

        root = target_project_path.expanduser().resolve(strict=True)
        requested = Path(rel_or_abs_path).expanduser()
        if not requested.is_absolute() and ".." in requested.parts:
            raise PermissionError("parent path traversal is not allowed.")

        candidate = requested if requested.is_absolute() else (root / requested)
        resolved = candidate.resolve(strict=True)
        if os.path.commonpath([str(root), str(resolved)]) != str(root):
            raise PermissionError("path escapes target_project_path.")
        if not resolved.is_file():
            raise FileNotFoundError(f"file not found: {resolved}")

        with resolved.open("rb") as fh:
            blob = fh.read(max_bytes + 1)
        truncated = len(blob) > max_bytes
        if truncated:
            blob = blob[:max_bytes]
        return blob.decode("utf-8", errors="replace"), resolved, truncated

    def _resolve_codex_thread_metadata(
        self, new_items: Sequence[Any]
    ) -> tuple[str | None, str, str | None]:
        codex_thread_id, codex_thread_status, codex_thread_source = (
            self._extract_codex_thread_metadata(new_items)
        )
        if codex_thread_id:
            return codex_thread_id, codex_thread_status, codex_thread_source

        if self.bridge.observed_thread_id:
            source = self.bridge.observed_thread_id_source or "message_text.threadId"
            return (
                self.bridge.observed_thread_id,
                "captured_from_mcp_message_handler",
                source,
            )
        return (None, "pending_capture_from_mcp_tool_result", None)

    def _iter_tool_result_payloads(
        self, new_items: Sequence[Any]
    ) -> Sequence[tuple[str, Any]]:
        candidates: list[tuple[str, Any]] = []
        for idx, item in enumerate(new_items):
            class_name = item.__class__.__name__.lower()
            item_type = str(getattr(item, "type", "")).lower()
            likely_tool_item = (
                "tool" in class_name
                or "mcp" in class_name
                or "tool" in item_type
                or "mcp" in item_type
            )
            if not likely_tool_item:
                continue

            for attr_name in ("output", "raw_item"):
                if hasattr(item, attr_name):
                    candidates.append((f"new_items[{idx}].{attr_name}", getattr(item, attr_name)))

            candidates.append((f"new_items[{idx}]", item))
        if candidates:
            return candidates

        for idx, item in enumerate(new_items):
            for attr_name in ("output", "raw_item"):
                if hasattr(item, attr_name):
                    candidates.append((f"new_items[{idx}].{attr_name}", getattr(item, attr_name)))
            candidates.append((f"new_items[{idx}]", item))
        return candidates

    @classmethod
    def _find_thread_id_in_payload(cls, payload: Any) -> tuple[str | None, str | None]:
        search_paths = (
            ("structuredContent", "threadId"),
            ("structuredContent", "thread_id"),
            ("threadId",),
            ("thread_id",),
            ("conversationId",),
            ("conversation_id",),
        )
        for mapping_payload, location in cls._iter_mappings(payload):
            for path in search_paths:
                value = cls._get_path(mapping_payload, path)
                if cls._is_valid_id(value):
                    return str(value), ".".join((location, *path)) if location else ".".join(path)
        return None, None

    @classmethod
    def _iter_mappings(cls, payload: Any) -> Sequence[tuple[dict[str, Any], str]]:
        normalized = cls._normalize_payload(payload)
        output: list[tuple[dict[str, Any], str]] = []

        def walk(node: Any, location: str) -> None:
            if isinstance(node, Mapping):
                node_dict = {str(k): v for k, v in node.items()}
                output.append((node_dict, location))
                for key, value in node_dict.items():
                    next_location = f"{location}.{key}" if location else key
                    walk(value, next_location)
            elif isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
                for idx, value in enumerate(node):
                    next_location = f"{location}[{idx}]" if location else f"[{idx}]"
                    walk(value, next_location)

        walk(normalized, "")
        return output

    @classmethod
    def _normalize_payload(cls, payload: Any, depth: int = 0) -> Any:
        if depth > 6:
            return None
        if payload is None or isinstance(payload, (bool, int, float, str)):
            if isinstance(payload, str):
                parsed = cls._parse_json(payload)
                if parsed is not None:
                    return cls._normalize_payload(parsed, depth + 1)
            return payload
        if isinstance(payload, Mapping):
            return {
                str(key): cls._normalize_payload(value, depth + 1)
                for key, value in list(payload.items())[:40]
            }
        if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
            return [cls._normalize_payload(item, depth + 1) for item in list(payload)[:40]]
        if hasattr(payload, "model_dump"):
            try:
                return cls._normalize_payload(payload.model_dump(), depth + 1)
            except Exception:
                pass
        if hasattr(payload, "__dict__"):
            raw_dict = {
                key: value
                for key, value in vars(payload).items()
                if not key.startswith("_")
            }
            if raw_dict:
                return cls._normalize_payload(raw_dict, depth + 1)
        return str(payload)

    @staticmethod
    def _parse_json(text: str) -> Any | None:
        candidate = text.strip()
        if not candidate:
            return None
        if candidate[0] not in ("{", "["):
            return None
        try:
            return json.loads(candidate)
        except Exception:
            return None

    @staticmethod
    def _get_path(payload: Mapping[str, Any], path: Sequence[str]) -> Any:
        current: Any = payload
        for part in path:
            if not isinstance(current, Mapping):
                return None
            if part not in current:
                return None
            current = current[part]
        return current

    @staticmethod
    def _is_valid_id(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def _debug_new_items(self, new_items: Sequence[Any]) -> None:
        if os.getenv("SUPERVISOR_DEBUG_NEW_ITEMS") not in {"1", "true", "TRUE"}:
            return
        summary = []
        for idx, item in enumerate(new_items):
            row: dict[str, Any] = {
                "index": idx,
                "class": item.__class__.__name__,
                "type": getattr(item, "type", None),
                "has_output": hasattr(item, "output"),
                "has_raw_item": hasattr(item, "raw_item"),
            }
            if hasattr(item, "output"):
                normalized_output = self._normalize_payload(getattr(item, "output"))
                if isinstance(normalized_output, Mapping):
                    row["output_keys"] = list(normalized_output.keys())[:12]
            if hasattr(item, "raw_item"):
                normalized_raw = self._normalize_payload(getattr(item, "raw_item"))
                if isinstance(normalized_raw, Mapping):
                    row["raw_item_keys"] = list(normalized_raw.keys())[:12]
            summary.append(row)
        print(f"DEBUG new_items summary: {json.dumps(summary, ensure_ascii=True)}")

    def _summarize_new_items_for_audit(
        self, new_items: Sequence[Any]
    ) -> list[dict[str, Any]]:
        summary: list[dict[str, Any]] = []
        for idx, item in enumerate(new_items[:20]):
            row: dict[str, Any] = {
                "index": idx,
                "class": item.__class__.__name__,
                "type": getattr(item, "type", None),
            }
            if hasattr(item, "output"):
                normalized_output = self._normalize_payload(getattr(item, "output"))
                if isinstance(normalized_output, Mapping):
                    row["output_keys"] = list(normalized_output.keys())[:12]
                    thread_id, path = self._find_thread_id_in_payload(normalized_output)
                    if thread_id:
                        row["thread_candidate_source"] = path
            if hasattr(item, "raw_item"):
                normalized_raw = self._normalize_payload(getattr(item, "raw_item"))
                if isinstance(normalized_raw, Mapping):
                    row["raw_item_keys"] = list(normalized_raw.keys())[:12]
            summary.append(row)
        return summary
