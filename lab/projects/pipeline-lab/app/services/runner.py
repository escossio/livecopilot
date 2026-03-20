import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core import config
from app.core.paths import DATA_DIR
from app.services.stage_gate import StageGate
from app.storage.runs_store import RunsStore


@dataclass
class RunRecord:
    id: str
    domain: str
    stage: str
    status: str
    started_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Runner:
    def __init__(self, store: RunsStore | None = None, run_dir_base: Path | None = None):
        self.store = store or RunsStore()
        self.gate = StageGate()
        self.run_dir_base = run_dir_base or DATA_DIR
        self.run_dir_base.mkdir(parents=True, exist_ok=True)

    def start_run(self, domain: str, stage: str | None = None) -> dict:
        stage = stage or config.PIPELINE_STAGES[0]
        record = RunRecord(
            id=str(uuid4()),
            domain=domain,
            stage=stage,
            status="created",
            started_at=datetime.utcnow().isoformat() + "Z",
        )
        return self.store.save_run(asdict(record))

    def can_advance(self, current: str, next_stage: str) -> bool:
        return self.gate.can_advance(current, next_stage)

    def execute_stage(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        if run is None:
            raise ValueError(f"run not found: {run_id}")
        stage = run.get("stage")
        if stage not in config.PIPELINE_STAGES:
            raise ValueError(f"unknown stage: {stage}")
        previous_status = run.get("status") or "unknown"
        self.store.update_run(run_id, status="running", metadata={"last_status": previous_status})

        metadata = dict(run.get("metadata") or {})
        history = list(metadata.get("executed_stages", []))
        allowed, gate_reason = self.gate.check(stage, history)

        run_dir = self.run_dir_base / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        artifacts_path = run_dir / "artifacts.json"
        artifacts: list[dict[str, Any]] = []
        if artifacts_path.exists():
            raw = artifacts_path.read_text(encoding="utf-8").strip()
            if raw:
                artifacts = json.loads(raw)

        executed_at = datetime.utcnow().isoformat() + "Z"
        log_path = run_dir / "log.txt"

        if not allowed:
            result_text = f"gate blocked: {gate_reason}"
            entry = {
                "stage": stage,
                "timestamp": executed_at,
                "result": result_text,
                "blocked": True,
                "gate": {"checked": stage, "allowed": False, "reason": gate_reason},
            }
            history.append(entry)
            metadata["executed_stages"] = history
            metadata["last_status"] = "blocked"
            metadata["gate_blocked_reason"] = gate_reason
            artifacts.append(
                {
                    "timestamp": executed_at,
                    "stage": stage,
                    "result": result_text,
                    "blocked": True,
                    "gate_reason": gate_reason,
                }
            )
            artifacts_path.write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(f"{executed_at} - gate blocked for {stage}: {gate_reason}\n")
            summary = {
                "run_id": run_id,
                "domain": run.get("domain"),
                "stage": stage,
                "previous_status": previous_status,
                "final_status": "blocked",
                "executed_at": executed_at,
                "result": result_text,
                "gate": {"checked": stage, "allowed": False, "reason": gate_reason},
                "history": history,
            }
            summary_path = run_dir / "summary.json"
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            run_stage = stage
            self.store.update_run(
                run_id,
                stage=run_stage,
                status="blocked",
                metadata=metadata,
            )
            return summary

        result_text = f"executed stage {stage} at {executed_at}"
        artifact_path = run_dir / f"stage_artifact_{stage}.md"
        artifact_body = f"# Stage artifact\nRun: {run_id}\nStage: {stage}\nDomain: {run.get('domain')}\nTimestamp: {executed_at}\n\nResultado:\n- {result_text}\n"
        artifact_path.write_text(artifact_body, encoding="utf-8")

        entry = {
            "stage": stage,
            "timestamp": executed_at,
            "result": result_text,
            "artifact": str(artifact_path.relative_to(run_dir)),
            "gate": {"checked": stage, "allowed": True, "reason": gate_reason},
        }
        history.append(entry)
        metadata["executed_stages"] = history
        metadata["last_executed_stage"] = stage
        metadata["last_status"] = "completed"

        artifacts.append(
            {
                "timestamp": executed_at,
                "stage": stage,
                "result": result_text,
                "artifact": str(artifact_path.relative_to(run_dir)),
                "blocked": False,
            }
        )
        artifacts_path.write_text(json.dumps(artifacts, indent=2), encoding="utf-8")

        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(f"{executed_at} - {result_text}\n")

        summary = {
            "run_id": run_id,
            "domain": run.get("domain"),
            "stage": stage,
            "previous_status": previous_status,
            "final_status": "completed",
            "executed_at": executed_at,
            "result": result_text,
            "artifact": str(artifact_path.relative_to(run_dir)),
            "gate": entry["gate"],
            "history": history,
        }
        summary_path = run_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        stage_index = config.PIPELINE_STAGES.index(stage)
        next_stage = config.PIPELINE_STAGES[stage_index + 1] if stage_index + 1 < len(config.PIPELINE_STAGES) else stage
        self.store.update_run(run_id, stage=next_stage, status="completed", metadata=metadata)
        return summary
