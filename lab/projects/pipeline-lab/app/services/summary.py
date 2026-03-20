from typing import Any


def summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run.get("id"),
        "domain": run.get("domain"),
        "stage": run.get("stage"),
        "started_at": run.get("started_at"),
    }
