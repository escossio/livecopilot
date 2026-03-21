import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RESPONSE_QUALITY_FILE = Path("/lab/projects/livecopilot/var/response_quality.ndjson")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _preview(text: str, limit: int = 180) -> str:
    value = " ".join(str(text or "").split()).strip()
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].strip() + "..."


def _is_pt_br(text: str) -> bool:
    return bool(re.search(r"[áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]", str(text or "")))


def _looks_like_fallback(text: str) -> bool:
    lowered = str(text or "").strip().lower()
    fallback_markers = (
        "caminho inicial",
        "falta uma fonte confiável",
        "ainda falta uma fonte",
        "posso te adiantar",
        "posso responder de forma curta",
        "sem despejar a fonte bruta",
        "contexto completa",
        "só um instante",
    )
    return any(marker in lowered for marker in fallback_markers)


def _looks_like_raw_doc(text: str) -> bool:
    lowered = str(text or "").strip().lower()
    raw_markers = (
        "this tutorial",
        "in this section",
        "for more information",
        "please note",
        "use the following",
        "documentation",
        "reference",
        "kubernetes.io",
        "docs/",
        "http://",
        "https://",
    )
    return any(marker in lowered for marker in raw_markers)


def _looks_mixed(text: str) -> bool:
    lowered = str(text or "").lower()
    english_markers = (" the ", " and ", " you ", " use ", " this ", " that ", " with ")
    pt_markers = (" você ", " voce ", " para ", " como ", " no ", " em ")
    english_hits = sum(1 for marker in english_markers if marker in f" {lowered} ")
    pt_hits = sum(1 for marker in pt_markers if marker in f" {lowered} ")
    return english_hits >= 2 and pt_hits >= 1


def _looks_english(text: str) -> bool:
    lowered = str(text or "").lower()
    english_markers = (" the ", " and ", " you ", " use ", " this ", " that ", " with ", " tutorial ")
    pt_markers = (" você ", " voce ", " para ", " como ", " no ", " em ", " lscpu ", " apt ", " systemctl ")
    english_hits = sum(1 for marker in english_markers if marker in f" {lowered} ")
    pt_hits = sum(1 for marker in pt_markers if marker in f" {lowered} ")
    return english_hits >= 3 and pt_hits == 0


def _looks_like_drift(query: str, response: str) -> bool:
    q = str(query or "").lower()
    r = str(response or "").lower()
    if not q or not r:
        return False
    if "linux" in q and any(token in r for token in ("kubernetes", "docker", "terraform", "pod", "service")) and not any(
        token in r for token in ("cpu", "lscpu", "nginx", "apt", "systemctl")
    ):
        return True
    if "terraform" in q and not any(token in r for token in ("terraform", "infraestrutura como código", "state", "plan", "apply")):
        return True
    return False


def _quality_label(query: str, response: str) -> tuple[str, str]:
    clean = str(response or "").strip()
    if not clean:
        return "RESPOSTA_FRACA", "resposta vazia"
    if _looks_like_raw_doc(clean):
        return "TRECHO_CRU_DE_DOCUMENTACAO", "trecho com cara de documentacao bruta"
    if _looks_like_fallback(clean):
        return "FALLBACK_DISFARCADO", "linguagem de fallback ou clarificacao"
    if _looks_english(clean) and not _is_pt_br(clean):
        return "IDIOMA_ERRADO", "ingles predominante"
    if _looks_mixed(clean):
        return "MISTA", "mistura de pt e en"
    if _looks_like_drift(query, clean):
        return "DRIFT_DE_DOMINIO", "desvio de dominio na resposta"
    if len(re.findall(r"[a-zA-ZÀ-ÿ0-9]+", clean)) < 4:
        return "RESPOSTA_FRACA", "resposta curta demais"
    if len(clean) < 40 and ("?" in clean or "posso" in clean.lower()):
        return "RESPOSTA_FRACA", "resposta curta ou indecisa"
    return "OK", "resposta aceitavel"


def classify_response_quality(
    *,
    query: str,
    response: str,
    knowledge_context: dict[str, Any] | None = None,
    route_or_source_hint: str = "",
) -> dict[str, Any]:
    knowledge_context = knowledge_context if isinstance(knowledge_context, dict) else {}
    label, reason = _quality_label(query, response)
    language_detected = "pt-BR" if _is_pt_br(response) else "en/misto" if _looks_mixed(response) else "en" if _looks_english(response) else "pt-BR"
    row = {
        "ts": _now_iso(),
        "query": str(query or "").strip(),
        "response_preview": _preview(response, limit=180),
        "quality_label": label,
        "quality_reason": reason,
        "language_detected": language_detected,
        "route_or_source_hint": str(route_or_source_hint or "").strip(),
        "confidence": knowledge_context.get("confidence"),
        "result_count": int(knowledge_context.get("result_count", 0) or 0),
        "search_backend": str(knowledge_context.get("search_backend", "") or ""),
    }
    return row


def append_response_quality_event(row: dict[str, Any]) -> None:
    RESPONSE_QUALITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESPONSE_QUALITY_FILE.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")
