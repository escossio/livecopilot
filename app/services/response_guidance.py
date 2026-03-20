import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESPONSE_GUIDANCE_FILE = Path("/lab/projects/livecopilot/data/response_guidance.json")
RESPONSE_GUIDANCE_PROPOSALS_DIR = Path("/lab/projects/livecopilot/data/response_guidance_proposals")
VALID_TRIGGER_TYPES = {"normalized_text", "semantic_key"}
VALID_PROPOSAL_STATUSES = {"pending", "approved", "rejected"}
DEFAULT_SCOPE = "livecopilot_reply"


def _normalize(text: str) -> str:
    lowered = str(text or "").strip().lower()
    ascii_text = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_payload() -> dict[str, Any]:
    return {"version": 1, "rules": []}


def _proposal_path(proposal_id: str) -> Path:
    return RESPONSE_GUIDANCE_PROPOSALS_DIR / f"{str(proposal_id or '').strip()}.json"


def _json_tmp_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.tmp")


def _backup_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.bak.{_now_iso().replace(':', '').replace('-', '')}")


def _write_json_atomic(path: Path, payload: dict[str, Any], *, backup_existing: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup_existing and path.exists():
        path.replace(_backup_path(path))
    tmp_path = _json_tmp_path(path)
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _build_rule_payload(
    *,
    rule_id: str,
    scope: str,
    trigger_type: str,
    match_examples: list[str],
    answer: str,
    bullets: list[str] | None = None,
    policy_notes: str = "",
    active: bool = True,
    priority: int = 100,
    created_at: str | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    now_iso = _now_iso()
    return {
        "id": str(rule_id or "").strip(),
        "scope": str(scope or DEFAULT_SCOPE).strip() or DEFAULT_SCOPE,
        "trigger_type": str(trigger_type or "").strip(),
        "match_examples": [str(item).strip() for item in (match_examples or []) if str(item).strip()],
        "preferred_response": {
            "answer": str(answer or "").strip(),
            "bullets": [str(item).strip() for item in (bullets or []) if str(item).strip()],
        },
        "policy_notes": str(policy_notes or "").strip(),
        "active": bool(active),
        "priority": int(priority),
        "created_at": str(created_at or now_iso).strip(),
        "updated_at": str(updated_at or now_iso).strip(),
    }


def _extract_preferred_response(rule: dict[str, Any]) -> dict[str, Any]:
    payload = rule.get("preferred_response", {})
    if isinstance(payload, str):
        return {"answer": payload.strip(), "bullets": []}
    if not isinstance(payload, dict):
        return {"answer": "", "bullets": []}
    answer = str(payload.get("answer", "")).strip()
    bullets = [str(item).strip() for item in payload.get("bullets", []) if str(item).strip()]
    return {"answer": answer, "bullets": bullets}


def load_response_guidance() -> dict[str, Any]:
    try:
        payload = json.loads(RESPONSE_GUIDANCE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return _safe_payload()
    if not isinstance(payload, dict):
        return _safe_payload()
    rules = payload.get("rules", [])
    return {
        "version": int(payload.get("version", 1) or 1),
        "rules": rules if isinstance(rules, list) else [],
    }


def validate_response_guidance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload de response guidance deve ser um objeto")
    version = int(payload.get("version", 1) or 1)
    raw_rules = payload.get("rules", [])
    if not isinstance(raw_rules, list):
        raise ValueError("rules deve ser uma lista")

    normalized_rules: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise ValueError("cada regra deve ser um objeto")
        rule_id = str(raw_rule.get("id", "")).strip()
        if not rule_id:
            raise ValueError("regra sem id")
        if rule_id in seen_ids:
            raise ValueError(f"id duplicado em response_guidance: {rule_id}")
        seen_ids.add(rule_id)

        scope = str(raw_rule.get("scope", "")).strip()
        if not scope:
            raise ValueError(f"regra {rule_id} sem scope")
        trigger_type = str(raw_rule.get("trigger_type", "")).strip()
        if trigger_type not in VALID_TRIGGER_TYPES:
            raise ValueError(f"regra {rule_id} com trigger_type invalido: {trigger_type}")

        match_examples = [str(item).strip() for item in raw_rule.get("match_examples", []) if str(item).strip()]
        if not match_examples:
            raise ValueError(f"regra {rule_id} sem match_examples")

        preferred_response = _extract_preferred_response(raw_rule)
        if not preferred_response.get("answer"):
            raise ValueError(f"regra {rule_id} sem preferred_response.answer")

        created_at = str(raw_rule.get("created_at", "")).strip()
        updated_at = str(raw_rule.get("updated_at", "")).strip()
        if not created_at or not updated_at:
            raise ValueError(f"regra {rule_id} sem created_at/updated_at")

        normalized_rules.append(
            {
                "id": rule_id,
                "scope": scope,
                "trigger_type": trigger_type,
                "match_examples": match_examples,
                "preferred_response": preferred_response,
                "policy_notes": str(raw_rule.get("policy_notes", "")).strip(),
                "active": bool(raw_rule.get("active", False)),
                "priority": int(raw_rule.get("priority", 0) or 0),
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    return {"version": version, "rules": normalized_rules}


def save_response_guidance(payload: dict[str, Any]) -> dict[str, Any]:
    validated = validate_response_guidance_payload(payload)
    _write_json_atomic(RESPONSE_GUIDANCE_FILE, validated, backup_existing=True)
    return validated


def list_response_guidance_rules(*, include_inactive: bool = True) -> list[dict[str, Any]]:
    payload = validate_response_guidance_payload(load_response_guidance())
    rules = payload["rules"]
    if include_inactive:
        return rules
    return [rule for rule in rules if bool(rule.get("active", False))]


def get_response_guidance_rule(rule_id: str) -> dict[str, Any] | None:
    clean_id = str(rule_id or "").strip()
    if not clean_id:
        return None
    for rule in list_response_guidance_rules(include_inactive=True):
        if str(rule.get("id", "")).strip() == clean_id:
            return rule
    return None


def add_response_guidance_rule(
    *,
    rule_id: str,
    scope: str,
    trigger_type: str,
    match_examples: list[str],
    answer: str,
    bullets: list[str] | None = None,
    policy_notes: str = "",
    active: bool = True,
    priority: int = 100,
    created_at: str | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    payload = validate_response_guidance_payload(load_response_guidance())
    clean_id = str(rule_id or "").strip()
    if not clean_id:
        raise ValueError("id obrigatorio")
    if get_response_guidance_rule(clean_id):
        raise ValueError(f"id duplicado em response_guidance: {clean_id}")

    payload["rules"].append(
        _build_rule_payload(
            rule_id=clean_id,
            scope=scope,
            trigger_type=trigger_type,
            match_examples=match_examples,
            answer=answer,
            bullets=bullets,
            policy_notes=policy_notes,
            active=active,
            priority=priority,
            created_at=created_at,
            updated_at=updated_at,
        )
    )
    saved = save_response_guidance(payload)
    rule = next((item for item in saved["rules"] if item["id"] == clean_id), None)
    if not rule:
        raise ValueError("falha ao persistir regra nova")
    return rule


def _safe_proposal_payload() -> dict[str, Any]:
    return {"proposal_id": "", "status": "pending", "created_at": "", "proposed_rule": {}}


def _iter_proposal_paths() -> list[Path]:
    if not RESPONSE_GUIDANCE_PROPOSALS_DIR.exists():
        return []
    return sorted(path for path in RESPONSE_GUIDANCE_PROPOSALS_DIR.glob("*.json") if path.is_file())


def load_response_guidance_proposal(proposal_id: str) -> dict[str, Any] | None:
    path = _proposal_path(proposal_id)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"falha ao ler proposal {proposal_id}: {exc}") from exc
    return validate_response_guidance_proposal_payload(payload)


def list_response_guidance_proposals(*, status: str | None = None) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    for path in _iter_proposal_paths():
        payload = validate_response_guidance_proposal_payload(json.loads(path.read_text(encoding="utf-8")))
        if status and payload["status"] != status:
            continue
        proposals.append(payload)
    return proposals


def validate_response_guidance_proposal_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("proposal deve ser um objeto")
    proposal_id = str(payload.get("proposal_id", "")).strip()
    if not proposal_id:
        raise ValueError("proposal sem proposal_id")
    status = str(payload.get("status", "")).strip()
    if status not in VALID_PROPOSAL_STATUSES:
        raise ValueError(f"proposal {proposal_id} com status invalido: {status}")
    created_at = str(payload.get("created_at", "")).strip()
    if not created_at:
        raise ValueError(f"proposal {proposal_id} sem created_at")
    proposed_rule_raw = payload.get("proposed_rule")
    normalized = validate_response_guidance_payload({"version": 1, "rules": [proposed_rule_raw]})
    return {
        "proposal_id": proposal_id,
        "status": status,
        "created_at": created_at,
        "proposed_rule": normalized["rules"][0],
    }


def save_response_guidance_proposal(payload: dict[str, Any], *, backup_existing: bool = True) -> dict[str, Any]:
    validated = validate_response_guidance_proposal_payload(payload)
    _write_json_atomic(_proposal_path(validated["proposal_id"]), validated, backup_existing=backup_existing)
    return validated


def _proposal_rule_id_exists(rule_id: str, *, include_rejected: bool = False, exclude_proposal_id: str | None = None) -> bool:
    clean_rule_id = str(rule_id or "").strip()
    if not clean_rule_id:
        return False
    for proposal in list_response_guidance_proposals():
        if exclude_proposal_id and proposal["proposal_id"] == exclude_proposal_id:
            continue
        if proposal["proposed_rule"]["id"] != clean_rule_id:
            continue
        if include_rejected or proposal["status"] != "rejected":
            return True
    return False


def propose_response_guidance_rule(
    *,
    proposal_id: str,
    rule_id: str,
    scope: str,
    trigger_type: str,
    match_examples: list[str],
    answer: str,
    bullets: list[str] | None = None,
    policy_notes: str = "",
    active: bool = True,
    priority: int = 100,
) -> dict[str, Any]:
    clean_proposal_id = str(proposal_id or "").strip()
    clean_rule_id = str(rule_id or "").strip()
    if not clean_proposal_id:
        raise ValueError("proposal_id obrigatorio")
    if _proposal_path(clean_proposal_id).exists():
        raise ValueError(f"proposal_id duplicado: {clean_proposal_id}")
    if get_response_guidance_rule(clean_rule_id):
        raise ValueError(f"id duplicado em response_guidance: {clean_rule_id}")
    if _proposal_rule_id_exists(clean_rule_id):
        raise ValueError(f"ja existe proposal pendente/aprovada para a regra: {clean_rule_id}")

    proposal = {
        "proposal_id": clean_proposal_id,
        "status": "pending",
        "created_at": _now_iso(),
        "proposed_rule": _build_rule_payload(
            rule_id=clean_rule_id,
            scope=scope,
            trigger_type=trigger_type,
            match_examples=match_examples,
            answer=answer,
            bullets=bullets,
            policy_notes=policy_notes,
            active=active,
            priority=priority,
        ),
    }
    return save_response_guidance_proposal(proposal, backup_existing=False)


def approve_response_guidance_proposal(proposal_id: str) -> dict[str, Any]:
    proposal = load_response_guidance_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"proposal nao encontrada: {proposal_id}")
    if proposal["status"] != "pending":
        raise ValueError(f"proposal {proposal_id} nao esta pending")

    proposed_rule = dict(proposal["proposed_rule"])
    proposed_rule["updated_at"] = _now_iso()
    add_response_guidance_rule(
        rule_id=proposed_rule["id"],
        scope=proposed_rule["scope"],
        trigger_type=proposed_rule["trigger_type"],
        match_examples=proposed_rule["match_examples"],
        answer=proposed_rule["preferred_response"]["answer"],
        bullets=proposed_rule["preferred_response"]["bullets"],
        policy_notes=proposed_rule["policy_notes"],
        active=proposed_rule["active"],
        priority=proposed_rule["priority"],
        created_at=proposed_rule["created_at"],
        updated_at=proposed_rule["updated_at"],
    )
    proposal["status"] = "approved"
    proposal["proposed_rule"]["updated_at"] = proposed_rule["updated_at"]
    return save_response_guidance_proposal(proposal, backup_existing=True)


def reject_response_guidance_proposal(proposal_id: str) -> dict[str, Any]:
    proposal = load_response_guidance_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"proposal nao encontrada: {proposal_id}")
    if proposal["status"] != "pending":
        raise ValueError(f"proposal {proposal_id} nao esta pending")
    proposal["status"] = "rejected"
    return save_response_guidance_proposal(proposal, backup_existing=True)


def set_response_guidance_rule_active(rule_id: str, active: bool) -> dict[str, Any]:
    payload = validate_response_guidance_payload(load_response_guidance())
    clean_id = str(rule_id or "").strip()
    now_iso = _now_iso()
    found = None
    for rule in payload["rules"]:
        if str(rule.get("id", "")).strip() != clean_id:
            continue
        rule["active"] = bool(active)
        rule["updated_at"] = now_iso
        found = rule
        break
    if not found:
        raise ValueError(f"regra nao encontrada: {clean_id}")
    save_response_guidance(payload)
    return found


def update_response_guidance_rule(
    *,
    rule_id: str,
    answer: str | None = None,
    bullets: list[str] | None = None,
    match_examples: list[str] | None = None,
    policy_notes: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    payload = validate_response_guidance_payload(load_response_guidance())
    clean_id = str(rule_id or "").strip()
    now_iso = _now_iso()
    found = None
    for rule in payload["rules"]:
        if str(rule.get("id", "")).strip() != clean_id:
            continue
        if answer is not None:
            preferred = _extract_preferred_response(rule)
            preferred["answer"] = str(answer).strip()
            if bullets is not None:
                preferred["bullets"] = [str(item).strip() for item in bullets if str(item).strip()]
            rule["preferred_response"] = preferred
        elif bullets is not None:
            preferred = _extract_preferred_response(rule)
            preferred["bullets"] = [str(item).strip() for item in bullets if str(item).strip()]
            rule["preferred_response"] = preferred
        if match_examples is not None:
            rule["match_examples"] = [str(item).strip() for item in match_examples if str(item).strip()]
        if policy_notes is not None:
            rule["policy_notes"] = str(policy_notes).strip()
        if priority is not None:
            rule["priority"] = int(priority)
        rule["updated_at"] = now_iso
        found = rule
        break
    if not found:
        raise ValueError(f"regra nao encontrada: {clean_id}")
    save_response_guidance(payload)
    return found


def resolve_response_guidance(
    *,
    query: str,
    semantic_keys: list[str] | None = None,
    scope: str = DEFAULT_SCOPE,
) -> dict[str, Any]:
    normalized_query = _normalize(query)
    normalized_scope = str(scope or "").strip()
    normalized_semantic_keys = {_normalize(item) for item in (semantic_keys or []) if _normalize(item)}
    payload = validate_response_guidance_payload(load_response_guidance())
    rules = payload.get("rules", [])

    candidates: list[dict[str, Any]] = []
    for raw_rule in rules:
        if not isinstance(raw_rule, dict):
            continue
        if not bool(raw_rule.get("active", False)):
            continue
        if str(raw_rule.get("scope", "")).strip() != normalized_scope:
            continue
        trigger_type = str(raw_rule.get("trigger_type", "")).strip()
        examples = [_normalize(item) for item in raw_rule.get("match_examples", []) if _normalize(item)]
        matched = False
        if trigger_type == "normalized_text" and normalized_query:
            matched = normalized_query in examples
        elif trigger_type == "semantic_key" and normalized_semantic_keys:
            matched = any(example in normalized_semantic_keys for example in examples)
        if matched:
            candidates.append(raw_rule)

    if not candidates:
        return {"matched": False}

    selected = sorted(
        candidates,
        key=lambda item: (
            1 if str(item.get("trigger_type", "")).strip() == "normalized_text" else 0,
            int(item.get("priority", 0) or 0),
            str(item.get("updated_at", "")).strip(),
            str(item.get("id", "")).strip(),
        ),
        reverse=True,
    )[0]
    preferred = _extract_preferred_response(selected)
    if not preferred.get("answer"):
        return {"matched": False}
    return {
        "matched": True,
        "rule_id": str(selected.get("id", "")).strip(),
        "scope": str(selected.get("scope", "")).strip(),
        "trigger_type": str(selected.get("trigger_type", "")).strip(),
        "match_examples": [str(item).strip() for item in selected.get("match_examples", []) if str(item).strip()],
        "answer": preferred["answer"],
        "bullets": preferred["bullets"],
        "policy_notes": str(selected.get("policy_notes", "")).strip(),
        "priority": int(selected.get("priority", 0) or 0),
        "created_at": str(selected.get("created_at", "")).strip(),
        "updated_at": str(selected.get("updated_at", "")).strip(),
        "version": int(payload.get("version", 0) or 0),
        "semantic_keys": sorted(normalized_semantic_keys),
        "source_file": str(RESPONSE_GUIDANCE_FILE),
    }


def _parse_json_list(value: str | None) -> list[str]:
    if value is None:
        return []
    raw = str(value).strip()
    if not raw:
        return []
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        raise ValueError("valor JSON deve ser lista")
    return [str(item).strip() for item in parsed if str(item).strip()]


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manutencao controlada de response guidance")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="Lista regras")
    list_cmd.add_argument("--inactive-only", action="store_true")

    add_cmd = sub.add_parser("add", help="Adiciona regra")
    add_cmd.add_argument("--id", required=True)
    add_cmd.add_argument("--scope", default=DEFAULT_SCOPE)
    add_cmd.add_argument("--trigger-type", required=True, choices=sorted(VALID_TRIGGER_TYPES))
    add_cmd.add_argument("--match-examples", required=True, help='JSON list, ex: ["bom dia"]')
    add_cmd.add_argument("--answer", required=True)
    add_cmd.add_argument("--bullets", default="[]", help='JSON list')
    add_cmd.add_argument("--policy-notes", default="")
    add_cmd.add_argument("--priority", type=int, default=100)
    add_cmd.add_argument("--inactive", action="store_true")

    update_cmd = sub.add_parser("update", help="Atualiza resposta/regra existente")
    update_cmd.add_argument("--id", required=True)
    update_cmd.add_argument("--answer")
    update_cmd.add_argument("--bullets", help='JSON list')
    update_cmd.add_argument("--match-examples", help='JSON list')
    update_cmd.add_argument("--policy-notes")
    update_cmd.add_argument("--priority", type=int)

    disable_cmd = sub.add_parser("disable", help="Desativa regra")
    disable_cmd.add_argument("--id", required=True)

    enable_cmd = sub.add_parser("enable", help="Reativa regra")
    enable_cmd.add_argument("--id", required=True)

    show_cmd = sub.add_parser("show", help="Mostra regra")
    show_cmd.add_argument("--id", required=True)

    propose_cmd = sub.add_parser("propose", help="Cria proposal de nova regra")
    propose_cmd.add_argument("--proposal-id", required=True)
    propose_cmd.add_argument("--id", required=True)
    propose_cmd.add_argument("--scope", default=DEFAULT_SCOPE)
    propose_cmd.add_argument("--trigger-type", required=True, choices=sorted(VALID_TRIGGER_TYPES))
    propose_cmd.add_argument("--match-examples", required=True, help='JSON list, ex: ["bom dia"]')
    propose_cmd.add_argument("--answer", required=True)
    propose_cmd.add_argument("--bullets", default="[]", help='JSON list')
    propose_cmd.add_argument("--policy-notes", default="")
    propose_cmd.add_argument("--priority", type=int, default=100)
    propose_cmd.add_argument("--inactive", action="store_true")

    list_proposals_cmd = sub.add_parser("list-proposals", help="Lista proposals")
    list_proposals_cmd.add_argument("--status", choices=sorted(VALID_PROPOSAL_STATUSES))

    show_proposal_cmd = sub.add_parser("show-proposal", help="Mostra proposal")
    show_proposal_cmd.add_argument("--proposal-id", required=True)

    approve_cmd = sub.add_parser("approve", help="Aprova proposal")
    approve_cmd.add_argument("--proposal-id", required=True)

    reject_cmd = sub.add_parser("reject", help="Rejeita proposal")
    reject_cmd.add_argument("--proposal-id", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_cli()
    args = parser.parse_args(argv)

    if args.command == "list":
        rules = list_response_guidance_rules(include_inactive=True)
        if args.inactive_only:
            rules = [rule for rule in rules if not bool(rule.get("active", False))]
        print(json.dumps({"version": load_response_guidance().get("version", 1), "rules": rules}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "show":
        rule = get_response_guidance_rule(args.id)
        if not rule:
            raise SystemExit(f"regra nao encontrada: {args.id}")
        print(json.dumps(rule, ensure_ascii=False, indent=2))
        return 0

    if args.command == "add":
        rule = add_response_guidance_rule(
            rule_id=args.id,
            scope=args.scope,
            trigger_type=args.trigger_type,
            match_examples=_parse_json_list(args.match_examples),
            answer=args.answer,
            bullets=_parse_json_list(args.bullets),
            policy_notes=args.policy_notes,
            active=not bool(args.inactive),
            priority=args.priority,
        )
        print(json.dumps(rule, ensure_ascii=False, indent=2))
        return 0

    if args.command == "propose":
        proposal = propose_response_guidance_rule(
            proposal_id=args.proposal_id,
            rule_id=args.id,
            scope=args.scope,
            trigger_type=args.trigger_type,
            match_examples=_parse_json_list(args.match_examples),
            answer=args.answer,
            bullets=_parse_json_list(args.bullets),
            policy_notes=args.policy_notes,
            active=not bool(args.inactive),
            priority=args.priority,
        )
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0

    if args.command == "list-proposals":
        print(json.dumps({"proposals": list_response_guidance_proposals(status=args.status)}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "show-proposal":
        proposal = load_response_guidance_proposal(args.proposal_id)
        if not proposal:
            raise SystemExit(f"proposal nao encontrada: {args.proposal_id}")
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0

    if args.command == "approve":
        proposal = approve_response_guidance_proposal(args.proposal_id)
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0

    if args.command == "reject":
        proposal = reject_response_guidance_proposal(args.proposal_id)
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0

    if args.command == "update":
        rule = update_response_guidance_rule(
            rule_id=args.id,
            answer=args.answer,
            bullets=_parse_json_list(args.bullets) if args.bullets is not None else None,
            match_examples=_parse_json_list(args.match_examples) if args.match_examples is not None else None,
            policy_notes=args.policy_notes,
            priority=args.priority,
        )
        print(json.dumps(rule, ensure_ascii=False, indent=2))
        return 0

    if args.command == "disable":
        rule = set_response_guidance_rule_active(args.id, False)
        print(json.dumps(rule, ensure_ascii=False, indent=2))
        return 0

    if args.command == "enable":
        rule = set_response_guidance_rule_active(args.id, True)
        print(json.dumps(rule, ensure_ascii=False, indent=2))
        return 0

    raise SystemExit(f"comando nao suportado: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
