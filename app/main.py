import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.api.routes import router as api_router
from app.services.state import ConversationState
from app.services.pubsub import WebSocketHub
from app.services.audio_capture import get_audio_capture

logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "payload invalido"
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
        detail = str(first.get("msg", "")).strip()
        if loc and detail:
            message = f"payload invalido: {loc} {detail}"
        elif detail:
            message = f"payload invalido: {detail}"
    return JSONResponse(status_code=422, content={"status": "error", "error": message})

PROJECT_STATUS_STATE_PATH = Path(__file__).resolve().parent.parent / "docs" / "project_status_state.json"

state = ConversationState()
hub = WebSocketHub()
audio_capture = get_audio_capture()

@app.on_event("startup")
async def on_startup():
    logger.info(
        "startup",
        extra={"event": "startup", "capture_mode": settings.capture_mode},
    )
    audio_capture.start()

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("shutdown", extra={"event": "shutdown"})
    audio_capture.stop()

@app.get("/project-status-data")
async def project_status_data():
    if not PROJECT_STATUS_STATE_PATH.exists():
        return JSONResponse(status_code=404, content={"status": "error", "error": "project_status_state.json nao encontrado"})
    try:
        payload = json.loads(PROJECT_STATUS_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return JSONResponse(status_code=500, content={"status": "error", "error": "falha ao ler project_status_state.json"})
    if not isinstance(payload, dict):
        return JSONResponse(status_code=500, content={"status": "error", "error": "project_status_state.json invalido"})
    return JSONResponse(content=payload)

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    if not settings.ws_enabled:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    await hub.connect(websocket)
    try:
        # Send initial snapshot
        await websocket.send_json(state.snapshot())
        while True:
            message = await websocket.receive_text()
            logger.info("ws_message", extra={"event": "ws_message", "message": message})
            # Optional future control messages can be handled here
    except WebSocketDisconnect:
        await hub.disconnect(websocket)
        logger.info("ws_disconnect", extra={"event": "ws_disconnect"})

# Dependency container for routes
app.state.conversation_state = state
app.state.ws_hub = hub
app.state.audio_capture = audio_capture
app.state.realtime_sessions = {}
