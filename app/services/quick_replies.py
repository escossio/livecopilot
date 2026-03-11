from typing import List

from app.core.config import settings
from app.services.state import ConversationState


def generate_quick_replies(state: ConversationState) -> List[str]:
    replies = [
        "Sim, pode seguir.",
        "Certo, entendi.",
        "Vamos revisar em 2 minutos.",
        "Pode repetir o ponto principal?",
        "Anotado.",
        "Vamos alinhar depois.",
    ]
    return replies[: settings.quick_replies_limit]
