from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class ArtifactRecord:
    domain: str
    stage: str
    path: str
    created_at: str
    meta: dict[str, Any] = None


class ArtifactRegistry:
    def __init__(self):
        self._records: list[ArtifactRecord] = []

    def register(self, domain: str, stage: str, path: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        record = ArtifactRecord(
            domain=domain,
            stage=stage,
            path=path,
            created_at=datetime.utcnow().isoformat() + "Z",
            meta=meta,
        )
        self._records.append(record)
        return asdict(record)

    def list(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self._records]
