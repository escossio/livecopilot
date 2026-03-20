import os
import base64
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_voice_output_runtime() -> dict[str, Any]:
    provider = str(settings.voice_output_provider or "external").strip().lower()
    enabled_default = bool(settings.voice_output_enabled)
    api_key_present = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return {
        "enabled_default": enabled_default,
        "provider": provider,
        "model": settings.voice_output_model,
        "api_key_present": api_key_present,
        "silent_mode_default": True,
        "voice_output_opt_in": True,
    }


def _disabled_payload(runtime: dict[str, Any], reason: str = "voice_output_disabled") -> dict[str, Any]:
    return {
        "voice_status": "disabled",
        "voice_provider": str(runtime.get("provider", "none") or "none"),
        "voice_enabled_effective": False,
        "fallback_reason": reason,
        "audio_output_available": False,
    }


def _fallback_payload(runtime: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "voice_status": "fallback_silent",
        "voice_provider": str(runtime.get("provider", "none") or "none"),
        "voice_enabled_effective": False,
        "fallback_reason": reason,
        "audio_output_available": False,
    }


def _synthesize_external(text: str, *, model: str) -> dict[str, Any]:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY ausente")

    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model=model,
        voice="alloy",
        input=text,
    )

    audio_bytes = b""
    if hasattr(response, "read"):
        audio_bytes = response.read() or b""
    elif hasattr(response, "content"):
        audio_bytes = bytes(getattr(response, "content") or b"")
    elif isinstance(response, (bytes, bytearray)):
        audio_bytes = bytes(response)

    if not audio_bytes:
        raise ValueError("tts external sem audio")

    return {
        "voice_status": "ready",
        "voice_provider": "external",
        "voice_enabled_effective": True,
        "fallback_reason": "",
        "audio_output_available": True,
        "audio_bytes": len(audio_bytes),
        "audio_base64": base64.b64encode(audio_bytes).decode("ascii"),
        "mime_type": "audio/mpeg",
        "model": model,
    }


def synthesize_voice_output_opt_in(
    *,
    text: str,
    enabled_override: bool | None = None,
) -> dict[str, Any]:
    runtime = get_voice_output_runtime()
    enabled_effective = bool(enabled_override) if enabled_override is not None else bool(runtime.get("enabled_default", False))
    if not enabled_effective:
        return _disabled_payload(runtime)

    provider = str(runtime.get("provider", "external") or "external")
    if provider == "none":
        return _disabled_payload(runtime, reason="voice_output_provider_none")
    if provider != "external":
        logger.info("voice_output_provider_unavailable", extra={"event": "voice_output_provider_unavailable", "provider": provider})
        return _fallback_payload(runtime, reason="voice_output_provider_unavailable")
    if not bool(runtime.get("api_key_present", False)):
        return _fallback_payload(runtime, reason="voice_output_missing_api_key")
    if not str(text or "").strip():
        return _fallback_payload(runtime, reason="voice_output_empty_text")

    try:
        payload = _synthesize_external(str(text), model=str(runtime.get("model", "gpt-4o-mini-tts") or "gpt-4o-mini-tts"))
        logger.info(
            "voice_output_ready",
            extra={
                "event": "voice_output_ready",
                "provider": payload.get("voice_provider", "external"),
                "audio_bytes": int(payload.get("audio_bytes", 0) or 0),
            },
        )
        return payload
    except Exception as exc:
        logger.info(
            "voice_output_fallback_silent",
            extra={"event": "voice_output_fallback_silent", "provider": provider, "error": str(exc)[:180]},
        )
        return _fallback_payload(runtime, reason="voice_output_external_error")


def synthesize_voice_output_realtime_controlled(
    *,
    text: str,
    response_stage: str,
    should_wait_more: bool,
    enabled_override: bool | None = None,
) -> dict[str, Any]:
    runtime = get_voice_output_runtime()
    stage = str(response_stage or "").strip().lower()
    if stage != "final" or bool(should_wait_more):
        payload = _disabled_payload(runtime, reason="voice_output_waiting_for_final_context")
        payload["voice_controlled_by_stage"] = True
        payload["response_stage"] = stage or "unknown"
        payload["should_wait_more"] = bool(should_wait_more)
        return payload

    payload = synthesize_voice_output_opt_in(
        text=text,
        enabled_override=enabled_override,
    )
    payload["voice_controlled_by_stage"] = True
    payload["response_stage"] = "final"
    payload["should_wait_more"] = False
    return payload
