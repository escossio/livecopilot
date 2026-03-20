import os
import time

from app.core.config import settings
from app.core.logging import get_logger
from app.services.transcription_local import get_local_asr_runtime, transcribe_local

logger = get_logger(__name__)


def transcribe_mock(text: str) -> str:
    logger.info("transcription_mock", extra={"event": "transcription_mock", "len": len(text)})
    return text


def transcribe_text_input_with_trace(text: str) -> dict:
    started = time.monotonic()
    output = transcribe_mock(text)
    return {
        "text": output,
        "provider_selected": "text",
        "provider_used": "mock",
        "fallback_used": False,
        "fallback_reason": "",
        "transcription_latency_ms": int((time.monotonic() - started) * 1000),
        "configured_provider": "text",
        "effective_provider": "mock",
        "local_available": False,
        "local_model": None,
        "local_timeout_ms": 0,
        "transcription_preference": "text",
        "external_preferred": False,
        "external_available": False,
        "external_model": "",
    }


def get_transcription_runtime() -> dict:
    provider = (settings.transcription_provider or "external").strip().lower()
    preference = (settings.transcription_preference or "").strip().lower()
    api_key_present = bool(os.getenv("OPENAI_API_KEY", "").strip())
    local_runtime = get_local_asr_runtime()
    local_available = bool(local_runtime.get("available", False))
    external_available = api_key_present

    provider_selected = provider
    if preference in {"local", "external", "auto"}:
        if preference == "auto":
            if local_available:
                provider_selected = "local"
            elif external_available:
                provider_selected = "external"
            else:
                provider_selected = "mock"
        else:
            provider_selected = preference

    return {
        "provider": provider,
        "provider_selected": provider_selected,
        "transcription_preference": preference or "none",
        "local_available": local_available,
        "local_model": local_runtime.get("model"),
        "local_timeout_ms": int(local_runtime.get("timeout_ms", 1200) or 1200),
        "external_preferred": provider == "external",
        "external_available": external_available,
        "external_model": settings.transcription_external_model,
    }


def _transcribe_external(text: str) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY ausente")

    client = OpenAI(api_key=api_key)
    model = settings.transcription_external_model
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "Normalize transcript text from speech. Keep original language and meaning. Return only the transcript text.",
            },
            {"role": "user", "content": text},
        ],
    )

    output_text = (getattr(response, "output_text", None) or "").strip()
    if not output_text:
        raise ValueError("resposta vazia do modelo externo")
    logger.info(
        "transcription_external_ok",
        extra={"event": "transcription_external_ok", "len": len(output_text), "model": model},
    )
    return output_text


def transcribe_with_trace(text: str) -> dict:
    started = time.monotonic()
    runtime = get_transcription_runtime()
    configured_provider = str(runtime.get("provider", "external") or "external").strip().lower()
    provider_selected = str(runtime.get("provider_selected", configured_provider) or configured_provider).strip().lower()

    trace = {
        "provider_selected": provider_selected,
        "provider_used": "mock",
        "fallback_used": False,
        "fallback_reason": "",
        "transcription_latency_ms": 0,
        "configured_provider": configured_provider,
        "effective_provider": "mock",
        "local_available": bool(runtime.get("local_available", False)),
        "local_model": runtime.get("local_model"),
        "local_timeout_ms": int(runtime.get("local_timeout_ms", 1200) or 1200),
        "transcription_preference": runtime.get("transcription_preference", "none"),
        "external_preferred": bool(runtime.get("external_preferred", False)),
        "external_available": bool(runtime.get("external_available", False)),
        "external_model": runtime.get("external_model"),
    }

    def _finalize(output: str) -> dict:
        trace["effective_provider"] = trace.get("provider_used", "mock")
        trace["transcription_latency_ms"] = int((time.monotonic() - started) * 1000)
        return {"text": output, **trace}

    if provider_selected == "mock":
        output = transcribe_mock(text)
        return _finalize(output)

    if provider_selected == "local":
        local_timeout_ms = int(runtime.get("local_timeout_ms", 1200) or 1200)
        try:
            output = transcribe_local(text)
            elapsed_ms = int((time.monotonic() - started) * 1000)
            if local_timeout_ms > 0 and elapsed_ms > local_timeout_ms:
                raise TimeoutError("local_asr_timeout")
            trace["provider_used"] = "local"
            return _finalize(output)
        except Exception as exc:
            logger.info(
                "transcription_local_fallback",
                extra={"event": "transcription_local_fallback", "provider": provider_selected, "error": str(exc)[:180]},
            )
            trace["fallback_used"] = True
            raw_error = str(exc).strip().lower()
            if "timeout" in raw_error:
                trace["fallback_reason"] = "local_timeout"
            elif "unavailable" in raw_error:
                trace["fallback_reason"] = "local_unavailable"
            else:
                trace["fallback_reason"] = "local_error"
            if bool(runtime.get("external_available", False)):
                try:
                    output = _transcribe_external(text)
                    trace["provider_used"] = "external"
                    return _finalize(output)
                except Exception as external_exc:
                    logger.info(
                        "transcription_external_fallback",
                        extra={
                            "event": "transcription_external_fallback",
                            "provider": "external",
                            "error": str(external_exc)[:180],
                        },
                    )
                    trace["fallback_reason"] = f"{trace['fallback_reason']}_external_error"
            else:
                trace["fallback_reason"] = f"{trace['fallback_reason']}_external_unavailable"
            trace["provider_used"] = "mock"
            output = transcribe_mock(text)
            return _finalize(output)

    if provider_selected != "external":
        logger.info(
            "transcription_provider_unavailable",
            extra={"event": "transcription_provider_unavailable", "provider": provider_selected},
        )
        trace["provider_used"] = "mock"
        output = transcribe_mock(text)
        trace["fallback_used"] = True
        trace["fallback_reason"] = "provider_unavailable"
        return _finalize(output)

    try:
        output = _transcribe_external(text)
        trace["provider_used"] = "external"
        return _finalize(output)
    except Exception as exc:
        logger.info(
            "transcription_external_fallback",
            extra={"event": "transcription_external_fallback", "provider": provider_selected, "error": str(exc)[:180]},
        )
        trace["provider_used"] = "mock"
        output = transcribe_mock(text)
        trace["fallback_used"] = True
        trace["fallback_reason"] = "external_error" if bool(runtime.get("external_available", False)) else "external_unavailable"
        return _finalize(output)


def transcribe_with_provider(text: str) -> str:
    payload = transcribe_with_trace(text)
    return str(payload.get("text", ""))
