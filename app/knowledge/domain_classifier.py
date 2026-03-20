import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from .router_types import CandidateFront, ClassifierOutcome


class DomainClassifier:
    """A simple keyword-based classifier backed by the knowledge front registry."""

    def __init__(self, registry_path: Optional[str] = None) -> None:
        registry_file = (
            Path(registry_path)
            if registry_path
            else Path(__file__).resolve().parent / "knowledge_front_registry.json"
        )
        self.registry_path = registry_file
        self.fronts = self._load_registry()
        self.alias_map = {
            "java": "JAVA",
            "thread": "JAVA",
            "lifecycle": "JAVA",
            "openai": "OPENAI_PRODUCTS",
            "codex": "OPENAI_PRODUCTS",
            "realtime": "OPENAI_PRODUCTS",
            "python": "PYTHON",
            "asyncio": "PYTHON",
            "pip": "PYTHON",
            "eventloop": "PYTHON",
            "postgresql": "POSTGRESQL",
            "postgres": "POSTGRESQL",
            "jsonb": "POSTGRESQL",
            "indexing": "POSTGRESQL",
            "systemd": "LINUX",
            "linux": "LINUX",
            "service": "LINUX",
            "restart": "LINUX",
            "docker": "DOCKER",
            "container": "DOCKER",
            "volume": "DOCKER",
            "bind": "DOCKER",
            "bindmount": "DOCKER",
            "mount": "DOCKER",
            "kubernetes": "KUBERNETES",
            "cluster": "KUBERNETES",
            "readiness": "KUBERNETES",
            "probe": "KUBERNETES",
            "terraform": "TERRAFORM",
            "provider": "TERRAFORM",
            "module": "TERRAFORM",
        }

    def _load_registry(self) -> List[Dict[str, object]]:
        with open(self.registry_path, "r", encoding="utf-8") as stream:
            data = json.load(stream)
        return data.get("fronts", [])

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def _keyword_matches(self, normalized_query: str, keyword: str) -> bool:
        normalized_keyword = self._normalize(keyword)
        if not normalized_keyword:
            return False
        if " " in normalized_keyword:
            pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
            return re.search(pattern, normalized_query) is not None
        return re.search(rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)", normalized_query) is not None

    def classify(self, query: str) -> ClassifierOutcome:
        normalized_query = self._normalize(query)
        best_score = 0
        selected_front: Optional[str] = None
        selected_reasons: List[str] = []
        selected_keyword_count = 1
        candidates: List[CandidateFront] = []
        query_tokens = set(re.findall(r"\w+", normalized_query))

        for front in self.fronts:
            if not front.get("enabled_for_routing"):
                continue
            keywords = [kw for kw in front.get("keywords", []) if isinstance(kw, str)]
            score = 0
            reasons: List[str] = []
            front_name = str(front.get("name", "")).upper()
            for keyword in keywords:
                normalized_keyword = self._normalize(keyword)
                if self._keyword_matches(normalized_query, normalized_keyword):
                    score += 1
                    reasons.append(f"matched keyword '{keyword}'")
            alias_hits = [
                token for token in query_tokens if self.alias_map.get(token) == front_name
            ]
            if alias_hits:
                score += len(alias_hits)
                reasons.append(
                    f"alias match for tokens {', '.join(sorted(alias_hits))}"
                )
            candidates.append(
                CandidateFront(
                    name=front.get("name", ""),
                    score=score,
                    enabled_for_routing=bool(front.get("enabled_for_routing")),
                    keywords=keywords,
                    reasons=reasons,
                )
            )
            if score > best_score:
                best_score = score
                selected_front = front.get("name")
                selected_reasons = reasons
                selected_keyword_count = max(1, len(keywords))

        candidate_fronts = sorted(
            candidates, key=lambda candidate: candidate.score, reverse=True
        )
        candidate_dicts = [candidate.to_dict() for candidate in candidate_fronts]
        confidence = 0.0
        if best_score > 0:
            confidence = min(1.0, best_score / selected_keyword_count)
        return ClassifierOutcome(
            query=query,
            selected_front=selected_front,
            confidence=confidence,
            reasons=selected_reasons,
            candidate_fronts=candidate_dicts,
            best_score=best_score,
        )
