from app.services.state import ConversationState
from app.core.logging import get_logger

logger = get_logger(__name__)


def update_context(state: ConversationState, speaker: str, text: str, metadata: dict | None = None) -> None:
    state.add_turn(speaker, text, metadata=metadata)
    logger.info("context_update", extra={"event": "context_update", "turns": len(state.transcript)})
