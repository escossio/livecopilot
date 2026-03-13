import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings
from app.services.knowledge_search import build_context_from_results, search_knowledge_chunks_with_debug
from app.services.semantic_min_api import semantic_search
from app.services.state import ConversationState
from app.services.topics import detect_topic
from app.services.job_market import match_terms

SEMANTIC_API_BASE = os.getenv("SEMANTIC_API_BASE", "http://127.0.0.1:8099")
SEMANTIC_TELEMETRY_PATH = Path("/lab/projects/livecopilot/var/semantic_telemetry.ndjson")
SEMANTIC_POLICY_PATH = Path(os.getenv("SEMANTIC_POLICY_PATH", "/lab/projects/livecopilot/config/semantic_policy.json"))
DEFAULT_SEMANTIC_POLICY = {
    "relevance_floor": 0.25,
    "context_limit": 3,
    "domain_signals_primary": [
        "kubernetes",
        "docker",
        "vpc",
        "security group",
        "nacl",
        "helm",
        "probe",
        "healthcheck",
        "cache",
        "backend",
        "api",
    ],
    "adjacent_technical_signals": [
        "regex",
        "javascript",
        "ansible",
        "jenkins",
        "sed",
        "awk",
        "windows",
        "cpf",
        "playbook",
        "pipeline",
    ],
}


