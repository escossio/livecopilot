import argparse
import filecmp
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SOURCE_INDEXES_DIR = DATA_DIR / "source_indexes"
SOURCE_CANDIDATES_DIR = DATA_DIR / "source_candidates"
RAW_REVIEW_DIR = DATA_DIR / "raw_review"
QUESTION_BANK_LOW_TRUST_DIR = DATA_DIR / "question_bank_low_trust"
COVERAGE_INPUTS_DIR = DATA_DIR / "coverage_inputs"

SOURCE_INDEXES_MANIFEST = SOURCE_INDEXES_DIR / "source_indexes_manifest.json"
SOURCE_CANDIDATES_MANIFEST = SOURCE_CANDIDATES_DIR / "source_candidates_manifest.json"
RAW_REVIEW_MANIFEST = RAW_REVIEW_DIR / "raw_review_manifest.json"
QUESTION_BANK_LOW_TRUST_MANIFEST = QUESTION_BANK_LOW_TRUST_DIR / "question_bank_low_trust_manifest.json"
COVERAGE_INPUTS_MANIFEST = COVERAGE_INPUTS_DIR / "coverage_inputs_manifest.json"

POLICY_VERSION = 1

TRUST_LEVELS = {"high_trust", "medium_trust", "curated_index", "low_trust", "gray_source"}
SOURCE_KINDS = {
    "curated_index",
    "candidate_resource",
    "knowledge_document",
    "question_bank_material",
    "coverage_input",
}
DESTINATIONS = {
    "source_candidates",
    "knowledge",
    "question_bank",
    "coverage_inputs",
    "question_bank_low_trust",
    "raw_review",
}
STATUSES = {"seeded", "candidate", "promoted", "discarded", "review_required", "active"}
SOURCE_ORIGINS = {"web", "local_file"}
ARTIFACT_EXISTS_FILTERS = {"present", "missing"}
BOOLEAN_FILTERS = {"true", "false"}
PROMOTABLE_DESTINATIONS = {"knowledge", "question_bank"}
REVIEW_DECISIONS = {"approved", "rejected", "needs_revision"}
REVIEW_DECISION_FILTERS = REVIEW_DECISIONS | {"none"}
LIST_CANDIDATE_FIELDS = {
    "candidate_id",
    "title",
    "source_origin",
    "destination",
    "status",
    "artifact_path",
    "artifact_exists",
    "eligibility_code",
    "review_decision",
    "review_decided_at",
}
WEAK_PARSER_HINTS = {"", "text", "file", "unknown"}

