from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api import routes

app = FastAPI(title="Pipeline Lab API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunCreateRequest(BaseModel):
    domain: str
    stage: str | None = None


@app.get("/api/runs")
def api_list_runs():
    return routes.get_runs()


@app.post("/api/runs")
def api_create_run(payload: RunCreateRequest):
    return routes.create_run(payload.domain, payload.stage)


@app.get("/api/runs/{run_id}")
def api_get_run(run_id: str):
    run = routes.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run não encontrada")
    return run


@app.post("/api/runs/{run_id}/next")
def api_next_stage(run_id: str):
    return routes.execute_next_stage(run_id)
