from typing import Optional

from .domain_classifier import DomainClassifier
from .router_types import ClassifierOutcome


class KnowledgeRouter:
    """Facade that exposes the domain routing envelope for queries."""

    def __init__(self, registry_path: Optional[str] = None) -> None:
        self.classifier = DomainClassifier(registry_path=registry_path)

    def route(self, query: str) -> dict:
        outcome: ClassifierOutcome = self.classifier.classify(query)
        routing_mode = "single_front" if outcome.best_score > 0 else "fallback"
        return {
            "query": outcome.query,
            "selected_front": outcome.selected_front,
            "confidence": round(outcome.confidence, 3),
            "reasons": outcome.reasons,
            "candidate_fronts": outcome.candidate_fronts,
            "routing_mode": routing_mode,
        }
