"""State and checkpoint persistence for supervisor runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import SupervisorConfig


@dataclass(slots=True)
class ActionRecord:
    """Execution record for real Agent + MCP runs."""

    timestamp: str
    status: str
    mode: str
    target_project_path: str
    final_output: str
    agent_session_id: str
    agent_session_backend: str
    codex_thread_id: str | None
    codex_thread_id_status: str
    codex_thread_id_source: str | None = None
    codex_continue_attempted: bool = False
    codex_continue_mode: str | None = None
    codex_continue_status: str | None = None
    codex_continue_route: str | None = None
    codex_continue_tool_name: str | None = None
    codex_continue_contract_mode: str | None = None
    codex_continue_strict_mode: bool = False
    codex_continue_deploy_profile: str = "compat"
    codex_continue_contract_validated: bool = False
    codex_continue_contract_validation_reason: str | None = None
    project_journal_enabled: bool = True
    project_journal_written: bool = False
    project_journal_checkpoint_path: str | None = None
    project_journal_status_path: str | None = None
    project_journal_error: str | None = None


@dataclass(slots=True)
class PersistedContinuationState:
    """Validated minimal continuation state from last_action.json."""

    agent_session_id: str
    codex_thread_id: str
    codex_thread_id_status: str
    codex_thread_id_source: str | None
    target_project_path: str


class StateStore:
    """Read/write mission state in local repository only."""

    def __init__(self, config: SupervisorConfig) -> None:
        self.config = config
        self.last_action_file = self.config.state_dir / "last_action.json"
        self.next_step_file = self.config.state_dir / "next_step.md"
        self.mission_file = self.config.state_dir / "mission.md"

    def ensure_layout(self) -> None:
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        self.config.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)

    def ensure_defaults(self) -> None:
        self.ensure_layout()

        if not self.last_action_file.exists():
            self.write_last_action(
                ActionRecord(
                    timestamp=self._now_iso(),
                    status="idle",
                    mode="agents_sdk_mcp",
                    target_project_path=(
                        str(self.config.target_project_path)
                        if self.config.target_project_configured
                        else ""
                    ),
                    final_output="State initialized.",
                    agent_session_id=self._safe_agent_session_id(),
                    agent_session_backend="sqlite",
                    codex_thread_id=None,
                    codex_thread_id_status="pending_capture_from_mcp_tool_result",
                    codex_continue_attempted=False,
                    codex_continue_mode=None,
                    codex_continue_status=None,
                    codex_continue_route=None,
                    codex_continue_tool_name=None,
                    codex_continue_contract_mode=None,
                    codex_continue_strict_mode=False,
                    codex_continue_deploy_profile="compat",
                    codex_continue_contract_validated=False,
                    codex_continue_contract_validation_reason=None,
                )
            )

        if not self.next_step_file.exists():
            self.next_step_file.write_text(
                "Definir o primeiro passo operacional do supervisor.\n",
                encoding="utf-8",
            )

        if not self.mission_file.exists():
            self.mission_file.write_text(
                "Orquestrar o projeto-alvo com segurança e rastreabilidade.\n",
                encoding="utf-8",
            )

    def read_mission(self) -> str:
        return self.mission_file.read_text(encoding="utf-8").strip()

    def read_next_step(self) -> str:
        return self.next_step_file.read_text(encoding="utf-8").strip()

    def write_next_step(self, text: str) -> None:
        self.next_step_file.write_text(text.strip() + "\n", encoding="utf-8")

    def write_last_action(self, action: ActionRecord) -> None:
        payload = self._merged_payload_with_existing_thread_metadata(action)
        self.last_action_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def write_checkpoint(self, action: ActionRecord) -> Path:
        payload = self._merged_payload_with_existing_thread_metadata(action)
        filename = (
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')}_{action.status}.json"
        )
        checkpoint_path = self.config.checkpoints_dir / filename
        checkpoint_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        return checkpoint_path

    def read_last_action_payload(self) -> dict[str, object]:
        payload = self._read_last_action_payload()
        return payload if payload is not None else {}

    def load_last_action_for_continue(self) -> PersistedContinuationState:
        payload = self._read_last_action_payload()
        if not payload:
            raise ValueError(
                "Cannot continue: state/last_action.json is missing or unreadable."
            )

        required_fields = (
            "agent_session_id",
            "codex_thread_id",
            "codex_thread_id_status",
            "target_project_path",
        )
        values: dict[str, str] = {}
        for field_name in required_fields:
            raw_value = payload.get(field_name)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(
                    f"Cannot continue: missing required field '{field_name}' in state/last_action.json."
                )
            values[field_name] = raw_value.strip()

        codex_thread_id_source = payload.get("codex_thread_id_source")
        if codex_thread_id_source is not None and not isinstance(
            codex_thread_id_source, str
        ):
            codex_thread_id_source = str(codex_thread_id_source)

        return PersistedContinuationState(
            agent_session_id=values["agent_session_id"],
            codex_thread_id=values["codex_thread_id"],
            codex_thread_id_status=values["codex_thread_id_status"],
            codex_thread_id_source=codex_thread_id_source,
            target_project_path=values["target_project_path"],
        )

    def _safe_agent_session_id(self) -> str:
        try:
            return self.config.resolved_agent_session_id()
        except Exception:
            return "pending_target_path"

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _merged_payload_with_existing_thread_metadata(
        self, action: ActionRecord
    ) -> dict[str, object]:
        payload = asdict(action)
        has_thread_id = isinstance(payload.get("codex_thread_id"), str) and bool(
            str(payload.get("codex_thread_id", "")).strip()
        )
        if has_thread_id:
            return payload

        current_payload = self._read_last_action_payload()
        if not current_payload:
            return payload

        current_thread_id = current_payload.get("codex_thread_id")
        if not isinstance(current_thread_id, str) or not current_thread_id.strip():
            return payload

        payload["codex_thread_id"] = current_thread_id
        if payload.get("codex_thread_id_status") == "pending_capture_from_mcp_tool_result":
            payload["codex_thread_id_status"] = str(
                current_payload.get("codex_thread_id_status")
                or "captured_from_mcp_message_handler"
            )
        if not payload.get("codex_thread_id_source"):
            payload["codex_thread_id_source"] = current_payload.get("codex_thread_id_source")
        return payload

    def _read_last_action_payload(self) -> dict[str, object] | None:
        if not self.last_action_file.exists():
            return None
        try:
            raw_payload = json.loads(self.last_action_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if isinstance(raw_payload, dict):
            return raw_payload
        return None
