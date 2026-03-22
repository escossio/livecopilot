from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field
import time
import re
import json
from pathlib import Path
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.core.config import settings
from app.services.knowledge_search import search_knowledge_chunks_with_debug
from app.services.knowledge_hygiene import build_knowledge_hygiene_report
from app.services.knowledge_gap_analyzer import analyze_knowledge_gap
from app.services.gap_priority_queue import get_gap_report, record_gap_analysis
from app.services.mikrotik_connector import resolve_mikrotik_query
from app.services.pipeline import process_ingest
from app.services.question_bank_action import build_question_bank_action_report
from app.services.question_bank_coverage import build_question_bank_coverage_report
from app.services.question_bank_search import search_question_bank_items_with_debug
from app.services.knowledge_search import build_context_from_results
from app.services.semantic_min_api import ingest_min_document, semantic_search
from app.services.infra_status_connector import resolve_infra_status_query
from app.services.operational_memory import append_event
from app.services.operational_skills import OPERATIONAL_SKILLS_FILE, match_operational_skill
from app.services.project_state_connector import resolve_project_state_query
from app.services.response_guidance import RESPONSE_GUIDANCE_FILE, resolve_response_guidance
from app.services.response_quality import append_response_quality_event, classify_response_quality
from app.services.state import ConversationState
from app.services.realtime_openai import create_realtime_client_secret, get_realtime_runtime
from app.services.transcription import get_transcription_runtime
from app.services.voice_output import get_voice_output_runtime, synthesize_voice_output_realtime_controlled
from app.services.voice_observability import (
    VOICE_EVENTS_FILE,
    VOICE_EVENTS_RETENTION_DAYS,
    VOICE_SESSION_ROOT,
    get_latest_voice_session_dir,
    record_voice_event,
    summarize_text,
)

router = APIRouter()
logger = get_logger(__name__)
REALTIME_MAX_SESSION_TURNS = 3
REALTIME_MAX_SESSIONS = 200
REALTIME_MAX_BUFFER_CHUNKS = 6
REALTIME_MAX_BUFFER_CHARS = 900
REALTIME_RESPOND_BUFFER_CHUNKS = 3
REALTIME_SESSION_TTL_SECONDS = 1800
REALTIME_PERSIST_DIR = Path("/lab/projects/livecopilot/var/realtime")
REALTIME_SESSIONS_FILE = REALTIME_PERSIST_DIR / "sessions.json"
REALTIME_METRICS_FILE = REALTIME_PERSIST_DIR / "realtime_metrics.ndjson"
SEMANTIC_TRACE_DIR = Path("/lab/projects/livecopilot/docs/diagnostics")


def _normalize_semantic_canary(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip().lower()
    cleaned = re.sub(r"[?!.]+$", "", cleaned).strip()
    return cleaned


def _is_semantic_canary(text: str) -> bool:
    normalized = _normalize_semantic_canary(text)
    return normalized in {
        "para que serve o arquivo de state no terraform",
        "qual a diferenca entre terraform plan e terraform apply",
        "qual a diferenca entre pod e service no kubernetes",
    }


def _write_semantic_trace(payload: dict) -> None:
    try:
        SEMANTIC_TRACE_DIR.mkdir(parents=True, exist_ok=True)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = SEMANTIC_TRACE_DIR / f"semantic_trace_run_{run_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("semantic_trace_write_failed", extra={"error": str(exc)})


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status": "error", "error": message})


def _is_blank(value: Optional[str]) -> bool:
    return not value or not value.strip()


def _handle_semantic_error(exc: Exception) -> JSONResponse:
    message = "erro interno"
    status_code = 500

    if isinstance(exc, FileNotFoundError):
        missing = getattr(exc, "filename", None) or str(exc)
        return _error_response(404, f"arquivo nao encontrado: {missing}")

    if isinstance(exc, ValueError):
        return _error_response(400, str(exc))

    try:
        import psycopg

        if isinstance(exc, psycopg.OperationalError):
            return _error_response(503, "falha de conexao com banco")
    except Exception:
        pass

    try:
        from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, RateLimitError

        if isinstance(exc, AuthenticationError):
            return _error_response(401, "falha de autenticacao na OpenAI API")
        if isinstance(exc, RateLimitError):
            return _error_response(429, "limite de requisicoes da OpenAI API excedido")
        if isinstance(exc, (APIConnectionError, APITimeoutError, APIError)):
            return _error_response(502, "falha na OpenAI API")
    except Exception:
        pass

    return _error_response(status_code, message)


def _build_operational_skill_static_payload(skill_match: dict[str, object], query: str, reason: str) -> dict:
    skill = skill_match.get("skill", {}) if isinstance(skill_match.get("skill", {}), dict) else {}
    response_policy = skill_match.get("response_policy", {}) if isinstance(skill_match.get("response_policy", {}), dict) else {}
    summary = str(response_policy.get("summary_template", "")).strip() or "Skill operacional reconhecida."
    detail = str(response_policy.get("detail_template", "")).strip()
    bullets = [detail] if detail else []
    if reason == "connector_not_integrated":
        bullets.append("Skill reconhecida no catalogo, mas ainda sem conector operacional integrado.")
    elif reason == "connector_unmatched":
        bullets.append("Skill reconhecida no roteador, mas o conector associado nao retornou match nesta consulta.")
    return {
        "matched": True,
        "intent": str(skill_match.get("intent", "")).strip(),
        "status": "info",
        "answer": summary,
        "bullets": bullets[:4],
        "knowledge_context": {
            "query": str(query or "").strip(),
            "used_search": False,
            "search_backend": "operational_skills",
            "context_used": False,
            "fallback_used": False,
            "semantic_api_ok": False,
            "semantic_duration_ms": 0,
            "result_count": 1,
            "context": summary,
            "sources": [
                {
                    "title": "operational_skills",
                    "source_file": str(OPERATIONAL_SKILLS_FILE),
                }
            ],
            "connector": "operational_skills",
            "intent": str(skill_match.get("intent", "")).strip(),
            "target": str(skill_match.get("target", "")).strip(),
            "status": "info",
            "reason": reason,
            "skill_id": str(skill.get("id", "")).strip(),
            "skill_source": str(skill_match.get("source", "")).strip(),
            "skill_operation": str(skill_match.get("action", {}).get("operation", "")).strip()
            if isinstance(skill_match.get("action", {}), dict)
            else "",
        },
    }


def _resolve_operational_skill_query(req: Request, query: str) -> dict:
    skill_match = match_operational_skill(query)
    if not bool(skill_match.get("matched", False)):
        return {"matched": False}

    skill = skill_match.get("skill", {}) if isinstance(skill_match.get("skill", {}), dict) else {}
    skill_id = str(skill.get("id", "")).strip()
    skill_source = str(skill_match.get("source", "")).strip()
    action = skill_match.get("action", {}) if isinstance(skill_match.get("action", {}), dict) else {}
    operation = str(action.get("operation", "")).strip()
    intent = str(skill_match.get("intent", "")).strip()
    target = str(skill_match.get("target", "")).strip()

    logger.info(
        "operational_skill_routed",
        extra={
            "skill_id": skill_id,
            "intent": intent,
            "target": target,
            "source": skill_source,
            "operation": operation,
        },
    )
    try:
        append_event(
            kind="project_event",
            target_type="operational_skill",
            target_name=skill_id or "unknown_skill",
            status="info",
            summary=f"skill routed intent={intent} target={target} source={skill_source} operation={operation}",
            source="operational_routing",
        )
    except Exception:
        pass

    if skill_source == "infra_status_connector":
        payload = resolve_infra_status_query(req, query)
    elif skill_source == "project_state_connector":
        payload = resolve_project_state_query(query)
    elif skill_source in {"mikrotik", "mikrotik_connector"}:
        payload = resolve_mikrotik_query(query, operation)
    else:
        payload = _build_operational_skill_static_payload(skill_match, query, reason="connector_not_integrated")

    if not bool(payload.get("matched", False)):
        payload = _build_operational_skill_static_payload(skill_match, query, reason="connector_unmatched")

    knowledge_context = payload.get("knowledge_context", {})
    if not isinstance(knowledge_context, dict):
        knowledge_context = {}
        payload["knowledge_context"] = knowledge_context
    sources = knowledge_context.get("sources")
    if not isinstance(sources, list):
        sources = []
        knowledge_context["sources"] = sources
    if not any(
        isinstance(item, dict) and str(item.get("source_file", "")).strip() == str(OPERATIONAL_SKILLS_FILE)
        for item in sources
    ):
        sources.append({"title": "operational_skills", "source_file": str(OPERATIONAL_SKILLS_FILE)})
    knowledge_context["routing_layer"] = "operational_skills"
    knowledge_context["skill_id"] = skill_id
    knowledge_context["skill_intent"] = intent
    knowledge_context["skill_target"] = target
    knowledge_context["skill_source"] = skill_source
    knowledge_context["skill_operation"] = operation
    return payload

class IngestRequest(BaseModel):
    text: str
    source: Optional[str] = None


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    source_file: Optional[str] = None
    return_context: bool = False


class SemanticIngestMinRequest(BaseModel):
    file_path: Optional[str] = None
    text: Optional[str] = None
    source_file: Optional[str] = None
    title: Optional[str] = None
    max_chunks: int = Field(default=5, ge=1, le=10)


class RealtimeRespondRequest(BaseModel):
    text: Optional[str] = Field(default=None)
    mode: Optional[str] = Field(default=None, pattern="^(interview|study|generic)$")
    conversation_id: Optional[str] = Field(default=None, max_length=128)
    voice_output_enabled: Optional[bool] = Field(default=None)


class RealtimeIngestRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=128)
    chunk_text: str = Field(..., min_length=1)
    is_final: bool = False
    mode: Optional[str] = Field(default=None, pattern="^(interview|study|generic)$")


