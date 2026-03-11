from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_local_asr_runtime() -> dict:
    enabled = bool(settings.local_asr_enabled or settings.transcription_local_enabled)
    model = str(settings.transcription_local_model or "local-asr-baseline")
    timeout_ms = int(settings.local_asr_timeout_ms)
    return {
        "enabled": enabled,
        "available": enabled,
        "model": model,
        "timeout_ms": timeout_ms,
    }


def transcribe_local(text: str) -> str:
    runtime = get_local_asr_runtime()
    if not bool(runtime.get("available", False)):
        raise ValueError("local_asr_unavailable")

    output = str(text or "").strip()
    if not output:
        raise ValueError("local_asr_empty_text")

    logger.info(
        "transcription_local_ok",
        extra={
            "event": "transcription_local_ok",
            "len": len(output),
            "model": runtime.get("model"),
        },
    )
    return output
