import argparse
import json
import math
import re
import time
from pathlib import Path
from typing import Any

from app.services.knowledge_chunks import CHUNKS_DIR
from app.services.knowledge_tags import infer_query_tags, infer_tags, merge_tags
from app.services.search_metrics import log_search_metrics

KNOWLEDGE_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_index" / "knowledge_manifest.json"

SEARCH_STOPWORDS = {
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
    "que",
    "como",
    "ao",
    "aos",
    "se",
    "sua",
    "seu",
    "suas",
    "seus",
    "mais",
    "menos",
    "sobre",
    "isso",
    "esta",
    "este",
    "essa",
    "esse",
    "funciona",
    "ser",
    "estar",
    "is",
    "are",
    "be",
    "with",
    "this",
    "that",
}

PRACTICALITY_POSITIVE_SIGNALS: tuple[tuple[str, float, str], ...] = (
    ("kubectl", 0.3, "kubectl"),
    ("helm", 0.25, "helm"),
    ("liveness probe", 0.26, "liveness-probe"),
    ("liveness", 0.18, "liveness"),
    ("readiness", 0.18, "readiness"),
    ("probe", 0.16, "probe"),
    ("nginx", 0.14, "nginx"),
    (" pod ", 0.14, "pod"),
    (" container ", 0.14, "container"),
    (" service ", 0.14, "service"),
    (" deployment ", 0.14, "deployment"),
    ("docker run", 0.3, "docker-run"),
    ("docker compose", 0.3, "docker-compose"),
    ("terraform apply", 0.3, "terraform-apply"),
    ("curl", 0.2, "curl"),
    ("wget", 0.2, "wget"),
    (" exec ", 0.18, "exec"),
    (" apply ", 0.14, "apply"),
    (" create ", 0.14, "create"),
    (" run ", 0.12, "run"),
    ("example", 0.16, "example"),
    ("exercise", 0.18, "exercise"),
    ("task", 0.18, "task"),
    ("step", 0.12, "step"),
)

PRACTICALITY_NEGATIVE_SIGNALS: tuple[tuple[str, float, str], ...] = (
    ("exam", 0.18, "exam"),
    ("certification", 0.18, "certification"),
    ("question", 0.14, "question"),
    ("answers", 0.14, "answers"),
    ("study guide", 0.2, "study-guide"),
    ("dump", 0.25, "dump"),
)

PRACTICALITY_DEVOPS_TERMS = (
    "kubernetes",
    "kubectl",
    "docker",
    "terraform",
    "helm",
    "devops",
    "linux",
)

PRACTICAL_INTENT_TERMS = {
    "kubectl",
    "helm",
    "docker",
    "container",
    "pod",
    "kubernetes",
    "manifest",
    "healthcheck",
    "terraform",
    "install",
    "apply",
    "create",
    "run",
    "deploy",
    "deployment",
    "namespace",
    "service",
    "ingress",
    "liveness",
    "readiness",
    "probe",
    "nginx",
    "chart",
}
PRACTICAL_INTENT_MIN_TERMS = 2
PRACTICAL_INTENT_MAX_QUERY_TERMS = 4
PRACTICALITY_BONUS_WEIGHT_DEFAULT = 1.0
PRACTICALITY_BONUS_WEIGHT_PRACTICAL_INTENT = 18.0
LEXICAL_WEIGHT = 0.85
MAX_RESULTS_PER_SOURCE_DEFAULT = 3
NEAR_DUPLICATE_SEQUENCE_GAP = 2
NEAR_DUPLICATE_JACCARD_THRESHOLD = 0.82
FALLBACK_MIN_SCORE_RATIO_TO_TOP1 = 0.30
FALLBACK_MIN_SIGNALLED_SCORE_RATIO_TO_TOP1 = 0.20
MIN_STRONG_RESULTS_BEFORE_FLOOR = 6
CONTEXT_SNIPPET_CHAR_LIMIT = 280
CONTEXT_CHAR_LIMIT = 3200


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9._/-]{1,}", _normalize(text))
    return [token for token in tokens if token not in SEARCH_STOPWORDS and len(token) >= 3]


