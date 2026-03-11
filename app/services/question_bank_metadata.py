import re
from typing import Any

from app.services.certification_map import iter_domains
from app.services.knowledge_gap_analyzer import _tokenize
from app.services.knowledge_tags import infer_tags, merge_tags

PYTHON_CERT_PATTERNS = {
    "PCEP": {"level": "basic"},
    "PCAP": {"level": "intermediate"},
    "PCPP1": {"level": "advanced"},
}

PYTHON_PROMPT_RULES = [
    {
        "id": "python-modules-packages",
        "keywords": ["module", "modules", "import", "package", "packages", "namespace", "directive", "__name__", "__pycache__"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": [],
        "cert_domain": "modules_packages",
    },
    {
        "id": "python-variables-scope",
        "keywords": ["variable", "variables", "scope", "namespace", "global", "local", "nonlocal", "parameter", "argument"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": [],
        "cert_domain": "fundamentals",
    },
    {
        "id": "python-oop",
        "keywords": ["class", "object", "method", "inheritance", "encapsulation", "polymorphism", "__init__", "super-class", "superclass"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": ["oop"],
        "cert_domain": "oop",
    },
    {
        "id": "python-exceptions",
        "keywords": ["exception", "exceptions", "traceback", "try", "except", "finally", "raise", "assert"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": [],
        "cert_domain": "exceptions",
    },
    {
        "id": "python-iterators-generators",
        "keywords": ["iterator", "iterators", "iterable", "iterables", "generator", "generators", "yield", "lambda", "closure"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": [],
        "cert_domain": "advanced_flow",
    },
    {
        "id": "python-collections-comprehensions",
        "keywords": ["list", "tuple", "dict", "dictionary", "set", "slice", "slicing", "comprehension", "comprehensions", "range", "filter", "map"],
        "technology": ["python"],
        "domain": ["backend"],
        "subtheme": [],
        "cert_domain": "data_collections",
    },
]

CERT_DOMAIN_TO_SUBTHEME = {
    "oop": "oop",
}

NON_PYTHON_TECHS = {"aws", "terraform", "docker", "linux", "react", "java", "fastapi", "kubernetes"}
NON_PYTHON_DOMAINS = {"cloud", "devops", "frontend", "networking", "security"}
EXPLICIT_NON_PYTHON_HINTS = {
    "aws": ["aws", "iam", "s3", "ec2", "vpc"],
    "terraform": ["terraform", "hcl", "terraform cloud", "terraform init"],
    "linux": ["linux", "bash", "systemd"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s", "kubectl", "pod", "pods", "deployment", "deployments", "service", "services", "namespace", "namespaces", "cluster", "node", "helm", "ingress", "cka", "ckad"],
    "react": ["react", "jsx", "tsx"],
    "java": ["java", "jvm"],
}
EXPLICIT_PYTHON_HINTS = [
    "python",
    "pip",
    "venv",
    "pytest",
    "pyproject",
    "__name__",
    "__pycache__",
    "django",
    "flask",
    "fastapi",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _has_term(text: str, term: str) -> bool:
    normalized_text = _normalize(text)
    normalized_term = _normalize(term)
    if not normalized_term:
        return False
    if " " in normalized_term or "/" in normalized_term or "_" in normalized_term:
        return normalized_term in normalized_text
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", normalized_text))


def _detect_python_source_context(source_file: str, title: str) -> dict[str, Any]:
    searchable = _normalize(f"{source_file} {title}")
    for cert, metadata in PYTHON_CERT_PATTERNS.items():
        if cert.lower() in searchable:
            return {
                "track": "python",
                "certification": cert,
                "level": metadata["level"],
            }
    return {}


def _load_python_domains() -> list[dict[str, Any]]:
    try:
        return [domain for domain in iter_domains("python") if isinstance(domain, dict)]
    except Exception:
        return []


def _score_python_cert_domain(prompt: str, choices: list[str], source_context: dict[str, Any]) -> dict[str, Any]:
    if source_context.get("track") != "python":
        return {}

    text = _normalize(" ".join([prompt, *choices]))
    query_tokens = set(_tokenize(text))
    best_match: dict[str, Any] = {}
    best_score = 0.0

    for candidate in _load_python_domains():
        score = 0.0
        topics = [str(item) for item in candidate.get("topics", [])]
        domain_name = str(candidate.get("domain_name", ""))
        domain_id = str(candidate.get("domain", ""))

        if candidate.get("certification") == source_context.get("certification"):
            score += 1.5

        for token in _tokenize(domain_name):
            if token in query_tokens:
                score += 1.0
        for token in _tokenize(domain_id):
            if token in query_tokens:
                score += 1.0
        for topic in topics:
            topic_norm = _normalize(topic)
            if topic_norm and topic_norm in text:
                score += 3.0
            for token in _tokenize(topic):
                if token in query_tokens:
                    score += 1.25

        if score > best_score:
            best_score = score
            best_match = {
                "certification": candidate.get("certification", ""),
                "level": candidate.get("level", ""),
                "domain": domain_id,
                "domain_name": domain_name,
                "score": round(score, 3),
            }

    return best_match if best_score > 0 else {}


def _explicit_non_python_matches(text: str) -> set[str]:
    matches: set[str] = set()
    for tech, hints in EXPLICIT_NON_PYTHON_HINTS.items():
        if any(_has_term(text, hint) for hint in hints):
            matches.add(tech)
    return matches


def _sanitize_base_tags_for_python_context(base_tags: dict[str, list[str]], text: str, source_context: dict[str, Any]) -> dict[str, list[str]]:
    if source_context.get("track") != "python":
        return base_tags

    explicit_non_python = _explicit_non_python_matches(text)
    technologies = [tag for tag in base_tags.get("technology", []) if tag not in NON_PYTHON_TECHS or tag in explicit_non_python]
    domains = [tag for tag in base_tags.get("domain", []) if tag not in NON_PYTHON_DOMAINS or explicit_non_python]
    subthemes = list(base_tags.get("subtheme", []))

    return merge_tags(
        {
            "technology": technologies,
            "domain": domains,
            "subtheme": subthemes,
        }
    )


def _should_skip_python_rule(rule: dict[str, Any], text: str) -> bool:
    rule_tech = {str(item) for item in rule.get("technology", []) if str(item).strip()}
    if "python" not in rule_tech:
        return False
    explicit_non_python = _explicit_non_python_matches(text)
    has_python_hint = any(_has_term(text, hint) for hint in EXPLICIT_PYTHON_HINTS)
    return bool(explicit_non_python) and not has_python_hint


def infer_question_metadata(
    source_file: str,
    title: str,
    prompt: str,
    choices: list[str] | None = None,
    answer_hint: str | None = None,
) -> dict[str, Any]:
    choices = choices or []
    answer_hint = answer_hint or ""
    combined_text = " ".join([source_file, title, prompt, *choices, answer_hint]).strip()

    source_context = _detect_python_source_context(source_file=source_file, title=title)
    base_tags = infer_tags(source_file=source_file, title=title, content=" ".join([prompt, *choices, answer_hint]))
    base_tags = _sanitize_base_tags_for_python_context(base_tags, text=combined_text, source_context=source_context)

    matched_rule_ids: list[str] = []
    heuristic_payloads: list[dict[str, list[str]]] = []
    selected_subtheme = None

    for rule in PYTHON_PROMPT_RULES:
        if _should_skip_python_rule(rule, combined_text):
            continue
        if any(_has_term(combined_text, keyword) for keyword in rule["keywords"]):
            matched_rule_ids.append(rule["id"])
            heuristic_payloads.append(
                {
                    "technology": list(rule["technology"]),
                    "domain": list(rule["domain"]),
                    "subtheme": list(rule["subtheme"]),
                }
            )
            if not selected_subtheme and rule["subtheme"]:
                selected_subtheme = rule["subtheme"][0]

    cert_domain_match = _score_python_cert_domain(prompt=prompt, choices=choices, source_context=source_context)
    cert_payload = None
    if cert_domain_match:
        matched_rule_ids.append(f"cert-map:{cert_domain_match['domain']}")
        cert_payload = {
            "technology": ["python"] if source_context.get("track") == "python" else [],
            "domain": ["backend"] if source_context.get("track") == "python" else [],
            "subtheme": [CERT_DOMAIN_TO_SUBTHEME[cert_domain_match["domain"]]] if cert_domain_match.get("domain") in CERT_DOMAIN_TO_SUBTHEME else [],
        }
        if not selected_subtheme and cert_payload["subtheme"]:
            selected_subtheme = cert_payload["subtheme"][0]

    context_payload = None
    if source_context.get("track") == "python":
        matched_rule_ids.append(f"source-context:{source_context.get('certification', 'python')}")
        context_payload = {
            "technology": ["python"],
            "domain": ["backend"],
            "subtheme": [],
        }

    explicit_non_python = _explicit_non_python_matches(combined_text)
    explicit_non_python_payload = None
    if "kubernetes" in explicit_non_python:
        explicit_non_python_payload = {
            "technology": ["kubernetes"],
            "domain": ["devops", "networking"],
            "subtheme": [],
        }
    elif "terraform" in explicit_non_python:
        explicit_non_python_payload = {
            "technology": ["terraform"],
            "domain": ["cloud", "devops"],
            "subtheme": [],
        }
    elif "aws" in explicit_non_python:
        explicit_non_python_payload = {
            "technology": ["aws"],
            "domain": ["cloud", "devops", "security"],
            "subtheme": [],
        }

    merged = merge_tags(base_tags, context_payload, cert_payload, explicit_non_python_payload, *heuristic_payloads)
    if explicit_non_python and "python" not in explicit_non_python and not any(_has_term(combined_text, hint) for hint in EXPLICIT_PYTHON_HINTS):
        merged = merge_tags(
            {
                "technology": [tag for tag in merged.get("technology", []) if tag != "python"],
                "domain": [tag for tag in merged.get("domain", []) if tag != "backend"],
                "subtheme": list(merged.get("subtheme", [])),
            }
        )
    inferred_domain = (merged.get("domain") or [None])[0]
    inferred_subtheme = selected_subtheme or (merged.get("subtheme") or [None])[0]

    difficulty_hint = None
    level = source_context.get("level", "")
    if level == "basic":
        difficulty_hint = "basic"
    elif level == "intermediate":
        difficulty_hint = "intermediate"
    elif level == "advanced":
        difficulty_hint = "advanced"

    return {
        "tags": merged,
        "inferred_domain": inferred_domain,
        "inferred_subtheme": inferred_subtheme,
        "difficulty_hint": difficulty_hint,
        "metadata_debug": {
            "source_context": source_context,
            "matched_rules": matched_rule_ids,
            "cert_domain_match": cert_domain_match,
        },
    }
