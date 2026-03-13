"""Bridge for Codex CLI MCP server lifecycle."""

from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator

from agents.mcp import MCPServerStdio, MCPServerStdioParams


@dataclass(slots=True)
class CodexBridgeConfig:
    """Configuration for spawning the local Codex MCP server."""

    target_project_path: Path
    client_session_timeout_seconds: float = 30.0
    audit_log_path: Path | None = None
    audit_enabled: bool = False
    continue_strict: bool = False
    deploy_profile: str = "compat"
    continue_expected_tool: str = "codex-reply"
    continue_expected_min_version: str | None = None


@dataclass(slots=True)
class CodexContinueAttemptResult:
    """Result of explicit Codex continue attempt by thread id."""

    attempted: bool
    mode: str
    status: str
    route: str
    tool_name: str | None = None
    contract_mode: str | None = None
    strict_mode: bool = False
    deploy_profile: str = "compat"
    contract_validated: bool = False
    contract_validation_reason: str | None = None
    error: str | None = None


@dataclass(slots=True)
class CodexContinueCapability:
    """Discovered tool capability for explicit continue by thread id."""

    tool_name: str
    detected_fields: tuple[str, ...]
    tool_version: str | None
    score: int


class CodexBridge:
    """Starts and stops Codex CLI as an MCP stdio server."""

    def __init__(self, config: CodexBridgeConfig) -> None:
        self.config = config
        self.observed_thread_id: str | None = None
        self.observed_thread_id_source: str | None = None
        self.observed_thread_id_event_type: str | None = None
        self._continue_capability: CodexContinueCapability | None = None
        self._continue_discovery_done = False
        self._tool_descriptors_cache: list[dict[str, Any]] | None = None
        self._warning_capture_handler: logging.Handler | None = None

    def reset_observed_thread_hint(self) -> None:
        self.observed_thread_id = None
        self.observed_thread_id_source = None
        self.observed_thread_id_event_type = None

    def audit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self.config.audit_enabled or not self.config.audit_log_path:
            return
        self.config.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "target_project_path": str(self.config.target_project_path),
            "payload": payload,
        }
        with self.config.audit_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + os.linesep)

    async def handle_mcp_message(self, message: Any) -> None:
        thread_id, source = self._extract_thread_id_hint(message)
        if thread_id and not self.observed_thread_id:
            self.observed_thread_id = thread_id
            self.observed_thread_id_source = source
            self.observed_thread_id_event_type = "mcp_message_handler"
            self.audit_event(
                "mcp_thread_hint_observed",
                {
                    "thread_id_hint": thread_id,
                    "source": source,
                    "event_type": self.observed_thread_id_event_type,
                },
            )

    async def continue_with_thread(
        self,
        *,
        server: MCPServerStdio,
        codex_thread_id: str,
        continuation_context: str,
    ) -> CodexContinueAttemptResult:
        """Try explicit Codex-side continuation using thread id as request parameter."""
        thread_id = codex_thread_id.strip()
        if not thread_id:
            return CodexContinueAttemptResult(
                attempted=False,
                mode="context_fallback",
                status="failed",
                route="not_attempted_empty_thread_id",
                contract_mode="context_fallback",
                strict_mode=self.config.continue_strict,
                deploy_profile=self.config.deploy_profile,
                contract_validated=False,
                contract_validation_reason="codex_thread_id is empty",
                error="codex_thread_id is empty",
            )

        default_payload = {
            "threadId": thread_id,
            "thread_id": thread_id,
            "prompt": continuation_context[:1500],
            "continuation_context": continuation_context[:1500],
        }
        self.audit_event(
            "codex_continue_request",
            {
                "attempted": True,
                "codex_thread_id": thread_id,
                "mode": "explicit_thread_id_attempt",
                "route": "tool_level_explicit_continue",
                "strict_mode": self.config.continue_strict,
                "deploy_profile": self.config.deploy_profile,
            },
        )

        contract_ok, contract_reason, capability = await self.validate_continue_contract(
            server=server
        )
        if self.config.deploy_profile == "production" and not contract_ok:
            self.audit_event(
                "codex_continue_production_profile_blocked",
                {
                    "deploy_profile": self.config.deploy_profile,
                    "strict_mode": self.config.continue_strict,
                    "reason": contract_reason,
                },
            )
            return CodexContinueAttemptResult(
                attempted=True,
                mode="deterministic_primary",
                status="failed",
                route=f"call_tool:{self.config.continue_expected_tool}",
                tool_name=self.config.continue_expected_tool,
                contract_mode="strict_blocked",
                strict_mode=self.config.continue_strict,
                deploy_profile=self.config.deploy_profile,
                contract_validated=False,
                contract_validation_reason=contract_reason,
                error=f"production profile blocked continuation: {contract_reason}",
            )

        capability = await self.discover_continue_capability(server=server)
        deterministic_failed = False
        if (
            capability is not None
            and capability.tool_name == self.config.continue_expected_tool
        ):
            route = f"call_tool:{capability.tool_name}"
            request_payload = self._build_continue_payload(
                thread_id=thread_id,
                continuation_context=continuation_context,
                detected_fields=capability.detected_fields,
            )
            self.audit_event(
                "codex_continue_frozen_contract_selected",
                {
                    "tool_name": self.config.continue_expected_tool,
                    "route": route,
                    "strict_mode": self.config.continue_strict,
                    "deploy_profile": self.config.deploy_profile,
                    "detected_fields": list(capability.detected_fields)[:12],
                    "tool_version": capability.tool_version,
                },
            )
            self.audit_event(
                "codex_continue_primary_route_selected",
                {
                    "mode": "deterministic",
                    "tool_name": capability.tool_name,
                    "route": route,
                    "strict_mode": self.config.continue_strict,
                    "deploy_profile": self.config.deploy_profile,
                    "detected_fields": list(capability.detected_fields)[:12],
                },
            )
            try:
                result = await self._safe_call_tool(server, capability.tool_name, request_payload)
            except Exception as exc:
                deterministic_failed = True
                self.audit_event(
                    "codex_continue_error",
                    {
                        "codex_thread_id": thread_id,
                        "mode": "deterministic",
                        "route": route,
                        "tool_name": capability.tool_name,
                        "strict_mode": self.config.continue_strict,
                        "deploy_profile": self.config.deploy_profile,
                        "error": str(exc)[:500],
                    },
                )
            else:
                if self._result_indicates_success(result):
                    self.audit_event(
                        "codex_continue_ack",
                        {
                            "codex_thread_id": thread_id,
                            "mode": "deterministic",
                            "route": route,
                            "tool_name": capability.tool_name,
                            "strict_mode": self.config.continue_strict,
                            "deploy_profile": self.config.deploy_profile,
                        },
                    )
                    return CodexContinueAttemptResult(
                        attempted=True,
                        mode="deterministic_primary",
                        status="acknowledged",
                        route=route,
                        tool_name=capability.tool_name,
                        contract_mode="deterministic",
                        strict_mode=self.config.continue_strict,
                        deploy_profile=self.config.deploy_profile,
                        contract_validated=contract_ok,
                        contract_validation_reason=contract_reason,
                    )
                deterministic_failed = True
                self.audit_event(
                    "codex_continue_error",
                    {
                        "codex_thread_id": thread_id,
                        "mode": "deterministic",
                        "route": route,
                        "tool_name": capability.tool_name,
                        "strict_mode": self.config.continue_strict,
                        "deploy_profile": self.config.deploy_profile,
                        "error": "deterministic continue call returned non-ack response",
                    },
                )
        elif self.config.continue_strict:
            self.audit_event(
                "codex_continue_strict_mode_blocked_fallback",
                {
                    "reason": "frozen tool codex-reply not available",
                    "tool_name": self.config.continue_expected_tool,
                    "route": f"call_tool:{self.config.continue_expected_tool}",
                    "strict_mode": True,
                    "deploy_profile": self.config.deploy_profile,
                },
            )
            return CodexContinueAttemptResult(
                attempted=True,
                mode="deterministic_primary",
                status="failed",
                route=f"call_tool:{self.config.continue_expected_tool}",
                tool_name=self.config.continue_expected_tool,
                contract_mode="strict_blocked",
                strict_mode=True,
                deploy_profile=self.config.deploy_profile,
                contract_validated=contract_ok,
                contract_validation_reason=contract_reason,
                error=(
                    "strict mode blocked fallback: "
                    f"{self.config.continue_expected_tool} unavailable"
                ),
            )
        if self.config.continue_strict and deterministic_failed:
            self.audit_event(
                "codex_continue_strict_mode_blocked_fallback",
                {
                    "reason": "frozen tool codex-reply failed",
                    "tool_name": self.config.continue_expected_tool,
                    "route": f"call_tool:{self.config.continue_expected_tool}",
                    "strict_mode": True,
                    "deploy_profile": self.config.deploy_profile,
                },
            )
            return CodexContinueAttemptResult(
                attempted=True,
                mode="deterministic_primary",
                status="failed",
                route=f"call_tool:{self.config.continue_expected_tool}",
                tool_name=self.config.continue_expected_tool,
                contract_mode="strict_blocked",
                strict_mode=True,
                deploy_profile=self.config.deploy_profile,
                contract_validated=contract_ok,
                contract_validation_reason=contract_reason,
                error=(
                    "strict mode blocked fallback: "
                    f"{self.config.continue_expected_tool} failed"
                ),
            )

        if self.config.deploy_profile == "production":
            self.audit_event(
                "codex_continue_production_profile_blocked",
                {
                    "deploy_profile": self.config.deploy_profile,
                    "strict_mode": self.config.continue_strict,
                    "reason": (
                        f"expected deterministic route {self.config.continue_expected_tool} "
                        "was not available"
                    ),
                },
            )
            return CodexContinueAttemptResult(
                attempted=True,
                mode="deterministic_primary",
                status="failed",
                route=f"call_tool:{self.config.continue_expected_tool}",
                tool_name=self.config.continue_expected_tool,
                contract_mode="strict_blocked",
                strict_mode=self.config.continue_strict,
                deploy_profile=self.config.deploy_profile,
                contract_validated=contract_ok,
                contract_validation_reason=contract_reason,
                error="production profile blocked fallback heuristic routes",
            )

        attempts: list[tuple[str, str, dict[str, Any]]] = []
        known_tool_names = (
            "codex_continue",
            "continue",
            "resume",
            "codex_resume",
            "conversation_continue",
        )
        excluded_tool = capability.tool_name if capability is not None else None
        for tool_name in known_tool_names:
            if tool_name != excluded_tool:
                attempts.append(("call_tool", tool_name, dict(default_payload)))

        tools = await self._safe_list_tools(server)
        for tool_name in tools:
            if tool_name == excluded_tool:
                continue
            if "continue" in tool_name or "resume" in tool_name:
                attempts.append(("call_tool", tool_name, dict(default_payload)))

        seen_routes: set[str] = set()
        for method_name, tool_name, payload in attempts:
            route = f"{method_name}:{tool_name}"
            if route in seen_routes:
                continue
            seen_routes.add(route)
            self.audit_event(
                "codex_continue_fallback_route_selected",
                {
                    "mode": "heuristic_fallback",
                    "tool_name": tool_name,
                    "route": route,
                    "strict_mode": self.config.continue_strict,
                    "deploy_profile": self.config.deploy_profile,
                    "detected_fields": ["threadId", "thread_id", "prompt", "continuation_context"],
                },
            )
            try:
                result = await self._safe_call_tool(server, tool_name, payload)
            except Exception as exc:
                self.audit_event(
                    "codex_continue_error",
                    {
                        "codex_thread_id": thread_id,
                        "mode": "heuristic_fallback",
                        "route": route,
                        "tool_name": tool_name,
                        "strict_mode": self.config.continue_strict,
                        "deploy_profile": self.config.deploy_profile,
                        "error": str(exc)[:500],
                    },
                )
                continue
            if self._result_indicates_success(result):
                self.audit_event(
                    "codex_continue_ack",
                    {
                        "codex_thread_id": thread_id,
                        "mode": "heuristic_fallback",
                        "route": route,
                        "tool_name": tool_name,
                        "strict_mode": self.config.continue_strict,
                        "deploy_profile": self.config.deploy_profile,
                    },
                )
                return CodexContinueAttemptResult(
                    attempted=True,
                    mode="heuristic_fallback",
                    status="acknowledged",
                    route=route,
                    tool_name=tool_name,
                    contract_mode="heuristic_fallback",
                    strict_mode=self.config.continue_strict,
                    deploy_profile=self.config.deploy_profile,
                    contract_validated=contract_ok,
                    contract_validation_reason=contract_reason,
                )
            self.audit_event(
                "codex_continue_error",
                {
                    "codex_thread_id": thread_id,
                    "mode": "heuristic_fallback",
                    "route": route,
                    "tool_name": tool_name,
                    "strict_mode": self.config.continue_strict,
                    "deploy_profile": self.config.deploy_profile,
                    "error": "explicit continue call returned non-ack response",
                },
            )

        self.audit_event(
            "codex_continue_error",
            {
                "codex_thread_id": thread_id,
                "mode": "context_fallback",
                "route": "tool_level_explicit_continue",
                "strict_mode": self.config.continue_strict,
                "deploy_profile": self.config.deploy_profile,
                "error": "no explicit continue route acknowledged by MCP server",
            },
        )
        return CodexContinueAttemptResult(
            attempted=True,
            mode="context_fallback",
            status="fallback_used",
            route="tool_level_explicit_continue",
            contract_mode="context_fallback",
            strict_mode=self.config.continue_strict,
            deploy_profile=self.config.deploy_profile,
            contract_validated=contract_ok,
            contract_validation_reason=contract_reason,
            error="explicit continue route not acknowledged",
        )

    async def validate_continue_contract(
        self, *, server: MCPServerStdio
    ) -> tuple[bool, str, CodexContinueCapability | None]:
        """Validate frozen continue contract compatibility for current MCP server."""
        self.audit_event(
            "codex_continue_contract_validation_start",
            {
                "deploy_profile": self.config.deploy_profile,
                "expected_tool": self.config.continue_expected_tool,
                "expected_min_version": self.config.continue_expected_min_version,
            },
        )
        capability = await self.discover_continue_capability(server=server)
        if capability is None:
            reason = "no continue capability discovered"
            self.audit_event(
                "codex_continue_contract_validation_failed",
                {
                    "deploy_profile": self.config.deploy_profile,
                    "reason": reason,
                },
            )
            return False, reason, None
        if capability.tool_name != self.config.continue_expected_tool:
            reason = (
                f"expected tool {self.config.continue_expected_tool}, "
                f"got {capability.tool_name}"
            )
            self.audit_event(
                "codex_continue_contract_validation_failed",
                {
                    "deploy_profile": self.config.deploy_profile,
                    "reason": reason,
                    "tool_name": capability.tool_name,
                },
            )
            return False, reason, capability
        required_fields = {"threadId", "prompt"}
        available_fields = set(capability.detected_fields)
        if not required_fields.issubset(available_fields):
            reason = (
                "missing required schema fields for frozen contract: "
                f"{sorted(required_fields - available_fields)}"
            )
            self.audit_event(
                "codex_continue_contract_validation_failed",
                {
                    "deploy_profile": self.config.deploy_profile,
                    "reason": reason,
                    "tool_name": capability.tool_name,
                    "detected_fields": list(capability.detected_fields)[:12],
                },
            )
            return False, reason, capability
        if self.config.continue_expected_min_version:
            if not capability.tool_version:
                reason = (
                    "tool version missing while expected_min_version is configured: "
                    f"{self.config.continue_expected_min_version}"
                )
                self.audit_event(
                    "codex_continue_contract_validation_failed",
                    {
                        "deploy_profile": self.config.deploy_profile,
                        "reason": reason,
                        "tool_name": capability.tool_name,
                    },
                )
                return False, reason, capability
            if capability.tool_version < self.config.continue_expected_min_version:
                reason = (
                    "tool version is below expected minimum: "
                    f"{capability.tool_version} < {self.config.continue_expected_min_version}"
                )
                self.audit_event(
                    "codex_continue_contract_validation_failed",
                    {
                        "deploy_profile": self.config.deploy_profile,
                        "reason": reason,
                        "tool_name": capability.tool_name,
                        "tool_version": capability.tool_version,
                    },
                )
                return False, reason, capability
        reason = "frozen codex-reply contract validated"
        self.audit_event(
            "codex_continue_contract_validation_ok",
            {
                "deploy_profile": self.config.deploy_profile,
                "tool_name": capability.tool_name,
                "tool_version": capability.tool_version,
                "detected_fields": list(capability.detected_fields)[:12],
            },
        )
        return True, reason, capability

    async def discover_continue_capability(
        self, *, server: MCPServerStdio
    ) -> CodexContinueCapability | None:
        """Discover and cache the best continue tool capability in current MCP server."""
        if self._continue_discovery_done:
            return self._continue_capability

        self._continue_discovery_done = True
        self.audit_event("codex_continue_discovery_start", {"mode": "deterministic"})
        descriptors = await self._safe_list_tool_descriptors(server)
        frozen_capability = next(
            (
                CodexContinueCapability(
                    tool_name=str(item["name"]),
                    detected_fields=tuple(item.get("detected_fields", [])),
                    tool_version=(
                        str(item["tool_version"])
                        if isinstance(item.get("tool_version"), str)
                        else None
                    ),
                    score=1000,
                )
                for item in descriptors
                if item.get("name") == "codex-reply"
            ),
            None,
        )
        if frozen_capability is not None:
            self._continue_capability = frozen_capability
            self.audit_event(
                "codex_continue_discovery_result",
                {
                    "discovered": True,
                    "tool_name": self._continue_capability.tool_name,
                    "detected_fields": list(self._continue_capability.detected_fields)[:12],
                    "contract_mode": "deterministic",
                    "frozen_contract": True,
                    "tool_version": self._continue_capability.tool_version,
                    "score": self._continue_capability.score,
                    "candidate_count": 1,
                },
            )
            return self._continue_capability
        candidates: list[CodexContinueCapability] = []
        for descriptor in descriptors:
            tool_name = descriptor.get("name")
            if not isinstance(tool_name, str) or not tool_name.strip():
                continue
            name = tool_name.strip()
            fields = tuple(descriptor.get("detected_fields", []))
            score = self._score_continue_capability(name=name, detected_fields=fields)
            if score <= 0:
                continue
            candidates.append(
                CodexContinueCapability(
                    tool_name=name,
                    detected_fields=fields,
                    tool_version=(
                        str(descriptor["tool_version"])
                        if isinstance(descriptor.get("tool_version"), str)
                        else None
                    ),
                    score=score,
                )
            )

        if candidates:
            candidates.sort(key=lambda item: item.score, reverse=True)
            self._continue_capability = candidates[0]
            self.audit_event(
                "codex_continue_discovery_result",
                {
                    "discovered": True,
                    "tool_name": self._continue_capability.tool_name,
                    "detected_fields": list(self._continue_capability.detected_fields)[:12],
                    "contract_mode": "deterministic",
                    "frozen_contract": False,
                    "tool_version": self._continue_capability.tool_version,
                    "score": self._continue_capability.score,
                    "candidate_count": len(candidates),
                },
            )
            return self._continue_capability

        self.audit_event(
            "codex_continue_discovery_result",
            {
                "discovered": False,
                "tool_name": None,
                "detected_fields": [],
                "contract_mode": "heuristic_fallback",
                "frozen_contract": False,
                "tool_version": None,
                "score": 0,
                "candidate_count": 0,
            },
        )
        return None

    @asynccontextmanager
    async def codex_mcp_server(self) -> AsyncIterator[MCPServerStdio]:
        """Yield a connected MCP stdio server for Agent/Runner usage."""
        self._install_warning_capture_handler()
        try:
            params: MCPServerStdioParams = {
                "command": "npx",
                "args": ["-y", "codex", "mcp-server"],
                "cwd": str(self.config.target_project_path),
            }
            server = MCPServerStdio(
                params=params,
                client_session_timeout_seconds=self.config.client_session_timeout_seconds,
                name="codex-cli-mcp",
                message_handler=self.handle_mcp_message,
            )
            self.audit_event(
                "mcp_server_spawn",
                {
                    "command": params["command"],
                    "args": params["args"],
                    "cwd": params["cwd"],
                },
            )
            async with server:
                self.audit_event("mcp_server_connected", {"name": "codex-cli-mcp"})
                try:
                    yield server
                finally:
                    self.audit_event("mcp_server_closed", {"name": "codex-cli-mcp"})
        finally:
            self._remove_warning_capture_handler()

    def _extract_thread_id_hint(self, message: Any) -> tuple[str | None, str | None]:
        normalized = self._normalize_message(message)
        if isinstance(normalized, dict):
            for path in (
                ("params", "_meta", "threadId"),
                ("params", "_meta", "thread_id"),
                ("params", "msg", "thread_id"),
                ("params", "msg", "threadId"),
                ("params", "msg", "session_id"),
                ("params", "msg", "sessionId"),
                ("structuredContent", "threadId"),
                ("structuredContent", "thread_id"),
                ("threadId",),
                ("thread_id",),
                ("conversationId",),
                ("conversation_id",),
            ):
                value = self._get_path(normalized, path)
                if isinstance(value, str) and value.strip():
                    return value, ".".join(path)
        message_text = str(message)
        regex_match = re.search(r"(threadId|thread_id|session_id)['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]", message_text)
        if regex_match:
            return regex_match.group(2).strip(), f"message_text.{regex_match.group(1)}"
        return None, None

    def _install_warning_capture_handler(self) -> None:
        if self._warning_capture_handler is not None:
            return
        if os.getenv("SUPERVISOR_MCP_WARNING_CAPTURE", "1") not in {"1", "true", "TRUE"}:
            return

        bridge = self

        class _CodexWarningCaptureHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                message_text = record.getMessage()
                if "method='codex/event'" not in message_text:
                    return
                thread_id, source = bridge._extract_thread_id_hint(message_text)
                if thread_id and not bridge.observed_thread_id:
                    bridge.observed_thread_id = thread_id
                    bridge.observed_thread_id_source = source or "warning_message.threadId"
                    bridge.observed_thread_id_event_type = "sdk_warning_codex_event"
                    bridge.audit_event(
                        "mcp_thread_hint_observed",
                        {
                            "thread_id_hint": thread_id,
                            "source": bridge.observed_thread_id_source,
                            "event_type": bridge.observed_thread_id_event_type,
                        },
                    )

        handler = _CodexWarningCaptureHandler(level=logging.WARNING)
        logging.getLogger().addHandler(handler)
        self._warning_capture_handler = handler

    def _remove_warning_capture_handler(self) -> None:
        if self._warning_capture_handler is None:
            return
        logging.getLogger().removeHandler(self._warning_capture_handler)
        self._warning_capture_handler = None

    def _normalize_message(self, message: Any, depth: int = 0) -> Any:
        if depth > 5:
            return None
        if message is None or isinstance(message, (bool, int, float, str)):
            return message
        if isinstance(message, dict):
            return {
                str(key): self._normalize_message(value, depth + 1)
                for key, value in list(message.items())[:50]
            }
        if isinstance(message, (list, tuple)):
            return [self._normalize_message(item, depth + 1) for item in list(message)[:50]]
        if hasattr(message, "model_dump"):
            try:
                return self._normalize_message(message.model_dump(), depth + 1)
            except Exception:
                pass
        if hasattr(message, "__dict__"):
            return self._normalize_message(vars(message), depth + 1)
        root = getattr(message, "root", None)
        if root is not None:
            return self._normalize_message(root, depth + 1)
        return str(message)

    @staticmethod
    def _get_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
        current: Any = data
        for part in path:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None
        return current

    async def _safe_list_tools(self, server: MCPServerStdio) -> list[str]:
        descriptors = await self._safe_list_tool_descriptors(server)
        return [item["name"] for item in descriptors if isinstance(item.get("name"), str)]

    async def _safe_list_tool_descriptors(
        self, server: MCPServerStdio
    ) -> list[dict[str, Any]]:
        if self._tool_descriptors_cache is not None:
            return self._tool_descriptors_cache
        list_tools_fn = getattr(server, "list_tools", None)
        if not callable(list_tools_fn):
            return []
        try:
            listed = await list_tools_fn()
        except Exception:
            return []
        descriptors: list[dict[str, Any]] = []
        if isinstance(listed, Sequence) and not isinstance(listed, (str, bytes, bytearray)):
            for item in listed:
                descriptor = self._extract_tool_descriptor(item)
                if descriptor:
                    descriptors.append(descriptor)
            self._tool_descriptors_cache = descriptors
            return descriptors
        if isinstance(listed, Mapping):
            tools = listed.get("tools")
            if isinstance(tools, Sequence) and not isinstance(
                tools, (str, bytes, bytearray)
            ):
                for item in tools:
                    descriptor = self._extract_tool_descriptor(item)
                    if descriptor:
                        descriptors.append(descriptor)
        self._tool_descriptors_cache = descriptors
        return descriptors

    async def _safe_call_tool(
        self, server: MCPServerStdio, tool_name: str, payload: dict[str, Any]
    ) -> Any:
        call_tool_fn = getattr(server, "call_tool", None)
        if not callable(call_tool_fn):
            raise RuntimeError("MCP server does not expose call_tool")
        try:
            return await call_tool_fn(tool_name, payload)
        except TypeError:
            return await call_tool_fn(name=tool_name, arguments=payload)

    @staticmethod
    def _extract_tool_name(tool_item: Any) -> str | None:
        if isinstance(tool_item, str) and tool_item.strip():
            return tool_item.strip()
        if isinstance(tool_item, Mapping):
            candidate = tool_item.get("name")
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
            return None
        candidate = getattr(tool_item, "name", None)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        return None

    def _extract_tool_descriptor(self, tool_item: Any) -> dict[str, Any] | None:
        name = self._extract_tool_name(tool_item)
        if not name:
            return None
        normalized = self._normalize_message(tool_item)
        detected_fields = self._extract_detected_fields(normalized)
        tool_version = self._extract_tool_version(normalized)
        return {
            "name": name,
            "detected_fields": detected_fields,
            "tool_version": tool_version,
        }

    def _extract_detected_fields(self, normalized_tool: Any) -> list[str]:
        if not isinstance(normalized_tool, Mapping):
            return []
        candidate_paths = (
            ("inputSchema", "properties"),
            ("input_schema", "properties"),
            ("parameters", "properties"),
            ("args_schema", "properties"),
        )
        fields: list[str] = []
        for path in candidate_paths:
            props = self._get_mapping_path(normalized_tool, path)
            if isinstance(props, Mapping):
                for key in props.keys():
                    key_text = str(key).strip()
                    if key_text and key_text not in fields:
                        fields.append(key_text)
        return fields

    def _extract_tool_version(self, normalized_tool: Any) -> str | None:
        if not isinstance(normalized_tool, Mapping):
            return None
        for key in ("version", "toolVersion", "capabilityVersion", "capability_version"):
            value = normalized_tool.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    def _get_mapping_path(payload: Mapping[str, Any], path: tuple[str, ...]) -> Any:
        current: Any = payload
        for part in path:
            if not isinstance(current, Mapping):
                return None
            current = current.get(part)
            if current is None:
                return None
        return current

    def _build_continue_payload(
        self,
        *,
        thread_id: str,
        continuation_context: str,
        detected_fields: Sequence[str],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        context_excerpt = continuation_context[:1500]
        field_set = {field for field in detected_fields}
        thread_field_candidates = ("threadId", "thread_id", "conversationId", "conversation_id")
        prompt_field_candidates = ("prompt", "input", "message", "continuation_context")

        for field_name in thread_field_candidates:
            if field_name in field_set:
                payload[field_name] = thread_id
        for field_name in prompt_field_candidates:
            if field_name in field_set:
                payload[field_name] = context_excerpt

        if not payload:
            payload = {
                "threadId": thread_id,
                "thread_id": thread_id,
                "prompt": context_excerpt,
                "continuation_context": context_excerpt,
            }
        return payload

    def _score_continue_capability(
        self, *, name: str, detected_fields: Sequence[str]
    ) -> int:
        name_lower = name.lower()
        score = 0
        if "continue" in name_lower:
            score += 60
        if "resume" in name_lower:
            score += 55
        if "codex" in name_lower:
            score += 15
        if "thread" in name_lower:
            score += 20
        field_set = {field.lower() for field in detected_fields}
        if "threadid" in field_set or "thread_id" in field_set:
            score += 30
        if "conversationid" in field_set or "conversation_id" in field_set:
            score += 20
        if "prompt" in field_set or "input" in field_set or "message" in field_set:
            score += 10
        return score

    def _result_indicates_success(self, result: Any) -> bool:
        if result is None:
            return False
        thread_id, _ = self._extract_thread_id_hint(result)
        if thread_id:
            return True
        normalized = self._normalize_message(result)
        if isinstance(normalized, Mapping):
            status = normalized.get("status")
            if isinstance(status, str) and status.lower() in {"ok", "success", "ack"}:
                return True
            acknowledged = normalized.get("acknowledged")
            if isinstance(acknowledged, bool):
                return acknowledged
        return False