def _match_count(text: str, token: str) -> int:
    if not token:
        return 0
    escaped = re.escape(token)
    return len(re.findall(rf"(?<!\w){escaped}(?!\w)", text))


def _score_structural_context(
    chapter_title: str,
    section_hint: str,
    normalized_query: str,
    terms: list[str],
    term_weights: dict[str, float],
) -> tuple[float, list[str]]:
    signals: list[str] = []
    score = 0.0

    for field_name, field_value, term_multiplier, phrase_boost in (
        ("chapter_title", chapter_title, 1.2, 4.0),
        ("section_hint", section_hint, 0.9, 3.0),
    ):
        normalized_field = _normalize(field_value)
        if not normalized_field:
            continue
        term_hits = sum(_match_count(normalized_field, term) * term_weights.get(term, 1.0) for term in terms)
        if term_hits > 0:
            score += term_hits * term_multiplier
            signals.append(field_name)
        if normalized_query and normalized_query in normalized_field:
            score += phrase_boost
            if field_name not in signals:
                signals.append(field_name)

    return score, signals


def _build_why_matched(
    *,
    chapter_title: str,
    section_hint: str,
    structural_score: float,
    structural_signals: list[str],
    hygiene_score: float,
    hygiene_flags: list[str],
    base_score: float,
    adjusted_score: float,
) -> str:
    reasons: list[str] = []

    if structural_score >= 8 and structural_signals:
        if "chapter_title" in structural_signals and "section_hint" in structural_signals:
            reasons.append("Matched strongly because the query aligns with the chapter title and section heading.")
        elif "chapter_title" in structural_signals:
            label = chapter_title or "the chapter title"
            reasons.append(f"Matched strongly because the query aligns with the chapter context ({label}).")
        elif "section_hint" in structural_signals:
            label = section_hint or "the section heading"
            reasons.append(f"Matched strongly because the query aligns with the section context ({label}).")
    elif structural_score > 0 and structural_signals:
        reasons.append("Relevant text match with some support from structural context.")
    else:
        reasons.append("Relevant text match, but without structural signals.")

    if hygiene_score < 0.999:
        if hygiene_flags:
            reasons.append(f"Rank reduced due to hygiene penalties ({', '.join(hygiene_flags[:2])}).")
        else:
            reasons.append("Rank reduced due to hygiene penalties.")
    elif adjusted_score > base_score:
        reasons.append("Rank increased after document-quality adjustments.")

    return " ".join(reasons)


def _score_practicality(
    *,
    normalized_query: str,
    query_terms: list[str],
    title: str,
    chapter_title: str,
    section_hint: str,
    content: str,
) -> tuple[float, list[str], str]:
    text = f" { _normalize(title) } { _normalize(chapter_title) } { _normalize(section_hint) } { _normalize(content) } "
    if not text.strip():
        return 0.0, [], ""

    positive_score = 0.0
    negative_score = 0.0
    positive_signals: list[str] = []
    negative_signals: list[str] = []
    query_term_set = set(query_terms)

    for term, weight, label in PRACTICALITY_POSITIVE_SIGNALS:
        normalized_term = _normalize(term).strip()
        signal_tokens = _tokenize(normalized_term) if normalized_term else []
        aligned_with_query = normalized_term in normalized_query if normalized_term else False
        if not aligned_with_query and signal_tokens:
            aligned_with_query = all(token in query_term_set for token in signal_tokens)
        if term in text and aligned_with_query:
            positive_score += weight
            positive_signals.append(label)

    for term, weight, label in PRACTICALITY_NEGATIVE_SIGNALS:
        if term in text:
            negative_score += weight
            negative_signals.append(label)

    devops_context = sum(1 for term in PRACTICALITY_DEVOPS_TERMS if term in text)
    if devops_context >= 2 and positive_signals:
        positive_score += 0.12
        positive_signals.append("devops-context")

    practicality_bonus = max(-0.6, min(1.1, positive_score - negative_score))
    if abs(practicality_bonus) < 0.01:
        return 0.0, [], ""

    if practicality_bonus > 0:
        why = f"Practicality boosted by {', '.join(positive_signals[:4])}."
    else:
        why = f"Practicality reduced by {', '.join(negative_signals[:3])}."
    return round(practicality_bonus, 3), positive_signals[:5] if practicality_bonus > 0 else negative_signals[:5], why