PILOT_INDEXES = [
    {
        "source_id": "awesome-python",
        "title": "Awesome Python",
        "source_url": "https://github.com/vinta/awesome-python",
        "topics": ["python", "backend", "automation"],
    },
    {
        "source_id": "awesome-react",
        "title": "Awesome React",
        "source_url": "https://github.com/enaqx/awesome-react",
        "topics": ["react", "frontend", "ui"],
    },
    {
        "source_id": "awesome-fastapi",
        "title": "Awesome FastAPI",
        "source_url": "https://github.com/mjhea0/awesome-fastapi",
        "topics": ["fastapi", "python", "backend", "api"],
    },
    {
        "source_id": "awesome-kubernetes",
        "title": "Awesome Kubernetes",
        "source_url": "https://github.com/ramitsurana/awesome-kubernetes",
        "topics": ["kubernetes", "containers", "devops", "cloud"],
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    lowered = str(text or "").strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return re.sub(r"-{2,}", "-", lowered).strip("-") or "source"


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return payload if isinstance(payload, dict) else fallback


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _default_manifest(pipeline: str, collection_key: str) -> dict[str, Any]:
    return {
        "pipeline": pipeline,
        "policy_version": POLICY_VERSION,
        "updated_at": None,
        collection_key: [],
    }


def ensure_curated_source_dirs() -> None:
    for path in (
        SOURCE_INDEXES_DIR,
        SOURCE_CANDIDATES_DIR,
        RAW_REVIEW_DIR,
        QUESTION_BANK_LOW_TRUST_DIR,
        COVERAGE_INPUTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def _parser_hint_from_url(source_url: str) -> str:
    lowered = str(source_url or "").strip().lower()
    if lowered.endswith(".md") or "github.com" in lowered:
        return "markdown_index"
    if lowered.endswith(".pdf"):
        return "pdf"
    if lowered.endswith(".html") or lowered.endswith(".htm"):
        return "html"
    return "link_only"


def _default_strong_evidence(
    trust_level: str,
    source_kind: str,
    destination: str,
) -> bool:
    if source_kind == "curated_index":
        return False
    if trust_level in {"curated_index", "low_trust", "gray_source"}:
        return False
    if destination in {"source_candidates", "question_bank_low_trust", "raw_review"}:
        return False
    return trust_level == "high_trust"


def _validate_choice(value: str, allowed: set[str], field_name: str) -> str:
    cleaned = str(value or "").strip()
    if cleaned not in allowed:
        raise ValueError(f"{field_name} must be one of: {', '.join(sorted(allowed))}")
    return cleaned


def _infer_source_origin(source_url: str, artifact_path: str = "") -> str:
    if str(artifact_path or "").strip():
        return "local_file"
    lowered = str(source_url or "").strip().lower()
    if lowered.startswith("local://"):
        return "local_file"
    return "web"


def _normalize_artifact_path(artifact_path: str) -> str:
    cleaned = str(artifact_path or "").strip()
    if not cleaned:
        raise ValueError("artifact_path is required for local file candidates")
    artifact = Path(cleaned)
    if artifact.is_absolute():
        raise ValueError("artifact_path must be relative to the project root")
    resolved = (PROJECT_ROOT / artifact).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("artifact_path must stay within the project root") from exc
    if not resolved.exists() or not resolved.is_file():
        raise ValueError(f"artifact_path not found: {cleaned}")
    return artifact.as_posix()


def _artifact_path_exists(artifact_path: str) -> bool:
    cleaned = str(artifact_path or "").strip()
    if not cleaned:
        return False
    artifact = Path(cleaned)
    if artifact.is_absolute():
        return False
    resolved = (PROJECT_ROOT / artifact).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError:
        return False
    return resolved.exists() and resolved.is_file()


def _resolve_project_relative_path(relative_path: str) -> Path:
    cleaned = str(relative_path or "").strip()
    if not cleaned:
        raise ValueError("relative path is required")
    path = Path(cleaned)
    if path.is_absolute():
        raise ValueError("path must be relative to the project root")
    resolved = (PROJECT_ROOT / path).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("path must stay within the project root") from exc
    return resolved


def _promotion_target_dir(destination: str) -> Path:
    if destination == "knowledge":
        return PROJECT_ROOT / "data" / "knowledge_raw"
    if destination == "question_bank":
        return PROJECT_ROOT / "data" / "question_bank_raw"
    raise ValueError(f"destination not eligible for promotion: {destination}")


def _relative_promotion_target_path(destination: str, artifact_path: str) -> str:
    target_dir = _promotion_target_dir(destination)
    target_path = target_dir / Path(str(artifact_path).strip()).name
    return target_path.relative_to(PROJECT_ROOT).as_posix()


def _inspect_promotion_target(source_path: Path, target_path: Path) -> dict[str, bool]:
    if not target_path.exists():
        return {
            "target_already_matches": False,
            "would_copy": True,
            "has_conflict": False,
            "conflict_reason": "",
        }
    if filecmp.cmp(source_path, target_path, shallow=False):
        return {
            "target_already_matches": True,
            "would_copy": False,
            "has_conflict": False,
            "conflict_reason": "",
        }
    return {
        "target_already_matches": False,
        "would_copy": False,
        "has_conflict": True,
        "conflict_reason": "destination_content_mismatch",
    }


def _build_promotion_log_event(candidate: dict[str, Any], *, promoted_at: str, promoted_to: str, promoted_artifact_path: str) -> dict[str, Any]:
    event = {
        "promoted_at": promoted_at,
        "promoted_to": promoted_to,
        "promoted_artifact_path": promoted_artifact_path,
    }
    review_decision = candidate.get("review_decision")
    review_decided_at = candidate.get("review_decided_at")
    if review_decision:
        event["review_decision"] = review_decision
    if review_decided_at:
        event["review_decided_at"] = review_decided_at
    return event


def _build_destination_change_event(
    *,
    changed_at: str,
    changed_from: str,
    changed_to: str,
    reason: str,
) -> dict[str, str]:
    return {
        "destination_changed_at": changed_at,
        "destination_changed_from": changed_from,
        "destination_changed_to": changed_to,
        "destination_changed_reason": reason,
    }


def _summarize_promotion_log(candidate: dict[str, Any]) -> dict[str, Any]:
    promotion_log = candidate.get("promotion_log")
    if not isinstance(promotion_log, list):
        promotion_log = []
    latest_promotion = promotion_log[-1] if promotion_log and isinstance(promotion_log[-1], dict) else None
    return {
        "has_promotion_history": len(promotion_log) > 0,
        "promotion_log_count": len(promotion_log),
        "latest_promotion": latest_promotion,
    }


def _warning_items_include_candidate(items: Any, candidate_id: str) -> bool:
    normalized_candidate_id = str(candidate_id).strip()
    if isinstance(items, list):
        for item in items:
            if isinstance(item, str) and item.strip() == normalized_candidate_id:
                return True
            if isinstance(item, dict) and str(item.get("candidate_id", "")).strip() == normalized_candidate_id:
                return True
    return False


def _collect_candidate_audit_flags(candidate_id: str) -> list[str]:
    normalized_candidate_id = str(candidate_id).strip()
    reports = {
        "validate_candidates": build_candidate_validation_report(),
        "audit_metadata": build_candidate_metadata_audit_report(),
        "audit_semantic": build_candidate_semantic_audit_report(),
        "audit_operational": build_candidate_operational_audit_report(),
    }
    flags: list[str] = []
    for report_name, report in reports.items():
        warnings = report.get("warnings")
        if isinstance(warnings, dict):
            for category, items in warnings.items():
                if _warning_items_include_candidate(items, normalized_candidate_id):
                    flags.append(f"{report_name}:{category}")
            continue
        for category, items in report.items():
            if category in {"candidate_count", "warning_count"}:
                continue
            if _warning_items_include_candidate(items, normalized_candidate_id):
                flags.append(f"{report_name}:{category}")
    return flags


def _build_candidate_consistency(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    warnings = {
        "web_with_artifact_path": [],
        "local_file_without_artifact_path": [],
        "missing_source_origin": [],
    }
    for item in candidates:
        candidate_id = str(item.get("candidate_id", "")).strip()
        source_origin = str(item.get("source_origin", "")).strip()
        artifact_path = str(item.get("artifact_path", "")).strip()
        if not source_origin:
            warnings["missing_source_origin"].append(candidate_id)
            continue
        if source_origin == "web" and artifact_path:
            warnings["web_with_artifact_path"].append(candidate_id)
        if source_origin == "local_file" and not artifact_path:
            warnings["local_file_without_artifact_path"].append(candidate_id)
    return {
        "candidate_count": len(candidates),
        "warning_count": sum(len(items) for items in warnings.values()),
        "warnings": warnings,
    }


def build_candidate_validation_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    candidate_consistency = _build_candidate_consistency(candidates)
    return {
        "candidate_count": candidate_consistency["candidate_count"],
        "warning_count": candidate_consistency["warning_count"],
        "web_with_artifact_path": candidate_consistency["warnings"]["web_with_artifact_path"],
        "local_file_without_artifact_path": candidate_consistency["warnings"]["local_file_without_artifact_path"],
        "missing_source_origin": candidate_consistency["warnings"]["missing_source_origin"],
    }


def build_candidate_metadata_audit_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    warnings = {
        "missing_notes": [],
        "weak_parser_hint": [],
        "missing_source_kind": [],
        "missing_trust_level": [],
        "missing_destination": [],
        "missing_status": [],
    }
    for item in candidates:
        candidate_id = str(item.get("candidate_id", "")).strip()
        title = str(item.get("title", "")).strip()
        summary = {"candidate_id": candidate_id, "title": title}
        if not str(item.get("notes", "")).strip():
            warnings["missing_notes"].append(summary)
        if str(item.get("parser_hint", "")).strip().lower() in WEAK_PARSER_HINTS:
            warnings["weak_parser_hint"].append(summary)
        if not str(item.get("source_kind", "")).strip():
            warnings["missing_source_kind"].append(summary)
        if not str(item.get("trust_level", "")).strip():
            warnings["missing_trust_level"].append(summary)
        if not str(item.get("destination", "")).strip():
            warnings["missing_destination"].append(summary)
        if not str(item.get("status", "")).strip():
            warnings["missing_status"].append(summary)
    return {
        "candidate_count": len(candidates),
        "warning_count": sum(len(items) for items in warnings.values()),
        "warnings": warnings,
    }


def build_candidate_semantic_audit_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    warnings = {
        "local_file_without_artifact": [],
        "low_trust_destination_mismatch": [],
        "raw_review_high_trust": [],
        "question_material_in_knowledge": [],
        "web_with_artifact_path": [],
    }
    for item in candidates:
        candidate_id = str(item.get("candidate_id", "")).strip()
        title = str(item.get("title", "")).strip()
        source_origin = str(item.get("source_origin", "")).strip()
        destination = str(item.get("destination", "")).strip()
        trust_level = str(item.get("trust_level", "")).strip()
        source_kind = str(item.get("source_kind", "")).strip()
        artifact_path = str(item.get("artifact_path", "")).strip()
        summary = {"candidate_id": candidate_id, "title": title}
        if source_origin == "local_file" and not artifact_path:
            warnings["local_file_without_artifact"].append(summary)
        if destination == "question_bank_low_trust" and trust_level != "low_trust":
            warnings["low_trust_destination_mismatch"].append(summary)
        if destination == "raw_review" and trust_level == "high_trust":
            warnings["raw_review_high_trust"].append(summary)
        if source_kind == "question_bank_material" and destination == "knowledge":
            warnings["question_material_in_knowledge"].append(summary)
        if source_origin == "web" and artifact_path:
            warnings["web_with_artifact_path"].append(summary)
    return {
        "candidate_count": len(candidates),
        "warning_count": sum(len(items) for items in warnings.values()),
        "warnings": warnings,
    }


def build_candidate_operational_audit_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    warnings = {
        "missing_discovered_from": [],
        "artifact_without_parser_hint": [],
        "artifact_parser_mismatch": [],
        "local_url_without_artifact": [],
        "local_file_missing_discovered_from": [],
    }
    for item in candidates:
        candidate_id = str(item.get("candidate_id", "")).strip()
        title = str(item.get("title", "")).strip()
        discovered_from = str(item.get("discovered_from", "")).strip()
        parser_hint = str(item.get("parser_hint", "")).strip().lower()
        artifact_path = str(item.get("artifact_path", "")).strip()
        source_url = str(item.get("source_url", "")).strip().lower()
        source_origin = str(item.get("source_origin", "")).strip()
        summary = {"candidate_id": candidate_id, "title": title}
        if not discovered_from:
            warnings["missing_discovered_from"].append(summary)
        if artifact_path and not parser_hint:
            warnings["artifact_without_parser_hint"].append(summary)
        if artifact_path and parser_hint in {"url", "link_only"}:
            warnings["artifact_parser_mismatch"].append(summary)
        if source_url.startswith("local://") and not artifact_path:
            warnings["local_url_without_artifact"].append(summary)
        if source_origin == "local_file" and not discovered_from:
            warnings["local_file_missing_discovered_from"].append(summary)
    return {
        "candidate_count": len(candidates),
        "warning_count": sum(len(items) for items in warnings.values()),
        "warnings": warnings,
    }


def _extract_nonzero_warning_categories(report: dict[str, Any]) -> list[str]:
    warnings = report.get("warnings")
    if isinstance(warnings, dict):
        return [category for category, items in warnings.items() if items]
    return [
        key
        for key, value in report.items()
        if key not in {"candidate_count", "warning_count"} and isinstance(value, list) and value
    ]


def _extract_nonzero_warning_category_counts(report: dict[str, Any]) -> dict[str, int]:
    warnings = report.get("warnings")
    if isinstance(warnings, dict):
        return {category: len(items) for category, items in warnings.items() if items}
    return {
        key: len(value)
        for key, value in report.items()
        if key not in {"candidate_count", "warning_count"} and isinstance(value, list) and value
    }


def _sort_warning_category_counts(category_counts: dict[str, int]) -> dict[str, int]:
    return {
        category: count
        for category, count in sorted(
            category_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    }


def build_candidate_audit_summary_report(
    *,
    show_nonzero_categories: bool = False,
    show_category_counts: bool = False,
    sort_category_counts: bool = False,
) -> dict[str, Any]:
    validate_candidates = build_candidate_validation_report()
    audit_metadata = build_candidate_metadata_audit_report()
    audit_semantic = build_candidate_semantic_audit_report()
    audit_operational = build_candidate_operational_audit_report()
    candidate_count = validate_candidates["candidate_count"]
    checks = {
        "validate_candidates": {
            "warning_count": validate_candidates["warning_count"],
        },
        "audit_metadata": {
            "warning_count": audit_metadata["warning_count"],
        },
        "audit_semantic": {
            "warning_count": audit_semantic["warning_count"],
        },
        "audit_operational": {
            "warning_count": audit_operational["warning_count"],
        },
    }
    total_warning_count = sum(check["warning_count"] for check in checks.values())
    return {
        **(
            {
                "nonzero_categories": {
                    check_name: categories
                    for check_name, categories in {
                        "validate_candidates": _extract_nonzero_warning_categories(validate_candidates),
                        "audit_metadata": _extract_nonzero_warning_categories(audit_metadata),
                        "audit_semantic": _extract_nonzero_warning_categories(audit_semantic),
                        "audit_operational": _extract_nonzero_warning_categories(audit_operational),
                    }.items()
                    if categories
                }
            }
            if show_nonzero_categories
            else {}
        ),
        **(
            {
                "category_counts": {
                    check_name: (_sort_warning_category_counts(counts) if sort_category_counts else counts)
                    for check_name, counts in {
                        "validate_candidates": _extract_nonzero_warning_category_counts(validate_candidates),
                        "audit_metadata": _extract_nonzero_warning_category_counts(audit_metadata),
                        "audit_semantic": _extract_nonzero_warning_category_counts(audit_semantic),
                        "audit_operational": _extract_nonzero_warning_category_counts(audit_operational),
                    }.items()
                    if counts
                }
            }
            if show_category_counts
            else {}
        ),
        "candidate_count": candidate_count,
        "total_warning_count": total_warning_count,
        "is_clean": total_warning_count == 0,
        "checks": checks,
    }


def build_candidate_stats_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    with_artifact_path = 0
    without_artifact_path = 0
    artifact_present = 0
    artifact_missing = 0
    by_origin = {origin: 0 for origin in sorted(SOURCE_ORIGINS)}
    by_destination = {destination: 0 for destination in sorted(DESTINATIONS)}
    by_review_decision = {
        "approved": 0,
        "rejected": 0,
        "needs_revision": 0,
        "none": 0,
    }
    by_promotion_history = {
        "with_history": 0,
        "without_history": 0,
    }
    promotion_readiness = {
        "ready": 0,
        "not_ready": 0,
    }
    promotion_blockers: dict[str, int] = {}
    for item in candidates:
        resolved_origin = str(item.get("source_origin", "")).strip() or _infer_source_origin(
            str(item.get("source_url", "")).strip(),
            str(item.get("artifact_path", "")).strip(),
        )
        if resolved_origin in by_origin:
            by_origin[resolved_origin] += 1
        destination = str(item.get("destination", "")).strip()
        if destination in by_destination:
            by_destination[destination] += 1
        review_decision = str(item.get("review_decision", "") or "").strip()
        if review_decision in REVIEW_DECISIONS:
            by_review_decision[review_decision] += 1
        else:
            by_review_decision["none"] += 1
        promotion_log = item.get("promotion_log")
        if isinstance(promotion_log, list) and promotion_log:
            by_promotion_history["with_history"] += 1
        else:
            by_promotion_history["without_history"] += 1
        readiness = _candidate_promotion_readiness(item)
        if readiness["ready"]:
            promotion_readiness["ready"] += 1
        else:
            promotion_readiness["not_ready"] += 1
            blocker = str(readiness.get("eligibility_code", "")).strip() or "unknown_blocker"
            promotion_blockers[blocker] = promotion_blockers.get(blocker, 0) + 1
        artifact_path = str(item.get("artifact_path", "")).strip()
        if artifact_path:
            with_artifact_path += 1
            if _artifact_path_exists(artifact_path):
                artifact_present += 1
            else:
                artifact_missing += 1
        else:
            without_artifact_path += 1
    return {
        "candidate_count": len(candidates),
        "by_origin": by_origin,
        "by_destination": by_destination,
        "by_review_decision": by_review_decision,
        "by_promotion_history": by_promotion_history,
        "promotion_readiness": promotion_readiness,
        "promotion_blockers": dict(sorted(promotion_blockers.items())),
        "with_artifact_path": with_artifact_path,
        "without_artifact_path": without_artifact_path,
        "artifact_exists": {
            "present": artifact_present,
            "missing": artifact_missing,
        },
    }


def build_candidate_listing_report(
    *,
    origin: str = "",
    destination: str = "",
    status: str = "",
    review_decision: str = "",
    has_promotion_history: str = "",
    eligibility_code: str = "",
    query: str = "",
    has_artifact_path: bool = False,
    artifact_exists: str = "",
    promotion_ready: str = "",
    fields: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    ensure_curated_source_dirs()
    normalized_origin = _validate_choice(origin, SOURCE_ORIGINS, "origin") if str(origin).strip() else ""
    normalized_destination = _validate_choice(destination, DESTINATIONS, "destination") if str(destination).strip() else ""
    normalized_status = _validate_choice(status, STATUSES, "status") if str(status).strip() else ""
    normalized_review_decision = (
        _validate_choice(review_decision, REVIEW_DECISION_FILTERS, "review_decision")
        if str(review_decision).strip()
        else ""
    )
    normalized_has_promotion_history = (
        _validate_choice(has_promotion_history, BOOLEAN_FILTERS, "has_promotion_history")
        if str(has_promotion_history).strip()
        else ""
    )
    normalized_eligibility_code = str(eligibility_code or "").strip()
    normalized_query = str(query or "").strip().lower()
    normalized_artifact_exists = (
        _validate_choice(artifact_exists, ARTIFACT_EXISTS_FILTERS, "artifact_exists")
        if str(artifact_exists).strip()
        else ""
    )
    normalized_promotion_ready = (
        _validate_choice(promotion_ready, BOOLEAN_FILTERS, "promotion_ready")
        if str(promotion_ready).strip()
        else ""
    )
    normalized_fields = []
    for field in fields or []:
        normalized_fields.append(_validate_choice(field, LIST_CANDIDATE_FIELDS, "field"))
    normalized_limit = None if limit is None else max(1, int(limit))
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    items: list[dict[str, Any]] = []
    for item in candidates:
        resolved_origin = str(item.get("source_origin", "")).strip() or _infer_source_origin(
            str(item.get("source_url", "")).strip(),
            str(item.get("artifact_path", "")).strip(),
        )
        if normalized_origin and resolved_origin != normalized_origin:
            continue
        if normalized_destination and str(item.get("destination", "")).strip() != normalized_destination:
            continue
        if normalized_status and str(item.get("status", "")).strip() != normalized_status:
            continue
        candidate_review_decision = str(item.get("review_decision", "") or "").strip()
        if normalized_review_decision:
            if normalized_review_decision == "none":
                if candidate_review_decision:
                    continue
            elif candidate_review_decision != normalized_review_decision:
                continue
        promotion_log = item.get("promotion_log")
        has_promotion_history_value = isinstance(promotion_log, list) and len(promotion_log) > 0
        if normalized_has_promotion_history:
            expected_has_promotion_history = normalized_has_promotion_history == "true"
            if has_promotion_history_value != expected_has_promotion_history:
                continue
        artifact_path = str(item.get("artifact_path", "")).strip()
        if has_artifact_path and not artifact_path:
            continue
        artifact_exists_value = _artifact_path_exists(artifact_path) if artifact_path else False
        if normalized_artifact_exists:
            if not artifact_path:
                continue
            if normalized_artifact_exists == "present" and not artifact_exists_value:
                continue
            if normalized_artifact_exists == "missing" and artifact_exists_value:
                continue
        if normalized_query:
            haystacks = [
                str(item.get("title", "")).strip().lower(),
                str(item.get("candidate_id", "")).strip().lower(),
            ]
            if not any(normalized_query in haystack for haystack in haystacks):
                continue
        promotion_state = None
        needs_promotion_state = bool(normalized_promotion_ready or normalized_eligibility_code or "eligibility_code" in normalized_fields)
        if needs_promotion_state:
            promotion_state = _candidate_promotion_readiness(item)
        if normalized_promotion_ready:
            expected_promotion_ready = normalized_promotion_ready == "true"
            if bool(promotion_state.get("ready", False)) != expected_promotion_ready:
                continue
        if normalized_eligibility_code:
            if str(promotion_state.get("eligibility_code", "")).strip() != normalized_eligibility_code:
                continue
        payload = {
            "candidate_id": str(item.get("candidate_id", "")).strip(),
            "title": str(item.get("title", "")).strip(),
            "source_origin": resolved_origin,
            "destination": str(item.get("destination", "")).strip(),
            "status": str(item.get("status", "")).strip(),
        }
        if artifact_path:
            payload["artifact_path"] = artifact_path
            payload["artifact_exists"] = artifact_exists_value
        if candidate_review_decision:
            payload["review_decision"] = candidate_review_decision
        review_decided_at = item.get("review_decided_at")
        if review_decided_at:
            payload["review_decided_at"] = review_decided_at
        if promotion_state and promotion_state.get("eligibility_code"):
            payload["eligibility_code"] = promotion_state["eligibility_code"]
        if has_promotion_history_value:
            payload["has_promotion_history"] = True
            payload["promotion_log_count"] = len(promotion_log)
        if normalized_fields:
            payload = {field: payload[field] for field in normalized_fields if field in payload}
        items.append(payload)
    if normalized_limit is not None:
        items = items[:normalized_limit]
    return {
        "count": len(items),
        "filters": {
            "origin": normalized_origin,
            "destination": normalized_destination,
            "status": normalized_status,
            "review_decision": normalized_review_decision,
            "has_promotion_history": normalized_has_promotion_history,
            "eligibility_code": normalized_eligibility_code,
            "promotion_ready": normalized_promotion_ready,
            "query": normalized_query,
            "has_artifact_path": has_artifact_path,
            "artifact_exists": normalized_artifact_exists,
            "fields": normalized_fields,
            "limit": normalized_limit,
        },
        "items": items,
    }


def render_candidate_listing_report(report: dict[str, Any], *, json_lines: bool = False, compact: bool = False) -> str:
    items = report.get("items", [])
    if not json_lines:
        if compact:
            report = {
                "count": report.get("count", 0),
                "items": items,
            }
        return json.dumps(report, ensure_ascii=False, indent=2)
    return "\n".join(json.dumps(item, ensure_ascii=False) for item in items)


def _candidate_promotion_readiness(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id", "")).strip()
    if not candidate_id:
        return {
            "ready": False,
            "eligibility_code": "unknown_blocker",
        }
    if str(candidate.get("review_decision", "") or "").strip() != "approved":
        return {
            "ready": False,
            "eligibility_code": "review_not_approved",
        }
    readiness_report = inspect_promotion_candidate(candidate_id)
    return {
        "ready": bool(readiness_report.get("eligible", False)),
        "eligibility_code": str(readiness_report.get("eligibility_code", "")).strip() or "unknown_blocker",
    }


def _candidate_is_promotion_ready(candidate: dict[str, Any]) -> bool:
    return bool(_candidate_promotion_readiness(candidate).get("ready", False))


def build_source_index_record(
    *,
    source_id: str,
    title: str,
    source_url: str,
    topics: list[str],
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "title": title,
        "source_url": source_url,
        "topics": sorted({str(topic).strip() for topic in topics if str(topic).strip()}),
        "source_kind": "curated_index",
        "trust_level": "curated_index",
        "destination": "source_candidates",
        "status": "active",
        "parser_hint": _parser_hint_from_url(source_url),
        "is_strong_evidence": False,
        "discovery_only": True,
        "notes": "Indice curado: serve para descoberta e triagem, nunca como evidencia forte direta.",
    }


def build_source_candidate_record(
    *,
    title: str,
    source_url: str,
    source_kind: str,
    trust_level: str,
    destination: str,
    status: str = "candidate",
    parser_hint: str = "",
    discovered_from: str = "",
    notes: str = "",
    is_strong_evidence: bool | None = None,
    source_origin: str = "",
    artifact_path: str = "",
) -> dict[str, Any]:
    source_kind = _validate_choice(source_kind, SOURCE_KINDS, "source_kind")
    trust_level = _validate_choice(trust_level, TRUST_LEVELS, "trust_level")
    destination = _validate_choice(destination, DESTINATIONS, "destination")
    status = _validate_choice(status, STATUSES, "status")
    candidate_id = _slugify(f"{title}-{source_url}")[:80]
    parser_hint = str(parser_hint or _parser_hint_from_url(source_url)).strip()
    strong_evidence = (
        _default_strong_evidence(trust_level=trust_level, source_kind=source_kind, destination=destination)
        if is_strong_evidence is None
        else bool(is_strong_evidence)
    )
    source_origin = _validate_choice(
        str(source_origin or _infer_source_origin(source_url)).strip(),
        SOURCE_ORIGINS,
        "source_origin",
    )
    return {
        "candidate_id": candidate_id,
        "title": str(title).strip(),
        "source_url": str(source_url).strip(),
        "source_origin": source_origin,
        **({"artifact_path": str(artifact_path).strip()} if str(artifact_path).strip() else {}),
        "source_kind": source_kind,
        "trust_level": trust_level,
        "destination": destination,
        "status": status,
        "parser_hint": parser_hint,
        "is_strong_evidence": strong_evidence,
        "discovered_from": str(discovered_from).strip(),
        "notes": str(notes).strip(),
        "promoted_at": None,
        "reviewed_at": None,
        "review_decision": None,
        "review_decided_at": None,
        "review_notes": "",
        "destination_changed_at": None,
        "destination_changed_from": "",
        "destination_changed_reason": "",
        "destination_change_log": [],
        "promotion_log": [],
    }


def load_source_indexes_manifest() -> dict[str, Any]:
    return _read_json(
        SOURCE_INDEXES_MANIFEST,
        _default_manifest("curated_source_indexes", "indexes"),
    )


def write_source_indexes_manifest(indexes: list[dict[str, Any]]) -> Path:
    payload = _default_manifest("curated_source_indexes", "indexes")
    payload["policy_version"] = POLICY_VERSION
    payload["updated_at"] = _now_iso()
    payload["indexes"] = indexes
    return _write_json(SOURCE_INDEXES_MANIFEST, payload)


def load_source_candidates_manifest() -> dict[str, Any]:
    return _read_json(
        SOURCE_CANDIDATES_MANIFEST,
        _default_manifest("curated_source_candidates", "candidates"),
    )


def write_source_candidates_manifest(candidates: list[dict[str, Any]]) -> Path:
    payload = _default_manifest("curated_source_candidates", "candidates")
    payload["policy_version"] = POLICY_VERSION
    payload["updated_at"] = _now_iso()
    payload["candidates"] = candidates
    return _write_json(SOURCE_CANDIDATES_MANIFEST, payload)


def _write_destination_manifest(path: Path, pipeline: str, collection_key: str, records: list[dict[str, Any]]) -> Path:
    payload = _default_manifest(pipeline, collection_key)
    payload["policy_version"] = POLICY_VERSION
    payload["updated_at"] = _now_iso()
    payload[collection_key] = records
    return _write_json(path, payload)


def sync_destination_manifests(candidates: list[dict[str, Any]]) -> dict[str, Path]:
    coverage_inputs = [
        candidate
        for candidate in candidates
        if candidate.get("destination") == "coverage_inputs"
    ]
    low_trust_items = [
        candidate
        for candidate in candidates
        if candidate.get("destination") == "question_bank_low_trust"
    ]
    raw_review_items = [
        candidate
        for candidate in candidates
        if candidate.get("destination") == "raw_review" or candidate.get("status") == "review_required"
    ]
    return {
        "coverage_inputs": _write_destination_manifest(
            COVERAGE_INPUTS_MANIFEST,
            "coverage_inputs",
            "items",
            coverage_inputs,
        ),
        "question_bank_low_trust": _write_destination_manifest(
            QUESTION_BANK_LOW_TRUST_MANIFEST,
            "question_bank_low_trust",
            "items",
            low_trust_items,
        ),
        "raw_review": _write_destination_manifest(
            RAW_REVIEW_MANIFEST,
            "raw_review",
            "items",
            raw_review_items,
        ),
    }


def bootstrap_pilot_curated_sources() -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_indexes_manifest()
    existing = {
        str(item.get("source_id", "")).strip(): item
        for item in manifest.get("indexes", [])
        if isinstance(item, dict)
    }
    for seed in PILOT_INDEXES:
        existing[seed["source_id"]] = build_source_index_record(**seed)
    index_path = write_source_indexes_manifest(sorted(existing.values(), key=lambda item: str(item.get("source_id", ""))))

    candidate_manifest = load_source_candidates_manifest()
    candidate_path = write_source_candidates_manifest(
        [item for item in candidate_manifest.get("candidates", []) if isinstance(item, dict)]
    )
    destination_paths = sync_destination_manifests(
        [item for item in candidate_manifest.get("candidates", []) if isinstance(item, dict)]
    )

    return {
        "index_path": str(index_path),
        "candidate_path": str(candidate_path),
        "destination_paths": {key: str(value) for key, value in destination_paths.items()},
        "seeded_indexes": len(existing),
    }


def register_source_candidate(
    *,
    title: str,
    source_url: str = "",
    artifact_path: str = "",
    source_kind: str,
    trust_level: str,
    destination: str,
    status: str = "candidate",
    parser_hint: str = "",
    discovered_from: str = "",
    notes: str = "",
    is_strong_evidence: bool | None = None,
) -> dict[str, Any]:
    ensure_curated_source_dirs()
    cleaned_url = str(source_url or "").strip()
    cleaned_artifact_path = str(artifact_path or "").strip()
    if not cleaned_url and not cleaned_artifact_path:
        raise ValueError("register_source_candidate requires source_url or artifact_path")
    if cleaned_url and cleaned_artifact_path:
        raise ValueError("register_source_candidate accepts either source_url or artifact_path, not both")
    normalized_artifact_path = _normalize_artifact_path(cleaned_artifact_path) if cleaned_artifact_path else ""
    record_source_url = cleaned_url or f"local://{normalized_artifact_path}"
    record_source_origin = "local_file" if normalized_artifact_path else "web"
    record_parser_hint = parser_hint or _parser_hint_from_url(normalized_artifact_path or record_source_url)
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    record = build_source_candidate_record(
        title=title,
        source_url=record_source_url,
        source_kind=source_kind,
        trust_level=trust_level,
        destination=destination,
        status=status,
        parser_hint=record_parser_hint,
        discovered_from=discovered_from,
        notes=notes,
        is_strong_evidence=is_strong_evidence,
        source_origin=record_source_origin,
        artifact_path=normalized_artifact_path,
    )
    for index, candidate in enumerate(candidates):
        if str(candidate.get("candidate_id", "")).strip() == record["candidate_id"]:
            candidates[index] = record
            break
    else:
        candidates.append(record)
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    sync_destination_manifests(candidates)
    return record


def promote_source_candidate(candidate_id: str, *, confirm: bool = False) -> dict[str, Any]:
    ensure_curated_source_dirs()
    if not confirm:
        raise ValueError("manual promotion requires --confirm")
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    report = inspect_promotion_candidate(candidate_id)
    if not report["eligible"]:
        raise ValueError(str(report["blocking_reason"]).strip() or f"candidate not eligible for promotion: {candidate_id}")

    target = next(
        candidate
        for candidate in candidates
        if str(candidate.get("candidate_id", "")).strip() == str(candidate_id).strip()
    )

    destination = str(target.get("destination", "")).strip()
    artifact_path = str(target.get("artifact_path", "")).strip()
    source_path = _resolve_project_relative_path(artifact_path)
    target_dir = _promotion_target_dir(destination)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / source_path.name
    if target_path.exists():
        if not filecmp.cmp(source_path, target_path, shallow=False):
            raise ValueError(f"promotion target already exists with different content: {target_path.name}")
    else:
        shutil.copy2(source_path, target_path)

    timestamp = _now_iso()
    target["status"] = "promoted"
    target["promoted_at"] = timestamp
    target["promoted_to"] = destination
    target["promoted_artifact_path"] = target_path.relative_to(PROJECT_ROOT).as_posix()
    promotion_log = target.get("promotion_log")
    if not isinstance(promotion_log, list):
        promotion_log = []
    promotion_log.append(
        _build_promotion_log_event(
            target,
            promoted_at=timestamp,
            promoted_to=destination,
            promoted_artifact_path=target["promoted_artifact_path"],
        )
    )
    target["promotion_log"] = promotion_log
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    sync_destination_manifests(candidates)
    return target


def reconcile_target_match_candidate(candidate_id: str) -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    candidate_key = str(candidate_id).strip()
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() == candidate_key:
            target = candidate
            break
    if target is None:
        raise ValueError(f"candidate_id not found: {candidate_id}")

    status = str(target.get("status", "")).strip()
    if status == "promoted":
        raise ValueError("candidate is already promoted")

    promotion_log = target.get("promotion_log")
    normalized_promotion_log = promotion_log if isinstance(promotion_log, list) else []
    if normalized_promotion_log:
        raise ValueError("candidate already has promotion history; refusing legacy reconciliation")

    inspection = build_target_match_inspection_report(candidate_key)
    if not inspection.get("exists", False):
        raise ValueError(f"candidate_id not found: {candidate_id}")
    if not inspection.get("is_legacy_target_match", False):
        raise ValueError("candidate is not a legacy target-match case")

    promoted_to = str(target.get("destination", "")).strip()
    promoted_artifact_path = str(inspection.get("planned_target_path") or "").strip()
    if not promoted_artifact_path:
        raise ValueError("legacy target-match case requires a planned_target_path")

    timestamp = _now_iso()
    target["status"] = "promoted"
    target["promoted_at"] = timestamp
    target["promoted_to"] = promoted_to
    target["promoted_artifact_path"] = promoted_artifact_path
    normalized_promotion_log.append(
        {
            **_build_promotion_log_event(
                target,
                promoted_at=timestamp,
                promoted_to=promoted_to,
                promoted_artifact_path=promoted_artifact_path,
            ),
            "reconciled_from_target_match": True,
        }
    )
    target["promotion_log"] = normalized_promotion_log
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    sync_destination_manifests(candidates)
    return target


def inspect_promotion_candidate(candidate_id: str) -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    candidate_key = str(candidate_id).strip()
    report: dict[str, Any] = {
        "candidate_id": candidate_key,
        "exists": False,
        "eligible": False,
        "eligibility_code": "candidate_not_found",
        "blocking_reason": "",
        "reasons": [],
        "source_origin": "",
        "status": "",
        "destination": "",
        "artifact_path": "",
        "artifact_exists": False,
        "promotable_destination": False,
        "planned_target_path": None,
        "target_already_matches": False,
        "would_copy": False,
        "has_conflict": False,
        "conflict_reason": "",
    }
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() == candidate_key:
            target = candidate
            break
    if target is None:
        report["reasons"] = [f"candidate_id not found: {candidate_key}"]
        report["blocking_reason"] = report["reasons"][0]
        return report

    source_origin = str(target.get("source_origin", "")).strip()
    status = str(target.get("status", "")).strip()
    destination = str(target.get("destination", "")).strip()
    artifact_path = str(target.get("artifact_path", "")).strip()
    review_decision = str(target.get("review_decision", "") or "").strip()
    artifact_exists = _artifact_path_exists(artifact_path) if artifact_path else False
    promotable_destination = destination in PROMOTABLE_DESTINATIONS

    report.update(
        {
            "exists": True,
            "source_origin": source_origin,
            "status": status,
            "destination": destination,
            "artifact_path": artifact_path,
            "artifact_exists": artifact_exists,
            "promotable_destination": promotable_destination,
        }
    )

    if promotable_destination and artifact_path and not Path(artifact_path).is_absolute():
        report["planned_target_path"] = _relative_promotion_target_path(destination, artifact_path)

    reasons: list[str] = []
    eligibility_code = "eligible"
    if status == "promoted":
        reasons.append(f"candidate already promoted: {candidate_key}")
        eligibility_code = "already_promoted"
    elif status != "candidate":
        reasons.append("candidate status must be 'candidate' for manual promotion")
        eligibility_code = "invalid_status"
    if not promotable_destination:
        reasons.append(f"destination not eligible for promotion: {destination}")
        if eligibility_code == "eligible":
            eligibility_code = "non_promotable_destination"
    if source_origin != "local_file":
        reasons.append("manual promotion currently supports only local_file candidates")
        if eligibility_code == "eligible":
            eligibility_code = "non_local_source"
    if not artifact_path:
        reasons.append("artifact_path must point to an existing local file for promotion")
        if eligibility_code == "eligible":
            eligibility_code = "missing_artifact_path"
    elif not artifact_exists:
        reasons.append("artifact_path must point to an existing local file for promotion")
        if eligibility_code == "eligible":
            eligibility_code = "artifact_not_found"
    if _build_candidate_consistency([target])["warning_count"] > 0:
        reasons.append("candidate has consistency warnings and cannot be promoted")
        if eligibility_code == "eligible":
            eligibility_code = "consistency_blocked"
    if review_decision != "approved":
        reasons.append("manual promotion requires review_decision=approved")
        if eligibility_code == "eligible":
            eligibility_code = "review_not_approved"

    if not reasons and artifact_path and report["planned_target_path"]:
        source_path = _resolve_project_relative_path(artifact_path)
        target_path = PROJECT_ROOT / str(report["planned_target_path"]).strip()
        target_state = _inspect_promotion_target(source_path, target_path)
        report["target_already_matches"] = target_state["target_already_matches"]
        report["would_copy"] = target_state["would_copy"]
        report["has_conflict"] = target_state["has_conflict"]
        report["conflict_reason"] = target_state["conflict_reason"]
        if target_state["has_conflict"]:
            reasons.append(f"promotion target already exists with different content: {target_path.name}")
            eligibility_code = "destination_conflict"

    report["eligible"] = len(reasons) == 0
    report["eligibility_code"] = "eligible" if report["eligible"] else eligibility_code
    report["reasons"] = reasons
    report["blocking_reason"] = reasons[0] if reasons else ""
    return report


def render_promotion_check_report(report: dict[str, Any], *, compact: bool = False) -> str:
    if not compact:
        return json.dumps(report, ensure_ascii=False, indent=2)
    compact_report = {
        "candidate_id": report.get("candidate_id", ""),
        "eligible": bool(report.get("eligible", False)),
        "eligibility_code": report.get("eligibility_code", ""),
        "planned_target_path": report.get("planned_target_path"),
        "would_copy": bool(report.get("would_copy", False)),
        "target_already_matches": bool(report.get("target_already_matches", False)),
        "has_conflict": bool(report.get("has_conflict", False)),
        "conflict_reason": report.get("conflict_reason", ""),
    }
    if report.get("review_decision"):
        compact_report["review_decision"] = report.get("review_decision")
    if report.get("review_decided_at"):
        compact_report["review_decided_at"] = report.get("review_decided_at")
    if not bool(report.get("exists", False)):
        compact_report["exists"] = False
    return json.dumps(compact_report, ensure_ascii=False, indent=2)


def _compact_promotion_check_report(report: dict[str, Any]) -> str:
    candidate_key = str(report.get("candidate_id", "")).strip()
    if candidate_key and bool(report.get("exists", False)):
        manifest = load_source_candidates_manifest()
        candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
        target = next(
            (
                candidate
                for candidate in candidates
                if str(candidate.get("candidate_id", "")).strip() == candidate_key
            ),
            None,
        )
        if target is not None:
            review_decision = target.get("review_decision")
            review_decided_at = target.get("review_decided_at")
            enriched_report = dict(report)
            if review_decision:
                enriched_report["review_decision"] = review_decision
            if review_decided_at:
                enriched_report["review_decided_at"] = review_decided_at
            report = enriched_report
    compact_payload = json.loads(render_promotion_check_report(report, compact=True))
    if report.get("review_decision"):
        compact_payload["review_decision"] = report.get("review_decision")
    if report.get("review_decided_at"):
        compact_payload["review_decided_at"] = report.get("review_decided_at")
    return json.dumps(compact_payload, ensure_ascii=False, indent=2)


def build_candidate_review_report(candidate_id: str) -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    candidate_key = str(candidate_id).strip()
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() == candidate_key:
            target = candidate
            break

    promotion_check = inspect_promotion_candidate(candidate_key)
    if target is None:
        return {
            "candidate_id": candidate_key,
            "exists": False,
            "identity": {
                "candidate_id": candidate_key,
                "title": "",
                "source_origin": "",
                "source_kind": "",
                "trust_level": "",
                "destination": "",
                "status": "",
                "discovered_from": "",
            },
            "artifact": {
                "artifact_path": "",
                "artifact_exists": False,
                "parser_hint": "",
            },
            "review": {
                "review_decision": None,
                "review_decided_at": None,
                "review_notes": "",
            },
            "promotion_history": {
                "has_promotion_history": False,
                "promotion_log_count": 0,
                "latest_promotion": None,
            },
            "promotion_check": promotion_check,
            "audit_flags": [],
        }

    artifact_path = str(target.get("artifact_path", "")).strip()
    return {
        "candidate_id": candidate_key,
        "exists": True,
        "identity": {
            "candidate_id": candidate_key,
            "title": str(target.get("title", "")).strip(),
            "source_origin": str(target.get("source_origin", "")).strip(),
            "source_kind": str(target.get("source_kind", "")).strip(),
            "trust_level": str(target.get("trust_level", "")).strip(),
            "destination": str(target.get("destination", "")).strip(),
            "status": str(target.get("status", "")).strip(),
            "discovered_from": str(target.get("discovered_from", "")).strip(),
        },
        "artifact": {
            "artifact_path": artifact_path,
            "artifact_exists": _artifact_path_exists(artifact_path) if artifact_path else False,
            "parser_hint": str(target.get("parser_hint", "")).strip(),
        },
        "review": {
            "review_decision": target.get("review_decision"),
            "review_decided_at": target.get("review_decided_at"),
            "review_notes": str(target.get("review_notes", "")).strip(),
        },
        "promotion_history": _summarize_promotion_log(target),
        "promotion_check": promotion_check,
        "audit_flags": _collect_candidate_audit_flags(candidate_key),
    }


def build_candidate_promotion_log_report(candidate_id: str, *, latest_only: bool = False) -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    candidate_key = str(candidate_id).strip()
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() == candidate_key:
            target = candidate
            break
    if target is None:
        return {
            "candidate_id": candidate_key,
            "exists": False,
            "has_promotion_history": False,
            "promotion_log_count": 0,
            "promotion_log": [],
        }
    promotion_log = target.get("promotion_log")
    normalized_promotion_log = promotion_log if isinstance(promotion_log, list) else []
    summary = _summarize_promotion_log(target)
    if latest_only and normalized_promotion_log:
        normalized_promotion_log = [normalized_promotion_log[-1]]
    return {
        "candidate_id": candidate_key,
        "exists": True,
        "has_promotion_history": summary["has_promotion_history"],
        "promotion_log_count": summary["promotion_log_count"],
        "promotion_log": normalized_promotion_log,
    }


def build_target_match_inspection_report(candidate_id: str) -> dict[str, Any]:
    ensure_curated_source_dirs()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    candidate_key = str(candidate_id).strip()
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() == candidate_key:
            target = candidate
            break

    promotion_check = inspect_promotion_candidate(candidate_key)
    if target is None:
        return {
            "candidate_id": candidate_key,
            "exists": False,
            "status": "",
            "destination": "",
            "source_origin": "",
            "planned_target_path": promotion_check.get("planned_target_path"),
            "target_exists": False,
            "target_already_matches": bool(promotion_check.get("target_already_matches", False)),
            "has_promotion_history": False,
            "promotion_log_count": 0,
            "is_legacy_target_match": False,
        }

    planned_target_path = promotion_check.get("planned_target_path")
    target_exists = False
    if isinstance(planned_target_path, str) and planned_target_path.strip():
        target_exists = _resolve_project_relative_path(planned_target_path).exists()
    promotion_history = _summarize_promotion_log(target)
    status = str(target.get("status", "")).strip()
    target_already_matches = bool(promotion_check.get("target_already_matches", False))
    would_copy = bool(promotion_check.get("would_copy", False))
    promotion_log_count = int(promotion_history.get("promotion_log_count", 0))
    return {
        "candidate_id": candidate_key,
        "exists": True,
        "status": status,
        "destination": str(target.get("destination", "")).strip(),
        "source_origin": str(target.get("source_origin", "")).strip()
        or _infer_source_origin(
            str(target.get("source_url", "")).strip(),
            str(target.get("artifact_path", "")).strip(),
        ),
        "planned_target_path": planned_target_path,
        "target_exists": target_exists,
        "target_already_matches": target_already_matches,
        "has_promotion_history": bool(promotion_history.get("has_promotion_history", False)),
        "promotion_log_count": promotion_log_count,
        "is_legacy_target_match": (
            target_already_matches
            and not would_copy
            and status != "promoted"
            and promotion_log_count == 0
        ),
    }


def render_candidate_promotion_log_report(report: dict[str, Any], *, compact: bool = False) -> str:
    if not compact:
        return json.dumps(report, ensure_ascii=False, indent=2)
    promotion_log = report.get("promotion_log", [])
    latest_promotion = promotion_log[-1] if isinstance(promotion_log, list) and promotion_log else None
    compact_report = {
        "candidate_id": report.get("candidate_id", ""),
        "exists": bool(report.get("exists", False)),
        "has_promotion_history": bool(report.get("has_promotion_history", False)),
        "promotion_log_count": int(report.get("promotion_log_count", 0)),
    }
    if latest_promotion is not None:
        compact_report["latest_promotion"] = latest_promotion
    return json.dumps(compact_report, ensure_ascii=False, indent=2)


def render_candidate_review_report(report: dict[str, Any], *, compact: bool = False) -> str:
    if not compact:
        return json.dumps(report, ensure_ascii=False, indent=2)
    identity = report.get("identity", {}) if isinstance(report.get("identity"), dict) else {}
    review = report.get("review", {}) if isinstance(report.get("review"), dict) else {}
    promotion_check = report.get("promotion_check", {}) if isinstance(report.get("promotion_check"), dict) else {}
    promotion_history = report.get("promotion_history", {}) if isinstance(report.get("promotion_history"), dict) else {}
    compact_report = {
        "candidate_id": report.get("candidate_id", ""),
        "exists": bool(report.get("exists", False)),
        "title": identity.get("title", ""),
        "destination": identity.get("destination", ""),
        "status": identity.get("status", ""),
        "trust_level": identity.get("trust_level", ""),
        "eligible": bool(promotion_check.get("eligible", False)),
        "eligibility_code": promotion_check.get("eligibility_code", ""),
        "planned_target_path": promotion_check.get("planned_target_path"),
        "would_copy": bool(promotion_check.get("would_copy", False)),
        "target_already_matches": bool(promotion_check.get("target_already_matches", False)),
        "has_conflict": bool(promotion_check.get("has_conflict", False)),
        "conflict_reason": promotion_check.get("conflict_reason", ""),
        "has_promotion_history": bool(promotion_history.get("has_promotion_history", False)),
        "promotion_log_count": int(promotion_history.get("promotion_log_count", 0)),
        "audit_flags": report.get("audit_flags", []),
    }
    if review.get("review_decision"):
        compact_report["review_decision"] = review.get("review_decision")
    if review.get("review_decided_at"):
        compact_report["review_decided_at"] = review.get("review_decided_at")
    return json.dumps(compact_report, ensure_ascii=False, indent=2)


def record_candidate_review_decision(candidate_id: str, decision: str, *, notes: str = "") -> dict[str, Any]:
    ensure_curated_source_dirs()
    normalized_decision = _validate_choice(decision, REVIEW_DECISIONS, "decision")
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() != str(candidate_id).strip():
            continue
        if str(candidate.get("status", "")).strip() == "promoted":
            raise ValueError("review decision cannot be recorded for an already promoted candidate")
        timestamp = _now_iso()
        candidate["review_decision"] = normalized_decision
        candidate["review_decided_at"] = timestamp
        candidate["review_notes"] = str(notes or "").strip()
        target = candidate
        break
    if target is None:
        raise ValueError(f"candidate_id not found: {candidate_id}")
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    return target


def reclassify_candidate_destination(candidate_id: str, destination: str, *, reason: str = "") -> dict[str, Any]:
    ensure_curated_source_dirs()
    normalized_destination = _validate_choice(destination, DESTINATIONS, "destination")
    normalized_reason = str(reason or "").strip()
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() != str(candidate_id).strip():
            continue
        if str(candidate.get("status", "")).strip() == "promoted":
            raise ValueError("destination cannot be reclassified for an already promoted candidate")
        current_destination = str(candidate.get("destination", "")).strip()
        if current_destination == normalized_destination:
            raise ValueError("destination is already set to the requested value")
        timestamp = _now_iso()
        candidate["destination"] = normalized_destination
        candidate["destination_changed_at"] = timestamp
        candidate["destination_changed_from"] = current_destination
        candidate["destination_changed_reason"] = normalized_reason
        destination_change_log = candidate.get("destination_change_log")
        if not isinstance(destination_change_log, list):
            destination_change_log = []
        destination_change_log.append(
            _build_destination_change_event(
                changed_at=timestamp,
                changed_from=current_destination,
                changed_to=normalized_destination,
                reason=normalized_reason,
            )
        )
        candidate["destination_change_log"] = destination_change_log
        target = candidate
        break
    if target is None:
        raise ValueError(f"candidate_id not found: {candidate_id}")
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    sync_destination_manifests(candidates)
    return target


def update_candidate_status(candidate_id: str, status: str) -> dict[str, Any]:
    ensure_curated_source_dirs()
    status = _validate_choice(status, STATUSES, "status")
    manifest = load_source_candidates_manifest()
    candidates = [item for item in manifest.get("candidates", []) if isinstance(item, dict)]
    target = None
    for candidate in candidates:
        if str(candidate.get("candidate_id", "")).strip() != str(candidate_id).strip():
            continue
        candidate["status"] = status
        timestamp = _now_iso()
        if status == "promoted":
            candidate["promoted_at"] = timestamp
        else:
            candidate["reviewed_at"] = timestamp
        target = candidate
        break
    if target is None:
        raise ValueError(f"candidate_id not found: {candidate_id}")
    write_source_candidates_manifest(sorted(candidates, key=lambda item: str(item.get("candidate_id", ""))))
    sync_destination_manifests(candidates)
    return target


def build_curated_sources_report() -> dict[str, Any]:
    ensure_curated_source_dirs()
    indexes = [item for item in load_source_indexes_manifest().get("indexes", []) if isinstance(item, dict)]
    candidates = [item for item in load_source_candidates_manifest().get("candidates", []) if isinstance(item, dict)]
    candidate_consistency = _build_candidate_consistency(candidates)
    return {
        "policy_version": POLICY_VERSION,
        "index_summary": {
            "count": len(indexes),
            "by_trust_level": {
                trust_level: sum(1 for item in indexes if str(item.get("trust_level", "")).strip() == trust_level)
                for trust_level in sorted(TRUST_LEVELS)
            },
            "by_destination": {
                destination: sum(1 for item in indexes if str(item.get("destination", "")).strip() == destination)
                for destination in sorted(DESTINATIONS)
            },
        },
        "candidate_summary": {
            "count": len(candidates),
            "promoted_count": sum(1 for item in candidates if str(item.get("status", "")).strip() == "promoted"),
            "by_origin": {
                origin: sum(
                    1
                    for item in candidates
                    if (
                        str(item.get("source_origin", "")).strip()
                        or _infer_source_origin(
                            str(item.get("source_url", "")).strip(),
                            str(item.get("artifact_path", "")).strip(),
                        )
                    )
                    == origin
                )
                for origin in sorted(SOURCE_ORIGINS)
            },
            "by_destination": {
                destination: sum(1 for item in candidates if str(item.get("destination", "")).strip() == destination)
                for destination in sorted(DESTINATIONS)
            },
            "by_trust_level": {
                trust_level: sum(1 for item in candidates if str(item.get("trust_level", "")).strip() == trust_level)
                for trust_level in sorted(TRUST_LEVELS)
            },
            "by_status": {
                status: sum(1 for item in candidates if str(item.get("status", "")).strip() == status)
                for status in sorted(STATUSES)
            },
        },
        "candidate_consistency": candidate_consistency,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Gerencia a camada de ingestao por fontes curadas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("bootstrap-pilot", help="Cria manifests e seeds do piloto de indices curados.")
    subparsers.add_parser("report", help="Mostra um resumo da camada de fontes curadas.")
    subparsers.add_parser("validate-candidates", help="Audita rapidamente a consistencia dos candidatos.")
    subparsers.add_parser("candidate-stats", help="Mostra um resumo operacional curto dos candidatos.")
    subparsers.add_parser("audit-metadata", help="Audita qualidade de metadados dos candidatos.")
    subparsers.add_parser("audit-semantic", help="Audita coerencia semantica entre metadados dos candidatos.")
    subparsers.add_parser("audit-operational", help="Audita cobertura e coerencia operacional dos metadados.")
    audit_summary = subparsers.add_parser("candidate-audit-summary", help="Mostra um snapshot curto do estado das auditorias.")
    audit_summary.add_argument("--show-nonzero-categories", action="store_true")
    audit_summary.add_argument("--show-category-counts", action="store_true")
    audit_summary.add_argument("--sort-category-counts", action="store_true")
    list_candidates = subparsers.add_parser("list-candidates", help="Lista candidatos com filtros operacionais.")
    list_candidates.add_argument("--origin", default="", choices=[""] + sorted(SOURCE_ORIGINS))
    list_candidates.add_argument("--destination", default="", choices=[""] + sorted(DESTINATIONS))
    list_candidates.add_argument("--status", default="", choices=[""] + sorted(STATUSES))
    list_candidates.add_argument("--review-decision", default="", choices=[""] + sorted(REVIEW_DECISION_FILTERS))
    list_candidates.add_argument("--has-promotion-history", default="", choices=[""] + sorted(BOOLEAN_FILTERS))
    list_candidates.add_argument("--eligibility-code", default="")
    list_candidates.add_argument("--promotion-ready", default="", choices=[""] + sorted(BOOLEAN_FILTERS))
    list_candidates.add_argument("--query", default="")
    list_candidates.add_argument("--has-artifact-path", action="store_true")
    list_candidates.add_argument("--artifact-exists", default="", choices=[""] + sorted(ARTIFACT_EXISTS_FILTERS))
    list_candidates.add_argument("--field", action="append", choices=sorted(LIST_CANDIDATE_FIELDS), default=[])
    list_candidates.add_argument("--json-lines", action="store_true")
    list_candidates.add_argument("--compact", action="store_true")
    list_candidates.add_argument("--limit", type=int, default=None)

    register = subparsers.add_parser("register-candidate", help="Registra um recurso candidato descoberto por indice curado.")
    register.add_argument("--title", required=True)
    register_source = register.add_mutually_exclusive_group(required=True)
    register_source.add_argument("--url")
    register_source.add_argument("--artifact-path")
    register.add_argument("--source-kind", default="candidate_resource", choices=sorted(SOURCE_KINDS))
    register.add_argument("--trust-level", default="medium_trust", choices=sorted(TRUST_LEVELS))
    register.add_argument("--destination", default="raw_review", choices=sorted(DESTINATIONS))
    register.add_argument("--status", default="candidate", choices=sorted(STATUSES))
    register.add_argument("--parser-hint", default="")
    register.add_argument("--discovered-from", default="")
    register.add_argument("--notes", default="")
    register.add_argument("--strong-evidence", action="store_true", help="Marca explicitamente como evidencia forte.")

    promote = subparsers.add_parser("promote-candidate", help="Promove manualmente um candidato local para o nucleo.")
    promote.add_argument("--candidate-id", required=True)
    promote.add_argument("--confirm", action="store_true")

    reconcile = subparsers.add_parser(
        "reconcile-target-match",
        help="Reconcilia manualmente um caso legado ja materializado no destino, sem copia fisica.",
    )
    reconcile.add_argument("--candidate-id", required=True)

    check = subparsers.add_parser("check-promotion", help="Faz preflight somente leitura da promocao de um candidato.")
    check.add_argument("--candidate-id", required=True)
    check.add_argument("--compact", action="store_true")

    review = subparsers.add_parser("review-candidate", help="Mostra uma revisao humana assistida antes da promocao.")
    review.add_argument("--candidate-id", required=True)
    review.add_argument("--compact", action="store_true")

    inspect_target_match = subparsers.add_parser(
        "inspect-target-match",
        help="Inspeciona em modo somente leitura casos em que o alvo ja existe no destino.",
    )
    inspect_target_match.add_argument("--candidate-id", required=True)

    promotion_log = subparsers.add_parser("show-promotion-log", help="Mostra o historico completo de promocao de um candidato.")
    promotion_log.add_argument("--candidate-id", required=True)
    promotion_log.add_argument("--latest-only", action="store_true")
    promotion_log.add_argument("--compact", action="store_true")

    review_decision = subparsers.add_parser(
        "record-review-decision",
        help="Registra explicitamente uma decisao humana de revisao para um candidato.",
    )
    review_decision.add_argument("--candidate-id", required=True)
    review_decision.add_argument("--decision", required=True, choices=sorted(REVIEW_DECISIONS))
    review_decision.add_argument("--notes", default="")

    reclassify_destination = subparsers.add_parser(
        "reclassify-destination",
        help="Reclassifica manualmente o destination de um candidato sem promover nada.",
    )
    reclassify_destination.add_argument("--candidate-id", required=True)
    reclassify_destination.add_argument("--destination", required=True, choices=sorted(DESTINATIONS))
    reclassify_destination.add_argument("--reason", default="")

    update = subparsers.add_parser("set-status", help="Atualiza o status de um candidato.")
    update.add_argument("--candidate-id", required=True)
    update.add_argument("--status", required=True, choices=sorted(STATUSES))

    args = parser.parse_args()

    if args.command == "bootstrap-pilot":
        print(json.dumps(bootstrap_pilot_curated_sources(), ensure_ascii=False, indent=2))
        return

    if args.command == "report":
        print(json.dumps(build_curated_sources_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "validate-candidates":
        print(json.dumps(build_candidate_validation_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "candidate-stats":
        print(json.dumps(build_candidate_stats_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "audit-metadata":
        print(json.dumps(build_candidate_metadata_audit_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "audit-semantic":
        print(json.dumps(build_candidate_semantic_audit_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "audit-operational":
        print(json.dumps(build_candidate_operational_audit_report(), ensure_ascii=False, indent=2))
        return

    if args.command == "candidate-audit-summary":
        print(
            json.dumps(
                build_candidate_audit_summary_report(
                    show_nonzero_categories=args.show_nonzero_categories,
                    show_category_counts=args.show_category_counts,
                    sort_category_counts=args.sort_category_counts,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "list-candidates":
        payload = build_candidate_listing_report(
            origin=args.origin,
            destination=args.destination,
            status=args.status,
            review_decision=args.review_decision,
            has_promotion_history=args.has_promotion_history,
            eligibility_code=args.eligibility_code,
            promotion_ready=args.promotion_ready,
            query=args.query,
            has_artifact_path=args.has_artifact_path,
            artifact_exists=args.artifact_exists,
            fields=args.field,
            limit=args.limit,
        )
        print(render_candidate_listing_report(payload, json_lines=args.json_lines, compact=args.compact))
        return

    if args.command == "register-candidate":
        payload = register_source_candidate(
            title=args.title,
            source_url=args.url or "",
            artifact_path=getattr(args, "artifact_path", "") or "",
            source_kind=args.source_kind,
            trust_level=args.trust_level,
            destination=args.destination,
            status=args.status,
            parser_hint=args.parser_hint,
            discovered_from=args.discovered_from,
            notes=args.notes,
            is_strong_evidence=True if args.strong_evidence else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.command == "promote-candidate":
        print(
            json.dumps(
                promote_source_candidate(
                    args.candidate_id,
                    confirm=args.confirm,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "reconcile-target-match":
        print(json.dumps(reconcile_target_match_candidate(args.candidate_id), ensure_ascii=False, indent=2))
        return

    if args.command == "check-promotion":
        report = inspect_promotion_candidate(args.candidate_id)
        print(_compact_promotion_check_report(report) if args.compact else render_promotion_check_report(report, compact=False))
        return

    if args.command == "review-candidate":
        print(render_candidate_review_report(build_candidate_review_report(args.candidate_id), compact=args.compact))
        return

    if args.command == "inspect-target-match":
        print(json.dumps(build_target_match_inspection_report(args.candidate_id), ensure_ascii=False, indent=2))
        return

    if args.command == "show-promotion-log":
        print(
            render_candidate_promotion_log_report(
                build_candidate_promotion_log_report(args.candidate_id, latest_only=args.latest_only and not args.compact),
                compact=args.compact,
            )
        )
        return

    if args.command == "record-review-decision":
        print(
            json.dumps(
                record_candidate_review_decision(
                    args.candidate_id,
                    args.decision,
                    notes=args.notes,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "reclassify-destination":
        print(
            json.dumps(
                reclassify_candidate_destination(
                    args.candidate_id,
                    args.destination,
                    reason=args.reason,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "set-status":
        print(json.dumps(update_candidate_status(args.candidate_id, args.status), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    _main()
