import json
from pathlib import Path
from typing import Any

from app.core import config


class RunsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config.RUNS_STORE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def _read(self) -> list[Any]:
        return json.loads(self.path.read_text())

    def _write(self, data: list[Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2))

    def save_run(self, payload: dict) -> dict:
        data = self._read()
        data.append(payload)
        self._write(data)
        return payload

    def list_runs(self) -> list[Any]:
        return self._read()

    def get_run(self, run_id: str) -> dict | None:
        for entry in self._read():
            if entry.get("id") == run_id:
                return entry
        return None

    def update_run(
        self,
        run_id: str,
        *,
        stage: str | None = None,
        status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict | None:
        data = self._read()
        updated: dict | None = None
        for entry in data:
            if entry.get("id") != run_id:
                continue
            if stage is not None:
                entry["stage"] = stage
            if status is not None:
                entry["status"] = status
            if metadata:
                entry.setdefault("metadata", {})
                entry["metadata"].update(metadata)
            updated = entry
            break
        if updated is not None:
            self._write(data)
        return updated
