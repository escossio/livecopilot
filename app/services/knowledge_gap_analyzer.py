import argparse
import json
import re
from typing import Any

from app.services.certification_map import iter_domains
from app.services.knowledge_search import search_knowledge_chunks

STOPWORDS = {
    "a",
    "o",
    "os",
    "as",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "com",
    "sem",
    "por",
    "para",
    "um",
    "uma",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "python",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9._/-]{1,}", _normalize(text))
    return [token for token in tokens if token not in STOPWORDS and len(token) >= 3]


def _truncate(text: str, limit: int = 130) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rsplit(" ", 1)[0].strip() + "..."


def _is_relevant_match(topic: str, match: dict[str, Any], track: str) -> bool:
    searchable = _normalize(
        " ".join(
            [
                str(match.get("title", "")),
                str(match.get("source_file", "")),
                str(match.get("trecho_relevante", "")),
            ]
        )
    )
    topic_tokens = _tokenize(topic)
    token_hits = sum(1 for token in topic_tokens if token in searchable)
    min_hits = 1 if len(topic_tokens) <= 2 else 2
    if token_hits < min_hits:
        return False

    if track == "python":
        python_markers = {
            "python",
            "pcep",
            "pcap",
            "pcpp",
            "pip",
            "virtualenv",
            "fastapi",
            "flask",
            "django",
            ".py",
        }
        return any(marker in searchable for marker in python_markers)
    return True


def map_topic_to_domain(topic_query: str, track: str = "python") -> dict[str, Any]:
    query = _normalize(topic_query)
    query_tokens = _tokenize(query)
    best_match: dict[str, Any] | None = None
    best_score = 0.0

    for candidate in iter_domains(track):
        domain_name = _normalize(str(candidate.get("domain_name", "")))
        topics = [str(item) for item in candidate.get("topics", [])]

        score = 0.0
        if query and query in domain_name:
            score += 5.0

        for topic in topics:
            topic_norm = _normalize(topic)
            if query and query in topic_norm:
                score += 7.0
            for token in query_tokens:
                if token in topic_norm:
                    score += 2.0
                if token in domain_name:
                    score += 1.0

        if score > best_score:
            best_score = score
            best_match = {
                **candidate,
                "mapping_score": round(score, 3),
            }

    if not best_match:
        return {}
    return best_match


def _evaluate_topic_coverage(topic: str, track: str = "python", min_score: float = 1.0) -> dict[str, Any]:
    matches = search_knowledge_chunks(topic, limit=1)
    if not matches:
        return {
            "topic": topic,
            "covered": False,
            "best_score": 0.0,
            "evidence": "",
        }

    top = matches[0]
    score = float(top.get("score", 0.0) or 0.0)
    is_relevant = _is_relevant_match(topic, top, track=track)
    return {
        "topic": topic,
        "covered": score >= min_score and is_relevant,
        "best_score": score,
        "relevant_match": is_relevant,
        "evidence": _truncate(str(top.get("trecho_relevante", ""))),
        "source_file": top.get("source_file", ""),
        "chunk_id": top.get("chunk_id", ""),
    }


def _classify_coverage(covered_count: int, total: int) -> str:
    if total <= 0:
        return "missing"
    ratio = covered_count / total
    if ratio >= 0.7:
        return "covered"
    if ratio >= 0.35:
        return "partial"
    return "missing"


def analyze_knowledge_gap(topic_query: str, track: str = "python") -> dict[str, Any]:
    mapping = map_topic_to_domain(topic_query, track=track)
    if not mapping:
        return {
            "query": topic_query,
            "track": track,
            "status": "missing",
            "message": "No certification domain matched this topic.",
            "recommended_topics": [],
        }

    topic_results = [_evaluate_topic_coverage(topic, track=track) for topic in mapping.get("topics", [])]
    covered_count = sum(1 for item in topic_results if item.get("covered"))
    total_topics = len(topic_results)
    status = _classify_coverage(covered_count, total_topics)

    recommended_topics = [item["topic"] for item in topic_results if not item.get("covered")][:6]

    return {
        "query": topic_query,
        "track": track,
        "status": status,
        "coverage": {
            "covered_topics": covered_count,
            "total_topics": total_topics,
            "ratio": round((covered_count / total_topics) if total_topics else 0.0, 3),
        },
        "domain": {
            "provider": mapping.get("provider", ""),
            "certification": mapping.get("certification", ""),
            "level": mapping.get("level", ""),
            "domain": mapping.get("domain", ""),
            "domain_name": mapping.get("domain_name", ""),
            "mapping_score": mapping.get("mapping_score", 0.0),
        },
        "topic_assessment": topic_results,
        "recommended_topics": recommended_topics,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Analyze knowledge coverage against certification domains")
    parser.add_argument("query", nargs="?", default="", help="Theme or question to analyze")
    parser.add_argument("--track", default="python", help="Certification track map")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    args = parser.parse_args()

    output = analyze_knowledge_gap(args.query, track=args.track)
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()