def _load_semantic_policy() -> Dict[str, Any]:
    try:
        if not SEMANTIC_POLICY_PATH.exists():
            return dict(DEFAULT_SEMANTIC_POLICY)
        data = json.loads(SEMANTIC_POLICY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(DEFAULT_SEMANTIC_POLICY)
        policy = dict(DEFAULT_SEMANTIC_POLICY)
        policy.update(data)
        return policy
    except Exception:
        return dict(DEFAULT_SEMANTIC_POLICY)


SEMANTIC_POLICY = _load_semantic_policy()
RELEVANCE_FLOOR = float(SEMANTIC_POLICY.get("relevance_floor", DEFAULT_SEMANTIC_POLICY["relevance_floor"]) or 0.0)
CONTEXT_LIMIT = max(int(SEMANTIC_POLICY.get("context_limit", DEFAULT_SEMANTIC_POLICY["context_limit"]) or 1), 1)
DOMAIN_SIGNALS = [str(token).lower() for token in SEMANTIC_POLICY.get("domain_signals_primary", []) if str(token).strip()]
if not DOMAIN_SIGNALS:
    DOMAIN_SIGNALS = list(DEFAULT_SEMANTIC_POLICY["domain_signals_primary"])
ADJACENT_TECH_SIGNALS = [
    str(token).lower() for token in SEMANTIC_POLICY.get("adjacent_technical_signals", []) if str(token).strip()
]
if not ADJACENT_TECH_SIGNALS:
    ADJACENT_TECH_SIGNALS = list(DEFAULT_SEMANTIC_POLICY["adjacent_technical_signals"])
TECH_QUERY_SIGNALS = [
    "api",
    "backend",
    "frontend",
    "python",
    "javascript",
    "fastapi",
    "docker",
    "kubernetes",
    "cloud",
    "aws",
    "linux",
    "sql",
    "microserv",
    "regex",
    "ansible",
    "jenkins",
    "sed",
    "awk",
    "playbook",
    "pipeline",
]

def _classify_input(text: str) -> str:
    lowered = text.lower().strip()
    if any(token in lowered for token in ["pode explicar", "explica", "explique", "o que é", "o que eh"]):
        return "pedido de explicação"
    if any(token in lowered for token in ["você já", "voce ja", "sua experiência", "sua experiencia", "você conhece", "voce conhece"]):
        return "pergunta sobre experiência/conhecimento"
    if any(token in lowered for token in ["conte", "fale sobre", "me dê um exemplo", "me de um exemplo", "descreva"]):
        return "pergunta aberta de entrevista"
    if any(token in lowered for token in ["certo?", "é isso", "é isso mesmo", "confirmar", "confirma"]):
        return "confirmação"
    if any(token in lowered for token in ["continuando", "além disso", "além do mais", "voltando", "sobre isso"]):
        return "continuação de assunto"
    if lowered.startswith("e ") or lowered.startswith("e,"):
        return "continuação de assunto"
    if "?" in lowered:
        return "pergunta técnica"
    return "neutro"


def _build_topic_suggestions(
    text: str,
    topic_name: str,
    short_answer: str,
    long_answer: str,
    time_gain: str,
    counter: str,
    experience_link: str,
) -> List[str]:
    return [
        short_answer,
        long_answer,
        time_gain,
        counter,
        experience_link,
        f"Posso confirmar se entendi a sua dúvida sobre {topic_name}?",
    ]


def _build_generic_suggestions(text: str, classification: str) -> List[str]:
    if classification == "pedido de explicação":
        return [
            "Claro. Quer uma explicação rápida ou aprofundada?",
            "Posso explicar com um exemplo simples e depois detalhar.",
            "Só um instante para organizar a explicação.",
            f"Você quer foco no conceito ou na prática aplicada: {text}?",
        ]
    if classification == "pergunta sobre experiência/conhecimento":
        return [
            "Posso resumir minha experiência de forma objetiva.",
            "Tenho experiência prática com casos semelhantes e posso detalhar.",
            "Só um instante para estruturar a resposta.",
            "Quer um exemplo concreto de projeto ou uma visão geral?",
        ]
    if classification == "pergunta aberta de entrevista":
        return [
            "Posso responder no formato situação, ação e resultado.",
            "Tenho um exemplo relevante e posso destacar aprendizados.",
            "Só um segundo para estruturar a resposta.",
            "Quer foco em desafios técnicos ou em liderança/colaboração?",
        ]
    if classification == "confirmação":
        return [
            "Sim, é isso mesmo.",
            "Exato. Posso detalhar o próximo passo se quiser.",
            "Só confirmando: quer que eu aprofunde algum ponto específico?",
            "Entendido. Quer um resumo curto do que alinhamos?",
        ]
    if classification == "continuação de assunto":
        return [
            "Certo, seguindo por esse caminho...",
            "Podemos continuar a partir do último ponto.",
            "Só um instante para alinhar o fio da conversa.",
            "Quer que eu conecte isso ao que já discutimos?",
        ]
    if classification == "pergunta técnica":
        return [
            "Posso responder direto e depois detalhar.",
            "Quer uma resposta rápida ou uma explicação completa?",
            "Só um instante para organizar a resposta.",
            "Tem algum contexto ou restrição importante?",
        ]
    return [
        "Entendi. Quer que eu aprofunde ou resuma?",
        "Posso ajudar a detalhar isso.",
        "Só um instante para organizar os pontos.",
        f"Você pode confirmar se entendi corretamente: {text}",
    ]


def _should_lookup_knowledge(text: str, classification: str, has_topic: bool, market_terms: List[str]) -> bool:
    lowered = text.lower()
    technical_keywords = [
        "api",
        "backend",
        "frontend",
        "python",
        "javascript",
        "fastapi",
        "docker",
        "kubernetes",
        "cloud",
        "aws",
        "linux",
        "sql",
        "arquitetura",
        "microserv",
    ]
    has_keyword = any(keyword in lowered for keyword in technical_keywords)
    return has_topic or classification == "pergunta técnica" or bool(market_terms) or has_keyword


def _compose_search_query_with_context(state: ConversationState, current_text: str) -> tuple[str, bool]:
    current = (current_text or "").strip()
    if not current:
        return "", False

    previous_user_text = ""
    for turn in reversed(state.transcript[:-1]):
        if str(turn.get("speaker", "")).lower() != "user":
            continue
        candidate = str(turn.get("text", "")).strip()
        if candidate and candidate != current:
            previous_user_text = candidate
            break

    if not previous_user_text:
        return current, False

    if len(previous_user_text) > 180:
        previous_user_text = previous_user_text[:180].rsplit(" ", 1)[0].strip()
    if len(current) > 220:
        current = current[:220].rsplit(" ", 1)[0].strip()

    return f"{previous_user_text} | {current}", True


def _clean_excerpt(text: str, limit: int = 240) -> str:
    cleaned = re.sub(r"\|{2,}", " ", text or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,:;-")
    if len(cleaned) > limit:
        cleaned = cleaned[:limit].rsplit(" ", 1)[0].strip() + "..."
    return cleaned


def _build_knowledge_summary(matches: List[Dict[str, Any]]) -> str:
    if not matches:
        return ""
    snippets = []
    for item in matches[:2]:
        snippet = _clean_excerpt(str(item.get("trecho_relevante", "")))
        if snippet:
            snippets.append(snippet)
    if not snippets:
        return ""
    if len(snippets) == 1:
        return snippets[0]
    return f"{snippets[0]} Além disso, {snippets[1]}"


def _build_knowledge_sources(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources: List[Dict[str, Any]] = []
    for item in matches:
        sources.append(
            {
                "source_file": item.get("source_file", ""),
                "title": item.get("title", ""),
                "chunk_id": item.get("chunk_id", ""),
                "sequence": item.get("sequence", 0),
                "score": item.get("score", 0),
                "matched_tags": item.get("matched_tags", []),
            }
        )
    return sources


def _build_debug_sources(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    debug_sources: List[Dict[str, Any]] = []
    for item in matches:
        debug_sources.append(
            {
                "title": item.get("title", ""),
                "source_file": item.get("source_file", ""),
                "chunk_id": item.get("chunk_id", ""),
                "score": item.get("score", 0),
                "matched_tags": item.get("matched_tags", []),
                "excerpt_summary": _clean_excerpt(str(item.get("trecho_relevante", "")), limit=140),
            }
        )
    return debug_sources


def _build_knowledge_enriched_suggestions(
    text: str,
    topic,
    knowledge_summary: str,
) -> List[str]:
    short_answer = topic.short_answer if topic else "Pelo contexto técnico, o caminho mais seguro é começar por fundamentos e validar em ambiente controlado."
    long_answer = (
        f"Resumo técnico inicial: {knowledge_summary}"
        if knowledge_summary
        else "Posso estruturar a resposta em conceito, implementação e validação prática."
    )
    time_gain = "Só um instante para consolidar os pontos técnicos mais relevantes antes de te responder com precisão."
    counter = f"Você quer foco em visão de arquitetura, passo a passo de implementação, ou troubleshooting para: {text}?"
    kb_line = (
        f"A base de conhecimento local sugere: {knowledge_summary}"
        if knowledge_summary
        else "A base local não retornou detalhe útil agora; posso responder pelo contexto geral e ajustar com exemplos."
    )
    return [short_answer, long_answer, time_gain, counter, kb_line]


def _search_semantic_api_with_context(query: str, limit: int = CONTEXT_LIMIT) -> Dict[str, Any]:
    url = SEMANTIC_API_BASE.rstrip("/") + "/semantic/search"
    payload = {"query": query, "limit": limit, "return_context": True}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"semantic_api_http_error[{exc.code}]: {raw}") from exc
    except Exception as exc:
        raise RuntimeError(f"semantic_api_unavailable: {exc}") from exc

    if data.get("status") != "ok":
        raise RuntimeError(f"semantic_api_error: {data.get('error', 'erro desconhecido')}")

    results = data.get("results", [])
    matches: List[Dict[str, Any]] = []
    for item in results:
        matches.append(
            {
                "source_file": item.get("source_file", ""),
                "title": item.get("title", ""),
                "chunk_id": item.get("chunk_id", ""),
                "sequence": 0,
                "score": item.get("similarity", 0),
                "matched_tags": [],
                "trecho_relevante": item.get("snippet", ""),
            }
        )
    return {
        "matches": matches,
        "context": str(data.get("context", "") or "").strip(),
        "model": data.get("model", ""),
        "count": int(data.get("count", len(matches))),
        "search_cache_hit": bool(data.get("search_cache_hit", False)),
        "embedding_cache_hit": bool(data.get("embedding_cache_hit", False)),
        "openai_called": bool(data.get("openai_called", False)),
        "semantic_path": str(data.get("semantic_path", "") or ""),
    }


def _search_semantic_local_with_context(query: str, limit: int = CONTEXT_LIMIT) -> Dict[str, Any]:
    data = semantic_search(query=query, limit=limit)
    results = data.get("results", [])
    matches: List[Dict[str, Any]] = []
    for item in results:
        matches.append(
            {
                "source_file": item.get("source_file", ""),
                "title": item.get("title", ""),
                "chunk_id": item.get("chunk_id", ""),
                "sequence": 0,
                "score": item.get("similarity", 0),
                "matched_tags": [],
                "trecho_relevante": item.get("snippet", ""),
            }
        )
    return {
        "matches": matches,
        "context": build_context_from_results(query=query, results=matches, top_k=limit) if matches else "",
        "model": data.get("model", ""),
        "count": int(data.get("count", len(matches))),
        "search_cache_hit": bool(data.get("search_cache_hit", False)),
        "embedding_cache_hit": bool(data.get("embedding_cache_hit", False)),
        "openai_called": bool(data.get("openai_called", False)),
        "semantic_path": str(data.get("semantic_path", "") or ""),
    }


def _append_semantic_telemetry(
    *,
    query: str,
    backend: str,
    result_count: int,
    context_len: int,
    semantic_api_ok: bool,
    fallback_used: bool,
    semantic_duration_ms: int,
    search_cache_hit: bool,
    embedding_cache_hit: bool,
    openai_called: bool,
    semantic_path: str,
) -> None:
    try:
        SEMANTIC_TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "backend": backend,
            "result_count": int(result_count),
            "context_len": int(context_len),
            "semantic_api_ok": bool(semantic_api_ok),
            "fallback_used": bool(fallback_used),
            "semantic_duration_ms": int(semantic_duration_ms),
            "search_cache_hit": bool(search_cache_hit),
            "embedding_cache_hit": bool(embedding_cache_hit),
            "openai_called": bool(openai_called),
            "semantic_path": semantic_path,
        }
        with SEMANTIC_TELEMETRY_PATH.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Observabilidade nao deve quebrar o fluxo principal.
        pass


def _apply_relevance_floor(matches: List[Dict[str, Any]], floor: float = RELEVANCE_FLOOR) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for item in matches:
        score = float(item.get("score", 0) or 0)
        if score >= floor:
            filtered.append(item)
    return filtered


def _has_domain_signal(text: str) -> bool:
    return _count_domain_signals(text) > 0


def _count_domain_signals(text: str) -> int:
    lowered = (text or "").lower()
    if not lowered:
        return 0
    return sum(1 for signal in DOMAIN_SIGNALS if signal in lowered)


def _looks_technical_query(text: str) -> bool:
    lowered = (text or "").lower()
    if not lowered:
        return False
    return any(token in lowered for token in TECH_QUERY_SIGNALS)


def _passes_domain_gating(query: str, classification: str, matches: List[Dict[str, Any]], context: str) -> bool:
    if classification != "pergunta técnica" and not _looks_technical_query(query):
        return True
    if _count_domain_signals(query) > 0:
        return True

    chunks: List[str] = []
    for item in matches[:CONTEXT_LIMIT]:
        tags = item.get("matched_tags", [])
        tags_text = " ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""
        chunks.append(
            " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("source_file", "")),
                    str(item.get("trecho_relevante", "")),
                    tags_text,
                ]
            )
        )
    chunks.append(str(context or ""))
    corpus_text = " ".join(chunks)
    corpus_signal_count = _count_domain_signals(corpus_text)
    query_lower = query.lower()
    is_adjacent_tech = any(token in query_lower for token in ADJACENT_TECH_SIGNALS)
    if is_adjacent_tech:
        top_score = 0.0
        if matches:
            try:
                top_score = float(matches[0].get("score", 0) or 0)
            except Exception:
                top_score = 0.0
        # Adjacent technical queries are easier to drift to weak context.
        return corpus_signal_count >= 3 and top_score >= 0.45
    return corpus_signal_count >= 2


