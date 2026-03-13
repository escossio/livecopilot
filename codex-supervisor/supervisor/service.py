"""Stable service interface for external orchestrators (e.g. custom GPT)."""

from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from .config import SupervisorConfig
from .state_store import StateStore
from .workflow import SupervisorWorkflow


class SupervisorService:
    """Small facade over workflow/state for stable external integration."""

    def __init__(self, config: SupervisorConfig) -> None:
        self.config = config
        self.workflow = SupervisorWorkflow(config)
        self.state = StateStore(config)
        self._execution_lock = Lock()
        self._jobs_lock = Lock()
        self._jobs_dir = self.config.state_dir / "jobs"
        self._jobs: dict[str, dict[str, Any]] = {}
        self._job_timeout_seconds = self._load_job_timeout_seconds()
        self._blocked_target_paths = {
            Path("/lab/projects").resolve(),
            Path("/lab").resolve(),
        }
        self._default_target_raw = os.getenv("SUPERVISOR_DEFAULT_TARGET_PROJECT_PATH", "").strip()
        self._default_target_path = self._parse_target_path_or_none(self._default_target_raw)
        self._load_persisted_jobs()

    def initialize(self) -> None:
        self.workflow.initialize()
        self._jobs_dir.mkdir(parents=True, exist_ok=True)

    def get_last_action(self) -> dict[str, object]:
        self.state.ensure_defaults()
        return self.state.read_last_action_payload()

    def get_next_step(self) -> str:
        self.state.ensure_defaults()
        return self.state.read_next_step()

    def get_status(self) -> dict[str, object]:
        self.state.ensure_defaults()
        last_action = self.state.read_last_action_payload()
        can_continue = True
        continue_reason: str | None = None
        try:
            self.state.load_last_action_for_continue()
        except Exception as exc:
            can_continue = False
            continue_reason = str(exc)

        blocked_target: Path | None = None
        if self.config.target_project_configured:
            blocked_target = self._blocked_match(self.config.target_project_path)
        elif self._default_target_path is not None:
            blocked_target = self._blocked_match(self._default_target_path)

        return {
            "service": "codex-supervisor",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_project_configured": self.config.target_project_configured,
            "target_project_path": (
                str(self.config.target_project_path)
                if self.config.target_project_configured
                else None
            ),
            "target_default_configured": bool(self._default_target_raw),
            "target_default_path": (
                str(self._default_target_path) if self._default_target_path is not None else None
            ),
            "target_path_is_blocked": blocked_target is not None,
            "last_status": last_action.get("status"),
            "codex_thread_id": last_action.get("codex_thread_id"),
            "codex_continue_mode": last_action.get("codex_continue_mode"),
            "codex_continue_status": last_action.get("codex_continue_status"),
            "deploy_profile": self._deploy_profile(),
            "continue_strict": self._continue_strict_enabled(),
            "last_action_status": last_action.get("status"),
            "last_action_timestamp": last_action.get("timestamp"),
            "can_continue": can_continue,
            "continue_reason": continue_reason,
        }

    def run_once(self) -> dict[str, object]:
        with self._execution_lock:
            return self._run_once_unlocked()

    def run_once_with_overrides(
        self,
        *,
        target_project_path: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, object]:
        with self._execution_lock:
            return self._run_once_with_overrides_unlocked(
                target_project_path=target_project_path,
                session_id=session_id,
            )

    def _run_once_with_overrides_unlocked(
        self,
        *,
        target_project_path: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, object]:
        effective_workflow = self.workflow
        if target_project_path is not None or session_id is not None:
            effective_config = self.config
            if target_project_path is not None:
                effective_config = effective_config.with_target(Path(target_project_path))
            if session_id is not None:
                effective_config = effective_config.with_session_id(session_id)
            effective_workflow = SupervisorWorkflow(effective_config)
        action = self._run_with_timeout(effective_workflow.run_once())
        return asdict(action)

    def continue_run(self) -> dict[str, object]:
        with self._execution_lock:
            return self._continue_run_unlocked()

    def _run_once_unlocked(self) -> dict[str, object]:
        action = self._run_with_timeout(self.workflow.run_once())
        return asdict(action)

    def _continue_run_unlocked(self) -> dict[str, object]:
        action = self._run_with_timeout(self.workflow.continue_run())
        return asdict(action)

    def enqueue_run_once(
        self,
        *,
        target_project_path: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, object]:
        resolved_target = self._resolve_run_once_target(target_project_path)
        return self._enqueue_job(
            kind="run_once",
            payload={
                "target_project_path": resolved_target,
                "session_id": session_id,
            },
        )

    def enqueue_continue_run(self) -> dict[str, object]:
        return self._enqueue_job(kind="continue_run", payload={})

    def list_jobs(self, limit: int = 20) -> dict[str, object]:
        safe_limit = min(max(limit, 1), 200)
        with self._jobs_lock:
            ordered_jobs = sorted(
                self._jobs.values(),
                key=lambda job: str(job.get("created_at", "")),
                reverse=True,
            )
            jobs = [self._job_summary(job) for job in ordered_jobs[:safe_limit]]
        return {"jobs": jobs}

    def get_job(self, job_id: str) -> dict[str, object] | None:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            return self._job_summary(job) if job is not None else None

    def get_job_result(self, job_id: str) -> dict[str, object] | None:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            status = str(job.get("status", "queued"))
            result = job.get("result")
            error_message = job.get("error")

        if status == "done" and isinstance(result, dict):
            return result
        if status == "failed":
            return {
                "ready": True,
                "job_id": job_id,
                "status": status,
                "error": error_message,
                "last_action": self.get_last_action(),
                "next_step": self.get_next_step(),
            }
        return {
            "ready": False,
            "job_id": job_id,
            "status": status,
        }

    def get_audit_tail(self, limit: int = 20) -> dict[str, object]:
        safe_limit = min(max(limit, 1), 50)
        audit_file = self.config.logs_dir / "codex_mcp_audit.jsonl"
        if not audit_file.exists():
            return {"audit_enabled": False, "entries": []}

        lines = audit_file.read_text(encoding="utf-8").splitlines()
        entries: list[dict[str, Any]] = []
        for raw_line in lines[-safe_limit:]:
            try:
                payload = json.loads(raw_line)
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            entries.append(
                {
                    "timestamp": payload.get("timestamp"),
                    "event": payload.get("event"),
                    "status": payload.get("status"),
                    "summary": payload.get("summary"),
                }
            )
        return {"audit_enabled": True, "entries": entries}

    @staticmethod
    def _deploy_profile() -> str:
        profile = os.getenv("SUPERVISOR_DEPLOY_PROFILE", "compat").strip().lower()
        return profile if profile in {"compat", "production"} else "compat"

    def _continue_strict_enabled(self) -> bool:
        strict_env = os.getenv("SUPERVISOR_CONTINUE_STRICT", "0") in {"1", "true", "TRUE"}
        return strict_env or self._deploy_profile() == "production"

    def _load_job_timeout_seconds(self) -> int:
        raw_timeout = os.getenv("SUPERVISOR_JOB_TIMEOUT_SECONDS", "180")
        try:
            timeout = int(raw_timeout)
        except Exception:
            timeout = 180
        return max(timeout, 1)

    @staticmethod
    def _parse_target_path_or_none(value: str | None) -> Path | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        return Path(raw).expanduser().resolve()

    def _blocked_match(self, target_path: Path) -> Path | None:
        resolved = target_path.expanduser().resolve()
        for blocked in self._blocked_target_paths:
            if resolved == blocked:
                return blocked
        return None

    def _resolve_run_once_target(self, target_project_path: str | None) -> str:
        target_raw = (target_project_path or "").strip()
        if not target_raw:
            target_raw = self._default_target_raw

        if not target_raw:
            raise ValueError(
                "target_project_path is required. Send it in POST /run-once or set "
                "SUPERVISOR_DEFAULT_TARGET_PROJECT_PATH."
            )

        target_path = Path(target_raw).expanduser().resolve()
        blocked_path = self._blocked_match(target_path)
        if blocked_path is not None:
            raise ValueError(
                f"target_project_path '{target_path}' is blocked. "
                "Use a project directory (example: /lab/projects/livecopilot)."
            )
        if not target_path.exists() or not target_path.is_dir():
            raise ValueError(
                f"target_project_path '{target_path}' does not exist or is not a directory."
            )

        return str(target_path)

    def _run_with_timeout(self, awaitable: Any) -> Any:
        try:
            return asyncio.run(asyncio.wait_for(awaitable, timeout=self._job_timeout_seconds))
        except asyncio.TimeoutError as exc:
            raise TimeoutError("timeout") from exc

    def _enqueue_job(self, *, kind: str, payload: dict[str, Any]) -> dict[str, object]:
        self.state.ensure_layout()
        self._jobs_dir.mkdir(parents=True, exist_ok=True)

        active_job_id, active_job_status = self._find_active_job()
        if active_job_id is not None:
            raise ValueError(
                "Another job is already in progress "
                f"(job_id={active_job_id}, status={active_job_status}). "
                "Wait for completion before enqueueing a new run."
            )

        job_id = str(uuid.uuid4())
        now = self._now_iso()
        job: dict[str, Any] = {
            "job_id": job_id,
            "kind": kind,
            "status": "queued",
            "created_at": now,
            "started_at": None,
            "finished_at": None,
            "error": None,
            "last_action_timestamp": None,
            "payload": payload,
            "result": None,
        }

        with self._jobs_lock:
            self._jobs[job_id] = job
        self._persist_job(job)

        worker = threading.Thread(
            target=self._run_job_worker,
            kwargs={"job_id": job_id},
            name=f"supervisor-job-{job_id[:8]}",
            daemon=True,
        )
        worker.start()

        return {
            "accepted": True,
            "job_id": job_id,
            "status": "queued",
        }

    def _find_active_job(self) -> tuple[str | None, str | None]:
        with self._jobs_lock:
            for job_id, job in self._jobs.items():
                status = str(job.get("status", ""))
                if status in {"queued", "running"}:
                    return job_id, status
        return None, None

    def _run_job_worker(self, *, job_id: str) -> None:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            kind = str(job.get("kind", ""))
            payload = job.get("payload") if isinstance(job.get("payload"), dict) else {}

        result: dict[str, object] | None = None
        error_message: str | None = None
        try:
            with self._execution_lock:
                with self._jobs_lock:
                    job = self._jobs.get(job_id)
                    if job is None:
                        return
                    job["status"] = "running"
                    job["started_at"] = self._now_iso()
                    job["error"] = None
                    self._persist_job(job)

                if kind == "continue_run":
                    result = self._continue_run_unlocked()
                else:
                    result = self._run_once_with_overrides_unlocked(
                        target_project_path=self._optional_str(payload.get("target_project_path")),
                        session_id=self._optional_str(payload.get("session_id")),
                    )
        except TimeoutError:
            error_message = "timeout"
        except Exception as exc:
            error_message = str(exc)

        last_action_timestamp = self._extract_last_action_timestamp()

        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job["finished_at"] = self._now_iso()
            job["last_action_timestamp"] = last_action_timestamp
            if error_message is None:
                job["status"] = "done"
                job["error"] = None
                job["result"] = result
            else:
                job["status"] = "failed"
                job["error"] = error_message
                job["result"] = None
            self._persist_job(job)

    def _load_persisted_jobs(self) -> None:
        self.state.ensure_layout()
        self._jobs_dir.mkdir(parents=True, exist_ok=True)
        now = self._now_iso()
        for path in sorted(self._jobs_dir.glob("*.json"), key=lambda item: item.name):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            raw_job_id = payload.get("job_id")
            if not isinstance(raw_job_id, str) or not raw_job_id.strip():
                continue
            if payload.get("status") in {"queued", "running"}:
                payload["status"] = "failed"
                payload["error"] = "interrupted_by_restart"
                payload["finished_at"] = payload.get("finished_at") or now
                try:
                    path.write_text(
                        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
                        encoding="utf-8",
                    )
                except Exception:
                    pass
            self._jobs[raw_job_id] = payload

    def _persist_job(self, job: dict[str, Any]) -> None:
        job_id = str(job.get("job_id", "")).strip()
        if not job_id:
            return
        target_file = self._jobs_dir / f"{job_id}.json"
        target_file.write_text(
            json.dumps(job, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def _extract_last_action_timestamp(self) -> str | None:
        try:
            payload = self.state.read_last_action_payload()
        except Exception:
            return None
        raw_timestamp = payload.get("timestamp")
        if isinstance(raw_timestamp, str) and raw_timestamp.strip():
            return raw_timestamp
        return None

    @staticmethod
    def _job_summary(job: dict[str, Any]) -> dict[str, object]:
        return {
            "job_id": job.get("job_id"),
            "kind": job.get("kind"),
            "status": job.get("status"),
            "created_at": job.get("created_at"),
            "started_at": job.get("started_at"),
            "finished_at": job.get("finished_at"),
            "error": job.get("error"),
            "last_action_timestamp": job.get("last_action_timestamp"),
        }

    @staticmethod
    def _optional_str(value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        clean_value = value.strip()
        return clean_value if clean_value else None

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
