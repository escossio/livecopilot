#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.state import ConversationState
from app.services.suggestions import generate_suggestions


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def main() -> int:
    dataset_path = PROJECT_ROOT / "scripts" / "eval_queries.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    for item in dataset:
        query = str(item.get("query", "")).strip()
        if not query:
            continue

        state = ConversationState()
        state.add_turn("user", query)
        suggestions = generate_suggestions(state)
        knowledge_context = state.knowledge_context if isinstance(state.knowledge_context, dict) else {}
        knowledge_debug = state.knowledge_debug if isinstance(state.knowledge_debug, dict) else {}

        context_text = str(knowledge_context.get("context", "") or "")
        context_len = len(context_text)

        rows.append(
            {
                "query": query,
                "expected_domain": item.get("expected_domain", ""),
                "search_backend": str(knowledge_context.get("search_backend", "") or ""),
                "result_count": _safe_int(knowledge_context.get("result_count"), 0),
                "context_len": context_len,
                "has_contexto_final": bool(context_len > 0),
                "semantic_duration_ms": _safe_int(knowledge_context.get("semantic_duration_ms"), 0),
                "semantic_api_ok": bool(knowledge_context.get("semantic_api_ok", False)),
                "fallback_used": bool(knowledge_context.get("fallback_used", False)),
                "suggestions_count": len(suggestions),
                "search_cache_hit": bool(knowledge_debug.get("search_cache_hit", False)),
                "semantic_path": str(knowledge_debug.get("semantic_path", "") or ""),
            }
        )

    total = len(rows)
    queries_com_contexto_relevante = sum(1 for r in rows if bool(r.get("has_contexto_final")))
    queries_sem_contexto = sum(1 for r in rows if _safe_int(r.get("context_len"), 0) == 0)
    avg_context_len = (sum(_safe_int(r.get("context_len"), 0) for r in rows) / total) if total else 0.0
    avg_semantic_duration_ms = (sum(_safe_float(r.get("semantic_duration_ms"), 0.0) for r in rows) / total) if total else 0.0
    out_scope_rows = [r for r in rows if str(r.get("expected_domain", "")).strip().lower() == "out_of_scope"]
    in_scope_rows = [r for r in rows if str(r.get("expected_domain", "")).strip().lower() != "out_of_scope"]
    out_of_scope_com_contexto = sum(1 for r in out_scope_rows if _safe_int(r.get("context_len"), 0) > 0)
    out_of_scope_sem_contexto = sum(1 for r in out_scope_rows if _safe_int(r.get("context_len"), 0) == 0)
    out_scope_examples_with_context = [r["query"] for r in out_scope_rows if _safe_int(r.get("context_len"), 0) > 0][:5]
    out_scope_examples_without_context = [r["query"] for r in out_scope_rows if _safe_int(r.get("context_len"), 0) == 0][:5]

    print("Semantic Eval")
    print(f"dataset: {dataset_path}")
    print(f"total_queries: {total}")
    print(f"queries_com_contexto_relevante: {queries_com_contexto_relevante}")
    print(f"queries_sem_contexto: {queries_sem_contexto}")
    print(f"avg_context_len: {avg_context_len:.2f}")
    print(f"avg_semantic_duration_ms: {avg_semantic_duration_ms:.2f}")
    print(f"in_scope_queries: {len(in_scope_rows)}")
    print(f"out_of_scope_queries: {len(out_scope_rows)}")
    print(f"out_of_scope_com_contexto_no_fluxo_real: {out_of_scope_com_contexto}")
    print(f"out_of_scope_sem_contexto_no_fluxo_real: {out_of_scope_sem_contexto}")

    print("\nOut-of-scope examples")
    print("sem_contexto_no_fluxo_real:")
    if out_scope_examples_without_context:
        for q in out_scope_examples_without_context:
            print(f"- {q}")
    else:
        print("- (nenhum)")
    print("com_contexto_no_fluxo_real:")
    if out_scope_examples_with_context:
        for q in out_scope_examples_with_context:
            print(f"- {q}")
    else:
        print("- (nenhum)")

    print("\nPer-query")
    for idx, row in enumerate(rows, start=1):
        print(
            f"{idx:02d}. rc={row['result_count']} ctx={row['context_len']} dur={row['semantic_duration_ms']}ms "
            f"semantic_ok={str(row['semantic_api_ok']).lower()} fallback={str(row['fallback_used']).lower()} "
            f"has_ctx={str(row['has_contexto_final']).lower()} backend={row['search_backend'] or '-'} "
            f"path={row['semantic_path'] or '-'} cache_hit={str(row['search_cache_hit']).lower()} | {row['query']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
