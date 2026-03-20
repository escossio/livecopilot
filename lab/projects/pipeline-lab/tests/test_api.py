from app.api import routes
from app.services.runner import Runner
from app.storage.runs_store import RunsStore


def test_api_routes_use_custom_store(tmp_path):
    store = RunsStore(path=tmp_path / "runs.json")
    runner = Runner(store=store)

    routes.store = store
    routes.runner = runner

    created = routes.create_run("terraform")
    assert created["domain"] == "terraform"
    runs = routes.get_runs()
    assert len(runs) == 1