class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: Optional[str] = Field(default=None, pattern="^(interview|study|generic)$")
    conversation_id: Optional[str] = Field(default=None, max_length=128)


class RealtimeSessionRequest(BaseModel):
    mode: Optional[str] = Field(default=None, pattern="^(interview|study|generic)$")


class VoiceEventRequest(BaseModel):
    event: str = Field(..., min_length=1, max_length=80)
    session_id: Optional[str] = Field(default=None, max_length=128)
    conversation_id: Optional[str] = Field(default=None, max_length=128)
    transcript_excerpt: Optional[str] = Field(default=None, max_length=240)
    response_summary: Optional[str] = Field(default=None, max_length=240)
    error_message: Optional[str] = Field(default=None, max_length=240)
    http_status: Optional[int] = Field(default=None, ge=100, le=599)
    source: Optional[str] = Field(default="frontend", max_length=32)
    transport: Optional[str] = Field(default=None, max_length=32)
    provider_event_type: Optional[str] = Field(default=None, max_length=120)
    ts: Optional[str] = Field(default=None, max_length=64)
    started_at: Optional[str] = Field(default=None, max_length=64)
    url: Optional[str] = Field(default=None, max_length=512)
    model: Optional[str] = Field(default=None, max_length=128)
    voice: Optional[str] = Field(default=None, max_length=64)
    secure_context: Optional[bool] = Field(default=None)
    media_devices: Optional[bool] = Field(default=None)
    get_user_media: Optional[bool] = Field(default=None)
    user_agent: Optional[str] = Field(default=None, max_length=512)
    model_config = {"extra": "allow"}


def _default_short_answer(mode: str) -> str:
    if mode == "interview":
        return "Posso responder de forma objetiva e depois detalhar com exemplo prático."
    if mode == "study":
        return "Posso resumir o conceito e sugerir um próximo passo de estudo."
    return "Posso responder de forma curta agora e aprofundar se você quiser."


def _subject_from_query(query: str) -> str:
    text = str(query or "").strip()
    lowered = text.lower()
    prefixes = [
        "como ",
        "o que é ",
        "o que e ",
        "me explica ",
        "explica ",
        "explique ",
        "criar ",
        "como funciona ",
        "como instalar ",
        "como configurar ",
        "como consultar ",
        "como listar ",
        "para que serve ",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" ?.")
    return text.strip(" ?.")


def _finalize_response_text(answer: str, query: str, bullets: list[str], *, partial: bool = False) -> tuple[str, list[str]]:
    subject = _subject_from_query(query)
    clean_answer = str(answer or "").strip()
    lowered = clean_answer.lower()

    if "ainda nao sei responder isso com confianca" in lowered or "não sei responder isso com confiança" in lowered:
        clean_answer = f"Posso te dar um caminho inicial sobre {subject} em português, mas ainda falta uma fonte confiável para fechar a resposta."
        bullets = [
            "Comece pelo conceito principal e pelo comando ou recurso mais direto.",
            "Se quiser, eu também posso te passar um exemplo curto e prático.",
        ]
    elif "entendi. quer que eu aprofunde ou resuma?" in lowered:
        clean_answer = f"Posso responder de forma objetiva sobre {subject} e seguir com um exemplo prático, se você quiser."
        bullets = [
            "Se preferir, eu aprofundo o conceito.",
            "Se preferir, eu também posso resumir em poucos passos.",
        ]
    elif "contexto ainda parcial" in lowered:
        clean_answer = f"Posso te adiantar um caminho inicial sobre {subject} enquanto o contexto completa."
        bullets = [
            "Primeiro, confirme o recurso ou comando principal.",
            "Depois, valide com um exemplo simples antes de aprofundar.",
        ]

    if partial and clean_answer and "contexto ainda parcial" not in lowered:
        clean_answer = f"Posso te adiantar um caminho inicial sobre {subject} enquanto o contexto completa."

    return clean_answer, bullets


def _looks_technical_text(text: str) -> bool:
    lowered = (text or "").lower()
    words = set(re.findall(r"[a-z0-9_]+", lowered))
    tech_signals = (
        "processos",
        "ps",
        "top",
        "htop",
        "api",
        "backend",
        "frontend",
        "python",
        "kubernetes",
        "docker",
        "helm",
        "terraform",
        "deploy",
        "deployment",
        "probe",
        "service",
        "cluster",
        "cloud",
        "aws",
        "sql",
        "nginx",
        "apt",
        "apt-get",
        "yum",
        "dnf",
        "rpm",
        "systemctl",
        "install",
        "instalar",
        "package",
        "package-manager",
        "debian",
        "ubuntu",
        "fedora",
    )
    return any(signal in words for signal in tech_signals)


def _clean_text(text: str, limit: int = 220) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].strip() + "..."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso_to_epoch(value: str) -> Optional[float]:
    try:
        return datetime.fromisoformat(str(value)).timestamp()
    except Exception:
        return None


def _is_expired_last_seen(last_seen: str, now_epoch: Optional[float] = None) -> bool:
    epoch = _iso_to_epoch(last_seen)
    if epoch is None:
        return False
    ref = now_epoch if now_epoch is not None else time.time()
    return (ref - epoch) > REALTIME_SESSION_TTL_SECONDS


def _ensure_realtime_storage() -> None:
    REALTIME_PERSIST_DIR.mkdir(parents=True, exist_ok=True)


