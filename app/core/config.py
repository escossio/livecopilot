import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    CANONICAL_ENV_FILE = Path("/etc/livecopilot-semantic.env")
    if CANONICAL_ENV_FILE.is_file():
        load_dotenv(CANONICAL_ENV_FILE)
    load_dotenv()
except Exception:
    pass


def _get_env(key: str, default: str) -> str:
    return os.getenv(key, default)


def _get_env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = _get_env("APP_NAME", "livecopilot")
    log_level: str = _get_env("LOG_LEVEL", "INFO")
    max_context_turns: int = int(_get_env("MAX_CONTEXT_TURNS", "8"))
    suggestions_limit: int = int(_get_env("SUGGESTIONS_LIMIT", "4"))
    fillers_limit: int = int(_get_env("FILLERS_LIMIT", "4"))
    quick_replies_limit: int = int(_get_env("QUICK_REPLIES_LIMIT", "4"))
    capture_mode: str = _get_env("CAPTURE_MODE", "mock")
    transcription_provider: str = _get_env("TRANSCRIPTION_PROVIDER", "external")
    transcription_preference: str = _get_env("TRANSCRIPTION_PREFERENCE", "")
    local_asr_enabled: bool = _get_env_bool("LOCAL_ASR_ENABLED", False)
    local_asr_timeout_ms: int = int(_get_env("LOCAL_ASR_TIMEOUT_MS", "1200"))
    transcription_local_enabled: bool = _get_env_bool("TRANSCRIPTION_LOCAL_ENABLED", False)
    transcription_local_model: str = _get_env("TRANSCRIPTION_LOCAL_MODEL", "local-asr-baseline")
    transcription_external_model: str = _get_env("TRANSCRIPTION_EXTERNAL_MODEL", "gpt-4o-mini")
    voice_output_enabled: bool = _get_env_bool("VOICE_OUTPUT_ENABLED", False)
    voice_output_provider: str = _get_env("VOICE_OUTPUT_PROVIDER", "external")
    voice_output_model: str = _get_env("VOICE_OUTPUT_MODEL", "gpt-4o-mini-tts")
    realtime_api_enabled: bool = _get_env_bool("REALTIME_API_ENABLED", True)
    realtime_api_model: str = _get_env("REALTIME_API_MODEL", "gpt-realtime-mini")
    realtime_api_voice: str = _get_env("REALTIME_API_VOICE", "alloy")
    realtime_api_language: str = _get_env("REALTIME_API_LANGUAGE", "pt")
    realtime_api_transcription_model: str = _get_env("REALTIME_API_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")
    realtime_api_prompt: str = _get_env(
        "REALTIME_API_PROMPT",
        "Voce e o Livecopilot. Responda em portugues do Brasil, de forma objetiva, tecnica e auditavel. "
        "Quando a pergunta estiver incompleta, reconheca que o contexto ainda esta parcial em vez de inventar detalhes.",
    )
    ws_enabled: bool = _get_env_bool("WS_ENABLED", True)
    downloads_watch_dir: str = _get_env("DOWNLOADS_WATCH_DIR", "~/Downloads")
    downloads_import_mode: str = _get_env("DOWNLOADS_IMPORT_MODE", "copy")
    downloads_normalize_names: bool = _get_env_bool("DOWNLOADS_NORMALIZE_NAMES", True)
    downloads_trigger_ingest: bool = _get_env_bool("DOWNLOADS_TRIGGER_INGEST", True)
    knowledge_debug: bool = _get_env_bool("KNOWLEDGE_DEBUG", False)


settings = Settings()
