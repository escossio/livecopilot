from typing import Any, Sequence

from app.core import config


class StageGate:
    REQUIREMENTS: dict[str, str] = {
        "source_manifest": "source_policy",
        "corpus_freeze": "source_manifest",
        "parsing": "corpus_freeze",
        "chunking": "parsing",
        "lexical_validation": "chunking",
        "chunk_refinement": "lexical_validation",
        "semantic_baseline": "chunk_refinement",
        "semantic_refinement": "semantic_baseline",
        "domain_closure": "semantic_refinement",
    }

    def __init__(self, stages: Sequence[str] | None = None) -> None:
        self.stages = list(stages or config.PIPELINE_STAGES)

    def can_advance(self, current_stage: str, next_stage: str) -> bool:
        if current_stage not in self.stages or next_stage not in self.stages:
            return False
        current_index = self.stages.index(current_stage)
        next_index = self.stages.index(next_stage)
        return next_index == current_index + 1

    def check(self, stage: str, executed_stages: Sequence[dict[str, Any]] | None) -> tuple[bool, str]:
        executed = {entry.get("stage") for entry in (executed_stages or []) if not entry.get("blocked")}
        requirement = self.REQUIREMENTS.get(stage)
        if not requirement:
            return True, "sem gate específico"
        if requirement in executed:
            return True, f"pré-requisito {requirement} satisfeito"
        return False, f"aguardando pré-requisito {requirement}"
