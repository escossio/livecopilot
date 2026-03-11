import argparse
import json
import re
import time

from app.services.question_bank_items import load_items_payload
from app.services.question_bank_parsers import QUESTION_BANK_ITEMS_DIR, ensure_question_bank_dirs
from app.services.search_metrics import log_search_metrics

PRACTICAL_QUERY_TERMS = {
    "kubectl",
    "helm",
    "docker",
    "terraform",
    "curl",
    "ingress",
    "service",
    "deploy",
    "deployment",
    "namespace",
    "install",
    "apply",
    "create",
    "run",
    "configure",
}

PRACTICAL_ITEM_TERMS = (
    "kubectl",
    "helm",
    "docker",
    "terraform",
    "curl",
    "ingress",
    "service",
    "deploy",
    "deployment",
    "namespace",
    "install",
    "apply",
    "create",
    "run",
    "configure",
)

EXAM_STYLE_TERMS = (
    "question",
    "questions",
    "which",
    "select all that apply",
    "pick the",
    "correct responses",
    "most voted",
    "explanation:",
)

DOMAIN_HINT_TERMS = {
    "devops": {"kubernetes", "kubectl", "helm", "configmap", "clusterip", "liveness", "probe", "nginx", "docker", "terraform"},
    "backend": {"python", "fastapi", "flask", "django", "api", "dependency", "injection"},
    "cloud": {"aws", "terraform", "cloud", "iam", "s3", "ec2"},
}

SUBTHEME_HINT_TERMS = {
    "containers": {"container", "containers", "docker", "kubernetes", "pod", "pods", "nginx", "liveness", "probe"},
    "oop": {"oop", "class", "object", "inheritance", "polymorphism"},
}


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", (text or "").lower()) if token]


def _score_item(item: dict, query_tokens: list[str]) -> int:
    haystack = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("prompt", "")),
            " ".join(str(choice) for choice in item.get("choices", [])),
            " ".join(str(tag) for tag in item.get("inferred_tags", [])),
        ]
    ).lower()
    return sum(3 if token in str(item.get("prompt", "")).lower() else 1 for token in query_tokens if token in haystack)


def _score_practicality(item: dict, query_tokens: list[str]) -> tuple[float, list[str], str]:
    query_token_set = set(query_tokens)
    if not query_token_set:
        return 0.0, [], ""

    title = str(item.get("title", "")).lower()
    prompt = str(item.get("prompt", "")).lower()
    text = f" {title} {prompt} "
    bonus = 0.0
    signals: list[str] = []

    if str(item.get("item_type", "")).strip().lower() == "exercise":
        bonus += 0.75
        signals.append("item_type=exercise")

    if str(item.get("inferred_domain", "")).strip().lower() == "devops":
        bonus += 0.35
        signals.append("inferred_domain=devops")

    inferred_domain = str(item.get("inferred_domain", "")).strip().lower()
    if inferred_domain:
        domain_hints = DOMAIN_HINT_TERMS.get(inferred_domain, set())
        if inferred_domain in query_token_set:
            bonus += 0.3
            signals.append(f"domain_match={inferred_domain}")
        elif domain_hints and (query_token_set & domain_hints):
            bonus += 0.25
            signals.append(f"domain_hint={inferred_domain}")

    inferred_subtheme = str(item.get("inferred_subtheme", "")).strip().lower()
    if inferred_subtheme:
        subtheme_hints = SUBTHEME_HINT_TERMS.get(inferred_subtheme, set())
        if inferred_subtheme in query_token_set:
            bonus += 0.28
            signals.append(f"subtheme_match={inferred_subtheme}")
        elif subtheme_hints and (query_token_set & subtheme_hints):
            bonus += 0.22
            signals.append(f"subtheme_hint={inferred_subtheme}")

    inferred_tags = {str(tag).strip().lower() for tag in item.get("inferred_tags", []) if str(tag).strip()}
    matched_tags = sorted(inferred_tags & query_token_set)
    if matched_tags:
        bonus += min(0.45, 0.2 * len(matched_tags))
        signals.append(f"matched_tags={','.join(matched_tags[:3])}")

    matched_terms = [term for term in PRACTICAL_ITEM_TERMS if term in text]
    if matched_terms:
        bonus += min(0.5, 0.12 * len(matched_terms))
        signals.append(f"practical_terms={','.join(matched_terms[:3])}")

    if str(item.get("item_type", "")).strip().lower() == "multiple_choice":
        bonus -= 0.35
        signals.append("item_type=multiple_choice")

    exam_terms = [term for term in EXAM_STYLE_TERMS if term in text]
    if exam_terms:
        bonus -= min(0.45, 0.15 * len(exam_terms))
        signals.append(f"exam_style={','.join(exam_terms[:2])}")

    bonus = max(-0.8, min(1.52, bonus))
    if abs(bonus) < 0.01:
        return 0.0, [], ""

    if bonus > 0:
        why = f"Practicality boosted by {', '.join(signals[:4])}."
    else:
        why = f"Practicality reduced by {', '.join(signals[:4])}."
    return round(bonus, 3), signals[:5], why


def search_question_bank_items_with_debug(query: str, limit: int = 5) -> dict:
    started_at = time.perf_counter()
    ensure_question_bank_dirs()
    query_tokens = _tokenize(query)
    matches = []

    for path in sorted(QUESTION_BANK_ITEMS_DIR.glob("*.items.json")):
        payload = load_items_payload(path)
        if not payload:
            continue
        for item in payload.get("items", []):
            base_score = _score_item(item, query_tokens)
            if base_score <= 0:
                continue
            practicality_bonus, practicality_signals, why_practicality = _score_practicality(item, query_tokens)
            score = round(base_score + practicality_bonus, 3)
            enriched = dict(item)
            enriched["base_score"] = base_score
            enriched["practicality_bonus"] = practicality_bonus
            enriched["practicality_signals"] = practicality_signals
            enriched["why_practicality"] = why_practicality
            enriched["score"] = score
            matches.append(enriched)

    matches.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("question_id", ""))))
    results = matches[: max(1, limit)]
    payload = {
        "query": query,
        "results": results,
        "debug": {
            "query_tokens": query_tokens,
            "searched_files": len(list(QUESTION_BANK_ITEMS_DIR.glob("*.items.json"))),
            "pipeline": "question_bank",
        },
    }
    elapsed_ms = (time.perf_counter() - started_at) * 1000.0
    log_search_metrics(
        search_type="question_bank",
        query=query,
        limit=max(1, limit),
        elapsed_ms=elapsed_ms,
        results=results,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Busca textual simples em data/question_bank_items")
    parser.add_argument("query", nargs="?", default="", help="Pergunta, termo ou tema para buscar")
    parser.add_argument("--limit", type=int, default=5, help="Quantidade maxima de resultados")
    parser.add_argument("--pretty", action="store_true", help="Renderiza JSON identado")
    args = parser.parse_args()

    payload = search_question_bank_items_with_debug(args.query, limit=max(1, args.limit))
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
