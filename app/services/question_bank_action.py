import argparse
import json
import math
import re
from collections import defaultdict
from typing import Any

from app.services.gap_priority_queue import get_gap_report
from app.services.question_bank_coverage import build_question_bank_coverage_report

ACTION_PRIORITY_WEIGHT = {
    "missing": 3.0,
    "partial": 1.75,
    "covered": 0.25,
}

ACTION_PRIORITY_LABEL = {
    "missing": "max",
    "partial": "high",
    "covered": "low",
}
ACTION_PRIORITY_RANK = {
    "max": 3,
    "high": 2,
    "low": 1,
}

DEFAULT_SOURCE_HINTS = [
    "documentação oficial",
    "guias técnicos",
    "tutoriais de referência",
]

SOURCE_HINT_RULES = [
    {
        "keywords": {"python", "modules", "packages", "import", "namespace", "biblioteca padrao"},
        "source_hints": [
            "documentação oficial",
            "library reference",
            "language tutorial",
            "material de certificação/estudo",
        ],
    },
    {
        "keywords": {"backend", "web", "api", "fastapi", "flask", "wsgi", "asgi", "autenticacao", "banco de dados"},
        "source_hints": [
            "documentação oficial",
            "guides de framework",
            "tutoriais de referência",
            "material de certificação/estudo",
        ],
    },
    {
        "keywords": {"oop", "classes", "objetos", "heranca", "encapsulamento", "polimorfismo"},
        "source_hints": [
            "documentação oficial",
            "guias técnicos",
            "language tutorial",
            "material de certificação/estudo",
        ],
    },
]

CONSOLIDATION_RULES = [
    {
        "key": "python-modules-packages",
        "canonical_topic": "python modules and packages",
        "domains": {"modulos e pacotes"},
        "keywords": {"modules e packages", "import", "namespace", "pacotes python", "biblioteca padrao"},
    },
    {
        "key": "python-exceptions",
        "canonical_topic": "python exceptions and error handling",
        "domains": {"tratamento de erros"},
        "keywords": {"exceptions em python", "try except", "finally", "raise", "assert"},
    },
    {
        "key": "python-backend-web",
        "canonical_topic": "python backend web",
        "domains": {"backend web com python"},
        "keywords": {"api rest com python", "wsgi e asgi", "fastapi", "flask", "autenticacao", "integracao com banco de dados"},
    },
    {
        "key": "python-data-collections",
        "canonical_topic": "python data collections",
        "domains": {"colecoes e operacoes em dados"},
        "keywords": {"listas", "tuplas", "dicionarios", "fatiamento", "iteracao", "comprehensions"},
    },
    {
        "key": "python-oop",
        "canonical_topic": "python oop",
        "domains": {"programacao orientada a objetos"},
        "keywords": {"object-oriented programming", "classes", "objetos", "heranca", "encapsulamento", "polimorfismo", "oop"},
    },
]


