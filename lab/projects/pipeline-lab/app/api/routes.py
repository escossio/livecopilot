from typing import Any

from app.storage.runs_store import RunsStore
from app.services.runner import Runner

store = RunsStore()
runner = Runner(store=store)


def get_runs() -> list[Any]:
    return store.list_runs()


def create_run(domain: str, stage: str | None = None) -> dict[Any, Any]:
    return runner.start_run(domain, stage)


def get_run(run_id: str) -> dict[Any, Any] | None:
    return store.get_run(run_id)


def execute_run_stage(run_id: str) -> dict[str, Any]:
    return runner.execute_stage(run_id)


def execute_next_stage(run_id: str) -> dict[str, Any]:
    return runner.execute_stage(run_id)
