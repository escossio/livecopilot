from app.core.logging import get_logger

logger = get_logger(__name__)


def normalize_input(text: str) -> str:
    cleaned = text.strip()
    logger.info("ingestion_normalize", extra={"event": "ingestion_normalize", "len": len(cleaned)})
    return cleaned
