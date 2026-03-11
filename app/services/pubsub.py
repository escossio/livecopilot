from typing import Set
from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketHub:
    def __init__(self) -> None:
        self.connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        self.connections.add(websocket)
        logger.info("ws_connect", extra={"event": "ws_connect", "connections": len(self.connections)})

    async def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)
        logger.info("ws_disconnect", extra={"event": "ws_disconnect", "connections": len(self.connections)})

    async def broadcast(self, payload: dict) -> None:
        for ws in list(self.connections):
            try:
                await ws.send_json(payload)
            except Exception:
                self.connections.discard(ws)
        logger.info("ws_broadcast", extra={"event": "ws_broadcast", "connections": len(self.connections)})
