from typing import List

from app.core.config import settings


def generate_fillers() -> List[str]:
    fillers = [
        "Só um segundo para organizar.",
        "Estou acompanhando, pode continuar.",
        "Deixa eu alinhar os pontos aqui.",
        "Vou resumir para garantir entendimento.",
    ]
    return fillers[: settings.fillers_limit]
