import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.question_bank_items import load_items_payload
from app.services.question_bank_parsers import QUESTION_BANK_ITEMS_DIR, ensure_question_bank_dirs

KNOWLEDGE_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_index" / "knowledge_manifest.json"

COVERAGE_COVERED = "covered"
COVERAGE_PARTIAL = "partial"
COVERAGE_MISSING = "missing"

PROMPT_RULE_PREFIXES = ("python-",)
CONTEXT_RULE_PREFIXES = ("source-context:", "cert-map:")
SUPPORT_PREVIEW_LIMIT = 5
SUPPORT_AGGREGATION_LIMIT = 8
TECHNOLOGY_HINTS = {"python", "aws", "terraform", "fastapi", "react", "docker", "linux", "java"}
HEAVY_HYGIENE_FLAGS = {"mismatched_file_type", "exact_duplicate"}
MODERATE_HYGIENE_FLAGS = {"near_duplicate", "low_value_document"}


def _load_knowledge_documents() -> list[dict[str, Any]]:
    if not KNOWLEDGE_MANIFEST_PATH.exists():
        return []
    try:
        payload = json.loads(KNOWLEDGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    documents = payload.get("documents", [])
    if not isinstance(documents, list):
        return []
    return [
        document
        for document in documents
        if isinstance(document, dict)
        and str(document.get("status", "")).strip() == "parsed"
        and int(document.get("chunk_count", 0) or 0) > 0
    ]


def _load_question_items() -> list[dict[str, Any]]:
    ensure_question_bank_dirs()
    items: list[dict[str, Any]] = []
    for path in sorted(QUESTION_BANK_ITEMS_DIR.glob("*.items.json")):
        payload = load_items_payload(path)
        if not payload:
            continue
        items.extend(item for item in payload.get("items", []) if isinstance(item, dict))
    return items


def _normalize_tags(tags: Any) -> dict[str, set[str]]:
    if not isinstance(tags, dict):
        return {"all": set(), "domain": set(), "subtheme": set()}
    return {
        "all": {str(item) for item in tags.get("all", []) if str(item).strip()},
        "domain": {str(item) for item in tags.get("domain", []) if str(item).strip()},
        "subtheme": {str(item) for item in tags.get("subtheme", []) if str(item).strip()},
    }


def _normalize_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def _has_term(text: str, term: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_term = _normalize_text(term)
    if not normalized_term:
        return False
    if " " in normalized_term or "/" in normalized_term or "-" in normalized_term:
        return normalized_term in normalized_text
    escaped = re.escape(normalized_term)
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", normalized_text))


def _matched_rule_sets(item: dict[str, Any]) -> tuple[list[str], list[str]]:
    debug = item.get("metadata_debug") if isinstance(item.get("metadata_debug"), dict) else {}
    rules = [str(rule) for rule in debug.get("matched_rules", []) if str(rule).strip()]
    prompt_rules = [rule for rule in rules if rule.startswith(PROMPT_RULE_PREFIXES)]
    context_rules = [rule for rule in rules if rule.startswith(CONTEXT_RULE_PREFIXES)]
    return prompt_rules, context_rules


def _build_document_alignment_bonus(
    document: dict[str, Any],
    item_tags: set[str],
    item_domain: str,
    item_subtheme: str,
) -> tuple[float, list[str]]:
    title = str(document.get("title", ""))
    source_file = str(document.get("source_file", ""))
    text = f"{title} {source_file}"
    matched_terms: list[str] = []
    bonus = 0.0

    if item_subtheme and _has_term(text, item_subtheme):
        matched_terms.append(item_subtheme)
        bonus += 2.0
    if item_domain and _has_term(text, item_domain):
        matched_terms.append(item_domain)
        bonus += 1.0

    for tag in sorted(item_tags):
        if tag in {"backend", "frontend", "cloud", "devops", "networking", "security"}:
            continue
        if _has_term(text, tag):
            matched_terms.append(tag)
            bonus += 1.5 if tag in TECHNOLOGY_HINTS else 1.0

    if item_tags == {"backend", "python"} and _has_term(text, "python"):
        if "python" not in matched_terms:
            matched_terms.append("python")
        bonus += 1.0

    return round(bonus, 3), matched_terms


def _build_document_support(item: dict[str, Any], knowledge_documents: list[dict[str, Any]]) -> dict[str, Any]:
    item_tags = {str(tag) for tag in item.get("inferred_tags", []) if str(tag).strip()}
    item_domain = str(item.get("inferred_domain") or "").strip()
    item_subtheme = str(item.get("inferred_subtheme") or "").strip()

    supporting_documents = []
    matched_tags: set[str] = set()
    domain_match_count = 0
    subtheme_match_count = 0

    for document in knowledge_documents:
        doc_tags = _normalize_tags(document.get("tags"))
        shared_tags = sorted(item_tags & doc_tags["all"])
        domain_matched = bool(item_domain and item_domain in doc_tags["domain"])
        subtheme_matched = bool(item_subtheme and item_subtheme in doc_tags["subtheme"])
        if not shared_tags and not domain_matched and not subtheme_matched:
            continue
        matched_tags.update(shared_tags)
        domain_match_count += 1 if domain_matched else 0
        subtheme_match_count += 1 if subtheme_matched else 0
        alignment_bonus, title_matches = _build_document_alignment_bonus(
            document=document,
            item_tags=item_tags,
            item_domain=item_domain,
            item_subtheme=item_subtheme,
        )
        hygiene_flags = {str(flag) for flag in document.get("hygiene_flags", []) if str(flag).strip()}
        hygiene_score = float(document.get("hygiene_score", 1.0) or 1.0)
        is_strong_evidence = bool(document.get("is_strong_evidence", True))
        chunk_count = int(document.get("chunk_count", 0) or 0)
        depth_bonus = min(1.25, math.log10(chunk_count + 1))
        support_score = (
            len(shared_tags)
            + (1.5 if domain_matched else 0.0)
            + (3.0 if subtheme_matched else 0.0)
            + alignment_bonus
            + depth_bonus
        )
        if hygiene_flags & HEAVY_HYGIENE_FLAGS:
            support_score *= 0.2
        elif hygiene_flags & MODERATE_HYGIENE_FLAGS:
            support_score *= 0.65
        else:
            support_score *= max(0.5, min(1.0, hygiene_score))
        if not is_strong_evidence:
            support_score *= 0.35
        supporting_documents.append(
            {
                "source_file": document.get("source_file", ""),
                "title": document.get("title", ""),
                "shared_tags": shared_tags,
                "domain_matched": domain_matched,
                "subtheme_matched": subtheme_matched,
                "chunk_count": chunk_count,
                "alignment_bonus": alignment_bonus,
                "title_matches": title_matches,
                "hygiene_flags": sorted(hygiene_flags),
                "hygiene_score": round(hygiene_score, 3),
                "trust_level": str(document.get("trust_level", "")).strip(),
                "source_kind": str(document.get("source_kind", "")).strip(),
                "is_strong_evidence": is_strong_evidence,
                "strong_evidence_eligible": is_strong_evidence and not bool(hygiene_flags & HEAVY_HYGIENE_FLAGS),
                "score": round(support_score, 3),
            }
        )

    supporting_documents.sort(
        key=lambda doc: (
            -float(doc.get("score", 0.0)),
            -float(doc.get("alignment_bonus", 0.0)),
            -int(doc.get("chunk_count", 0)),
            str(doc.get("source_file", "")),
        )
    )
    aggregated_documents = supporting_documents[:SUPPORT_AGGREGATION_LIMIT]
    preview_documents = aggregated_documents[:SUPPORT_PREVIEW_LIMIT]
    return {
        "supporting_documents": preview_documents,
        "aggregated_documents": aggregated_documents,
        "matched_tags": matched_tags,
        "domain_match_count": domain_match_count,
        "subtheme_match_count": subtheme_match_count,
    }


def _build_chunk_support(aggregated_documents: list[dict[str, Any]]) -> dict[str, Any]:
    strong_documents = [support for support in aggregated_documents if bool(support.get("strong_evidence_eligible", True))]
    chunk_counts = [int(support.get("chunk_count", 0) or 0) for support in strong_documents]
    chunk_total = sum(chunk_counts)
    chunk_max = max(chunk_counts) if chunk_counts else 0
    support_score = 0.0
    supporting_document_count = len(aggregated_documents)
    strong_supporting_document_count = len(strong_documents)
    aligned_document_count = sum(1 for support in strong_documents if float(support.get("alignment_bonus", 0.0)) >= 1.0)
    title_match_count = len(
        {
            match
            for support in strong_documents
            for match in support.get("title_matches", [])
            if str(match).strip()
        }
    )
    weighted_document_score = sum(
        float(support.get("score", 0.0)) / math.sqrt(index)
        for index, support in enumerate(strong_documents, start=1)
    )

    if strong_supporting_document_count >= 2:
        support_score += 1.0
    if strong_supporting_document_count >= 4:
        support_score += 1.0
    if strong_supporting_document_count >= 6:
        support_score += 0.75
    if strong_supporting_document_count >= 8:
        support_score += 0.5

    if chunk_total >= 200:
        support_score += 1.0
    if chunk_total >= 800:
        support_score += 0.75
    if chunk_total >= 2000:
        support_score += 0.75
    if chunk_total >= 5000:
        support_score += 0.5
    if chunk_max >= 100:
        support_score += 0.5
    if chunk_max >= 500:
        support_score += 0.5

    if aligned_document_count >= 2:
        support_score += 0.75
    if aligned_document_count >= 4:
        support_score += 0.75
    if title_match_count >= 2:
        support_score += 0.5
    if weighted_document_score >= 20:
        support_score += 0.75
    if weighted_document_score >= 35:
        support_score += 0.75

    return {
        "supporting_document_count": supporting_document_count,
        "strong_supporting_document_count": strong_supporting_document_count,
        "supporting_chunk_total": chunk_total,
        "largest_supporting_document_chunks": chunk_max,
        "aligned_document_count": aligned_document_count,
        "title_match_count": title_match_count,
        "weighted_document_score": round(weighted_document_score, 3),
        "support_score": round(support_score, 3),
    }


def _calculate_coverage(item: dict[str, Any], knowledge_documents: list[dict[str, Any]]) -> dict[str, Any]:
    item_tags = {str(tag) for tag in item.get("inferred_tags", []) if str(tag).strip()}
    prompt_rules, context_rules = _matched_rule_sets(item)
    support = _build_document_support(item, knowledge_documents)
    supporting_documents = support["supporting_documents"]
    matched_tags = support["matched_tags"]
    domain_match_count = support["domain_match_count"]
    subtheme_match_count = support["subtheme_match_count"]
    chunk_support = _build_chunk_support(support["aggregated_documents"])

    score = 0.0
    evidence_signals: list[str] = []

    if subtheme_match_count >= 1:
        score += 4.0
        evidence_signals.append("subtheme_match")
    if len(matched_tags) >= 3:
        score += 3.0
        evidence_signals.append("multi_tag_match")
    elif len(matched_tags) >= 2:
        score += 2.0
        evidence_signals.append("two_tag_match")
    elif len(matched_tags) == 1:
        score += 1.0
        evidence_signals.append("single_tag_match")
    if domain_match_count >= 2:
        score += 2.0
        evidence_signals.append("multiple_domain_matches")
    elif domain_match_count == 1:
        score += 1.0
        evidence_signals.append("single_domain_match")
    if chunk_support["support_score"] >= 4.0:
        score += 3.0
        evidence_signals.append("strong_knowledge_volume")
    elif chunk_support["support_score"] >= 2.0:
        score += 2.0
        evidence_signals.append("medium_knowledge_volume")
    elif chunk_support["support_score"] > 0:
        score += 1.0
        evidence_signals.append("light_knowledge_volume")
    if chunk_support["aligned_document_count"] >= 4:
        score += 1.5
        evidence_signals.append("aligned_source_diversity")
    elif chunk_support["aligned_document_count"] >= 2:
        score += 1.0
        evidence_signals.append("aligned_source_support")
    if chunk_support["title_match_count"] >= 2:
        score += 0.75
        evidence_signals.append("title_level_alignment")
    if prompt_rules:
        score += 2.0
        evidence_signals.append("prompt_based_metadata")
    elif context_rules:
        score += 0.5
        evidence_signals.append("context_based_metadata")
    if item_tags == {"backend", "python"}:
        penalty = 1.5
        if chunk_support["aligned_document_count"] >= 3 and chunk_support["support_score"] >= 5.0:
            penalty = 0.5
            evidence_signals.append("generic_python_penalty_softened")
        score -= penalty
        evidence_signals.append("generic_python_penalty")
    if context_rules and not prompt_rules:
        penalty = 1.5
        if chunk_support["aligned_document_count"] >= 3 or chunk_support["title_match_count"] >= 2:
            penalty = 0.5
            evidence_signals.append("context_only_penalty_softened")
        score -= penalty
        evidence_signals.append("context_only_penalty")
    if not matched_tags and domain_match_count == 0 and chunk_support["support_score"] <= 0:
        score -= 2.0
        evidence_signals.append("weak_knowledge_evidence")

    coverage_score = round(score, 3)
    if coverage_score >= 7.0 and (
        subtheme_match_count >= 1
        or len(matched_tags) >= 2
        or chunk_support["support_score"] >= 3.0
    ):
        coverage = COVERAGE_COVERED
        reason = "Strong evidence from knowledge tags/chunks."
    elif coverage_score >= 3.0:
        coverage = COVERAGE_PARTIAL
        reason = "Some evidence exists, but it is generic or mostly contextual."
    else:
        coverage = COVERAGE_MISSING
        reason = "Knowledge evidence is weak or absent."

    return {
        "question_id": item.get("question_id", ""),
        "source_file": item.get("source_file", ""),
        "prompt": item.get("prompt", ""),
        "item_type": item.get("item_type", ""),
        "inferred_tags": sorted(item_tags),
        "inferred_domain": item.get("inferred_domain"),
        "inferred_subtheme": item.get("inferred_subtheme"),
        "coverage": coverage,
        "coverage_score": coverage_score,
        "evidence_signals": evidence_signals,
        "reason": reason,
        "metadata_strength": {
            "prompt_rules": prompt_rules,
            "context_rules": context_rules,
        },
        "matched_tags": sorted(matched_tags),
        "domain_match_count": domain_match_count,
        "subtheme_match_count": subtheme_match_count,
        "supporting_documents": supporting_documents,
        "chunk_support": chunk_support,
    }


def _coverage_record(bucket_key: str) -> dict[str, Any]:
    return {
        bucket_key: "",
        "question_count": 0,
        "covered": 0,
        "partial": 0,
        "missing": 0,
    }


def _append_bucket_stat(bucket: dict[str, Any], coverage: str) -> None:
    bucket["question_count"] += 1
    bucket[coverage] += 1


def build_question_bank_coverage_report(top: int = 10) -> dict[str, Any]:
    knowledge_documents = _load_knowledge_documents()
    question_items = _load_question_items()
    comparisons = [_calculate_coverage(item, knowledge_documents) for item in question_items]

    coverage_counts = {
        COVERAGE_COVERED: sum(1 for item in comparisons if item["coverage"] == COVERAGE_COVERED),
        COVERAGE_PARTIAL: sum(1 for item in comparisons if item["coverage"] == COVERAGE_PARTIAL),
        COVERAGE_MISSING: sum(1 for item in comparisons if item["coverage"] == COVERAGE_MISSING),
    }

    tags_map: dict[str, dict[str, Any]] = {}
    domains_map: dict[str, dict[str, Any]] = {}
    subthemes_map: dict[str, dict[str, Any]] = {}

    for item in comparisons:
        coverage = item["coverage"]
        for tag in item.get("inferred_tags", []):
            bucket = tags_map.setdefault(tag, _coverage_record("tag"))
            bucket["tag"] = tag
            _append_bucket_stat(bucket, coverage)
        if not item.get("inferred_tags"):
            bucket = tags_map.setdefault("_untagged", _coverage_record("tag"))
            bucket["tag"] = "_untagged"
            _append_bucket_stat(bucket, coverage)
        domain = item.get("inferred_domain")
        if domain:
            bucket = domains_map.setdefault(domain, _coverage_record("domain"))
            bucket["domain"] = domain
            _append_bucket_stat(bucket, coverage)
        else:
            bucket = domains_map.setdefault("_unknown", _coverage_record("domain"))
            bucket["domain"] = "_unknown"
            _append_bucket_stat(bucket, coverage)
        subtheme = item.get("inferred_subtheme")
        if subtheme:
            bucket = subthemes_map.setdefault(subtheme, _coverage_record("subtheme"))
            bucket["subtheme"] = subtheme
            _append_bucket_stat(bucket, coverage)
        else:
            bucket = subthemes_map.setdefault("_none", _coverage_record("subtheme"))
            bucket["subtheme"] = "_none"
            _append_bucket_stat(bucket, coverage)

    def sort_buckets(records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        items = [record for record in records.values() if int(record["missing"]) > 0 or int(record["partial"]) > 0]
        items.sort(key=lambda record: (-int(record["missing"]), -int(record["partial"]), -int(record["question_count"])))
        return items[:top]

    covered_examples = [item for item in comparisons if item["coverage"] == COVERAGE_COVERED][:top]
    partial_examples = [item for item in comparisons if item["coverage"] == COVERAGE_PARTIAL][:top]
    missing_examples = [item for item in comparisons if item["coverage"] == COVERAGE_MISSING][:top]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": "question_bank_coverage",
        "question_item_count": len(question_items),
        "knowledge_document_count": len(knowledge_documents),
        "coverage_counts": coverage_counts,
        "tag_gaps": sort_buckets(tags_map),
        "domain_gaps": sort_buckets(domains_map),
        "subtheme_gaps": sort_buckets(subthemes_map),
        "covered_examples": covered_examples,
        "partial_examples": partial_examples,
        "missing_examples": missing_examples,
        "items": comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara cobertura entre question_bank e knowledge por tags, dominio e subtema")
    parser.add_argument("--top", type=int, default=10, help="Quantidade maxima por lista do diagnostico")
    parser.add_argument("--pretty", action="store_true", help="Renderiza JSON identado")
    args = parser.parse_args()

    payload = build_question_bank_coverage_report(top=max(1, args.top))
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