def _safe_load_sessions_payload() -> dict:
    try:
        if not REALTIME_SESSIONS_FILE.exists():
            return {}
        raw = json.loads(REALTIME_SESSIONS_FILE.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _write_sessions_payload(payload: dict) -> None:
    _ensure_realtime_storage()
    tmp_path = REALTIME_SESSIONS_FILE.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(REALTIME_SESSIONS_FILE)


def _session_to_persistable(entry: dict) -> dict:
    state = entry.get("state")
    transcript_tail = []
    if isinstance(state, ConversationState):
        for turn in (state.transcript or [])[-REALTIME_MAX_SESSION_TURNS:]:
            speaker = str(turn.get("speaker", "")).strip()
            text = _clean_text(str(turn.get("text", "")), limit=240)
            if speaker and text:
                transcript_tail.append({"speaker": speaker, "text": text})
    chunks = _trim_chunk_buffer(list(entry.get("chunks", [])))
    return {
        "mode": _normalize_mode(entry.get("mode", "generic"), fallback="generic"),
        "last_seen": str(entry.get("last_seen_iso", "") or _now_iso()),
        "last_is_final": bool(entry.get("last_is_final", True)),
        "chunks": chunks,
        "buffer_chunks": len(chunks),
        "buffer_chars": len(_buffer_to_text(chunks, max_chunks=REALTIME_MAX_BUFFER_CHUNKS)),
        "transcript_tail": transcript_tail,
        "latest_text": chunks[-1] if chunks else "",
    }


def _persist_realtime_session(conversation_id: str, entry: dict) -> None:
    payload = _safe_load_sessions_payload()
    entry["last_seen_iso"] = _now_iso()
    payload[conversation_id] = _session_to_persistable(entry)
    if len(payload) > REALTIME_MAX_SESSIONS:
        ordered = sorted(
            payload.items(),
            key=lambda item: str((item[1] or {}).get("last_seen", "")),
        )
        for old_id, _data in ordered[: len(payload) - REALTIME_MAX_SESSIONS]:
            payload.pop(old_id, None)
    _write_sessions_payload(payload)


def _load_persisted_session(conversation_id: str) -> Optional[dict]:
    payload = _safe_load_sessions_payload()
    row = payload.get(conversation_id)
    if not isinstance(row, dict):
        return None
    if _is_expired_last_seen(str(row.get("last_seen", "") or "")):
        return None
    state = ConversationState()
    transcript = row.get("transcript_tail", [])
    if isinstance(transcript, list):
        clean_transcript = []
        for item in transcript[-REALTIME_MAX_SESSION_TURNS:]:
            if not isinstance(item, dict):
                continue
            speaker = str(item.get("speaker", "")).strip()
            text = _clean_text(str(item.get("text", "")), limit=240)
            if speaker and text:
                clean_transcript.append({"speaker": speaker, "text": text})
        state.transcript = clean_transcript
    chunks = _trim_chunk_buffer(list(row.get("chunks", [])) if isinstance(row.get("chunks", []), list) else [])
    return {
        "state": state,
        "last_seen": time.monotonic(),
        "last_seen_iso": str(row.get("last_seen", "") or _now_iso()),
        "chunks": chunks,
        "last_is_final": bool(row.get("last_is_final", True)),
        "mode": _normalize_mode(row.get("mode", "generic"), fallback="generic"),
    }


def _append_realtime_metric(event: str, payload: dict) -> None:
    try:
        _ensure_realtime_storage()
        row = {
            "ts": _now_iso(),
            "event": event,
            **payload,
        }
        with REALTIME_METRICS_FILE.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        # Telemetria nao deve quebrar o fluxo principal.
        pass


def _cleanup_expired_realtime_sessions(req: Request) -> dict:
    now_epoch = time.time()
    removed_mem = 0
    removed_persisted = 0

    sessions = getattr(req.app.state, "realtime_sessions", {})
    if isinstance(sessions, dict):
        for conv_id in list(sessions.keys()):
            entry = sessions.get(conv_id, {})
            if not isinstance(entry, dict):
                continue
            last_seen_iso = str(entry.get("last_seen_iso", "") or "")
            if last_seen_iso and _is_expired_last_seen(last_seen_iso, now_epoch=now_epoch):
                sessions.pop(conv_id, None)
                removed_mem += 1

    payload = _safe_load_sessions_payload()
    changed = False
    for conv_id in list(payload.keys()):
        row = payload.get(conv_id, {})
        if not isinstance(row, dict):
            continue
        last_seen = str(row.get("last_seen", "") or "")
        if last_seen and _is_expired_last_seen(last_seen, now_epoch=now_epoch):
            payload.pop(conv_id, None)
            removed_persisted += 1
            changed = True
    if changed:
        _write_sessions_payload(payload)

    return {
        "removed_memory_sessions": removed_mem,
        "removed_persisted_sessions": removed_persisted,
    }


def _handle_realtime_api_error(exc: Exception) -> JSONResponse:
    if isinstance(exc, ValueError):
        message = str(exc)
        if "OPENAI_API_KEY ausente" in message:
            return _error_response(503, "OPENAI_API_KEY ausente para Realtime API")
        return _error_response(400, message)

    try:
        from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, RateLimitError

        if isinstance(exc, AuthenticationError):
            return _error_response(401, "falha de autenticacao na OpenAI Realtime API")
        if isinstance(exc, RateLimitError):
            return _error_response(429, "limite de requisicoes da OpenAI Realtime API excedido")
        if isinstance(exc, (APIConnectionError, APITimeoutError, APIError)):
            return _error_response(502, "falha na OpenAI Realtime API")
    except Exception:
        pass

    return _error_response(500, "falha ao criar sessao da OpenAI Realtime API")


def _compress_answer(answer: str, mode: str) -> str:
    text = _clean_text(answer, limit=320)
    if not text:
        return _default_short_answer(mode)
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    max_sentences = 1 if mode == "interview" else 2
    selected = " ".join(parts[:max_sentences]) if parts else text
    limit = 180 if mode == "interview" else 260
    return _clean_text(selected, limit=limit)


def _compress_bullets(bullets: list[str], mode: str) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for raw in bullets:
        cleaned = _clean_text(raw, limit=180)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    limit = 2 if mode == "interview" else 3
    return deduped[:limit]


def _query_is_portuguese(query: str) -> bool:
    text = re.sub(r"\s+", " ", str(query or "").strip().lower())
    if not text:
        return False
    pt_signals = (
        " o que ",
        " como ",
        " para que ",
        " explique ",
        " explicação ",
        " instalar ",
        " criar ",
        " funciona ",
        " linux ",
        " exemplo",
    )
    return any(signal in f" {text} " for signal in pt_signals) or bool(re.search(r"[àâêôãõçáéíóú]", text))


def _looks_like_raw_documentation(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", str(text or "").strip().lower())
    if not lowered:
        return False
    doc_markers = (
        "this tutorial",
        "in this tutorial",
        "this section",
        "in this section",
        "you can",
        "please note",
        "for more information",
        "the following",
        "documentation",
        "reference",
        "overview",
        "use the",
        "after reading",
    )
    if any(marker in lowered for marker in doc_markers):
        return True
    english_tokens = {"the", "and", "you", "can", "use", "for", "with", "this", "that", "section"}
    pt_tokens = {"o", "a", "de", "que", "para", "com", "em", "um", "uma", "você", "voce"}
    words = re.findall(r"[a-zà-ÿ0-9_]+", lowered)
    english_hits = sum(1 for word in words if word in english_tokens)
    pt_hits = sum(1 for word in words if word in pt_tokens)
    return english_hits >= 5 and english_hits > pt_hits + 1


def _safe_final_answer_for_query(query: str) -> tuple[str, list[str]]:
    subject = _subject_from_query(query)
    lowered = re.sub(r"\s+", " ", str(query or "").strip().lower())

    if "cpu" in lowered and "linux" in lowered:
        return (
            "No Linux, você pode consultar a CPU com `lscpu`, `cat /proc/cpuinfo` ou `top`.",
            [
                "Se quiser detalhes por núcleo, `lscpu` costuma ser o caminho mais direto.",
                "Se quiser a saída mais bruta, `cat /proc/cpuinfo` mostra os campos do processador.",
            ],
        )
    if ("processos" in lowered or "lista de processos" in lowered or "listar processos" in lowered) and "linux" in lowered:
        return (
            "No Linux, você pode listar processos com `ps aux`, `top` ou `htop`.",
            [
                "`ps aux` mostra os processos em execução com bastante detalhe.",
                "`top` e `htop` ajudam a ver uso de CPU, memória e processos em tempo real.",
            ],
        )
    if "terraform" in lowered:
        return (
            "Terraform é uma ferramenta de infraestrutura como código para definir, provisionar e versionar recursos.",
            [
                "Ele descreve a infraestrutura em arquivos declarativos.",
                "Depois, você aplica o plano para criar ou alterar os recursos.",
            ],
        )
    if "criar pod" in lowered or ("kubernetes" in lowered and "pod" in lowered):
        return (
            "Para criar um Pod no Kubernetes, use um manifesto YAML com `apiVersion`, `kind: Pod`, `metadata` e `spec`.",
            [
                "Você pode aplicar o arquivo com `kubectl apply -f pod.yaml`.",
                "Se quiser, também posso te passar um exemplo pronto de YAML.",
            ],
        )
    if "docker" in lowered:
        if "linux" in lowered or "por baixo" in lowered or "kernel" in lowered:
            return (
                "Docker usa recursos do Linux, como namespaces e cgroups, para isolar contêineres por baixo.",
                [
                    "Ele não cria uma máquina virtual inteira: compartilha o kernel do host.",
                    "Isso permite isolar processos, rede e consumo de recursos com mais leveza.",
                ],
            )
        return (
            "Docker é uma plataforma para empacotar e executar aplicações em contêineres.",
            [
                "Ele ajuda a isolar dependências e padronizar o ambiente de execução.",
                "Também facilita testar e distribuir a aplicação com menos variação entre máquinas.",
            ],
        )
    if "nginx" in lowered and "linux" in lowered:
        return (
            "Para instalar o Nginx no Linux, use o gerenciador de pacotes da sua distribuição e depois confirme o serviço.",
            [
                "Em Debian ou Ubuntu, normalmente você usa `apt`.",
                "Depois, valide com `systemctl status nginx` ou abra o serviço no navegador.",
            ],
        )
    if "liveness probe" in lowered or ("probe" in lowered and "kubernetes" in lowered):
        return (
            "Liveness probe é a checagem que o Kubernetes usa para reiniciar um contêiner quando ele deixa de responder.",
            [
                "Ela serve para detectar travamentos ou falhas de saúde durante a execução.",
                "Você pode configurá-la com `httpGet`, `tcpSocket` ou `exec`.",
            ],
        )
    if "container" in lowered and "imagem" in lowered and "máquina virtual" in lowered:
        return (
            "Container, imagem e máquina virtual são coisas diferentes: a imagem é o pacote, o container é a instância em execução e a VM isola um sistema operacional inteiro.",
            [
                "A imagem é imutável e serve como base para criar containers.",
                "O container compartilha o kernel do host, enquanto a VM virtualiza mais camadas.",
            ],
        )
    if "evitar fallback disfarçado" in lowered or ("fallback" in lowered and "conceitos técnicos" in lowered):
        return (
            "Para evitar fallback disfarçado, responda de forma direta ao tema, cite um exemplo concreto e só faça clarificação quando faltar dado essencial.",
            [
                "Comece pela definição ou passo prático mais importante.",
                "Evite frases que apenas anunciem que a resposta vai chegar depois.",
            ],
        )
    if "citar passos" in lowered and "resumir" in lowered:
        return (
            "Use passos quando a tarefa pede execução ou procedimento; use resumo quando a pergunta pede visão geral, definição ou comparação curta.",
            [
                "Se houver comando ou sequência operacional, priorize passos curtos.",
                "Se a pergunta for conceitual, uma síntese objetiva costuma ser melhor.",
            ],
        )
    if "fora do domínio" in lowered or "fora do dominio" in lowered:
        return (
            "Uma resposta ficou fora do domínio quando muda o assunto principal, troca a intenção da pergunta ou devolve um tema sem relação com o que foi pedido.",
            [
                "Compare a resposta com a intenção original da pergunta.",
                "Se o tópico principal mudou, trate como drift de domínio.",
            ],
        )

    if _query_is_portuguese(query):
        return (
            f"Posso te responder de forma direta sobre {subject} em português, sem despejar a fonte bruta.",
            [
                "Se você quiser, eu posso resumir em passos curtos.",
                "Se preferir, também posso dar um exemplo prático.",
            ],
        )
    return (
        f"Posso responder de forma curta sobre {subject} e aprofundar se você quiser.",
        [
            "Se quiser, eu também posso resumir em passos.",
            "Se preferir, eu posso dar um exemplo prático.",
        ],
    )


def _enforce_safe_final_answer(answer: str, bullets: list[str], query: str, *, partial: bool = False) -> tuple[str, list[str]]:
    clean_answer = _clean_text(answer, limit=320)
    clean_bullets = _compress_bullets(bullets, mode="generic")
    lowered_query = re.sub(r"\s+", " ", str(query or "").strip().lower())

    if _query_is_portuguese(query):
        if ("processos" in lowered_query or "listar processos" in lowered_query) and "linux" in lowered_query:
            if not any(token in clean_answer.lower() for token in ("ps", "top", "htop", "processos")):
                return _safe_final_answer_for_query(query)
        if _looks_like_raw_documentation(clean_answer):
            return _safe_final_answer_for_query(query)
        pt_response_markers = (
            " em português ",
            " no linux ",
            " para ",
            " você ",
            " voce ",
            " como ",
            " consulta ",
            " ferramenta ",
            " checagem ",
            " reiniciar ",
            " contêiner ",
            " container ",
            " recursos ",
        )
        if (
            not clean_answer
            or re.search(r"\b(the|and|you|use|this|that|with|building|shipping|running)\b", clean_answer.lower())
            and not any(marker in f" {clean_answer.lower()} " for marker in pt_response_markers)
        ):
            return _safe_final_answer_for_query(query)

    if partial and not clean_answer:
        return _safe_final_answer_for_query(query)
    if _looks_like_raw_documentation(clean_answer):
        return _safe_final_answer_for_query(query)
    return clean_answer, clean_bullets


def _style_answer_and_bullets(answer: str, bullets: list[str], mode: str) -> tuple[str, list[str]]:
    base_answer = _compress_answer(answer, mode=mode)
    base_bullets = _compress_bullets(bullets, mode=mode)

    if mode == "interview":
        styled_answer = base_answer
        styled_bullets = [f"Como responder: {item}" for item in base_bullets[:2]]
        if not styled_bullets:
            styled_bullets = ["Como responder: destaque o conceito em uma frase e cite um exemplo curto."]
        return styled_answer, styled_bullets

    if mode == "study":
        styled_answer = f"Resumo de estudo: {base_answer}"
        styled_bullets = [f"Para entender: {item}" for item in base_bullets]
        if not styled_bullets:
            styled_bullets = ["Para entender: conecte conceito, exemplo e validação prática."]
        return styled_answer, styled_bullets

    styled_answer = base_answer
    return styled_answer, base_bullets


def _summarize_knowledge_context(payload: dict) -> dict:
    sources = payload.get("sources", []) if isinstance(payload, dict) else []
    source_titles = []
    for item in sources[:2]:
        title = str(item.get("title", "")).strip()
        source_file = str(item.get("source_file", "")).strip()
        source_titles.append(title or source_file)
    return {
        "used_search": bool(payload.get("used_search", False)),
        "query": _clean_text(str(payload.get("query", "") or ""), limit=180),
        "result_count": int(payload.get("result_count", 0) or 0),
        "context": _clean_text(str(payload.get("context", "") or ""), limit=220),
        "search_backend": str(payload.get("search_backend", "") or ""),
        "fallback_used": bool(payload.get("fallback_used", False)),
        "context_used": bool(payload.get("context_used", False)),
        "semantic_api_ok": bool(payload.get("semantic_api_ok", False)),
        "semantic_duration_ms": int(payload.get("semantic_duration_ms", 0) or 0),
        "source_titles": source_titles,
        "routing_layer": str(payload.get("routing_layer", "") or ""),
        "skill_id": str(payload.get("skill_id", "") or ""),
        "skill_intent": str(payload.get("skill_intent", "") or ""),
        "skill_target": str(payload.get("skill_target", "") or ""),
        "skill_source": str(payload.get("skill_source", "") or ""),
        "skill_operation": str(payload.get("skill_operation", "") or ""),
    }


def _select_primary_answer(
    suggestions: list[str],
    knowledge_context: dict,
    default_answer: str,
) -> str:
    answer = str(default_answer or "").strip()
    if not suggestions:
        return answer

    result_count = int(knowledge_context.get("result_count", 0) or 0) if isinstance(knowledge_context, dict) else 0
    context = str(knowledge_context.get("context", "") or "").strip() if isinstance(knowledge_context, dict) else ""
    if result_count <= 0 or not context:
        return answer

    generic_prefixes = (
        "Pelo contexto técnico, o caminho mais seguro",
        "Automação de infraestrutura reduz erro humano",
    )
    if answer and not answer.startswith(generic_prefixes):
        return answer

    for candidate in suggestions:
        text = str(candidate).strip()
        if not text:
            continue
        if text.startswith("A base de conhecimento local sugere:"):
            return text
    return answer


def _normalize_mode(mode: Optional[str], fallback: str = "generic") -> str:
    clean = str(mode or "").strip().lower()
    return clean if clean in {"interview", "study", "generic"} else fallback


def _trim_chunk_buffer(chunks: list[str]) -> list[str]:
    cleaned = [_clean_text(item, limit=240) for item in chunks if _clean_text(item, limit=240)]
    cleaned = cleaned[-REALTIME_MAX_BUFFER_CHUNKS:]
    while len(cleaned) > 1 and sum(len(x) for x in cleaned) > REALTIME_MAX_BUFFER_CHARS:
        cleaned.pop(0)
    return cleaned


def _buffer_to_text(chunks: list[str], max_chunks: int = REALTIME_RESPOND_BUFFER_CHUNKS) -> str:
    selected = [str(x).strip() for x in (chunks or []) if str(x).strip()]
    if not selected:
        return ""
    selected = selected[-max_chunks:]
    return " ".join(selected).strip()


def _dedupe_incremental_chunks(chunks: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        clean = _clean_text(chunk, limit=240)
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(clean)
    return deduped


def _build_incremental_context(chunks: list[str]) -> dict:
    clean_chunks = _dedupe_incremental_chunks(chunks)
    if not clean_chunks:
        return {
            "current_text": "",
            "previous_context": "",
            "merged_text": "",
            "context_window_preview": "",
        }
    recent = clean_chunks[-REALTIME_RESPOND_BUFFER_CHUNKS:]
    current_text = recent[-1] if recent else ""
    previous_context = " ".join(recent[:-1]).strip()
    merged = f"{previous_context} {current_text}".strip() if previous_context else current_text
    preview_parts = []
    if previous_context:
        preview_parts.append(f"prev={_clean_text(previous_context, limit=110)}")
    if current_text:
        preview_parts.append(f"curr={_clean_text(current_text, limit=110)}")
    return {
        "current_text": current_text,
        "previous_context": previous_context,
        "merged_text": merged,
        "context_window_preview": " | ".join(preview_parts),
    }


def _evaluate_readiness(text: str, *, last_is_final: bool, from_buffer: bool) -> dict:
    clean = _clean_text(text, limit=320)
    lowered = clean.lower()
    words = re.findall(r"[a-zà-ÿ0-9_]+", lowered)
    word_count = len(words)
    has_question_mark = clean.endswith("?") or ("?" in clean)
    has_terminal = clean.endswith(("?", ".", "!", ":"))
    question_tokens = {
        "como",
        "o",
        "que",
        "qual",
        "quando",
        "por",
        "porque",
        "onde",
        "what",
        "how",
        "why",
        "when",
    }
    verb_tokens = {
        "é",
        "eh",
        "funciona",
        "usar",
        "explicar",
        "diferenciar",
        "fazer",
        "resolve",
        "works",
        "use",
        "explain",
        "work",
    }
    has_question_signal = bool(question_tokens.intersection(set(words)))
    has_verbish_signal = bool(verb_tokens.intersection(set(words)))
    min_len_ok = word_count >= 5

    score = 0
    if last_is_final:
        score += 2
    if has_question_mark:
        score += 2
    if has_terminal:
        score += 1
    if min_len_ok:
        score += 1
    if has_question_signal:
        score += 1
    if has_verbish_signal:
        score += 1

    if score >= 5:
        readiness = "high"
        stage = "final"
    elif score >= 3:
        readiness = "medium"
        stage = "final" if (last_is_final or has_question_mark) else "partial"
    else:
        readiness = "low"
        stage = "partial"

    if from_buffer and not last_is_final and readiness != "high":
        stage = "partial"
    should_wait_more = stage == "partial" and readiness != "high"
    return {
        "readiness": readiness,
        "response_stage": stage,
        "should_wait_more": should_wait_more,
        "signals": {
            "last_is_final": bool(last_is_final),
            "has_question_mark": has_question_mark,
            "has_terminal": has_terminal,
            "word_count": word_count,
            "has_question_signal": has_question_signal,
            "has_verbish_signal": has_verbish_signal,
        },
    }


def _prune_realtime_sessions(sessions: dict, keep_conversation_id: str) -> None:
    if len(sessions) <= REALTIME_MAX_SESSIONS:
        return
    ordered = sorted(
        sessions.items(),
        key=lambda item: float(item[1].get("last_seen", 0.0) if isinstance(item[1], dict) else 0.0),
    )
    to_remove = len(sessions) - REALTIME_MAX_SESSIONS
    removed = 0
    for conv_id, _entry in ordered:
        if conv_id == keep_conversation_id:
            continue
        sessions.pop(conv_id, None)
        removed += 1
        if removed >= to_remove:
            break


def _resolve_realtime_session(req: Request, conversation_id: str) -> dict:
    _cleanup_expired_realtime_sessions(req)
    sessions = getattr(req.app.state, "realtime_sessions", {})
    if not isinstance(sessions, dict):
        sessions = {}
        req.app.state.realtime_sessions = sessions

    now = time.monotonic()
    entry = sessions.get(conversation_id)
    if isinstance(entry, dict) and isinstance(entry.get("state"), ConversationState):
        entry["last_seen"] = now
        entry["chunks"] = _trim_chunk_buffer(entry.get("chunks", []) if isinstance(entry.get("chunks", []), list) else [])
        entry["mode"] = _normalize_mode(entry.get("mode", "generic"), fallback="generic")
        entry["last_is_final"] = bool(entry.get("last_is_final", True))
        entry["last_seen_iso"] = str(entry.get("last_seen_iso", "") or _now_iso())
        return entry
    if isinstance(entry, ConversationState):
        sessions[conversation_id] = {
            "state": entry,
            "last_seen": now,
            "last_seen_iso": _now_iso(),
            "chunks": [],
            "last_is_final": True,
            "mode": "generic",
        }
        _prune_realtime_sessions(sessions, keep_conversation_id=conversation_id)
        _persist_realtime_session(conversation_id, sessions[conversation_id])
        return sessions[conversation_id]

    persisted = _load_persisted_session(conversation_id)
    if isinstance(persisted, dict):
        sessions[conversation_id] = persisted
        _prune_realtime_sessions(sessions, keep_conversation_id=conversation_id)
        return sessions[conversation_id]

    sessions[conversation_id] = {
        "state": ConversationState(),
        "last_seen": now,
        "last_seen_iso": _now_iso(),
        "chunks": [],
        "last_is_final": True,
        "mode": "generic",
    }
    _prune_realtime_sessions(sessions, keep_conversation_id=conversation_id)
    _persist_realtime_session(conversation_id, sessions[conversation_id])
    return sessions[conversation_id]


def _find_realtime_session(req: Request, conversation_id: str) -> Optional[dict]:
    _cleanup_expired_realtime_sessions(req)
    sessions = getattr(req.app.state, "realtime_sessions", {})
    if isinstance(sessions, dict):
        row = sessions.get(conversation_id)
        if isinstance(row, dict) and isinstance(row.get("state"), ConversationState):
            row["last_seen"] = time.monotonic()
            row["last_seen_iso"] = str(row.get("last_seen_iso", "") or _now_iso())
            return row
    persisted = _load_persisted_session(conversation_id)
    if isinstance(persisted, dict):
        if not isinstance(sessions, dict):
            sessions = {}
            req.app.state.realtime_sessions = sessions
        sessions[conversation_id] = persisted
        return persisted
    return None


def _build_livecopilot_reply(
    *,
    req: Request,
    text_input: str,
    mode: Optional[str],
    conversation_id: Optional[str],
    voice_output_enabled: Optional[bool],
) -> dict:
    _cleanup_expired_realtime_sessions(req)
    text_input = str(text_input or "").strip()
    conversation_id = str(conversation_id or "").strip()
    started = time.monotonic()
    ingest_started = time.monotonic()

    session = None
    if conversation_id:
        session = _resolve_realtime_session(req, conversation_id)
        if mode:
            session["mode"] = _normalize_mode(mode, fallback=session.get("mode", "generic"))
        resolved_mode = _normalize_mode(mode, fallback=session.get("mode", "generic"))
        state = session["state"]
        buffer_chunks_list = list(session.get("chunks", []))
    else:
        resolved_mode = _normalize_mode(mode, fallback="generic")
        state = ConversationState()
        buffer_chunks_list = []

    context_preview = ""
    from_incremental_buffer = False
    if text_input:
        effective_input_text = _clean_text(text_input, limit=320)
    else:
        from_incremental_buffer = True
        assembled = _build_incremental_context(buffer_chunks_list)
        effective_input_text = assembled.get("merged_text", "")
        context_preview = assembled.get("context_window_preview", "")
        if not effective_input_text:
            raise ValueError("informe text ou conversation_id com buffer incremental")
        effective_input_text = _clean_text(effective_input_text, limit=320)

    previous_turns = len(state.transcript)
    connector_started = time.monotonic()
    connector_payload = _resolve_operational_skill_query(req, effective_input_text)
    skill_payload = connector_payload
    skill_matched = bool(connector_payload.get("matched", False))
    connector_ms = int((time.monotonic() - connector_started) * 1000)
    if skill_matched:
        state.add_turn(
            "user",
            effective_input_text,
            metadata={
                "context_source": "operational_skill_routing",
                "recognized_context": True,
                "skill_id": connector_payload.get("knowledge_context", {}).get("skill_id", ""),
                "skill_intent": connector_payload.get("knowledge_context", {}).get("skill_intent", ""),
                "skill_target": connector_payload.get("knowledge_context", {}).get("skill_target", ""),
            },
        )
        snapshot = state.snapshot()
        process_ingest_ms = 0
    else:
        snapshot = process_ingest(state, effective_input_text)
        process_ingest_ms = int((time.monotonic() - ingest_started) * 1000)
        if len(state.transcript) > REALTIME_MAX_SESSION_TURNS:
            state.transcript = state.transcript[-REALTIME_MAX_SESSION_TURNS:]
            snapshot = state.snapshot()

    suggestions = snapshot.get("suggestions", []) or []
    raw_knowledge_context = snapshot.get("knowledge_context", {}) or {}
    answer = str(suggestions[0]).strip() if suggestions else _default_short_answer(resolved_mode)
    answer = _select_primary_answer(suggestions, raw_knowledge_context, answer)
    bullets = [str(item).strip() for item in suggestions[1:4] if str(item).strip()]
    guidance_semantic_keys: list[str] = []
    guidance_context_fields: dict[str, object] = {}

    if not skill_matched:
        connector_started = time.monotonic()
        connector_payload = resolve_infra_status_query(req, effective_input_text)
        if not bool(connector_payload.get("matched", False)):
            connector_payload = resolve_project_state_query(effective_input_text)
        connector_ms = int((time.monotonic() - connector_started) * 1000)
    connector_matched = bool(connector_payload.get("matched", False))
    connector_context = connector_payload.get("knowledge_context", {}) if connector_matched else {}

    knowledge_context = _summarize_knowledge_context(raw_knowledge_context)
    backend = knowledge_context.get("search_backend", "") or "no_search"
    if knowledge_context.get("fallback_used", False):
        backend = "fallback"
    if connector_matched:
        answer = str(connector_payload.get("answer", "")).strip() or answer
        bullets = [str(item).strip() for item in connector_payload.get("bullets", []) if str(item).strip()] or bullets
        snapshot["suggestions"] = [answer, *bullets]
        snapshot["knowledge_context"] = connector_context
        knowledge_context = _summarize_knowledge_context(connector_context)
        knowledge_context["connector"] = str(connector_context.get("connector", "connector"))
        knowledge_context["intent"] = str(connector_payload.get("intent", ""))
        knowledge_context["source_paths"] = [
            str(item.get("source_file", "")).strip()
            for item in connector_context.get("sources", [])
            if isinstance(item, dict) and str(item.get("source_file", "")).strip()
        ]
        knowledge_context["target"] = str(connector_context.get("target", ""))
        backend = str(connector_context.get("search_backend", "connector")) or "connector"
        if str(connector_context.get("reason", "")).strip() == "server_target_not_mapped":
            guidance_semantic_keys.append("unmapped_target")
            for key in ("target", "requested_target", "checked_host", "reason"):
                if connector_context.get(key) not in (None, ""):
                    guidance_context_fields[key] = connector_context.get(key)
    elif int(knowledge_context.get("result_count", 0) or 0) == 0 and not _looks_technical_text(effective_input_text):
        answer = "Posso te dar um caminho inicial em português, mas ainda falta uma fonte confiável para fechar a resposta."
        bullets = [
            "Comece pelo conceito principal ou pelo comando mais direto.",
            "Se quiser, eu também posso te passar um exemplo curto e prático.",
            "Posso ajustar a resposta para modo técnico ou de entrevista.",
        ]
        guidance_semantic_keys.append("no_confident_source")
        guidance_context_fields["reason"] = "no_confident_source"
    else:
        answer, bullets = _style_answer_and_bullets(answer, bullets, mode=resolved_mode)

    last_is_final = bool(session.get("last_is_final", True)) if isinstance(session, dict) else True
    readiness_payload = _evaluate_readiness(
        effective_input_text,
        last_is_final=last_is_final,
        from_buffer=from_incremental_buffer,
    )
    response_stage = str(readiness_payload.get("response_stage", "final"))
    readiness = str(readiness_payload.get("readiness", "medium"))
    should_wait_more = bool(readiness_payload.get("should_wait_more", False))

    if response_stage == "partial" and (from_incremental_buffer or not connector_matched):
        if int(knowledge_context.get("result_count", 0) or 0) == 0 and not _looks_technical_text(effective_input_text):
            answer = f"Posso te adiantar um caminho inicial sobre {_subject_from_query(effective_input_text)} enquanto o contexto completa."
            bullets = [
                "Posso esperar mais contexto antes de fechar a resposta.",
            ]
        else:
            answer = f"Posso te adiantar um caminho inicial sobre {_subject_from_query(effective_input_text)} enquanto chega mais contexto."
            bullets = [
                "Leitura provisória: ainda pode faltar detalhe importante.",
                "Se você finalizar a frase/pergunta, eu consolido a resposta final.",
            ]

    guidance_payload = resolve_response_guidance(
        query=effective_input_text,
        semantic_keys=guidance_semantic_keys,
        scope="livecopilot_reply",
    )
    if bool(guidance_payload.get("matched", False)):
        answer = str(guidance_payload.get("answer", "")).strip() or answer
        bullets = [str(item).strip() for item in guidance_payload.get("bullets", []) if str(item).strip()] or bullets
        snapshot["suggestions"] = [answer, *bullets]
        guidance_context = {
            "query": effective_input_text,
            "used_search": False,
            "search_backend": "response_guidance",
            "context_used": False,
            "fallback_used": False,
            "semantic_api_ok": False,
            "semantic_duration_ms": 0,
            "result_count": 1,
            "context": "resposta ensinada explicitamente e persistida em response_guidance.json",
            "sources": [
                {
                    "title": "response_guidance",
                    "source_file": str(RESPONSE_GUIDANCE_FILE),
                }
            ],
            "connector": "response_guidance",
            "intent": "response_guidance",
            "target": str(guidance_context_fields.get("target", "") or ""),
            "guidance_rule_id": str(guidance_payload.get("rule_id", "")).strip(),
            "guidance_scope": str(guidance_payload.get("scope", "")).strip(),
            "guidance_trigger_type": str(guidance_payload.get("trigger_type", "")).strip(),
            "guidance_priority": int(guidance_payload.get("priority", 0) or 0),
            "guidance_version": int(guidance_payload.get("version", 0) or 0),
            "semantic_keys": list(guidance_payload.get("semantic_keys", []) or []),
            "policy_notes": str(guidance_payload.get("policy_notes", "")).strip(),
            **guidance_context_fields,
        }
        snapshot["knowledge_context"] = guidance_context
        knowledge_context = _summarize_knowledge_context(guidance_context)
        knowledge_context["connector"] = "response_guidance"
        knowledge_context["intent"] = "response_guidance"
        knowledge_context["target"] = str(guidance_context.get("target", "") or "")
        knowledge_context["source_paths"] = [str(RESPONSE_GUIDANCE_FILE)]
        backend = "response_guidance"

    answer, bullets = _finalize_response_text(answer, effective_input_text, bullets, partial=(response_stage == "partial"))
    answer, bullets = _enforce_safe_final_answer(answer, bullets, effective_input_text, partial=(response_stage == "partial"))
    quality_probe = classify_response_quality(
        query=effective_input_text,
        response=answer,
        knowledge_context=knowledge_context,
        route_or_source_hint=backend,
    )
    if quality_probe.get("quality_label") != "OK":
        safe_answer, safe_bullets = _safe_final_answer_for_query(effective_input_text)
        safe_answer, safe_bullets = _enforce_safe_final_answer(
            safe_answer,
            safe_bullets,
            effective_input_text,
            partial=False,
        )
        answer = safe_answer
        bullets = safe_bullets
        quality_probe = classify_response_quality(
            query=effective_input_text,
            response=answer,
            knowledge_context=knowledge_context,
            route_or_source_hint=backend,
        )
    quality_event = classify_response_quality(
        query=effective_input_text,
        response=answer,
        knowledge_context=knowledge_context,
        route_or_source_hint=backend,
    )
    append_response_quality_event(quality_event)

    voice_output_started = time.monotonic()
    voice_output = synthesize_voice_output_realtime_controlled(
        text=answer,
        response_stage=response_stage,
        should_wait_more=should_wait_more,
        enabled_override=voice_output_enabled,
    )
    voice_output_ms = int((time.monotonic() - voice_output_started) * 1000)
    if isinstance(voice_output, dict):
        voice_output["timing"] = {
            "voice_output_ms": voice_output_ms,
        }

    context_used = bool(knowledge_context.get("context_used", False))
    if not context_used and conversation_id and previous_turns > 0:
        context_used = True

    buffer_chunks = len(buffer_chunks_list)
    buffer_chars = len(_buffer_to_text(buffer_chunks_list, max_chunks=REALTIME_MAX_BUFFER_CHUNKS))
    latency_ms = int((time.monotonic() - started) * 1000)
    latency_breakdown = {
        "build_livecopilot_reply_ms": latency_ms,
        "process_ingest_ms": process_ingest_ms,
        "connector_ms": connector_ms,
        "voice_output_ms": voice_output_ms,
    }
    if isinstance(session, dict) and conversation_id:
        session["last_seen"] = time.monotonic()
        session["last_seen_iso"] = _now_iso()
        _persist_realtime_session(conversation_id, session)
    snapshot["suggestions"] = [answer, *bullets]
    _append_realtime_metric(
        "respond",
        {
            "conversation_id": conversation_id,
            "mode": resolved_mode,
            "response_stage": response_stage,
            "readiness": readiness,
            "backend": backend,
            "latency_ms": latency_ms,
            "latency_breakdown": latency_breakdown,
            "context_turns": len(snapshot.get("transcript", []) or []),
            "buffer_chunks": buffer_chunks,
            "buffer_chars": buffer_chars,
        },
    )

    if _is_semantic_canary(effective_input_text):
        transcript_tail = ""
        if isinstance(snapshot.get("transcript", []), list) and snapshot.get("transcript"):
            transcript_tail = str(snapshot.get("transcript", [])[-1].get("text", ""))
        trace_payload = {
            "ts": _now_iso(),
            "question": effective_input_text,
            "raw_input": text_input,
            "transcript_text": transcript_tail,
            "mode": resolved_mode,
            "conversation_id": conversation_id,
            "skill_routing": {
                "matched": skill_matched,
                "payload": skill_payload if skill_matched else {},
            },
            "connector_routing": {
                "matched": connector_matched,
                "intent": connector_payload.get("intent", ""),
                "backend": backend,
                "knowledge_context": connector_context if connector_matched else {},
            },
            "semantic_context": {
                "search_query": state.knowledge_context.get("query", ""),
                "used_search": state.knowledge_context.get("used_search", False),
                "search_backend": state.knowledge_context.get("search_backend", ""),
                "semantic_api_ok": state.knowledge_context.get("semantic_api_ok", False),
                "fallback_used": state.knowledge_context.get("fallback_used", False),
                "result_count": state.knowledge_context.get("result_count", 0),
                "query_tags": state.knowledge_context.get("query_tags", {}),
                "query_tags_used": state.knowledge_context.get("query_tags_used", []),
                "used_tag_routing": state.knowledge_context.get("used_tag_routing", False),
                "used_global_fallback": state.knowledge_context.get("used_global_fallback", False),
                "sources": state.knowledge_context.get("sources", []),
                "context": state.knowledge_context.get("context", ""),
                "debug": state.knowledge_debug,
            },
            "response": {
                "answer": answer,
                "bullets": bullets,
                "response_stage": response_stage,
                "readiness": readiness,
            },
        }
        _write_semantic_trace(trace_payload)

    quality_event["route_or_source_hint"] = backend
    quality_event["confidence"] = knowledge_context.get("confidence", None)

    return {
        "status": "ok",
        "mode": resolved_mode,
        "answer_style": resolved_mode,
        "response_stage": response_stage,
        "readiness": readiness,
        "should_wait_more": should_wait_more,
        "conversation_id": conversation_id,
        "input_text": effective_input_text,
        "answer": answer,
        "bullets": bullets,
        "quality": quality_event,
        "voice_output": voice_output,
        "latency_breakdown": latency_breakdown,
        "knowledge_context": {
            **knowledge_context,
            "context_used": context_used,
            "buffer_chunks": buffer_chunks,
            "buffer_chars": buffer_chars,
            "context_window_preview": _clean_text(context_preview, limit=180),
        },
        "latency_ms": latency_ms,
        "backend": backend,
        "context_turns": len(snapshot.get("transcript", []) or []),
        "context_used": context_used,
        "buffer_chunks": buffer_chunks,
        "buffer_chars": buffer_chars,
        "snapshot": snapshot,
    }


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/semantic/search")
async def semantic_search_endpoint(payload: SemanticSearchRequest):
    if _is_blank(payload.query):
        return _error_response(400, "query vazia")

    try:
        raw = semantic_search(
            query=payload.query,
            limit=payload.limit,
            source_file=payload.source_file,
        )
        response = {
            "status": "ok",
            "query": raw.get("query", payload.query),
            "model": raw.get("model", ""),
            "count": int(raw.get("count", 0)),
            "search_cache_hit": bool(raw.get("search_cache_hit", False)),
            "semantic_path": str(raw.get("semantic_path", "") or ""),
            "embedding_cache_hit": bool(raw.get("embedding_cache_hit", False)),
            "openai_called": bool(raw.get("openai_called", False)),
            "results": raw.get("results", []),
        }
        if payload.return_context:
            response["context"] = build_context_from_results(
                query=payload.query,
                results=response.get("results", []),
                top_k=payload.limit,
            )
        return response
    except Exception as exc:
        return _handle_semantic_error(exc)


@router.post("/semantic/ingest-min")
async def semantic_ingest_min_endpoint(payload: SemanticIngestMinRequest):
    if _is_blank(payload.file_path) and _is_blank(payload.text):
        return _error_response(400, "informe text ou file_path")

    try:
        result = ingest_min_document(
            file_path=payload.file_path,
            text=payload.text,
            source_file=payload.source_file,
            title=payload.title,
            max_chunks=payload.max_chunks,
        )
        chunks = result.get("chunks", [])
        document = result.get("document", {})
        cache_invalidation = result.get("cache_invalidation", {})
        return {
            "status": "ok",
            "document_id": document.get("document_id"),
            "chunks_created": len(chunks),
            "chunk_ids": [chunk.get("chunk_id") for chunk in chunks],
            "semantic_search_cache_entries_cleared": int(cache_invalidation.get("semantic_search_cache_entries_cleared", 0)),
        }
    except Exception as exc:
        return _handle_semantic_error(exc)

@router.get("/status")
async def status(req: Request):
    audio_capture = req.app.state.audio_capture
    transcription_runtime = get_transcription_runtime()
    voice_runtime = get_voice_output_runtime()
    realtime_runtime = get_realtime_runtime()
    return {
        "status": "ok",
        "ws_enabled": settings.ws_enabled,
        "capture_mode": settings.capture_mode,
        "capture_live": audio_capture.is_live(),
        "transcription_provider": transcription_runtime.get("provider"),
        "transcription_provider_selected": transcription_runtime.get("provider_selected"),
        "transcription_preference": transcription_runtime.get("transcription_preference"),
        "local_asr_enabled": bool(transcription_runtime.get("local_available", False)),
        "local_asr_model": transcription_runtime.get("local_model"),
        "local_asr_timeout_ms": int(transcription_runtime.get("local_timeout_ms", 1200) or 1200),
        "transcription_external_preferred": bool(transcription_runtime.get("external_preferred", False)),
        "transcription_external_available": bool(transcription_runtime.get("external_available", False)),
        "transcription_external_model": transcription_runtime.get("external_model"),
        "voice_output_enabled_default": bool(voice_runtime.get("enabled_default", False)),
        "voice_output_provider": voice_runtime.get("provider"),
        "voice_output_model": voice_runtime.get("model"),
        "voice_output_opt_in": bool(voice_runtime.get("voice_output_opt_in", True)),
        "voice_output_control_policy": "final_stage_only",
        "silent_mode_default": bool(voice_runtime.get("silent_mode_default", True)),
        "realtime_api_enabled": bool(realtime_runtime.get("enabled", False)),
        "realtime_api_provider": realtime_runtime.get("provider"),
        "realtime_api_model": realtime_runtime.get("model"),
        "realtime_api_voice": realtime_runtime.get("voice"),
        "realtime_api_language": realtime_runtime.get("language"),
        "realtime_api_key_present": bool(realtime_runtime.get("api_key_present", False)),
        "knowledge_debug_enabled": settings.knowledge_debug,
        "voice_observability_file": str(VOICE_EVENTS_FILE),
        "voice_observability_retention_days": VOICE_EVENTS_RETENTION_DAYS,
        "voice_session_trace_root": str(VOICE_SESSION_ROOT),
        "voice_session_trace_latest": get_latest_voice_session_dir(),
    }

@router.post("/ingest")
async def ingest(req: Request, payload: IngestRequest):
    state = req.app.state.conversation_state
    hub = req.app.state.ws_hub

    logger.info(
        "ingest",
        extra={
            "event": "ingest",
            "text_len": len(payload.text),
            "source": payload.source or "mock",
        },
    )
    snapshot = process_ingest(state, payload.text)
    await hub.broadcast(snapshot)
    return {"status": "accepted", "snapshot": snapshot}


@router.post("/api/chat")
async def api_chat(req: Request, payload: ChatRequest):
    try:
        response = _build_livecopilot_reply(
            req=req,
            text_input=payload.text,
            mode=payload.mode,
            conversation_id=payload.conversation_id,
            voice_output_enabled=False,
        )
    except ValueError as exc:
        return _error_response(400, str(exc))
    return {
        "status": "ok",
        "channel": "text",
        **response,
    }


@router.post("/api/realtime/session")
async def api_realtime_session(payload: RealtimeSessionRequest):
    try:
        runtime = get_realtime_runtime()
        created = create_realtime_client_secret(mode=_normalize_mode(payload.mode, fallback="generic"))
    except Exception as exc:
        return _handle_realtime_api_error(exc)
    return {
        "status": "ok",
        "channel": "voice",
        "provider": created.get("provider", runtime.get("provider", "openai_realtime")),
        "client_secret": created.get("client_secret", ""),
        "expires_at": created.get("expires_at"),
        "webrtc_url": created.get("webrtc_url", runtime.get("webrtc_url", "")),
        "model": created.get("model", runtime.get("model", "")),
        "voice": created.get("voice", runtime.get("voice", "")),
        "language": created.get("language", runtime.get("language", "")),
        "transcription_model": created.get("transcription_model", runtime.get("transcription_model", "")),
        "session": created.get("session", {}),
    }


@router.post("/api/voice/events")
async def api_voice_events(payload: VoiceEventRequest):
    event_payload = payload.model_dump(exclude_none=True)
    event_name = str(event_payload.pop("event", "") or "").strip()
    event_payload["session_id"] = str(event_payload.get("session_id", "") or "").strip()
    event_payload["conversation_id"] = str(event_payload.get("conversation_id", "") or "").strip()
    event_payload["transcript_excerpt"] = summarize_text(event_payload.get("transcript_excerpt", "") or "", limit=180)
    event_payload["response_summary"] = summarize_text(event_payload.get("response_summary", "") or "", limit=180)
    event_payload["error_message"] = summarize_text(event_payload.get("error_message", "") or "", limit=180)
    event_payload["source"] = str(event_payload.get("source", "frontend") or "frontend").strip() or "frontend"
    event_payload["transport"] = str(event_payload.get("transport", "") or "").strip()
    event_payload["provider_event_type"] = str(event_payload.get("provider_event_type", "") or "").strip()
    event_payload["client_ts"] = str(event_payload.pop("ts", "") or "").strip()
    event_payload["started_at"] = str(event_payload.get("started_at", "") or "").strip()
    event_payload["url"] = str(event_payload.get("url", "") or "").strip()
    event_payload["model"] = str(event_payload.get("model", "") or "").strip()
    event_payload["voice"] = str(event_payload.get("voice", "") or "").strip()
    event_payload["user_agent"] = str(event_payload.get("user_agent", "") or "").strip()
    session_dir = record_voice_event(event_name, **event_payload)
    return {"status": "ok", "accepted": True, "session_dir": session_dir}


@router.post("/realtime/ingest")
async def realtime_ingest(req: Request, payload: RealtimeIngestRequest):
    _cleanup_expired_realtime_sessions(req)
    conversation_id = str(payload.conversation_id or "").strip()
    if not conversation_id:
        return _error_response(400, "conversation_id vazio")
    chunk_text = _clean_text(payload.chunk_text, limit=260)
    if not chunk_text:
        return _error_response(400, "chunk_text vazio")

    session = _resolve_realtime_session(req, conversation_id)
    mode = _normalize_mode(payload.mode, fallback=session.get("mode", "generic"))
    chunks = list(session.get("chunks", []))
    chunks.append(chunk_text)
    session["chunks"] = _trim_chunk_buffer(chunks)
    session["last_is_final"] = bool(payload.is_final)
    session["mode"] = mode
    session["last_seen"] = time.monotonic()
    session["last_seen_iso"] = _now_iso()
    _persist_realtime_session(conversation_id, session)

    buffer_text = _buffer_to_text(session["chunks"], max_chunks=REALTIME_MAX_BUFFER_CHUNKS)
    _append_realtime_metric(
        "ingest",
        {
            "conversation_id": conversation_id,
            "mode": mode,
            "is_final": bool(payload.is_final),
            "buffer_chunks": len(session["chunks"]),
            "buffer_chars": len(buffer_text),
            "context_turns": len((session.get("state") or ConversationState()).transcript if isinstance(session.get("state"), ConversationState) else []),
        },
    )
    return {
        "status": "ok",
        "conversation_id": conversation_id,
        "accepted": True,
        "mode": mode,
        "is_final": bool(payload.is_final),
        "buffer_size": len(session["chunks"]),
        "buffer_chunks": len(session["chunks"]),
        "buffer_chars": len(buffer_text),
    }


@router.get("/realtime/session/{conversation_id}")
async def realtime_session_inspect(req: Request, conversation_id: str):
    _cleanup_expired_realtime_sessions(req)
    clean_id = str(conversation_id or "").strip()
    if not clean_id:
        return _error_response(400, "conversation_id vazio")
    session = _find_realtime_session(req, clean_id)
    if not isinstance(session, dict):
        return _error_response(404, f"sessao nao encontrada: {clean_id}")
    chunks = _trim_chunk_buffer(list(session.get("chunks", [])))
    state = session.get("state") if isinstance(session.get("state"), ConversationState) else ConversationState()
    latest_text = chunks[-1] if chunks else ""
    readiness_hint = "low"
    if latest_text:
        readiness_hint = _evaluate_readiness(
            latest_text,
            last_is_final=bool(session.get("last_is_final", True)),
            from_buffer=True,
        ).get("readiness", "low")
    return {
        "status": "ok",
        "conversation_id": clean_id,
        "mode": _normalize_mode(session.get("mode", "generic"), fallback="generic"),
        "context_turns": len(state.transcript),
        "buffer_chunks": len(chunks),
        "buffer_chars": len(_buffer_to_text(chunks, max_chunks=REALTIME_MAX_BUFFER_CHUNKS)),
        "last_seen": str(session.get("last_seen_iso", "") or _now_iso()),
        "latest_text": _clean_text(latest_text, limit=160),
        "readiness_hint": readiness_hint,
    }


@router.get("/realtime/sessions")
async def realtime_sessions(req: Request):
    _cleanup_expired_realtime_sessions(req)
    payload = _safe_load_sessions_payload()
    rows = []
    for conversation_id, row in payload.items():
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "conversation_id": str(conversation_id),
                "mode": _normalize_mode(row.get("mode", "generic"), fallback="generic"),
                "context_turns": len(row.get("transcript_tail", []) if isinstance(row.get("transcript_tail", []), list) else []),
                "buffer_chunks": int(row.get("buffer_chunks", 0) or 0),
                "buffer_chars": int(row.get("buffer_chars", 0) or 0),
                "last_seen": str(row.get("last_seen", "") or ""),
            }
        )
    rows.sort(key=lambda item: item.get("last_seen", ""), reverse=True)
    return {
        "status": "ok",
        "ttl_seconds": REALTIME_SESSION_TTL_SECONDS,
        "total_sessions": len(rows),
        "sessions": rows[:100],
    }


@router.get("/realtime/metrics")
async def realtime_metrics():
    if not REALTIME_METRICS_FILE.exists():
        return {
            "status": "ok",
            "events_total": 0,
            "by_event": {},
            "by_stage": {},
            "by_mode": {},
            "avg_latency_ms": 0.0,
        }
    by_event: dict[str, int] = {}
    by_stage: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    latency_values: list[float] = []
    events_total = 0
    try:
        with REALTIME_METRICS_FILE.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if not isinstance(row, dict):
                    continue
                events_total += 1
                ev = str(row.get("event", "") or "")
                mode = str(row.get("mode", "") or "")
                stage = str(row.get("response_stage", "") or "")
                if ev:
                    by_event[ev] = by_event.get(ev, 0) + 1
                if mode:
                    by_mode[mode] = by_mode.get(mode, 0) + 1
                if stage:
                    by_stage[stage] = by_stage.get(stage, 0) + 1
                try:
                    lat = float(row.get("latency_ms", 0) or 0)
                    if lat > 0:
                        latency_values.append(lat)
                except Exception:
                    pass
    except Exception:
        return _error_response(500, "falha ao ler realtime_metrics.ndjson")

    avg_latency = round(sum(latency_values) / len(latency_values), 2) if latency_values else 0.0
    return {
        "status": "ok",
        "events_total": events_total,
        "by_event": by_event,
        "by_stage": by_stage,
        "by_mode": by_mode,
        "avg_latency_ms": avg_latency,
    }


@router.post("/realtime/respond")
async def realtime_respond(req: Request, payload: RealtimeRespondRequest):
    started = time.monotonic()
    clean_text = summarize_text(payload.text or "", limit=180)
    clean_conversation_id = str(payload.conversation_id or "").strip()
    record_voice_event(
        "voice_backend_request_received",
        session_id=clean_conversation_id,
        conversation_id=clean_conversation_id,
        transcript_excerpt=clean_text,
        source="backend",
        transport="http",
    )
    try:
        response = _build_livecopilot_reply(
            req=req,
            text_input=payload.text or "",
            mode=payload.mode,
            conversation_id=payload.conversation_id,
            voice_output_enabled=payload.voice_output_enabled,
        )
        request_total_ms = int((time.monotonic() - started) * 1000)
        if isinstance(response.get("latency_breakdown"), dict):
            response["latency_breakdown"]["request_total_ms"] = request_total_ms
        record_voice_event(
            "voice_backend_response_completed",
            session_id=clean_conversation_id,
            conversation_id=response.get("conversation_id", clean_conversation_id),
            transcript_excerpt=clean_text,
            response_summary=summarize_text(response.get("answer", ""), limit=180),
            http_status=200,
            source="backend",
            transport="http",
            backend=str(response.get("backend", "")).strip(),
            response_stage=str(response.get("response_stage", "")).strip(),
            readiness=str(response.get("readiness", "")).strip(),
            latency_ms=request_total_ms,
            latency_breakdown=response.get("latency_breakdown", {}),
            latency_backend_total_ms=request_total_ms,
            latency_backend_build_reply_ms=response.get("latency_breakdown", {}).get("build_livecopilot_reply_ms"),
            latency_backend_process_ingest_ms=response.get("latency_breakdown", {}).get("process_ingest_ms"),
            latency_backend_connector_ms=response.get("latency_breakdown", {}).get("connector_ms"),
            latency_backend_voice_output_ms=response.get("latency_breakdown", {}).get("voice_output_ms"),
        )
        return response
    except ValueError as exc:
        record_voice_event(
            "voice_backend_response_failed",
            session_id=clean_conversation_id,
            conversation_id=clean_conversation_id,
            transcript_excerpt=clean_text,
            error_message=summarize_text(str(exc), limit=180),
            http_status=400,
            source="backend",
            transport="http",
            latency_ms=int((time.monotonic() - started) * 1000),
        )
        return _error_response(400, str(exc))
    except Exception as exc:
        record_voice_event(
            "voice_backend_response_failed",
            session_id=clean_conversation_id,
            conversation_id=clean_conversation_id,
            transcript_excerpt=clean_text,
            error_message=summarize_text(str(exc), limit=180),
            http_status=500,
            source="backend",
            transport="http",
            latency_ms=int((time.monotonic() - started) * 1000),
        )
        raise


@router.get("/api/knowledge/search")
async def knowledge_search(
    q: str = Query(..., min_length=1, description="Termo, frase ou palavras-chave para busca local"),
    limit: int = Query(5, ge=1, le=20, description="Quantidade maxima de resultados"),
):
    payload = search_knowledge_chunks_with_debug(q, limit=limit)
    results = payload.get("results", [])
    return {
        "query": q,
        "count": len(results),
        "results": results,
        "search_debug": payload.get("debug", {}),
    }


@router.get("/api/knowledge/debug")
async def knowledge_debug(req: Request):
    state = req.app.state.conversation_state
    return {
        "enabled": settings.knowledge_debug,
        "debug": state.knowledge_debug if settings.knowledge_debug else {},
    }


@router.get("/api/knowledge/hygiene")
async def knowledge_hygiene(
    top: int = Query(20, ge=1, le=100, description="Quantidade maxima por lista no relatorio de higiene"),
):
    return build_knowledge_hygiene_report(top=top)


@router.get("/api/question-bank/search")
async def question_bank_search(
    q: str = Query(..., min_length=1, description="Pergunta, termo ou tema para buscar na trilha de avaliacao"),
    limit: int = Query(5, ge=1, le=20, description="Quantidade maxima de itens retornados"),
):
    payload = search_question_bank_items_with_debug(q, limit=limit)
    results = payload.get("results", [])
    return {
        "query": q,
        "count": len(results),
        "results": results,
        "search_debug": payload.get("debug", {}),
    }


@router.get("/api/question-bank/coverage")
async def question_bank_coverage(
    top: int = Query(10, ge=1, le=50, description="Quantidade maxima por lista no diagnostico"),
):
    return build_question_bank_coverage_report(top=top)


@router.get("/api/question-bank/action-plan")
async def question_bank_action_plan(
    top: int = Query(10, ge=1, le=50, description="Quantidade maxima por lista no plano de acao"),
    track: str = Query("", description="Filtro opcional por trilha"),
):
    return build_question_bank_action_report(top=top, track=track or None)


@router.get("/api/certifications/gap")
async def certifications_gap(
    q: str = Query(..., min_length=1, description="Tema, pergunta ou dominio para mapear cobertura"),
    track: str = Query("python", min_length=1, description="Trilha de certificacao"),
):
    return analyze_knowledge_gap(q, track=track)


@router.get("/api/certifications/gap/plan")
async def certifications_gap_plan(
    q: str = Query(..., min_length=1, description="Tema, pergunta ou dominio para mapear cobertura"),
    track: str = Query("python", min_length=1, description="Trilha de certificacao"),
):
    analysis = analyze_knowledge_gap(q, track=track)
    persisted = record_gap_analysis(analysis)
    return {
        "analysis": analysis,
        "persisted": persisted,
    }


@router.get("/api/certifications/gap/queue")
async def certifications_gap_queue(
    track: str = Query("", description="Filtro opcional por trilha de certificacao"),
    top: int = Query(10, ge=1, le=100, description="Quantidade maxima de itens por lista"),
    section: str = Query(
        "all",
        pattern="^(all|gaps|topics|domains|certifications|tags|tags-technology|tags-domain|tags-subtheme|mismatches|mismatch-top)$",
        description="Recorte da consulta: all, gaps, topics, domains, certifications, tags, tags-technology, tags-domain, tags-subtheme, mismatches, mismatch-top",
    ),
):
    report = get_gap_report(track=track or None, top=top)
    if section == "all":
        return report

    section_map = {
        "gaps": "most_frequent_gaps",
        "topics": "recommended_ingestion_topics",
        "domains": "grouped_by_domain",
        "certifications": "grouped_by_certification",
        "tags": "top_gap_tags",
        "tags-technology": "grouped_by_tag.technology",
        "tags-domain": "grouped_by_tag.domain",
        "tags-subtheme": "grouped_by_tag.subtheme",
        "mismatches": "mismatch_records",
        "mismatch-top": "top_mismatches",
    }
    key = section_map[section]
    if key.startswith("grouped_by_tag."):
        grouped_by_tag = report.get("grouped_by_tag", {})
        tag_type = key.split(".", 1)[1]
        selected_items = grouped_by_tag.get(tag_type, []) if isinstance(grouped_by_tag, dict) else []
    else:
        selected_items = report.get(key, [])
    return {
        "track_filter": report.get("track_filter", ""),
        "history_count": report.get("history_count", 0),
        "queue_count": report.get("queue_count", 0),
        "section": section,
        "items": selected_items,
        "source_files": report.get("source_files", {}),
    }