def generate_suggestions(state: ConversationState) -> List[str]:
    if not state.transcript:
        return []

    last = state.transcript[-1]["text"]
    classification = _classify_input(last)
    topic = detect_topic(last)

    if topic:
        candidates = _build_topic_suggestions(
            last,
            topic.name,
            topic.short_answer,
            topic.long_answer,
            topic.time_gain,
            topic.counter_question,
            topic.experience_link,
        )
    else:
        candidates = _build_generic_suggestions(last, classification)

    market_terms = match_terms(last, limit=2)
    if market_terms:
        market_line = f"Tenho visto alta demanda por {', '.join(market_terms)} nas vagas recentes."
        candidates.insert(1, market_line)

    used_search = False
    search_query = ""
    search_error = ""
    semantic_error = ""
    semantic_api_ok = False
    fallback_used = False
    semantic_duration_ms = 0
    embedding_cache_hit = False
    search_cache_hit = False
    openai_called = False
    search_backend = ""
    semantic_path = ""
    search_context = ""
    matches: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    search_debug_payload: Dict[str, Any] = {}
    context_used = False
    if _should_lookup_knowledge(last, classification, bool(topic), market_terms):
        used_search = True
        search_query, context_used = _compose_search_query_with_context(state, last)
        semantic_started_at = time.monotonic()
        try:
            semantic_payload = _search_semantic_local_with_context(search_query, limit=CONTEXT_LIMIT)
            semantic_duration_ms = int((time.monotonic() - semantic_started_at) * 1000)
            semantic_api_ok = True
            semantic_matches = semantic_payload.get("matches", [])
            matches = _apply_relevance_floor(semantic_matches)
            search_context = build_context_from_results(query=search_query, results=matches, top_k=CONTEXT_LIMIT) if matches else ""
            domain_gating_blocked = False
            if matches and not _passes_domain_gating(search_query, classification, matches, search_context):
                matches = []
                search_context = ""
                domain_gating_blocked = True
            search_backend = "semantic_local"
            search_debug_payload = {
                "semantic_model": semantic_payload.get("model", ""),
                "semantic_result_count": semantic_payload.get("count", len(semantic_matches)),
                "search_cache_hit": bool(semantic_payload.get("search_cache_hit", False)),
                "embedding_cache_hit": bool(semantic_payload.get("embedding_cache_hit", False)),
                "openai_called": bool(semantic_payload.get("openai_called", False)),
                "semantic_path": str(semantic_payload.get("semantic_path", "") or ""),
                "domain_gating_blocked": domain_gating_blocked,
            }
            search_cache_hit = bool(semantic_payload.get("search_cache_hit", False))
            embedding_cache_hit = bool(semantic_payload.get("embedding_cache_hit", False))
            openai_called = bool(semantic_payload.get("openai_called", False))
            semantic_path = str(semantic_payload.get("semantic_path", "") or "")
        except Exception as local_exc:
            try:
                semantic_payload = _search_semantic_api_with_context(search_query, limit=CONTEXT_LIMIT)
                semantic_duration_ms = int((time.monotonic() - semantic_started_at) * 1000)
                semantic_api_ok = True
                semantic_matches = semantic_payload.get("matches", [])
                matches = _apply_relevance_floor(semantic_matches)
                search_context = (
                    build_context_from_results(query=search_query, results=matches, top_k=CONTEXT_LIMIT) if matches else ""
                )
                domain_gating_blocked = False
                if matches and not _passes_domain_gating(search_query, classification, matches, search_context):
                    matches = []
                    search_context = ""
                    domain_gating_blocked = True
                search_backend = "semantic_api"
                search_debug_payload = {
                    "semantic_model": semantic_payload.get("model", ""),
                    "semantic_result_count": semantic_payload.get("count", len(semantic_matches)),
                    "search_cache_hit": bool(semantic_payload.get("search_cache_hit", False)),
                    "embedding_cache_hit": bool(semantic_payload.get("embedding_cache_hit", False)),
                    "openai_called": bool(semantic_payload.get("openai_called", False)),
                    "semantic_path": str(semantic_payload.get("semantic_path", "") or ""),
                    "domain_gating_blocked": domain_gating_blocked,
                    "local_semantic_error": str(local_exc),
                }
                search_cache_hit = bool(semantic_payload.get("search_cache_hit", False))
                embedding_cache_hit = bool(semantic_payload.get("embedding_cache_hit", False))
                openai_called = bool(semantic_payload.get("openai_called", False))
                semantic_path = str(semantic_payload.get("semantic_path", "") or "")
            except Exception as exc:
                semantic_duration_ms = int((time.monotonic() - semantic_started_at) * 1000)
                semantic_error = f"local: {local_exc} | api: {exc}"
                fallback_used = True
                try:
                    search_payload = search_knowledge_chunks_with_debug(search_query, limit=CONTEXT_LIMIT)
                    matches = search_payload.get("results", [])
                    search_debug_payload = search_payload.get("debug", {})
                    search_backend = "local_knowledge_search"
                except Exception as lexical_exc:
                    matches = []
                    search_error = str(lexical_exc)
                    search_debug_payload = {}
        if matches:
            sources = _build_knowledge_sources(matches)
            knowledge_summary = search_context or _build_knowledge_summary(matches)
            candidates = _build_knowledge_enriched_suggestions(last, topic, knowledge_summary)
            if market_terms:
                candidates.append(f"Complemento de mercado: tenho visto demanda por {', '.join(market_terms)} nas vagas recentes.")

    state.knowledge_context = {
        "query": search_query,
        "used_search": used_search,
        "search_error": search_error,
        "semantic_error": semantic_error,
        "semantic_api_ok": semantic_api_ok,
        "fallback_used": fallback_used,
        "semantic_duration_ms": semantic_duration_ms,
        "search_backend": search_backend,
        "context_used": context_used,
        "context": search_context,
        "result_count": len(sources),
        "query_tags": search_debug_payload.get("query_tags_inferred", {}),
        "query_tags_used": search_debug_payload.get("query_tags_used", []),
        "used_tag_routing": search_debug_payload.get("used_tag_routing", False),
        "used_global_fallback": search_debug_payload.get("used_global_fallback", False),
        "sources": sources,
    }
    if used_search:
        _append_semantic_telemetry(
            query=search_query,
            backend=search_backend,
            result_count=len(sources),
            context_len=len(search_context),
            semantic_api_ok=semantic_api_ok,
            fallback_used=fallback_used,
            semantic_duration_ms=semantic_duration_ms,
            search_cache_hit=search_cache_hit,
            embedding_cache_hit=embedding_cache_hit,
            openai_called=openai_called,
            semantic_path=semantic_path,
        )
    state.knowledge_debug = {
        "used_search": used_search,
        "query": search_query,
        "result_count": len(sources),
        "search_error": search_error,
        "semantic_error": semantic_error,
        "semantic_api_ok": semantic_api_ok,
        "fallback_used": fallback_used,
        "semantic_duration_ms": semantic_duration_ms,
        "search_cache_hit": search_cache_hit,
        "embedding_cache_hit": embedding_cache_hit,
        "openai_called": openai_called,
        "semantic_path": semantic_path,
        "search_backend": search_backend,
        "context_used": context_used,
        "context_len": len(search_context),
        "query_tags_inferred": search_debug_payload.get("query_tags_inferred", {}),
        "query_tags_used": search_debug_payload.get("query_tags_used", []),
        "used_tag_routing": search_debug_payload.get("used_tag_routing", False),
        "used_global_fallback": search_debug_payload.get("used_global_fallback", False),
        "routed_result_count": search_debug_payload.get("routed_result_count", 0),
        "global_result_count": search_debug_payload.get("global_result_count", 0),
        "sources": _build_debug_sources(matches) if used_search else [],
    }

    limit = settings.suggestions_limit
    if sources:
        limit = max(limit, 5)
    return candidates[:limit]
