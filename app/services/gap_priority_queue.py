import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.certification_map import CERT_MAP_DIR
from app.services.knowledge_tags import infer_query_tags, infer_tags, merge_tags

GAP_HISTORY_FILE = CERT_MAP_DIR / "gap_history.json"
GAP_QUEUE_FILE = CERT_MAP_DIR / "gap_queue.json"
MISMATCH_RULE_VERSION = 2

STATUS_WEIGHT = {
    "missing": 3.0,
    "partial": 1.0,
    "covered": 0.0,
}
DOMAIN_REPEAT_BONUS = 0.75

TRACK_TAG_PROFILES: dict[str, dict[str, set[str]]] = {
    "python": {
        "technology": {"python", "fastapi"},
        "domain": {"backend"},
        "subtheme": {"dependency-injection", "api-design", "oop"},
    },
    "frontend": {
        "technology": {"react"},
        "domain": {"frontend"},
        "subtheme": set(),
    },
    "cloud": {
        "technology": {"aws", "terraform"},
        "domain": {"cloud"},
        "subtheme": {"iam-policy"},
    },
    "devops": {
        "technology": {"docker", "linux", "terraform", "aws"},
        "domain": {"devops", "networking", "security"},
        "subtheme": {"containers", "firewall"},
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    if isinstance(payload, dict):
        return payload
    return fallback


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_key(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _safe_tag_payload(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {"technology": [], "domain": [], "subtheme": [], "all": []}
    technology = [str(item).strip() for item in value.get("technology", []) if str(item).strip()]
    domain = [str(item).strip() for item in value.get("domain", []) if str(item).strip()]
    subtheme = [str(item).strip() for item in value.get("subtheme", []) if str(item).strip()]
    all_tags = sorted(set(technology + domain + subtheme))
    return {
        "technology": sorted(set(technology)),
        "domain": sorted(set(domain)),
        "subtheme": sorted(set(subtheme)),
        "all": all_tags,
    }


def _derive_used_tags_and_scope(inferred_tags: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    technology = inferred_tags.get("technology", [])
    subtheme = inferred_tags.get("subtheme", [])
    domain = inferred_tags.get("domain", [])
    used_tags = sorted(set([*technology, *subtheme])) or sorted(set(domain))
    scopes: list[str] = []
    if technology:
        scopes.append("technology")
    if domain:
        scopes.append("domain")
    if subtheme:
        scopes.append("subtheme")
    return used_tags, scopes


def _build_tag_context(analysis: dict[str, Any], domain_name: str, recommended_topics: list[str]) -> dict[str, Any]:
    inferred_tags = merge_tags(
        _safe_tag_payload(analysis.get("inferred_tags")),
        infer_query_tags(str(analysis.get("query", ""))),
        infer_tags(content=domain_name),
        infer_tags(content=" ".join(recommended_topics)),
    )
    used_tags, tag_scope = _derive_used_tags_and_scope(inferred_tags)
    return {
        "inferred_tags": inferred_tags,
        "used_tags": used_tags,
        "tag_scope": tag_scope,
    }


def _evaluate_track_coherence(track: str, inferred_tags: dict[str, list[str]]) -> dict[str, Any]:
    normalized_track = _normalize_key(track)
    if not normalized_track:
        return {
            "mismatched_track": False,
            "suggested_track": "",
            "confidence": 0.0,
        }

    tag_sets = {
        "technology": set(str(item) for item in inferred_tags.get("technology", []) if str(item).strip()),
        "domain": set(str(item) for item in inferred_tags.get("domain", []) if str(item).strip()),
        "subtheme": set(str(item) for item in inferred_tags.get("subtheme", []) if str(item).strip()),
    }
    if not any(tag_sets.values()):
        return {
            "mismatched_track": False,
            "suggested_track": "",
            "confidence": 0.0,
        }

    weights = {"technology": 3.0, "domain": 2.0, "subtheme": 2.0}
    scores: dict[str, float] = {}
    for candidate_track, profile in TRACK_TAG_PROFILES.items():
        score = 0.0
        for tag_type in ("technology", "domain", "subtheme"):
            profile_tags = profile.get(tag_type, set())
            score += len(tag_sets[tag_type] & profile_tags) * weights[tag_type]
        scores[candidate_track] = score

    best_track, best_score = max(scores.items(), key=lambda item: item[1], default=(normalized_track, 0.0))
    current_track_score = float(scores.get(normalized_track, 0.0) or 0.0)
    total_score = sum(value for value in scores.values() if value > 0.0)
    confidence = (best_score / total_score) if total_score > 0.0 else 0.0

    mismatched = bool(
        best_track != normalized_track
        and best_score >= 3.0
        and confidence >= 0.55
    )
    return {
        "mismatched_track": mismatched,
        "suggested_track": best_track if mismatched else "",
        "confidence": round(confidence, 3) if mismatched else 0.0,
    }


def _build_record(analysis: dict[str, Any]) -> dict[str, Any]:
    domain = analysis.get("domain", {}) if isinstance(analysis.get("domain"), dict) else {}
    recommended_topics = _safe_list(analysis.get("recommended_topics"))
    domain_name = str(domain.get("domain_name", "") or domain.get("domain", "")).strip()
    tag_context = _build_tag_context(analysis, domain_name=domain_name, recommended_topics=recommended_topics)
    track = str(analysis.get("track", "")).strip()
    coherence = _evaluate_track_coherence(track=track, inferred_tags=tag_context["inferred_tags"])
    return {
        "query": str(analysis.get("query", "")).strip(),
        "certification_track": track,
        "certification": str(domain.get("certification", "")).strip(),
        "domain": domain_name,
        "status": str(analysis.get("status", "missing")).strip().lower(),
        "recommended_topics": recommended_topics,
        "inferred_tags": tag_context["inferred_tags"],
        "used_tags": tag_context["used_tags"],
        "tag_scope": tag_context["tag_scope"],
        "mismatched_track": bool(coherence["mismatched_track"]),
        "suggested_track": str(coherence["suggested_track"]),
        "confidence": float(coherence["confidence"]),
        "mismatch_rule_version": MISMATCH_RULE_VERSION,
        "timestamp": _now_iso(),
    }


def _default_history() -> dict[str, Any]:
    return {"version": 1, "records": []}


def _default_queue() -> dict[str, Any]:
    return {
        "version": 1,
        "weights": {
            "missing": STATUS_WEIGHT["missing"],
            "partial": STATUS_WEIGHT["partial"],
            "domain_repeat_bonus": DOMAIN_REPEAT_BONUS,
        },
        "updated_at": "",
        "domain_gap_counts": {},
        "items": [],
    }


def _recompute_priorities(queue: dict[str, Any]) -> None:
    domain_counts = queue.get("domain_gap_counts", {})
    items = queue.get("items", [])
    if not isinstance(domain_counts, dict) or not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        missing_count = int(item.get("missing_count", 0) or 0)
        partial_count = int(item.get("partial_count", 0) or 0)
        domain_key = str(item.get("domain_key", ""))
        domain_repeat = int(domain_counts.get(domain_key, 0) or 0)
        base = (missing_count * STATUS_WEIGHT["missing"]) + (partial_count * STATUS_WEIGHT["partial"])
        repeat_bonus = max(0, domain_repeat - 1) * DOMAIN_REPEAT_BONUS
        item["domain_occurrences"] = domain_repeat
        item["priority_score"] = round(base + repeat_bonus, 3)


def _prune_queue_track_mismatch_fields(queue: dict[str, Any]) -> None:
    items = queue.get("items", [])
    if not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        item.pop("mismatched_track", None)
        item.pop("mismatch_count", None)
        item.pop("suggested_track", None)
        item.pop("confidence", None)


def _build_grouped_by_certification(items: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for item in items:
        key = "|".join(
            [
                str(item.get("track", "")),
                str(item.get("certification", "")),
            ]
        )
        bucket = groups.setdefault(
            key,
            {
                "track": item.get("track", ""),
                "certification": item.get("certification", ""),
                "total_priority": 0.0,
                "total_occurrences": 0,
                "missing_count": 0,
                "partial_count": 0,
                "unique_domains": set(),
                "unique_topics": 0,
            },
        )
        bucket["total_priority"] += float(item.get("priority_score", 0.0) or 0.0)
        bucket["total_occurrences"] += int(item.get("occurrences", 0) or 0)
        bucket["missing_count"] += int(item.get("missing_count", 0) or 0)
        bucket["partial_count"] += int(item.get("partial_count", 0) or 0)
        bucket["unique_domains"].add(str(item.get("domain_key", "")))
        bucket["unique_topics"] += 1

    output: list[dict[str, Any]] = []
    for row in groups.values():
        output.append(
            {
                "track": row["track"],
                "certification": row["certification"],
                "total_priority": round(float(row["total_priority"]), 3),
                "total_occurrences": int(row["total_occurrences"]),
                "missing_count": int(row["missing_count"]),
                "partial_count": int(row["partial_count"]),
                "unique_domains": len(row["unique_domains"]),
                "unique_topics": int(row["unique_topics"]),
            }
        )

    return sorted(
        output,
        key=lambda item: (-float(item.get("total_priority", 0.0)), -int(item.get("total_occurrences", 0))),
    )[:top]


def _build_grouped_by_domain(items: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for item in items:
        key = str(item.get("domain_key", ""))
        bucket = groups.setdefault(
            key,
            {
                "track": item.get("track", ""),
                "certification": item.get("certification", ""),
                "domain": item.get("domain", ""),
                "total_priority": 0.0,
                "total_occurrences": 0,
                "missing_count": 0,
                "partial_count": 0,
                "unique_topics": 0,
            },
        )
        bucket["total_priority"] += float(item.get("priority_score", 0.0) or 0.0)
        bucket["total_occurrences"] += int(item.get("occurrences", 0) or 0)
        bucket["missing_count"] += int(item.get("missing_count", 0) or 0)
        bucket["partial_count"] += int(item.get("partial_count", 0) or 0)
        bucket["unique_topics"] += 1

    output: list[dict[str, Any]] = []
    for row in groups.values():
        output.append(
            {
                "track": row["track"],
                "certification": row["certification"],
                "domain": row["domain"],
                "total_priority": round(float(row["total_priority"]), 3),
                "total_occurrences": int(row["total_occurrences"]),
                "missing_count": int(row["missing_count"]),
                "partial_count": int(row["partial_count"]),
                "unique_topics": int(row["unique_topics"]),
            }
        )

    return sorted(
        output,
        key=lambda item: (-float(item.get("total_priority", 0.0)), -int(item.get("total_occurrences", 0))),
    )[:top]


def _extract_item_tags(item: dict[str, Any]) -> dict[str, list[str]]:
    inferred_tags = _safe_tag_payload(item.get("inferred_tags"))
    if inferred_tags.get("all"):
        return inferred_tags
    fallback = merge_tags(
        infer_query_tags(str(item.get("recommended_topic", ""))),
        infer_tags(content=str(item.get("domain", ""))),
        infer_tags(content=" ".join([str(value) for value in item.get("queries", []) if str(value).strip()])),
    )
    return _safe_tag_payload(fallback)


def _build_grouped_by_tag(items: list[dict[str, Any]], tag_type: str, top: int) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for item in items:
        tags = _extract_item_tags(item).get(tag_type, [])
        if not tags:
            continue
        for tag in tags:
            bucket = groups.setdefault(
                str(tag),
                {
                    "tag_type": tag_type,
                    "tag": tag,
                    "total_priority": 0.0,
                    "total_occurrences": 0,
                    "missing_count": 0,
                    "partial_count": 0,
                    "unique_topics": set(),
                    "unique_domains": set(),
                },
            )
            bucket["total_priority"] += float(item.get("priority_score", 0.0) or 0.0)
            bucket["total_occurrences"] += int(item.get("occurrences", 0) or 0)
            bucket["missing_count"] += int(item.get("missing_count", 0) or 0)
            bucket["partial_count"] += int(item.get("partial_count", 0) or 0)
            bucket["unique_topics"].add(str(item.get("recommended_topic", "")))
            bucket["unique_domains"].add(str(item.get("domain_key", "")))

    output: list[dict[str, Any]] = []
    for row in groups.values():
        output.append(
            {
                "tag_type": row["tag_type"],
                "tag": row["tag"],
                "total_priority": round(float(row["total_priority"]), 3),
                "total_occurrences": int(row["total_occurrences"]),
                "missing_count": int(row["missing_count"]),
                "partial_count": int(row["partial_count"]),
                "unique_topics": len(row["unique_topics"]),
                "unique_domains": len(row["unique_domains"]),
            }
        )
    return sorted(
        output,
        key=lambda row: (-float(row.get("total_priority", 0.0)), -int(row.get("total_occurrences", 0))),
    )[:top]


def _select_latest_records_by_query(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_query: dict[str, dict[str, Any]] = {}
    for record in records:
        query_key = _normalize_key(str(record.get("query", "")))
        if not query_key:
            continue
        current = latest_by_query.get(query_key)
        current_timestamp = str(current.get("timestamp", "")) if isinstance(current, dict) else ""
        record_timestamp = str(record.get("timestamp", ""))
        if current is None or record_timestamp >= current_timestamp:
            latest_by_query[query_key] = record
    return list(latest_by_query.values())


def rebuild_mismatch_baseline() -> dict[str, Any]:
    history = _read_json(GAP_HISTORY_FILE, _default_history())
    records = history.get("records", [])
    if not isinstance(records, list):
        records = []
        history["records"] = records

    before_mismatch_count = sum(1 for record in records if isinstance(record, dict) and bool(record.get("mismatched_track", False)))
    changed_records = 0
    promoted_records = 0
    demoted_records = 0

    for record in records:
        if not isinstance(record, dict):
            continue
        previous_mismatch = bool(record.get("mismatched_track", False))
        previous_suggested = str(record.get("suggested_track", ""))
        previous_confidence = float(record.get("confidence", 0.0) or 0.0)

        coherence = _evaluate_track_coherence(
            track=str(record.get("certification_track", "")),
            inferred_tags=_safe_tag_payload(record.get("inferred_tags")),
        )
        new_mismatch = bool(coherence["mismatched_track"])
        new_suggested = str(coherence["suggested_track"])
        new_confidence = float(coherence["confidence"])

        if (
            previous_mismatch != new_mismatch
            or previous_suggested != new_suggested
            or round(previous_confidence, 3) != round(new_confidence, 3)
        ):
            changed_records += 1
            if previous_mismatch and not new_mismatch:
                demoted_records += 1
            elif not previous_mismatch and new_mismatch:
                promoted_records += 1

        record["mismatched_track"] = new_mismatch
        record["suggested_track"] = new_suggested
        record["confidence"] = new_confidence
        record["mismatch_rule_version"] = MISMATCH_RULE_VERSION

    backup_file = ""
    if GAP_HISTORY_FILE.exists():
        backup_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = GAP_HISTORY_FILE.with_name(f"gap_history.pre-mismatch-baseline-{backup_stamp}.json.backup")
        backup_path.write_text(GAP_HISTORY_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        backup_file = str(backup_path)

    after_mismatch_count = sum(1 for record in records if isinstance(record, dict) and bool(record.get("mismatched_track", False)))
    history["mismatch_baseline"] = {
        "rule_version": MISMATCH_RULE_VERSION,
        "rebuilt_at": _now_iso(),
        "criteria": {
            "best_track_differs_from_current_track": True,
            "best_score_min": 3.0,
            "confidence_min": 0.55,
        },
        "records_recomputed": len(records),
        "before_mismatch_count": before_mismatch_count,
        "after_mismatch_count": after_mismatch_count,
    }
    _write_json(GAP_HISTORY_FILE, history)

    return {
        "history_file": str(GAP_HISTORY_FILE),
        "backup_file": backup_file,
        "rule_version": MISMATCH_RULE_VERSION,
        "records_recomputed": len(records),
        "changed_records": changed_records,
        "promoted_records": promoted_records,
        "demoted_records": demoted_records,
        "before_mismatch_count": before_mismatch_count,
        "after_mismatch_count": after_mismatch_count,
    }


def record_gap_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    record = _build_record(analysis)
    status = record["status"]

    history = _read_json(GAP_HISTORY_FILE, _default_history())
    if not isinstance(history.get("records"), list):
        history["records"] = []
    history["records"].append(record)
    _write_json(GAP_HISTORY_FILE, history)

    queue = _read_json(GAP_QUEUE_FILE, _default_queue())
    if not isinstance(queue.get("items"), list):
        queue["items"] = []
    if not isinstance(queue.get("domain_gap_counts"), dict):
        queue["domain_gap_counts"] = {}
    _prune_queue_track_mismatch_fields(queue)

    touched_ids: list[str] = []
    if status in {"missing", "partial"}:
        track = record["certification_track"]
        certification = record["certification"]
        domain = record["domain"]
        domain_key = "|".join([track, certification, _normalize_key(domain)])

        domain_counts = queue["domain_gap_counts"]
        domain_counts[domain_key] = int(domain_counts.get(domain_key, 0) or 0) + 1

        topics = list(record["recommended_topics"])
        if not topics:
            topics = [domain]

        items = queue["items"]
        for topic in topics:
            topic_key = _normalize_key(topic)
            item_id = "|".join([track, certification, _normalize_key(domain), topic_key])
            existing = next((item for item in items if item.get("id") == item_id), None)
            if existing is None:
                existing = {
                    "id": item_id,
                    "track": track,
                    "certification": certification,
                    "domain": domain,
                    "domain_key": domain_key,
                    "recommended_topic": topic,
                    "occurrences": 0,
                    "missing_count": 0,
                    "partial_count": 0,
                    "priority_score": 0.0,
                    "domain_occurrences": 0,
                    "first_seen": record["timestamp"],
                    "last_seen": record["timestamp"],
                    "queries": [],
                    "inferred_tags": record.get("inferred_tags", {"technology": [], "domain": [], "subtheme": [], "all": []}),
                    "used_tags": record.get("used_tags", []),
                    "tag_scope": record.get("tag_scope", []),
                }
                items.append(existing)

            existing["occurrences"] = int(existing.get("occurrences", 0) or 0) + 1
            status_count_key = "missing_count" if status == "missing" else "partial_count"
            existing[status_count_key] = int(existing.get(status_count_key, 0) or 0) + 1
            existing["last_seen"] = record["timestamp"]
            queries = existing.get("queries", [])
            if not isinstance(queries, list):
                queries = []
            query = record["query"]
            if query and query not in queries:
                queries.append(query)
                queries = queries[-6:]
            existing["queries"] = queries
            merged_tags = merge_tags(
                _safe_tag_payload(existing.get("inferred_tags")),
                _safe_tag_payload(record.get("inferred_tags")),
            )
            used_tags, tag_scope = _derive_used_tags_and_scope(merged_tags)
            existing["inferred_tags"] = merged_tags
            existing["used_tags"] = used_tags
            existing["tag_scope"] = tag_scope
            touched_ids.append(item_id)

    _recompute_priorities(queue)
    queue["updated_at"] = _now_iso()
    queue["items"] = sorted(
        queue["items"],
        key=lambda item: (-float(item.get("priority_score", 0.0) or 0.0), -int(item.get("occurrences", 0) or 0)),
    )
    _write_json(GAP_QUEUE_FILE, queue)

    touched = [item for item in queue["items"] if item.get("id") in set(touched_ids)]
    touched = sorted(
        touched,
        key=lambda item: (-float(item.get("priority_score", 0.0) or 0.0), item.get("recommended_topic", "")),
    )
    return {
        "record": record,
        "queue_updates": touched,
        "history_file": str(GAP_HISTORY_FILE),
        "queue_file": str(GAP_QUEUE_FILE),
    }


def get_gap_report(track: str | None = None, top: int = 10) -> dict[str, Any]:
    normalized_track = _normalize_key(track or "")

    history = _read_json(GAP_HISTORY_FILE, _default_history())
    queue = _read_json(GAP_QUEUE_FILE, _default_queue())
    records = history.get("records", []) if isinstance(history.get("records"), list) else []
    items = queue.get("items", []) if isinstance(queue.get("items"), list) else []

    if normalized_track:
        records = [r for r in records if _normalize_key(str(r.get("certification_track", ""))) == normalized_track]
        items = [i for i in items if _normalize_key(str(i.get("track", ""))) == normalized_track]

    gap_records = [
        record
        for record in records
        if _normalize_key(str(record.get("status", ""))) in {"missing", "partial"}
    ]
    mismatch_records = [
        record
        for record in records
        if bool(record.get("mismatched_track", False))
    ]
    current_mismatch_records = [
        record
        for record in _select_latest_records_by_query(records)
        if bool(record.get("mismatched_track", False))
    ]

    frequency_map: dict[str, dict[str, Any]] = {}
    for record in gap_records:
        key = "|".join(
            [
                str(record.get("certification_track", "")),
                str(record.get("certification", "")),
                _normalize_key(str(record.get("domain", ""))),
                _normalize_key(str(record.get("status", ""))),
            ]
        )
        bucket = frequency_map.setdefault(
            key,
            {
                "track": record.get("certification_track", ""),
                "certification": record.get("certification", ""),
                "domain": record.get("domain", ""),
                "status": record.get("status", ""),
                "count": 0,
            },
        )
        bucket["count"] += 1

    most_frequent_gaps = sorted(frequency_map.values(), key=lambda item: -int(item.get("count", 0)))[:top]
    top_topics = sorted(
        items,
        key=lambda item: (
            -float(item.get("priority_score", 0.0) or 0.0),
            -int(item.get("occurrences", 0) or 0),
        ),
    )[:top]

    grouped_by_domain = _build_grouped_by_domain(items, top=top)
    grouped_by_certification = _build_grouped_by_certification(items, top=top)
    grouped_by_tag = {
        "technology": _build_grouped_by_tag(items, tag_type="technology", top=top),
        "domain": _build_grouped_by_tag(items, tag_type="domain", top=top),
        "subtheme": _build_grouped_by_tag(items, tag_type="subtheme", top=top),
    }
    top_gap_tags = sorted(
        grouped_by_tag["technology"] + grouped_by_tag["domain"] + grouped_by_tag["subtheme"],
        key=lambda row: (-float(row.get("total_priority", 0.0)), -int(row.get("total_occurrences", 0))),
    )[:top]

    top_mismatch_records = sorted(
        mismatch_records,
        key=lambda row: (float(row.get("confidence", 0.0) or 0.0), str(row.get("timestamp", ""))),
        reverse=True,
    )[:top]
    top_current_mismatch_records = sorted(
        current_mismatch_records,
        key=lambda row: (float(row.get("confidence", 0.0) or 0.0), str(row.get("timestamp", ""))),
        reverse=True,
    )[:top]

    mismatch_map: dict[str, dict[str, Any]] = {}
    for row in mismatch_records:
        key = "|".join(
            [
                str(row.get("certification_track", "")),
                str(row.get("suggested_track", "")),
            ]
        )
        bucket = mismatch_map.setdefault(
            key,
            {
                "track": row.get("certification_track", ""),
                "suggested_track": row.get("suggested_track", ""),
                "count": 0,
                "avg_confidence": 0.0,
                "sample_queries": [],
            },
        )
        bucket["count"] += 1
        bucket["avg_confidence"] += float(row.get("confidence", 0.0) or 0.0)
        query = str(row.get("query", "")).strip()
        if query and query not in bucket["sample_queries"]:
            bucket["sample_queries"].append(query)
            bucket["sample_queries"] = bucket["sample_queries"][:5]

    top_mismatches: list[dict[str, Any]] = []
    for row in mismatch_map.values():
        count = int(row["count"])
        top_mismatches.append(
            {
                "track": row["track"],
                "suggested_track": row["suggested_track"],
                "count": count,
                "avg_confidence": round(float(row["avg_confidence"]) / count if count else 0.0, 3),
                "sample_queries": row["sample_queries"],
            }
        )
    top_mismatches = sorted(
        top_mismatches,
        key=lambda row: (-int(row.get("count", 0)), -float(row.get("avg_confidence", 0.0))),
    )[:top]

    return {
        "track_filter": track or "",
        "history_count": len(records),
        "queue_count": len(items),
        "mismatch_count": len(mismatch_records),
        "current_mismatch_count": len(current_mismatch_records),
        "most_frequent_gaps": most_frequent_gaps,
        "recommended_ingestion_topics": top_topics,
        "domains_with_lowest_coverage": grouped_by_domain,
        "grouped_by_certification": grouped_by_certification,
        "grouped_by_domain": grouped_by_domain,
        "grouped_by_tag": grouped_by_tag,
        "top_gap_tags": top_gap_tags,
        "mismatch_records": top_mismatch_records,
        "current_mismatch_records": top_current_mismatch_records,
        "top_mismatches": top_mismatches,
        "source_files": {
            "gap_history": str(GAP_HISTORY_FILE),
            "gap_queue": str(GAP_QUEUE_FILE),
        },
    }
