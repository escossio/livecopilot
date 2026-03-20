import json
import re
import unicodedata
from pathlib import Path
from typing import Any

OPERATIONAL_SKILLS_FILE = Path("/lab/projects/livecopilot/data/operational_skills.json")
VALID_ACTION_TYPES = {"connector_call", "router_read_only"}
VALID_SAFETY_MODES = {"read_only", "controlled"}


def _normalize(text: str) -> str:
    lowered = str(text or "").strip().lower()
    ascii_text = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^a-z0-9]+", " ", ascii_text)
    return re.sub(r"\s+", " ", compact).strip()


def _safe_payload() -> dict[str, Any]:
    return {"version": 1, "skills": []}


def load_operational_skills() -> dict[str, Any]:
    try:
        payload = json.loads(OPERATIONAL_SKILLS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return _safe_payload()
    return validate_operational_skills_payload(payload)


def validate_operational_skills_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload de operational_skills deve ser um objeto")
    version = int(payload.get("version", 1) or 1)
    raw_skills = payload.get("skills", [])
    if not isinstance(raw_skills, list):
        raise ValueError("skills deve ser uma lista")

    normalized_skills: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw_skill in raw_skills:
        if not isinstance(raw_skill, dict):
            raise ValueError("cada skill deve ser um objeto")
        skill_id = str(raw_skill.get("id", "")).strip()
        if not skill_id:
            raise ValueError("skill sem id")
        if skill_id in seen_ids:
            raise ValueError(f"id duplicado em operational_skills: {skill_id}")
        seen_ids.add(skill_id)

        intent = str(raw_skill.get("intent", "")).strip()
        target = str(raw_skill.get("target", "")).strip()
        source = str(raw_skill.get("source", "")).strip()
        notes = str(raw_skill.get("notes", "")).strip()
        trigger_examples = [str(item).strip() for item in raw_skill.get("trigger_examples", []) if str(item).strip()]
        if not intent:
            raise ValueError(f"skill {skill_id} sem intent")
        if not trigger_examples:
            raise ValueError(f"skill {skill_id} sem trigger_examples")
        if not target:
            raise ValueError(f"skill {skill_id} sem target")
        if not source:
            raise ValueError(f"skill {skill_id} sem source")

        action = raw_skill.get("action", {})
        if not isinstance(action, dict):
            raise ValueError(f"skill {skill_id} com action invalido")
        action_type = str(action.get("type", "")).strip()
        operation = str(action.get("operation", "")).strip()
        if action_type not in VALID_ACTION_TYPES:
            raise ValueError(f"skill {skill_id} com action.type invalido: {action_type}")
        if not operation:
            raise ValueError(f"skill {skill_id} sem action.operation")

        response_policy = raw_skill.get("response_policy", {})
        if not isinstance(response_policy, dict):
            raise ValueError(f"skill {skill_id} com response_policy invalido")
        summary_template = str(response_policy.get("summary_template", "")).strip()
        detail_template = str(response_policy.get("detail_template", "")).strip()
        if not summary_template or not detail_template:
            raise ValueError(f"skill {skill_id} sem response_policy completo")

        safety = raw_skill.get("safety", {})
        if not isinstance(safety, dict):
            raise ValueError(f"skill {skill_id} com safety invalido")
        safety_mode = str(safety.get("mode", "")).strip()
        if safety_mode not in VALID_SAFETY_MODES:
            raise ValueError(f"skill {skill_id} com safety.mode invalido: {safety_mode}")

        normalized_skills.append(
            {
                "id": skill_id,
                "active": bool(raw_skill.get("active", False)),
                "intent": intent,
                "trigger_examples": trigger_examples,
                "target": target,
                "source": source,
                "action": {
                    "type": action_type,
                    "operation": operation,
                },
                "response_policy": {
                    "summary_template": summary_template,
                    "detail_template": detail_template,
                },
                "safety": {
                    "mode": safety_mode,
                    "approval_required": bool(safety.get("approval_required", False)),
                },
                "notes": notes,
            }
        )

    return {"version": version, "skills": normalized_skills}


def get_skill_by_id(skill_id: str) -> dict[str, Any] | None:
    clean_id = str(skill_id or "").strip()
    if not clean_id:
        return None
    for skill in load_operational_skills()["skills"]:
        if skill["id"] == clean_id:
            return skill
    return None


def match_operational_skill(text: str) -> dict[str, Any]:
    normalized_text = _normalize(text)
    if not normalized_text:
        return {"matched": False}

    candidates: list[dict[str, Any]] = []
    for skill in load_operational_skills()["skills"]:
        if not bool(skill.get("active", False)):
            continue
        examples = [_normalize(item) for item in skill.get("trigger_examples", []) if _normalize(item)]
        if normalized_text in examples:
            candidates.append(skill)

    if not candidates:
        return {"matched": False}

    selected = sorted(candidates, key=lambda item: (len(item.get("trigger_examples", [])), item["id"]), reverse=True)[0]
    return {
        "matched": True,
        "skill": selected,
        "intent": selected["intent"],
        "target": selected["target"],
        "source": selected["source"],
        "action": selected["action"],
        "response_policy": selected["response_policy"],
        "safety": selected["safety"],
    }
