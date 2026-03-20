import argparse
import json
from typing import List

from .knowledge_router import KnowledgeRouter


CLI_HELP = """Roteia uma query para o domínio de conhecimento mais relevante."""


def _print_candidates(candidates: List[dict]) -> None:
    if not candidates:
        print("  (nenhuma frente disponível)")
        return
    for candidate in candidates:
        score = candidate.get("score", 0)
        enabled = candidate.get("enabled_for_routing")
        print(
            f"  - {candidate.get('name')} (score={score}, enabled={enabled})",
            end="",
        )
        reasons = candidate.get("reasons") or []
        if reasons:
            print(" | "+"; ".join(reasons))
        else:
            print()


def main() -> None:
    parser = argparse.ArgumentParser(description=CLI_HELP)
    parser.add_argument("query", nargs="+", help="Texto a ser roteado")
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="imprime o resultado em JSON",
    )
    args = parser.parse_args()
    text_query = " ".join(args.query)
    router = KnowledgeRouter()
    result = router.route(text_query)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"Query: {result['query']}")
    print(f"Selected front: {result['selected_front'] or 'fallback'}")
    print(f"Confidence: {result['confidence']}")
    reasons = result.get("reasons") or []
    print("Reasons: " + (", ".join(reasons) if reasons else "nenhuma"))
    print(f"Routing mode: {result['routing_mode']}")
    print("Candidate fronts:")
    _print_candidates(result.get("candidate_fronts", []))


if __name__ == "__main__":
    main()
