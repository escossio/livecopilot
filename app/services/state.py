from dataclasses import dataclass, field
from typing import List, Dict, Any

from app.core.config import settings


@dataclass
class ConversationState:
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    quick_replies: List[str] = field(default_factory=list)
    fillers: List[str] = field(default_factory=list)
    term_hints: List[str] = field(default_factory=list)
    knowledge_context: Dict[str, Any] = field(default_factory=dict)
    knowledge_debug: Dict[str, Any] = field(default_factory=dict)

    def add_turn(self, speaker: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        turn: Dict[str, Any] = {"speaker": speaker, "text": text}
        if metadata:
            turn.update({str(k): v for k, v in metadata.items() if str(k).strip()})
        self.transcript.append(turn)
        if len(self.transcript) > settings.max_context_turns:
            self.transcript = self.transcript[-settings.max_context_turns :]

    def snapshot(self) -> Dict:
        data = {
            "transcript": self.transcript,
            "suggestions": self.suggestions,
            "quick_replies": self.quick_replies,
            "fillers": self.fillers,
            "term_hints": self.term_hints,
            "knowledge_context": self.knowledge_context,
        }
        if settings.knowledge_debug:
            data["knowledge_debug"] = self.knowledge_debug
        return data