def _normalize_key(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _append_unique(values: list[str], new_values: list[str], limit: int = 8) -> list[str]:
    for value in new_values:
        cleaned = str(value).strip()
        if cleaned and cleaned not in values:
            values.append(cleaned)
        if len(values) >= limit:
            break
    return values


def _suggest_search_targets(item: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    subtheme = str(item.get("inferred_subtheme") or "").strip()
    domain = str(item.get("inferred_domain") or "").strip()
    tags = _safe_list(item.get("inferred_tags"))
    prompt = str(item.get("prompt", "")).strip()

    if subtheme:
        targets.append(subtheme)
    if domain and domain not in targets:
        targets.append(domain)
    for tag in tags:
        if tag not in targets:
            targets.append(tag)
    if prompt:
        targets.append(prompt[:180])
    return targets[:5]


def _build_action_topic(item: dict[str, Any]) -> str:
    subtheme = str(item.get("inferred_subtheme") or "").strip()
    domain = str(item.get("inferred_domain") or "").strip()
    tags = _safe_list(item.get("inferred_tags"))
    prompt = str(item.get("prompt", "")).strip()

    if "kubernetes" in tags:
        return "kubernetes"
    if subtheme:
        return subtheme
    if domain and tags:
        specific_tags = [tag for tag in tags if tag != domain]
        if specific_tags:
            return f"{domain}: {specific_tags[0]}"
    if domain:
        return domain
    if tags:
        return tags[0]
    return prompt[:120] if prompt else "question-bank"


def _build_question_bank_priority_items(top: int = 20) -> list[dict[str, Any]]:
    coverage = build_question_bank_coverage_report(top=max(top, 20))
    grouped: dict[str, dict[str, Any]] = {}

    for item in coverage.get("items", []):
        if not isinstance(item, dict):
            continue
        coverage_status = str(item.get("coverage", "")).strip().lower()
        weight = float(ACTION_PRIORITY_WEIGHT.get(coverage_status, 0.0))
        if weight <= 0.0:
            continue

        action_topic = _build_action_topic(item)
        domain = str(item.get("inferred_domain") or "").strip()
        key = "|".join([_normalize_key(domain), _normalize_key(action_topic), coverage_status])
        bucket = grouped.setdefault(
            key,
            {
                "source": "question_bank",
                "action_type": coverage_status,
                "priority_band": ACTION_PRIORITY_LABEL.get(coverage_status, "low"),
                "action_topic": action_topic,
                "domain": domain,
                "question_count": 0,
                "priority_score": 0.0,
                "coverage_scores": [],
                "question_ids": [],
                "sample_prompts": [],
                "search_targets": set(),
                "reason_signals": defaultdict(int),
            },
        )
        bucket["question_count"] += 1
        bucket["priority_score"] += weight
        bucket["coverage_scores"].append(float(item.get("coverage_score", 0.0) or 0.0))
        question_id = str(item.get("question_id", "")).strip()
        if question_id and question_id not in bucket["question_ids"]:
            bucket["question_ids"].append(question_id)
        prompt = str(item.get("prompt", "")).strip()
        if prompt and prompt not in bucket["sample_prompts"]:
            bucket["sample_prompts"].append(prompt)
        for target in _suggest_search_targets(item):
            bucket["search_targets"].add(target)
        for signal in _safe_list(item.get("evidence_signals")):
            bucket["reason_signals"][signal] += 1

    output = []
    for bucket in grouped.values():
        avg_score = sum(bucket["coverage_scores"]) / len(bucket["coverage_scores"]) if bucket["coverage_scores"] else 0.0
        scaled_priority = ACTION_PRIORITY_WEIGHT.get(bucket["action_type"], 0.0) * min(int(bucket["question_count"]), 5)
        output.append(
            {
                "source": "question_bank",
                "action_type": bucket["action_type"],
                "priority_band": bucket["priority_band"],
                "priority_rank": ACTION_PRIORITY_RANK.get(bucket["priority_band"], 0),
                "action_topic": bucket["action_topic"],
                "domain": bucket["domain"],
                "question_count": int(bucket["question_count"]),
                "priority_score": round(float(scaled_priority), 3),
                "avg_coverage_score": round(avg_score, 3),
                "sample_prompts": bucket["sample_prompts"][:3],
                "question_ids": bucket["question_ids"][:6],
                "search_targets": sorted(bucket["search_targets"])[:6],
                "reason_signals": [
                    {"signal": signal, "count": count}
                    for signal, count in sorted(bucket["reason_signals"].items(), key=lambda item: (-int(item[1]), str(item[0])))
                ][:5],
            }
        )

    return sorted(
        output,
        key=lambda item: (
            -int(item.get("priority_rank", 0)),
            -float(item.get("priority_score", 0.0)),
            -int(item.get("question_count", 0)),
            float(item.get("avg_coverage_score", 0.0)),
        ),
    )[:top]


def _match_consolidation_rule(item: dict[str, Any]) -> dict[str, Any]:
    topic = _normalize_key(str(item.get("action_topic", "")))
    domain = _normalize_key(str(item.get("domain", "")))
    search_targets = {_normalize_key(value) for value in _safe_list(item.get("search_targets"))}
    terms = {topic, domain, *search_targets}

    for rule in CONSOLIDATION_RULES:
        if domain in rule["domains"]:
            return rule
        if terms & rule["keywords"]:
            return rule
    fallback_key = f"generic|{domain or topic or 'general'}"
    return {
        "key": fallback_key,
        "canonical_topic": str(item.get("domain") or item.get("action_topic") or "general ingestion"),
        "domains": {domain} if domain else set(),
        "keywords": set(),
    }


def _build_suggested_queries(canonical_topic: str, related_topics: list[str], domains: list[str]) -> list[str]:
    queries: list[str] = []
    _append_unique(queries, [canonical_topic], limit=6)
    if domains:
        _append_unique(queries, [f"{canonical_topic} {domains[0]}"], limit=6)
    _append_unique(queries, related_topics[:4], limit=6)
    if related_topics:
        _append_unique(queries, [f"{canonical_topic} {' '.join(related_topics[:2])}"], limit=6)
    return queries[:6]


def _build_search_queries(canonical_topic: str, related_topics: list[str], domains: list[str]) -> list[str]:
    queries: list[str] = []
    _append_unique(queries, [f"{canonical_topic} official documentation"], limit=8)
    _append_unique(queries, [f"{canonical_topic} guide"], limit=8)
    if domains:
        _append_unique(queries, [f"{canonical_topic} {domains[0]} documentation"], limit=8)
    if related_topics:
        _append_unique(queries, [f"{canonical_topic} {related_topics[0]}"], limit=8)
        _append_unique(queries, [f"{canonical_topic} {related_topics[0]} tutorial"], limit=8)
    if len(related_topics) > 1:
        _append_unique(queries, [f"{canonical_topic} {related_topics[1]} reference"], limit=8)
    _append_unique(queries, [f"{canonical_topic} certification study guide"], limit=8)
    return queries[:8]


def _build_source_hints(canonical_topic: str, related_topics: list[str], domains: list[str]) -> list[str]:
    terms = {
        _normalize_key(canonical_topic),
        *(_normalize_key(topic) for topic in related_topics),
        *(_normalize_key(domain) for domain in domains),
    }
    hints: list[str] = []
    for rule in SOURCE_HINT_RULES:
        if terms & rule["keywords"]:
            _append_unique(hints, [str(value) for value in rule["source_hints"]], limit=6)
    if not hints:
        _append_unique(hints, DEFAULT_SOURCE_HINTS, limit=6)
        _append_unique(hints, ["material de certificação/estudo"], limit=6)
    return hints[:6]


def _build_consolidated_blocks(merged_ranking: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for item in merged_ranking:
        if not isinstance(item, dict):
            continue
        rule = _match_consolidation_rule(item)
        block_key = str(rule["key"])
        bucket = grouped.setdefault(
            block_key,
            {
                "action_block": block_key,
                "canonical_topic": str(rule["canonical_topic"]),
                "related_topics": [],
                "total_priority": 0.0,
                "sources_contributing": set(),
                "suggested_queries": [],
                "priority_rank": 0,
                "sample_domains": [],
            },
        )
        bucket["total_priority"] += float(item.get("priority_score", 0.0) or 0.0)
        bucket["priority_rank"] = max(int(bucket["priority_rank"]), int(item.get("priority_rank", 0) or 0))
        bucket["sources_contributing"].add(str(item.get("source", "")))
        _append_unique(bucket["related_topics"], [str(item.get("action_topic", ""))], limit=10)
        _append_unique(bucket["related_topics"], _safe_list(item.get("queries")), limit=10)
        _append_unique(bucket["related_topics"], _safe_list(item.get("search_targets")), limit=10)
        _append_unique(bucket["sample_domains"], [str(item.get("domain", ""))], limit=4)

    output = []
    for bucket in grouped.values():
        related_topics = [topic for topic in bucket["related_topics"] if topic and topic != bucket["canonical_topic"]][:8]
        suggested_queries = _build_suggested_queries(
            canonical_topic=bucket["canonical_topic"],
            related_topics=related_topics,
            domains=[domain for domain in bucket["sample_domains"] if domain],
        )
        search_queries = _build_search_queries(
            canonical_topic=bucket["canonical_topic"],
            related_topics=related_topics,
            domains=[domain for domain in bucket["sample_domains"] if domain],
        )
        source_hints = _build_source_hints(
            canonical_topic=bucket["canonical_topic"],
            related_topics=related_topics,
            domains=[domain for domain in bucket["sample_domains"] if domain],
        )
        output.append(
            {
                "action_block": bucket["action_block"],
                "canonical_topic": bucket["canonical_topic"],
                "related_topics": related_topics,
                "total_priority": round(float(bucket["total_priority"]), 3),
                "sources_contributing": sorted(source for source in bucket["sources_contributing"] if source),
                "suggested_queries": suggested_queries,
                "search_queries": search_queries,
                "source_hints": source_hints,
                "priority_rank": int(bucket["priority_rank"]),
            }
        )

    ranked_blocks = sorted(
        output,
        key=lambda item: (
            -int(item.get("priority_rank", 0)),
            -float(item.get("total_priority", 0.0)),
            str(item.get("canonical_topic", "")),
        ),
    )[:top]
    for index, item in enumerate(ranked_blocks, start=1):
        item["priority_order"] = index
    return ranked_blocks


def _build_documentation_search_shortlist(consolidated_blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shortlist = []
    for block in consolidated_blocks:
        if not isinstance(block, dict):
            continue
        shortlist.append(
            {
                "block": str(block.get("canonical_topic", "")),
                "action_block": str(block.get("action_block", "")),
                "related_topics": _safe_list(block.get("related_topics")),
                "search_queries": _safe_list(block.get("search_queries")),
                "source_hints": _safe_list(block.get("source_hints")),
                "priority_order": int(block.get("priority_order", 0) or 0),
                "priority_band": "max" if int(block.get("priority_rank", 0) or 0) >= 3 else "high" if int(block.get("priority_rank", 0) or 0) == 2 else "low",
                "total_priority": round(float(block.get("total_priority", 0.0) or 0.0), 3),
            }
        )
    return shortlist


def build_question_bank_action_report(top: int = 10, track: str | None = None) -> dict[str, Any]:
    gap_report = get_gap_report(track=track or None, top=max(top, 20))
    coverage_report = build_question_bank_coverage_report(top=max(top, 20))
    question_bank_items = _build_question_bank_priority_items(top=max(top, 20))

    coverage_buckets = {
        "missing": [item for item in question_bank_items if item.get("action_type") == "missing"][:top],
        "partial": [item for item in question_bank_items if item.get("action_type") == "partial"][:top],
        "covered": [item for item in question_bank_items if item.get("action_type") == "covered"][:top],
    }

    existing_queue_items = []
    for item in gap_report.get("recommended_ingestion_topics", []):
        if not isinstance(item, dict):
            continue
        priority_band = "max" if int(item.get("missing_count", 0) or 0) > 0 else "high" if int(item.get("partial_count", 0) or 0) > 0 else "low"
        existing_queue_items.append(
            {
                "source": "gap_queue",
                "priority_band": priority_band,
                "priority_rank": ACTION_PRIORITY_RANK.get(priority_band, 0),
                "action_topic": str(item.get("recommended_topic", "")),
                "domain": str(item.get("domain", "")),
                "priority_score": float(item.get("priority_score", 0.0) or 0.0),
                "question_count": int(item.get("occurrences", 0) or 0),
                "missing_count": int(item.get("missing_count", 0) or 0),
                "partial_count": int(item.get("partial_count", 0) or 0),
                "queries": _safe_list(item.get("queries"))[:4],
                "search_targets": [str(item.get("recommended_topic", ""))],
            }
        )

    merged_ranking = sorted(
        existing_queue_items + question_bank_items,
        key=lambda item: (
            -int(item.get("priority_rank", 0)),
            -float(item.get("priority_score", 0.0)),
            -int(item.get("question_count", 0)),
            str(item.get("action_topic", "")),
        ),
    )[:top]
    consolidated_blocks = _build_consolidated_blocks(merged_ranking, top=top)
    documentation_search_shortlist = _build_documentation_search_shortlist(consolidated_blocks)

    return {
        "weights": ACTION_PRIORITY_WEIGHT,
        "coverage_counts": coverage_report.get("coverage_counts", {}),
        "existing_gap_queue_top": existing_queue_items[:top],
        "missing_actions": coverage_buckets["missing"],
        "partial_actions": coverage_buckets["partial"],
        "covered_actions": coverage_buckets["covered"],
        "merged_ingestion_ranking": merged_ranking,
        "consolidated_ingestion_blocks": consolidated_blocks,
        "documentation_search_shortlist": documentation_search_shortlist,
        "source_files": {
            "gap_queue": gap_report.get("source_files", {}).get("gap_queue", ""),
            "gap_history": gap_report.get("source_files", {}).get("gap_history", ""),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatorio pratico de acao para ingestao baseado em question_bank e gap queue")
    parser.add_argument("--top", type=int, default=10, help="Quantidade maxima por lista")
    parser.add_argument("--track", default="", help="Filtro opcional por trilha")
    parser.add_argument("--pretty", action="store_true", help="Renderiza JSON identado")
    args = parser.parse_args()

    payload = build_question_bank_action_report(top=max(1, args.top), track=args.track or None)
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
