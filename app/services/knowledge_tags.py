import re
from typing import Any

TAG_PIPELINE_VERSION = "2026-02-28-precision-v3"

TECH_TAG_HINTS: dict[str, list[str]] = {
    "java": ["java", "jvm", "spring", "springboot", "maven", "gradle", "jpa", "hibernate"],
    "python": ["python", "pip", "venv", "django", "flask", "pytest", "pyproject"],
    "fastapi": ["fastapi", "asgi", "pydantic", "uvicorn", "starlette"],
    "aws": ["aws", "ec2", "s3", "iam", "vpc", "cloudwatch", "lambda", "rds"],
    "terraform": ["terraform", "hcl", "tfstate", "iac", "infrastructure as code", "hashicorp"],
    "linux": ["linux", "bash", "systemd", "iptables", "nftables", "ubuntu", "debian", "redhat"],
    "react": ["react", "jsx", "tsx", "redux", "hooks", "next.js", "nextjs"],
    "docker": ["docker", "dockerfile", "docker compose", "containerd", "registry"],
    "kubernetes": ["kubernetes", "k8s", "kubectl", "pod", "pods", "deployment", "deployments", "service", "services", "namespace", "namespaces", "cluster", "node", "helm", "ingress", "cka", "ckad"],
}

DOMAIN_TAG_HINTS: dict[str, list[str]] = {
    "backend": ["backend", "api", "rest api", "microservice", "server", "endpoint", "orm", "wsgi", "asgi"],
    "frontend": ["frontend", "ui", "ux", "spa", "browser", "css", "html", "javascript", "dom"],
    "cloud": ["cloud", "aws", "azure", "gcp", "cloudformation", "serverless"],
    "devops": ["devops", "ci/cd", "pipeline", "infra as code", "terraform", "docker", "kubernetes", "observability"],
    "networking": ["network", "networking", "tcp", "udp", "dns", "subnet", "routing", "load balancer"],
    "security": ["security", "authentication", "authorization", "iam", "token", "tls", "encryption", "least privilege"],
}

SUBTHEME_HINTS: dict[str, list[str]] = {
    "oop": ["inheritance", "heranca", "encapsulation", "encapsulamento", "polymorphism", "polimorfismo", "object-oriented", "oriented programming", "super()"],
    "dependency-injection": ["dependency injection", "injeção de dependência", "di container"],
    "iam-policy": ["iam policy", "policy document", "principal", "assume role", "least privilege", "policy statement"],
    "firewall": ["firewall", "iptables", "nftables", "ufw", "security group", "network acl"],
    "api-design": ["rest api", "endpoint", "http method", "status code", "resource design", "request/response"],
    "containers": ["docker", "container runtime", "kubernetes", "pod", "image registry", "dockerfile"],
}

TECH_TO_DOMAIN: dict[str, list[str]] = {
    "fastapi": ["backend"],
    "react": ["frontend"],
    "aws": ["cloud", "devops"],
    "terraform": ["cloud", "devops"],
    "docker": ["devops"],
    "kubernetes": ["devops", "networking"],
    "linux": ["devops", "networking", "security"],
    "java": ["backend"],
    "python": ["backend"],
}

TAG_LIMITS = {
    "technology": 3,
    "domain": 3,
    "subtheme": 3,
}

MIN_SCORES = {
    "technology": 2.5,
    "domain": 2.5,
    "subtheme": 3.5,
}

STRONG_SOURCE_MULTIPLIER = 2.0
TEXT_WEIGHTS = {
    "source_file": 3.0,
    "path_hint": 2.5,
    "title": 2.5,
    "content": 1.0,
}

DOCUMENT_CONTENT_ONLY_MIN_HITS = {
    "technology": 12,
    "domain": 14,
    "subtheme": 18,
}

DOCUMENT_CONTENT_ONLY_MIN_DENSITY_PER_10K = {
    "technology": 0.35,
    "domain": 0.45,
    "subtheme": 0.6,
}

DOCUMENT_CONTENT_ONLY_MIN_MATCHED_TERMS = {
    "technology": 2,
    "domain": 2,
    "subtheme": 2,
}