def _build_excerpt(content: str, phrase: str, terms: list[str], window: int = 180) -> str:
    compact = re.sub(r"\s+", " ", content).strip()
    if not compact:
        return ""

    lowered = compact.lower()
    start_idx = -1
    if phrase:
        start_idx = lowered.find(phrase)
    if start_idx < 0:
        for term in terms:
            start_idx = lowered.find(term)
            if start_idx >= 0:
                break
    if start_idx < 0:
        snippet = compact[:window]
        return snippet + ("..." if len(compact) > window else "")

    start = max(0, start_idx - window // 3)
    end = min(len(compact), start_idx + (2 * window // 3))
    snippet = compact[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(compact):
        snippet = snippet + "..."
    return snippet


def _has_strong_practical_intent(query_terms: list[str], normalized_query: str) -> bool:
    if not query_terms:
        return False
    if len(query_terms) > PRACTICAL_INTENT_MAX_QUERY_TERMS:
        return False
    matched = len({term for term in query_terms if term in PRACTICAL_INTENT_TERMS})
    if matched >= PRACTICAL_INTENT_MIN_TERMS:
        return True
    return "liveness probe" in normalized_query or "helm install" in normalized_query


def _token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]{3,}", _normalize(text))}


def _jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    if union <= 0:
        return 0.0
    return intersection / union


def _is_near_duplicate(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> bool:
    candidate_source = str(candidate.get("source_file", "")).strip()
    candidate_title = _normalize(str(candidate.get("title", "")))
    candidate_sequence = int(candidate.get("sequence", 0) or 0)
    candidate_excerpt = _normalize(str(candidate.get("trecho_relevante", "")))
    candidate_tokens = _token_set(f"{candidate_title} {candidate_excerpt}")

    for previous in selected:
        previous_source = str(previous.get("source_file", "")).strip()
        previous_title = _normalize(str(previous.get("title", "")))
        previous_sequence = int(previous.get("sequence", 0) or 0)
        previous_excerpt = _normalize(str(previous.get("trecho_relevante", "")))

        # Local redundancy: neighbor chunks from same source and same section title.
        if (
            candidate_source
            and candidate_source == previous_source
            and candidate_title
            and candidate_title == previous_title
            and candidate_sequence
            and previous_sequence
            and abs(candidate_sequence - previous_sequence) <= NEAR_DUPLICATE_SEQUENCE_GAP
        ):
            return True

        previous_tokens = _token_set(f"{previous_title} {previous_excerpt}")
        if len(candidate_tokens) < 6 or len(previous_tokens) < 6:
            continue

        similarity = _jaccard_similarity(candidate_tokens, previous_tokens)
        if similarity < NEAR_DUPLICATE_JACCARD_THRESHOLD:
            continue

        # Same-source or same-title high overlap is likely redundant for top N.
        if candidate_source == previous_source or (candidate_title and candidate_title == previous_title):
            return True

    return False


def _has_useful_practical_signal(item: dict[str, Any]) -> bool:
    signals = [str(signal).strip().lower() for signal in item.get("practicality_signals", []) if str(signal).strip()]
    if not signals:
        return False
    negative_labels = {label for _, _, label in PRACTICALITY_NEGATIVE_SIGNALS}
    return any(signal not in negative_labels for signal in signals)


def _passes_fallback_relevance(item: dict[str, Any], top_score: float) -> bool:
    score = float(item.get("score", 0.0) or 0.0)
    if top_score <= 0:
        return score > 0
    ratio = score / top_score
    if ratio >= FALLBACK_MIN_SCORE_RATIO_TO_TOP1:
        return True
    if ratio >= FALLBACK_MIN_SIGNALLED_SCORE_RATIO_TO_TOP1 and _has_useful_practical_signal(item):
        return True
    return False


def _select_diverse_results(results: list[dict[str, Any]], limit: int, max_per_source: int = MAX_RESULTS_PER_SOURCE_DEFAULT) -> list[dict[str, Any]]:
    target = max(1, int(limit or 1))
    if target <= 4 or max_per_source <= 0:
        return results[:target]

    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    top_score = float(results[0].get("score", 0.0) or 0.0) if results else 0.0

    for item in results:
        source_file = str(item.get("source_file", "")).strip()
        is_redundant = _is_near_duplicate(item, selected)
        if len(selected) >= MIN_STRONG_RESULTS_BEFORE_FLOOR and not _passes_fallback_relevance(item, top_score):
            deferred.append(item)
            continue
        if not source_file:
            if is_redundant:
                deferred.append(item)
            else:
                selected.append(item)
        else:
            seen_for_source = source_counts.get(source_file, 0)
            if seen_for_source < max_per_source:
                if is_redundant:
                    deferred.append(item)
                else:
                    selected.append(item)
                    source_counts[source_file] = seen_for_source + 1
            else:
                deferred.append(item)
        if len(selected) >= target:
            return selected[:target]

    for item in deferred:
        source_file = str(item.get("source_file", "")).strip()
        if source_file and source_counts.get(source_file, 0) >= max_per_source:
            continue
        if _is_near_duplicate(item, selected):
            continue
        if not _passes_fallback_relevance(item, top_score):
            continue
        selected.append(item)
        if source_file:
            source_counts[source_file] = source_counts.get(source_file, 0) + 1
        if len(selected) >= target:
            break

    # Keep quality over quantity: do not force-fill very weak deferred items.
    if len(selected) < target:
        for item in deferred:
            source_file = str(item.get("source_file", "")).strip()
            if source_file and source_counts.get(source_file, 0) >= max_per_source:
                continue
            if _is_near_duplicate(item, selected):
                continue
            if not _passes_fallback_relevance(item, top_score):
                continue
            selected.append(item)
            if source_file:
                source_counts[source_file] = source_counts.get(source_file, 0) + 1
            if len(selected) >= target:
                break

    return selected[:target]


def _iter_chunk_files() -> list[Path]:
    if not CHUNKS_DIR.exists():
        return []
    return sorted(CHUNKS_DIR.glob("*.chunks.json"))


def _load_manifest_hygiene() -> dict[str, dict[str, Any]]:
    if not KNOWLEDGE_MANIFEST_PATH.exists():
        return {}
    try:
        payload = json.loads(KNOWLEDGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    documents = payload.get("documents", [])
    if not isinstance(documents, list):
        return {}
    return {
        str(document.get("source_file", "")): {
            "hygiene_score": float(document.get("hygiene_score", 1.0) or 1.0),
            "hygiene_flags": [str(flag) for flag in document.get("hygiene_flags", []) if str(flag).strip()],
            "hygiene_notes": [str(note) for note in document.get("hygiene_notes", []) if str(note).strip()],
        }
        for document in documents
        if isinstance(document, dict) and str(document.get("source_file", "")).strip()
    }


def _load_chunk_entries() -> list[dict[str, Any]]:
    manifest_hygiene = _load_manifest_hygiene()
    entries: list[dict[str, Any]] = []
    for chunk_file in _iter_chunk_files():
        try:
            payload = json.loads(chunk_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        chunks = payload.get("chunks", [])
        doc_tags = payload.get("tags") if isinstance(payload.get("tags"), dict) else {}
        if not isinstance(chunks, list):
            continue
        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
            chunk_tags = chunk.get("tags") if isinstance(chunk.get("tags"), dict) else {}
            if doc_tags or chunk_tags:
                chunk["tags"] = merge_tags(doc_tags, chunk_tags)
            else:
                # Backward compatibility for old chunks without tags.
                chunk["tags"] = infer_tags(
                    source_file=str(chunk.get("source_file", "")),
                    title=str(chunk.get("title", "")),
                    content="",
                    path_hint=str(Path(str(chunk.get("source_file", ""))).parent),
                )
            chunk["hygiene"] = manifest_hygiene.get(str(chunk.get("source_file", "")), {"hygiene_score": 1.0, "hygiene_flags": [], "hygiene_notes": []})
            entries.append(chunk)
    return entries


def _extract_all_tags(tag_payload: dict[str, Any]) -> set[str]:
    return set(str(item) for item in tag_payload.get("all", []) if str(item).strip())


def _extract_routing_tags(tag_payload: dict[str, Any]) -> set[str]:
    preferred = list(tag_payload.get("technology", [])) + list(tag_payload.get("subtheme", []))
    if preferred:
        return set(str(item) for item in preferred if str(item).strip())
    return set(str(item) for item in tag_payload.get("domain", []) if str(item).strip())


def _search_chunks_scored(
    query: str,
    terms: list[str],
    normalized_query: str,
    chunks: list[dict[str, Any]],
    term_weights: dict[str, float],
    query_tags: dict[str, list[str]],
    practicality_bonus_weight: float = PRACTICALITY_BONUS_WEIGHT_DEFAULT,
) -> list[dict[str, Any]]:
    query_tag_set = _extract_all_tags(query_tags)
    results: list[dict[str, Any]] = []

    for chunk in chunks:
        title = str(chunk.get("title", ""))
        content = str(chunk.get("content", ""))
        chapter_title = str(chunk.get("chapter_title", ""))
        section_hint = str(chunk.get("section_hint", ""))
        section_path = str(chunk.get("section_path", ""))
        if not content.strip():
            continue
        title_norm = _normalize(title)
        content_norm = _normalize(content)

        title_hits = sum(_match_count(title_norm, term) * term_weights.get(term, 1.0) for term in terms)
        content_hits = sum(_match_count(content_norm, term) * term_weights.get(term, 1.0) for term in terms)
        phrase_in_title = 1 if normalized_query in title_norm else 0
        phrase_in_content = 1 if normalized_query in content_norm else 0

        chunk_tags = chunk.get("tags") if isinstance(chunk.get("tags"), dict) else {}
        chunk_tag_set = _extract_all_tags(chunk_tags)
        matched_tags = sorted(query_tag_set & chunk_tag_set) if query_tag_set else []
        tag_boost = float(len(matched_tags) * 2.5)
        structural_score, structural_signals = _score_structural_context(
            chapter_title=chapter_title,
            section_hint=section_hint,
            normalized_query=normalized_query,
            terms=terms,
            term_weights=term_weights,
        )
        practicality_bonus, practicality_signals, why_practicality = _score_practicality(
            normalized_query=normalized_query,
            query_terms=terms,
            title=title,
            chapter_title=chapter_title,
            section_hint=section_hint,
            content=content,
        )

        base_score = float(
            (title_hits * 2.0)
            + (content_hits * 1.0)
            + (phrase_in_title * 6.0)
            + (phrase_in_content * 4.0)
            + tag_boost
            + structural_score
        )
        if base_score <= 0:
            continue
        hygiene = chunk.get("hygiene") if isinstance(chunk.get("hygiene"), dict) else {}
        hygiene_score = float(hygiene.get("hygiene_score", 1.0) or 1.0)
        hygiene_flags = [str(flag) for flag in hygiene.get("hygiene_flags", []) if str(flag).strip()]
        adjusted_score = (base_score * LEXICAL_WEIGHT * hygiene_score) + (practicality_bonus * practicality_bonus_weight)
        why_matched = _build_why_matched(
            chapter_title=chapter_title,
            section_hint=section_hint,
            structural_score=structural_score,
            structural_signals=structural_signals,
            hygiene_score=hygiene_score,
            hygiene_flags=hygiene_flags,
            base_score=base_score,
            adjusted_score=adjusted_score,
        )

        excerpt = _build_excerpt(content, normalized_query, terms)
        results.append(
            {
                "source_file": str(chunk.get("source_file", "")),
                "title": title,
                "chunk_id": str(chunk.get("chunk_id", "")),
                "sequence": int(chunk.get("sequence", 0) or 0),
                "trecho_relevante": excerpt,
                "score": round(adjusted_score, 3),
                "base_score": round(base_score, 3),
                "adjusted_score": round(adjusted_score, 3),
                "hygiene_score": round(hygiene_score, 3),
                "hygiene_flags": hygiene_flags,
                "structural_score": round(structural_score, 3),
                "structural_signals": structural_signals,
                "practicality_bonus": practicality_bonus,
                "practicality_bonus_weight": practicality_bonus_weight,
                "practicality_signals": practicality_signals,
                "why_practicality": why_practicality,
                "why_matched": why_matched,
                "tags": chunk_tags,
                "matched_tags": matched_tags,
            }
        )
        if chapter_title:
            results[-1]["chapter_title"] = chapter_title
        if section_hint:
            results[-1]["section_hint"] = section_hint
        if section_path:
            results[-1]["section_path"] = section_path
    results.sort(key=lambda item: (-item["score"], item["sequence"]))
    return results


def search_knowledge_chunks_with_debug(query: str, limit: int = 5) -> dict[str, Any]:
    started_at = time.perf_counter()

    def _finalize(payload: dict[str, Any]) -> dict[str, Any]:
        results = payload.get("results", []) if isinstance(payload.get("results"), list) else []
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        log_search_metrics(
            search_type="knowledge",
            query=query,
            limit=max(1, limit),
            elapsed_ms=elapsed_ms,
            results=results,
        )
        return payload

    normalized_query = _normalize(query)
    if not normalized_query:
        return _finalize(
            {
            "results": [],
            "debug": {
                "query_tags_inferred": {"technology": [], "domain": [], "subtheme": [], "all": []},
                "query_tags_used": [],
                "used_tag_routing": False,
                "used_global_fallback": False,
                "routed_result_count": 0,
                "global_result_count": 0,
            },
            },
        )

    terms = _tokenize(query)
    if not terms:
        terms = [normalized_query]

    chunks = _load_chunk_entries()
    doc_count = max(1, len(chunks))
    document_frequency: dict[str, int] = {term: 0 for term in terms}
    for chunk in chunks:
        title_norm = _normalize(str(chunk.get("title", "")))
        content_norm = _normalize(str(chunk.get("content", "")))
        searchable = f"{title_norm} {content_norm}"
        for term in terms:
            if term in searchable:
                document_frequency[term] = document_frequency.get(term, 0) + 1

    term_weights = {
        term: math.log((doc_count + 1) / (document_frequency.get(term, 0) + 1)) + 1.0
        for term in terms
    }

    query_tags = infer_query_tags(query)
    query_tag_set = _extract_all_tags(query_tags)
    route_tag_set = _extract_routing_tags(query_tags)
    routed_chunks = chunks
    used_tag_routing = False
    if route_tag_set:
        filtered = []
        for chunk in chunks:
            chunk_tags = chunk.get("tags") if isinstance(chunk.get("tags"), dict) else {}
            if _extract_all_tags(chunk_tags) & route_tag_set:
                filtered.append(chunk)
        routed_chunks = filtered
        used_tag_routing = True

    practical_intent_detected = _has_strong_practical_intent(terms, normalized_query)
    practicality_bonus_weight = PRACTICALITY_BONUS_WEIGHT_DEFAULT
    if used_tag_routing and practical_intent_detected:
        practicality_bonus_weight = PRACTICALITY_BONUS_WEIGHT_PRACTICAL_INTENT

    routed_results = _search_chunks_scored(
        query=query,
        terms=terms,
        normalized_query=normalized_query,
        chunks=routed_chunks,
        term_weights=term_weights,
        query_tags=query_tags,
        practicality_bonus_weight=practicality_bonus_weight,
    )

    min_tag_results = max(1, min(2, limit))
    used_global_fallback = bool(used_tag_routing and len(routed_results) < min_tag_results)
    if not used_global_fallback:
        selected_results = _select_diverse_results(routed_results, max(1, limit))
        return _finalize(
            {
            "results": selected_results,
            "debug": {
                "query_tags_inferred": query_tags,
                "query_tags_used": sorted(route_tag_set),
                "used_tag_routing": used_tag_routing,
                "used_global_fallback": False,
                "practical_intent_detected": practical_intent_detected,
                "practicality_bonus_weight": practicality_bonus_weight,
                "max_results_per_source": MAX_RESULTS_PER_SOURCE_DEFAULT,
                "routed_result_count": len(routed_results),
                "global_result_count": len(routed_results),
            },
            },
        )

    global_results = _search_chunks_scored(
        query=query,
        terms=terms,
        normalized_query=normalized_query,
        chunks=chunks,
        term_weights=term_weights,
        query_tags=query_tags,
        practicality_bonus_weight=practicality_bonus_weight,
    )

    merged_candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in routed_results + global_results:
        chunk_id = str(item.get("chunk_id", ""))
        if chunk_id and chunk_id in seen:
            continue
        if chunk_id:
            seen.add(chunk_id)
        merged_candidates.append(item)

    merged = _select_diverse_results(merged_candidates, max(1, limit))

    return _finalize(
        {
        "results": merged,
        "debug": {
                "query_tags_inferred": query_tags,
                "query_tags_used": sorted(route_tag_set),
                "used_tag_routing": used_tag_routing,
                "used_global_fallback": True,
                "practical_intent_detected": practical_intent_detected,
                "practicality_bonus_weight": practicality_bonus_weight,
                "max_results_per_source": MAX_RESULTS_PER_SOURCE_DEFAULT,
                "routed_result_count": len(routed_results),
                "global_result_count": len(global_results),
        },
        },
    )


def search_knowledge_chunks(query: str, limit: int = 5) -> list[dict[str, Any]]:
    return search_knowledge_chunks_with_debug(query, limit=limit).get("results", [])


def _compact_text(value: str, max_len: int) -> str:
    compact = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(compact) <= max_len:
        return compact
    return compact[: max(0, max_len - 3)].rstrip() + "..."


def _truncate_text(value: str, max_len: int) -> str:
    text = str(value or "")
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)].rstrip() + "..."


def _is_weak_context_snippet(snippet: str) -> bool:
    compact = str(snippet or "").strip()
    if not compact:
        return True

    token_count = len(re.findall(r"[A-Za-zÀ-ÿ0-9]{3,}", compact))
    if token_count < 6:
        return True

    if re.search(r"\.{5,}", compact):
        return True

    alnum_count = len(re.findall(r"[A-Za-zÀ-ÿ0-9]", compact))
    punctuation_count = len(re.findall(r"[^\w\s]", compact))
    if alnum_count <= 0:
        return True
    return (punctuation_count / alnum_count) > 0.28


def _context_candidate_priority(item: dict[str, Any]) -> tuple[int, int, int, int]:
    signals_raw = item.get("practicality_signals", [])
    if not isinstance(signals_raw, list):
        signals_raw = []
    signals = [str(signal).strip().lower() for signal in signals_raw if str(signal).strip()]
    negative_labels = {label for _, _, label in PRACTICALITY_NEGATIVE_SIGNALS}
    useful_signals = [signal for signal in signals if signal not in negative_labels]
    matched_tags = item.get("matched_tags", [])
    if not isinstance(matched_tags, list):
        matched_tags = []
    snippet = str(item.get("trecho_relevante", "")).strip() or str(item.get("snippet", "")).strip()
    weak_snippet = _is_weak_context_snippet(snippet)

    # 2: practical/useful; 1: neutral; 0: mostly negative-only (ex.: exam).
    signal_bucket = 0 if (signals and not useful_signals) else (2 if useful_signals else 1)
    snippet_bucket = 0 if weak_snippet else 1
    return (signal_bucket, snippet_bucket, len(useful_signals), len(snippet) + len(matched_tags))


def build_context_from_results(query: str, results: list[dict[str, Any]], top_k: int = 3) -> str:
    selected_top_k = max(1, int(top_k or 1))
    if not results:
        return f"QUERY: {query}\n\nNo relevant context found."

    ranked_candidates = results[: max(selected_top_k * 5, selected_top_k)]
    prioritized_candidates = [
        (idx, item, _context_candidate_priority(item))
        for idx, item in enumerate(ranked_candidates)
    ]
    prioritized_candidates.sort(key=lambda entry: (-entry[2][0], -entry[2][1], -entry[2][2], -entry[2][3], entry[0]))
    selected: list[dict[str, Any]] = []
    seen_sources: set[str] = set()

    # Keep ranking intent: always anchor context with top-1 result.
    anchor = results[0]
    selected.append(anchor)
    anchor_source = str(anchor.get("source_file", "")).strip()
    if anchor_source:
        seen_sources.add(anchor_source)

    candidates = [item for _, item, _ in prioritized_candidates if item is not anchor]

    # First pass: maximize source diversity for compact context.
    for item in candidates:
        source = str(item.get("source_file", "")).strip()
        if source and source in seen_sources:
            continue
        selected.append(item)
        if source:
            seen_sources.add(source)
        if len(selected) >= selected_top_k:
            break

    # Second pass: fill remaining slots with next best items.
    if len(selected) < selected_top_k:
        selected_ids = {str(item.get("chunk_id", "")) for item in selected if str(item.get("chunk_id", "")).strip()}
        for item in candidates:
            chunk_id = str(item.get("chunk_id", "")).strip()
            if chunk_id and chunk_id in selected_ids:
                continue
            selected.append(item)
            if chunk_id:
                selected_ids.add(chunk_id)
            if len(selected) >= selected_top_k:
                break

    blocks: list[str] = []
    for item in selected:
        source_file = str(item.get("source_file", "")).strip() or "unknown-source"
        title = str(item.get("title", "")).strip() or str(item.get("chapter_title", "")).strip() or "Sem título"
        snippet_raw = (
            str(item.get("trecho_relevante", "")).strip()
            or str(item.get("snippet", "")).strip()
            or str(item.get("content", "")).strip()
        )
        snippet = _compact_text(snippet_raw, CONTEXT_SNIPPET_CHAR_LIMIT) or "(sem trecho disponível)"
        signals_list = item.get("practicality_signals", [])
        if not isinstance(signals_list, list):
            signals_list = []
        signals = ", ".join(str(signal) for signal in signals_list if str(signal).strip()) or "none"

        blocks.append(
            "\n".join(
                [
                    f"SOURCE: {source_file}",
                    f"TITLE: {title}",
                    f"SIGNALS: {signals}",
                    f"SNIPPET: {snippet}",
                ]
            )
        )

    context = f"QUERY: {query}\n\n" + "\n\n".join(blocks)
    return _truncate_text(context, CONTEXT_CHAR_LIMIT)


def build_context_from_query(query: str, top_k: int = 3) -> str:
    selected_top_k = max(1, int(top_k or 1))
    payload = search_knowledge_chunks_with_debug(query, limit=max(selected_top_k * 4, selected_top_k))
    results = payload.get("results", []) if isinstance(payload, dict) else []
    return build_context_from_results(query=query, results=results, top_k=selected_top_k)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Busca textual local em data/knowledge_chunks")
    parser.add_argument("query", nargs="?", default="", help="Termo, frase ou palavras-chave para busca")
    parser.add_argument("--limit", type=int, default=5, help="Limite de resultados")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON com identacao")
    parser.add_argument("--build-context", action="store_true", help="Monta contexto textual compacto dos melhores resultados")
    parser.add_argument("--top-k", type=int, default=3, help="Quantidade de blocos no contexto textual")
    args = parser.parse_args()

    if args.build_context:
        print(build_context_from_query(args.query, top_k=max(1, args.top_k)))
        return

    output = {
        "query": args.query,
        "count": 0,
        "results": [],
        "search_debug": {},
    }
    if args.query.strip():
        enriched = search_knowledge_chunks_with_debug(args.query, limit=args.limit)
        matches = enriched.get("results", [])
        output["count"] = len(matches)
        output["results"] = matches
        output["search_debug"] = enriched.get("debug", {})

    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()
