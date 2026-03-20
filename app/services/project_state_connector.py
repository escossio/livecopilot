import json
import re
import unicodedata
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = PROJECT_ROOT / "docs"
STATUS_PATH = PROJECT_ROOT / "STATUS.md"
PROJECT_STATUS_STATE_PATH = DOCS_DIR / "project_status_state.json"
PROJECT_STAGE_INDEX_PATH = DOCS_DIR / "PROJECT_STAGE_INDEX.md"
PUBLIC_DEPLOYMENT_HANDOFF_PATH = DOCS_DIR / "HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z.md"


def _normalize(text: str) -> str:
    lowered = str(text or "").strip().lower()
    ascii_text = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _extract_section(markdown: str, heading: str) -> str:
    lines = str(markdown or "").splitlines()
    capture = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == heading.strip():
            capture = True
            collected.append(line)
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            collected.append(line)
    return "\n".join(collected).strip()


def _extract_latest_checkpoint(markdown: str) -> str:
    checkpoints: list[str] = []
    for line in str(markdown or "").splitlines():
        clean = line.strip()
        if clean.startswith("## Checkpoint "):
            checkpoints.append(clean.removeprefix("## ").strip())
    return checkpoints[-1] if checkpoints else ""


def _extract_handoff_timestamp(path: Path) -> str:
    match = re.search(r"_(\d{8}T\d{6}Z)\.md$", path.name)
    return match.group(1) if match else ""


def _find_latest_handoff() -> Path | None:
    handoffs = [path for path in DOCS_DIR.glob("HANDOFF_*.md") if path.is_file()]
    if not handoffs:
        return None
    return max(
        handoffs,
        key=lambda path: (
            _extract_handoff_timestamp(path),
            path.stat().st_mtime,
            path.name,
        ),
    )


def _summarize_handoff(path: Path | None) -> str:
    if path is None:
        return ""
    lines = [line.strip() for line in _read_text(path).splitlines() if line.strip()]
    filtered = []
    for line in lines[1:]:
        lowered = line.lower()
        if lowered.startswith("status final"):
            continue
        if line == "- concluido":
            continue
        filtered.append(line)
    return filtered[0] if filtered else path.name


def _infer_project_state_intent(query: str) -> str:
    normalized = _normalize(query)
    if not normalized:
        return ""
    if "ultimo handoff" in normalized or "ultimo repasse" in normalized or "latest handoff" in normalized:
        return "latest_handoff"
    if "checkpoint" in normalized or "ultimo status" in normalized or "estado atual" in normalized:
        return "latest_checkpoint"
    if "publicacao publica" in normalized or "public deployment" in normalized:
        return "public_deployment"
    if "status do projeto" in normalized or "estado do projeto" in normalized:
        return "project_status"
    project_signal = "livecopilot" in normalized or "projeto" in normalized or "infra" in normalized
    state_signal = any(
        token in normalized
        for token in (
            "status",
            "estado",
            "checkpoint",
            "handoff",
            "publicacao",
            "deployment",
            "dominio",
            "websocket",
        )
    )
    if project_signal and state_signal:
        return "project_status"
    return ""


def resolve_project_state_query(query: str) -> dict[str, Any]:
    intent = _infer_project_state_intent(query)
    if not intent:
        return {"matched": False}

    status_text = _read_text(STATUS_PATH)
    state_payload = _load_json(PROJECT_STATUS_STATE_PATH)
    latest_checkpoint = _extract_latest_checkpoint(status_text)
    latest_handoff = _find_latest_handoff()
    latest_handoff_name = latest_handoff.name if latest_handoff else ""
    latest_handoff_summary = _summarize_handoff(latest_handoff)
    publication_section = _extract_section(status_text, "## Publicacao Livecopilot HTTPS")
    deployment_handoff_exists = PUBLIC_DEPLOYMENT_HANDOFF_PATH.exists()

    current_stage = str(state_payload.get("now", {}).get("current_stage", "") or "").strip()
    current_blocker = str(state_payload.get("now", {}).get("current_blocker", "") or "").strip()
    next_step = str(state_payload.get("now", {}).get("next_step", "") or "").strip()

    if intent == "latest_handoff":
        answer = (
            f"O ultimo handoff local e `{latest_handoff_name}`."
            if latest_handoff_name
            else "Nao encontrei handoff local para resumir."
        )
        bullets = [
            f"Resumo: {latest_handoff_summary or 'sem resumo extraido'}",
            f"Checkpoint atual: {latest_checkpoint or 'nao identificado no STATUS.md'}",
            f"Fonte canonica: docs/HANDOFF_*.md",
        ]
    elif intent == "latest_checkpoint":
        answer = (
            f"O checkpoint mais recente registrado e `{latest_checkpoint}`."
            if latest_checkpoint
            else "Nao encontrei checkpoint recente no STATUS.md."
        )
        bullets = [
            f"Etapa atual: {current_stage or 'nao identificada em docs/project_status_state.json'}",
            f"Ultimo handoff: {latest_handoff_name or 'nao encontrado'}",
            f"Proximo passo registrado: {next_step or 'nao registrado'}",
        ]
    elif intent == "public_deployment":
        answer = "A publicacao publica atual do Livecopilot esta funcional em `https://livecopilot.escossio.dev.br`."
        bullets = [
            "Infra: Apache reverse proxy com TLS Let's Encrypt.",
            "Backend interno publicado: 10.45.0.3:8000.",
            "WebSocket operacional em /ws e interface de voz + texto ativa via HTTPS.",
        ]
    else:
        answer = "O estado atual do projeto aponta o Livecopilot como ativo, com publicacao HTTPS funcional e etapa oficial registrada em artefatos locais."
        bullets = [
            f"Etapa atual: {current_stage or 'nao identificada'}.",
            f"Checkpoint recente: {latest_checkpoint or 'nao identificado'}.",
            f"Ultimo handoff: {latest_handoff_name or 'nao encontrado'}.",
        ]
        if current_blocker:
            bullets.append(f"Bloqueio registrado: {current_blocker}.")
        if next_step:
            bullets.append(f"Proximo passo registrado: {next_step}.")

    source_paths = [
        str(STATUS_PATH),
        str(PROJECT_STATUS_STATE_PATH),
        str(PROJECT_STAGE_INDEX_PATH),
    ]
    if latest_handoff_name:
        source_paths.append(str(latest_handoff))
    if deployment_handoff_exists:
        source_paths.append(str(PUBLIC_DEPLOYMENT_HANDOFF_PATH))

    connector_context = {
        "query": str(query or "").strip(),
        "used_search": False,
        "search_backend": "project_state_connector",
        "context_used": False,
        "fallback_used": False,
        "semantic_api_ok": False,
        "semantic_duration_ms": 0,
        "result_count": len(source_paths),
        "context": publication_section or latest_handoff_summary or current_stage or latest_checkpoint,
        "sources": [{"title": Path(path).name, "source_file": path} for path in source_paths],
        "connector": "project_state_connector",
        "intent": intent,
        "latest_checkpoint": latest_checkpoint,
        "latest_handoff": latest_handoff_name,
    }
    return {
        "matched": True,
        "intent": intent,
        "answer": answer,
        "bullets": bullets[:4],
        "knowledge_context": connector_context,
    }
