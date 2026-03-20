from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CandidateFront:
    name: str
    score: int
    enabled_for_routing: bool
    keywords: List[str]
    reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "enabled_for_routing": self.enabled_for_routing,
            "keywords": self.keywords,
            "reasons": self.reasons,
        }


@dataclass
class ClassifierOutcome:
    query: str
    selected_front: Optional[str]
    confidence: float
    reasons: List[str]
    candidate_fronts: List[Dict[str, Any]]
    best_score: int