DOCUMENT_CONTENT_ONLY_MIN_SCORE = {
    "technology": 10.0,
    "domain": 12.0,
    "subtheme": 14.0,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _has_term(text: str, term: str) -> bool:
    normalized_text = _normalize(text)
    normalized_term = _normalize(term)
    if not normalized_term:
        return False
    if " " in normalized_term or "/" in normalized_term or "-" in normalized_term:
        return normalized_term in normalized_text
    escaped = re.escape(normalized_term)
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", normalized_text))


def _compose_text(source_file: str, title: str, content: str, path_hint: str = "") -> str:
    return " \n ".join(
        [
            _normalize(source_file),
            _normalize(path_hint),
            _normalize(title),
            _normalize(content),
        ]
    )


def _count_term_hits(text: str, term: str) -> int:
    normalized_text = _normalize(text)
    normalized_term = _normalize(term)
    if not normalized_text or not normalized_term:
        return 0
    if " " in normalized_term or "/" in normalized_term or "-" in normalized_term:
        return normalized_text.count(normalized_term)
    escaped = re.escape(normalized_term)
    return len(re.findall(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", normalized_text))


def _score_candidate(source_parts: dict[str, str], tag: str, hints: list[str], kind: str) -> tuple[float, dict[str, Any]]:
    score = 0.0
    matched_terms: set[str] = set()
    strong_matches = 0
    signals = []
    part_hits = {part_name: 0 for part_name in source_parts}
    terms = [tag, *hints]

    for part_name, text in source_parts.items():
        if not text:
            continue
        part_weight = TEXT_WEIGHTS[part_name]
        for term in terms:
            hits = _count_term_hits(text, term)
            if hits <= 0:
                continue
            matched_terms.add(term)
            hit_weight = part_weight * min(hits, 3)
            part_hits[part_name] += hits
            if part_name in {"source_file", "path_hint", "title"}:
                strong_matches += 1
                hit_weight *= STRONG_SOURCE_MULTIPLIER
            score += hit_weight
            signals.append(f"{part_name}:{term}:{hits}")

    if kind == "subtheme":
        # Subtheme needs a more specific signal than domains/technologies.
        specific_term_count = len(matched_terms)
        if strong_matches == 0 and specific_term_count < 2:
            return 0.0, {"matched_terms": [], "strong_matches": 0, "signals": []}

    if kind == "domain":
        broad_term_only = tag in matched_terms and len(matched_terms) == 1 and strong_matches == 0
        if broad_term_only:
            return 0.0, {"matched_terms": [], "strong_matches": 0, "signals": []}

    return round(score, 3), {
        "matched_terms": sorted(matched_terms),
        "strong_matches": strong_matches,
        "signals": signals[:8],
        "part_hits": part_hits,
        "content_density_per_10k": round((part_hits.get("content", 0) * 10000.0) / max(len(source_parts.get("content", "")), 1), 4),
    }


def _collect_scored_matches(
    source_parts: dict[str, str],
    candidates: dict[str, list[str]],
    kind: str,
    document_mode: bool = False,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    scored: list[tuple[float, str, dict[str, Any]]] = []
    debug: dict[str, dict[str, Any]] = {}
    min_score = MIN_SCORES[kind]
    limit = TAG_LIMITS[kind]

    for tag, hints in candidates.items():
        score, details = _score_candidate(source_parts=source_parts, tag=tag, hints=hints, kind=kind)
        if score < min_score:
            continue
        details["score"] = score
        debug[tag] = details
        scored.append((score, tag, details))

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected_items = scored
    if document_mode:
        selected_items = _refine_document_matches(scored=scored, kind=kind)
    selected = [tag for _, tag, _ in selected_items[:limit]]
    return selected, {tag: debug[tag] for tag in selected}


def _passes_document_content_gate(kind: str, details: dict[str, Any]) -> bool:
    part_hits = details.get("part_hits", {}) if isinstance(details.get("part_hits"), dict) else {}
    return (
        float(details.get("score", 0.0)) >= DOCUMENT_CONTENT_ONLY_MIN_SCORE[kind]
        and int(part_hits.get("content", 0) or 0) >= DOCUMENT_CONTENT_ONLY_MIN_HITS[kind]
        and float(details.get("content_density_per_10k", 0.0) or 0.0) >= DOCUMENT_CONTENT_ONLY_MIN_DENSITY_PER_10K[kind]
        and len(details.get("matched_terms", [])) >= DOCUMENT_CONTENT_ONLY_MIN_MATCHED_TERMS[kind]
    )


def _refine_document_matches(
    scored: list[tuple[float, str, dict[str, Any]]],
    kind: str,
) -> list[tuple[float, str, dict[str, Any]]]:
    anchored = [item for item in scored if int(item[2].get("strong_matches", 0) or 0) > 0]
    content_only = [item for item in scored if int(item[2].get("strong_matches", 0) or 0) == 0]
    precise_content = [item for item in content_only if _passes_document_content_gate(kind=kind, details=item[2])]
    primary_score = anchored[0][0] if anchored else (scored[0][0] if scored else 0.0)

    if kind == "technology":
        if primary_score > 0:
            precise_content = [item for item in precise_content if item[0] >= (primary_score * 0.45)]
        if anchored:
            return [*anchored[:2], *precise_content[:1]]
        return precise_content

    if kind == "domain":
        if primary_score > 0:
            precise_content = [item for item in precise_content if item[0] >= (primary_score * 0.5)]
        if anchored:
            return [*anchored[:2], *precise_content[:1]]
        return precise_content

    if anchored:
        return [*anchored[:1], *precise_content[:1]]
    return precise_content


def merge_tags(*tag_sets: dict[str, Any] | None) -> dict[str, list[str]]:
    technologies: set[str] = set()
    domains: set[str] = set()
    subthemes: set[str] = set()
    for payload in tag_sets:
        if not isinstance(payload, dict):
            continue
        technologies.update(str(item) for item in payload.get("technology", []) if str(item).strip())
        domains.update(str(item) for item in payload.get("domain", []) if str(item).strip())
        subthemes.update(str(item) for item in payload.get("subtheme", []) if str(item).strip())

    all_tags = sorted(technologies | domains | subthemes)
    return {
        "technology": sorted(technologies),
        "domain": sorted(domains),
        "subtheme": sorted(subthemes),
        "all": all_tags,
    }


def infer_tags(source_file: str = "", title: str = "", content: str = "", path_hint: str = "") -> dict[str, list[str]]:
    source_parts = {
        "source_file": _normalize(source_file),
        "path_hint": _normalize(path_hint),
        "title": _normalize(title),
        "content": _normalize(content),
    }
    document_mode = any(source_parts.get(key) for key in ("source_file", "path_hint", "title"))
    technologies, _ = _collect_scored_matches(source_parts, TECH_TAG_HINTS, kind="technology", document_mode=document_mode)
    domains, _ = _collect_scored_matches(source_parts, DOMAIN_TAG_HINTS, kind="domain", document_mode=document_mode)
    subthemes, _ = _collect_scored_matches(source_parts, SUBTHEME_HINTS, kind="subtheme", document_mode=document_mode)

    for tech in technologies:
        domains.extend(TECH_TO_DOMAIN.get(tech, []))
    domains = sorted(set(domains))

    return merge_tags(
        {
            "technology": technologies,
            "domain": domains,
            "subtheme": subthemes,
        }
    )


def infer_query_tags(query: str) -> dict[str, list[str]]:
    inferred = infer_tags(title=query, content=query)

    normalized = _normalize(query)
    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    if not tokens:
        return inferred

    fallback_tech: set[str] = set()
    fallback_domains: set[str] = set()
    fallback_subthemes: set[str] = set()

    if tokens & {"kubernetes", "k8s", "kubectl", "helm", "liveness", "readiness", "probe", "nginx"}:
        fallback_tech.add("kubernetes")
        fallback_domains.update({"devops", "networking"})
    if tokens & {"docker", "container", "containers", "pod", "pods", "nginx", "liveness", "readiness", "probe", "helm"}:
        fallback_subthemes.add("containers")

    if not (fallback_tech or fallback_domains or fallback_subthemes):
        return inferred

    return merge_tags(
        inferred,
        {
            "technology": sorted(fallback_tech),
            "domain": sorted(fallback_domains),
            "subtheme": sorted(fallback_subthemes),
        },
    )
