import json

from app.services.runner import Runner
from app.storage.runs_store import RunsStore


def test_runner_starts_and_records(tmp_path):
    store = RunsStore(path=tmp_path / "runs.json")
    runner = Runner(store=store)
    record = runner.start_run("python")
    assert record["domain"] == "python"
    assert record["stage"] == "source_policy"
    assert len(store.list_runs()) == 1


def test_runner_executes_stage(tmp_path):
    store = RunsStore(path=tmp_path / "runs.json")
    runner = Runner(store=store, run_dir_base=tmp_path / "runs")
    record = runner.start_run("python")
    summary = runner.execute_stage(record["id"])
    assert summary["final_status"] == "completed"
    assert store.get_run(record["id"])["status"] == "completed"
    assert (tmp_path / "runs" / record["id"] / "summary.json").exists()


def test_runner_executes_two_stages(tmp_path):
    store = RunsStore(path=tmp_path / "runs.json")
    runner = Runner(store=store, run_dir_base=tmp_path / "runs")
    record = runner.start_run("python")
    summary1 = runner.execute_stage(record["id"])
    assert summary1["stage"] == "source_policy"
    summary2 = runner.execute_stage(record["id"])
    assert summary2["stage"] == "source_manifest"
    run_record = store.get_run(record["id"])
    assert run_record["stage"] == "corpus_freeze"
    summary_path = tmp_path / "runs" / record["id"] / "summary.json"
    summary_data = json.loads(summary_path.read_text())
    assert len(summary_data["history"]) == 2


def test_runner_blocks_when_gate_fails(tmp_path):
    store = RunsStore(path=tmp_path / "runs.json")
    runner = Runner(store=store, run_dir_base=tmp_path / "runs")
    record = runner.start_run("python")
    store.update_run(record["id"], stage="chunking", metadata={})
    summary = runner.execute_stage(record["id"])
    assert summary["final_status"] == "blocked"
    assert store.get_run(record["id"])["status"] == "blocked"
    assert summary["gate"]["allowed"] is False
