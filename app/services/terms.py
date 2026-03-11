from typing import List

TERM_MAP = {
    "kpi": "KPI (Key Performance Indicator)",
    "sla": "SLA (Service Level Agreement)",
    "api": "API (Interface de Programacao de Aplicacoes)",
    "mvp": "MVP (Minimum Viable Product)",
    "ux": "UX (User Experience)",
}


def suggest_terms(text: str) -> List[str]:
    hints = []
    lowered = text.lower()
    for key, hint in TERM_MAP.items():
        if key in lowered:
            hints.append(hint)
    return hints
