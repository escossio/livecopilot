import os
from typing import Any

from app.core.config import settings


def get_realtime_runtime() -> dict[str, Any]:
    api_key_present = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return {
        "enabled": bool(settings.realtime_api_enabled),
        "provider": "openai_realtime",
        "api_key_present": api_key_present,
        "model": str(settings.realtime_api_model or "gpt-realtime-mini").strip(),
        "voice": str(settings.realtime_api_voice or "alloy").strip(),
        "language": str(settings.realtime_api_language or "pt").strip(),
        "transcription_model": str(settings.realtime_api_transcription_model or "gpt-4o-mini-transcribe").strip(),
        "instructions": str(settings.realtime_api_prompt or "").strip(),
        "webrtc_url": "https://api.openai.com/v1/realtime/calls",
    }


def _build_mode_instructions(mode: str) -> str:
    runtime = get_realtime_runtime()
    base = str(runtime.get("instructions", "") or "").strip()
    mode_clean = str(mode or "generic").strip().lower()
    if mode_clean == "interview":
        extra = " Priorize respostas curtas de entrevista, com uma linha principal e no maximo dois pontos de apoio."
    elif mode_clean == "study":
        extra = " Priorize explicacoes curtas, conceituais e com um proximo passo de estudo."
    else:
        extra = " Priorize respostas curtas, claras e utilitarias."
    return (base + extra).strip()


def create_realtime_client_secret(*, mode: str = "generic") -> dict[str, Any]:
    from openai import OpenAI

    runtime = get_realtime_runtime()
    if not bool(runtime.get("enabled", False)):
        raise ValueError("Realtime API desabilitada")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY ausente")

    client = OpenAI(api_key=api_key)
    response = client.realtime.client_secrets.create(
        expires_after={
            "anchor": "created_at",
            "seconds": 600,
        },
        session={
            "type": "realtime",
            "model": str(runtime.get("model", "gpt-realtime-mini") or "gpt-realtime-mini"),
            "instructions": _build_mode_instructions(mode),
            "output_modalities": ["audio"],
            "max_output_tokens": 1024,
            "audio": {
                "input": {
                    "transcription": {
                        "model": str(runtime.get("transcription_model", "gpt-4o-mini-transcribe") or "gpt-4o-mini-transcribe"),
                        "language": str(runtime.get("language", "pt") or "pt"),
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "create_response": True,
                        "interrupt_response": True,
                    },
                },
                "output": {
                    "voice": str(runtime.get("voice", "alloy") or "alloy"),
                },
            },
        },
    )
    session_payload = response.session.model_dump(mode="json") if hasattr(response.session, "model_dump") else {}
    return {
        "client_secret": str(response.value),
        "expires_at": int(response.expires_at),
        "session": session_payload,
        "webrtc_url": str(runtime.get("webrtc_url", "")),
        "model": str(runtime.get("model", "")),
        "voice": str(runtime.get("voice", "")),
        "language": str(runtime.get("language", "")),
        "transcription_model": str(runtime.get("transcription_model", "")),
        "provider": str(runtime.get("provider", "openai_realtime")),
    }
