"""Configuration loading for the local supervisor."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class SupervisorConfig:
    """Runtime configuration for supervisor orchestration."""

    supervisor_home: Path
    target_project_path: Path
    state_dir: Path
    checkpoints_dir: Path
    logs_dir: Path
    session_db_path: Path
    log_level: str = "INFO"
    target_project_configured: bool = False
    agent_session_id: str | None = None

    @classmethod
    def from_env(cls) -> "SupervisorConfig":
        supervisor_home = Path(
            os.getenv("SUPERVISOR_HOME", str(_repo_root()))
        ).expanduser().resolve()

        target_raw = os.getenv("TARGET_PROJECT_PATH", "")
        target_path = Path(target_raw).expanduser().resolve() if target_raw else Path()

        state_dir = supervisor_home / "state"
        checkpoints_dir = state_dir / "checkpoints"
        logs_dir = supervisor_home / "logs"
        session_db_path = Path(
            os.getenv("SESSION_DB_PATH", str(state_dir / "agent_sessions.db"))
        ).expanduser()
        if not session_db_path.is_absolute():
            session_db_path = (supervisor_home / session_db_path).resolve()
        else:
            session_db_path = session_db_path.resolve()

        return cls(
            supervisor_home=supervisor_home,
            target_project_path=target_path,
            state_dir=state_dir,
            checkpoints_dir=checkpoints_dir,
            logs_dir=logs_dir,
            session_db_path=session_db_path,
            log_level=os.getenv("SUPERVISOR_LOG_LEVEL", "INFO"),
            target_project_configured=bool(target_raw),
            agent_session_id=os.getenv("AGENT_SESSION_ID"),
        )

    def with_target(self, target_project_path: Path) -> "SupervisorConfig":
        """Create a new config with a runtime-provided target path."""
        return SupervisorConfig(
            supervisor_home=self.supervisor_home,
            target_project_path=target_project_path.expanduser().resolve(),
            state_dir=self.state_dir,
            checkpoints_dir=self.checkpoints_dir,
            logs_dir=self.logs_dir,
            session_db_path=self.session_db_path,
            log_level=self.log_level,
            target_project_configured=True,
            agent_session_id=self.agent_session_id,
        )

    def with_session_id(self, session_id: str) -> "SupervisorConfig":
        return SupervisorConfig(
            supervisor_home=self.supervisor_home,
            target_project_path=self.target_project_path,
            state_dir=self.state_dir,
            checkpoints_dir=self.checkpoints_dir,
            logs_dir=self.logs_dir,
            session_db_path=self.session_db_path,
            log_level=self.log_level,
            target_project_configured=self.target_project_configured,
            agent_session_id=session_id,
        )

    def resolved_agent_session_id(self) -> str:
        if self.agent_session_id:
            return self._normalize_session_id(self.agent_session_id)
        if not self.target_project_configured:
            raise ValueError(
                "agent_session_id requires TARGET_PROJECT_PATH or explicit --session-id."
            )
        return self._derive_session_id_from_target(self.target_project_path)

    @staticmethod
    def _normalize_session_id(session_id: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", session_id.strip())
        if not normalized:
            raise ValueError("agent_session_id is empty after normalization.")
        return normalized[:120]

    @classmethod
    def _derive_session_id_from_target(cls, target_project_path: Path) -> str:
        resolved = target_project_path.expanduser().resolve()
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", resolved.name.lower()).strip("-")
        slug = slug or "target"
        digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:12]
        return cls._normalize_session_id(f"agent-{slug}-{digest}")

    def validate(self) -> None:
        """Fail fast on invalid filesystem paths."""
        if not self.supervisor_home.exists():
            raise FileNotFoundError(
                f"Supervisor home not found: {self.supervisor_home}"
            )

        if not self.target_project_configured:
            raise ValueError(
                "TARGET_PROJECT_PATH is not configured. Use .env or --target-project."
            )
