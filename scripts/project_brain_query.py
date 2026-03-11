#!/usr/bin/env python3
import argparse
import math
import json
import os
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.knowledge_gap_logger import log_knowledge_gap


def _dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise RuntimeError("DSN ausente: defina DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    return dsn


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vec) + "]"


def _norm(value: str) -> str:
    return " ".join((value or "").strip().split())


def _fold_ascii(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _parse_created_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _recency_weight(created_at: str | None) -> float:
    dt = _parse_created_at(created_at)
    if dt is None:
        return 1.0
    now = datetime.now(timezone.utc)
    days_since = max(0.0, (now - dt).total_seconds() / 86400.0)
    return math.exp(-(days_since / 30.0))


def _fact_type_weight(fact_type: str | None) -> float:
    normalized = (fact_type or "").strip().lower()
    if normalized == "decision":
        return 1.5
    if normalized == "milestone":
        return 1.3
    if normalized == "risk":
        return 1.2
    return 1.1


def _canonical_memory_type(source_type: str | None) -> str:
    normalized = (source_type or "").strip().lower()
    if normalized == "fact":
        return "fact"
    if normalized == "run_summary":
        return "run_summary"
    if normalized in {"memory_chunk", "chunk"}:
        return "memory_chunk"
    return "other"


def _memory_type_weight(source_type: str | None, fact_type: str | None = None) -> float:
    memory_type = _canonical_memory_type(source_type)
    if memory_type == "fact":
        return _fact_type_weight(fact_type)
    if memory_type == "run_summary":
        return 1.0
    return 0.8


def _apply_diversity(
    ranked_items: list[dict[str, Any]],
    *,
    limit: int,
    type_key: str,
    max_share: float = 0.6,
) -> list[dict[str, Any]]:
    if not ranked_items:
        return []
    capped_limit = max(1, limit)
    max_per_type = max(1, int(math.ceil(capped_limit * max_share)))

    selected: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for item in ranked_items:
        item_type = str(item.get(type_key, "") or "unknown")
        if counts.get(item_type, 0) >= max_per_type:
            continue
        selected.append(item)
        counts[item_type] = counts.get(item_type, 0) + 1
        if len(selected) >= capped_limit:
            return selected

    if len(selected) < capped_limit:
        selected_ids = {id(item) for item in selected}
        for item in ranked_items:
            if id(item) in selected_ids:
                continue
            selected.append(item)
            if len(selected) >= capped_limit:
                break
    return selected


def _structured_search(
    cur: Any,
    *,
    project: str,
    query: str,
    facts_limit: int,
    fact_type: str | None,
    fact_status: str | None,
    component: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query_variants: list[str] = []
    for candidate in [query, _fold_ascii(query)]:
        clean = _norm(candidate)
        if clean and clean not in query_variants:
            query_variants.append(clean)

    likes = [f"%{item}%" for item in query_variants]
    like = likes[0]
    token_source = _norm(_fold_ascii(query)) or _norm(query)
    tokens = [token for token in token_source.split() if token]
    extra_filters: list[str] = []
    filter_params: list[Any] = []

    if fact_type:
        extra_filters.append("f.fact_type = %s")
        filter_params.append(fact_type)
    if fact_status:
        extra_filters.append("f.fact_status = %s")
        filter_params.append(fact_status)
    if component:
        extra_filters.append("COALESCE(f.component, '') ILIKE %s")
        filter_params.append(f"%{component}%")

    where_extra = ""
    if extra_filters:
        where_extra = " AND " + " AND ".join(extra_filters)

    # Structured-first: aceita match por frase completa ou por todos os tokens da query.
    token_clauses: list[str] = []
    token_params: list[Any] = []
    for token in tokens:
        token_like = f"%{token}%"
        token_clauses.append(
            "("
            "f.title ILIKE %s OR "
            "f.body ILIKE %s OR "
            "COALESCE(f.component, '') ILIKE %s"
            ")"
        )
        token_params.extend([token_like, token_like, token_like])

    full_phrase_parts: list[str] = []
    search_params: list[Any] = []
    for phrase_like in likes:
        full_phrase_parts.append("(f.title ILIKE %s OR f.body ILIKE %s OR COALESCE(f.component, '') ILIKE %s)")
        search_params.extend([phrase_like, phrase_like, phrase_like])

    full_phrase_clause = "(" + " OR ".join(full_phrase_parts) + ")"
    where_search = full_phrase_clause
    if token_clauses:
        where_search = f"({full_phrase_clause} OR ({' AND '.join(token_clauses)}))"
        search_params.extend(token_params)

    cur.execute(
        f"""
        SELECT
            f.id,
            f.run_id,
            r.run_key,
            f.fact_type,
            f.fact_status,
            f.title,
            f.body,
            f.component,
            f.priority,
            f.created_at,
            CASE WHEN f.fact_status = 'active' THEN 0 ELSE 1 END AS status_rank,
            CASE WHEN f.title ILIKE %s THEN 0 ELSE 1 END AS title_rank
        FROM project_facts f
        JOIN project_runs r ON r.id = f.run_id
        WHERE r.project_name = %s
          AND {where_search}
          {where_extra}
        ORDER BY status_rank ASC, title_rank ASC, f.created_at DESC
        LIMIT %s
        """,
        tuple([like, project] + search_params + filter_params + [max(1, facts_limit)]),
    )
    fact_rows = cur.fetchall()

    structured_facts = [
        {
            "id": int(row[0]),
            "run_id": int(row[1]),
            "run_key": row[2],
            "fact_type": row[3],
            "fact_status": row[4],
            "title": row[5],
            "body": row[6],
            "component": row[7],
            "priority": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
        }
        for row in fact_rows
    ]

    run_ids = sorted({item["run_id"] for item in structured_facts})
    structured_runs: list[dict[str, Any]] = []
    if run_ids:
        cur.execute(
            """
            SELECT id, run_key, session_id, actor, run_type, summary_short, checkpoint_path, created_at
            FROM project_runs
            WHERE project_name = %s
              AND id = ANY(%s)
            ORDER BY created_at DESC
            """,
            (project, run_ids),
        )
        structured_runs.extend(
            {
                "id": int(row[0]),
                "run_key": row[1],
                "session_id": row[2],
                "actor": row[3],
                "run_type": row[4],
                "summary_short": row[5],
                "checkpoint_path": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
            }
            for row in cur.fetchall()
        )

    # Complementa runs por resumo textual relacionado.
    cur.execute(
        """
        SELECT id, run_key, session_id, actor, run_type, summary_short, checkpoint_path, created_at
        FROM project_runs
        WHERE project_name = %s
          AND (summary_short ILIKE %s OR summary_full ILIKE %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (project, like, like, max(1, facts_limit)),
    )
    for row in cur.fetchall():
        run_id = int(row[0])
        if any(item["id"] == run_id for item in structured_runs):
            continue
        structured_runs.append(
            {
                "id": run_id,
                "run_key": row[1],
                "session_id": row[2],
                "actor": row[3],
                "run_type": row[4],
                "summary_short": row[5],
                "checkpoint_path": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
            }
        )

    return structured_facts, structured_runs


def _get_query_embedding(query: str, model: str) -> tuple[list[float] | None, str | None]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return (
            None,
            "OPENAI_API_KEY ausente no processo atual; semantic/hybrid degradado para structured. "
            "Use scripts/project_brain_query.sh ou carregue /etc/livecopilot-semantic.env.",
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(model=model, input=query)
        vec = resp.data[0].embedding
        if len(vec) != 1536:
            return None, f"embedding com dimensao inesperada: {len(vec)}"
        return vec, None
    except Exception as exc:
        return (
            None,
            "falha ao gerar embedding da query; semantic/hybrid degradado para structured. "
            f"detalhe: {exc}",
        )


def _semantic_search(
    cur: Any,
    *,
    project: str,
    query: str,
    memory_limit: int,
    embed_model: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str | None]:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE r.project_name = %s
          AND m.embedding IS NOT NULL
        """,
        (project,),
    )
    count_with_embedding = int(cur.fetchone()[0])
    if count_with_embedding == 0:
        return (
            [],
            [],
            [],
            "nenhum embedding disponivel em project_memory_chunks; "
            "execute scripts/maintain_continuity_embeddings.sh para preencher faltantes.",
        )

    qvec, warn = _get_query_embedding(query, embed_model)
    if qvec is None:
        return [], [], [], warn

    cur.execute(
        """
        SELECT
            m.id,
            m.run_id,
            m.fact_id,
            m.source_type,
            m.source_path,
            m.semantic_layer,
            m.tags,
            LEFT(m.content, 260) AS excerpt,
            ROUND((1 - (m.embedding <=> %s::vector))::numeric, 6) AS similarity,
            m.created_at
        FROM project_memory_chunks m
        JOIN project_runs r ON r.id = m.run_id
        WHERE r.project_name = %s
          AND m.embedding IS NOT NULL
        ORDER BY m.embedding <=> %s::vector ASC
        LIMIT %s
        """,
        (_vector_literal(qvec), project, _vector_literal(qvec), max(1, memory_limit)),
    )
    rows = cur.fetchall()

    semantic_hits = [
        {
            "id": int(row[0]),
            "run_id": int(row[1]),
            "fact_id": int(row[2]) if row[2] is not None else None,
            "source_type": row[3],
            "source_path": row[4],
            "semantic_layer": row[5],
            "tags": row[6],
            "excerpt": row[7],
            "similarity": float(row[8]),
            "created_at": row[9].isoformat() if row[9] else None,
        }
        for row in rows
    ]

    fact_ids = sorted({hit["fact_id"] for hit in semantic_hits if hit.get("fact_id") is not None})
    run_ids = sorted({hit["run_id"] for hit in semantic_hits})

    semantic_facts: list[dict[str, Any]] = []
    semantic_runs: list[dict[str, Any]] = []

    if fact_ids:
        cur.execute(
            """
            SELECT f.id, f.run_id, r.run_key, f.fact_type, f.fact_status, f.title, f.body, f.component, f.priority, f.created_at
            FROM project_facts f
            JOIN project_runs r ON r.id = f.run_id
            WHERE r.project_name = %s
              AND f.id = ANY(%s)
            ORDER BY f.created_at DESC
            """,
            (project, fact_ids),
        )
        semantic_facts = [
            {
                "id": int(row[0]),
                "run_id": int(row[1]),
                "run_key": row[2],
                "fact_type": row[3],
                "fact_status": row[4],
                "title": row[5],
                "body": row[6],
                "component": row[7],
                "priority": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
            }
            for row in cur.fetchall()
        ]

    if run_ids:
        cur.execute(
            """
            SELECT id, run_key, session_id, actor, run_type, summary_short, checkpoint_path, created_at
            FROM project_runs
            WHERE project_name = %s
              AND id = ANY(%s)
            ORDER BY created_at DESC
            """,
            (project, run_ids),
        )
        semantic_runs = [
            {
                "id": int(row[0]),
                "run_key": row[1],
                "session_id": row[2],
                "actor": row[3],
                "run_type": row[4],
                "summary_short": row[5],
                "checkpoint_path": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
            }
            for row in cur.fetchall()
        ]

    return semantic_hits, semantic_facts, semantic_runs, None


def _rank_semantic_hits(
    semantic_hits: list[dict[str, Any]],
    *,
    memory_limit: int,
    fact_type_by_id: dict[int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ranked: list[dict[str, Any]] = []
    debug_rows: list[dict[str, Any]] = []

    for hit in semantic_hits:
        source_type = str(hit.get("source_type") or "chunk")
        memory_type = _canonical_memory_type(source_type)
        fact_id = hit.get("fact_id")
        fact_type = fact_type_by_id.get(int(fact_id)) if fact_id is not None else None
        score_original = max(0.0, float(hit.get("similarity") or 0.0))
        type_weight = _memory_type_weight(memory_type, fact_type)
        recency = _recency_weight(str(hit.get("created_at") or ""))
        score_final = score_original * type_weight * recency

        row = dict(hit)
        row["_memory_type"] = memory_type
        row["_score_original"] = round(score_original, 6)
        row["_type_weight"] = round(type_weight, 6)
        row["_recency_weight"] = round(recency, 6)
        row["_score_final"] = round(score_final, 6)
        ranked.append(row)

    ranked.sort(key=lambda x: float(x.get("_score_final") or 0.0), reverse=True)
    # Calibracao conservadora: limita dominancia de um unico memory_type no ranking semantic.
    ranked = _apply_diversity(ranked, limit=max(1, memory_limit), type_key="_memory_type", max_share=0.25)

    cleaned: list[dict[str, Any]] = []
    for item in ranked:
        cleaned_item = {k: v for k, v in item.items() if not k.startswith("_")}
        cleaned_item["memory_type"] = item.get("_memory_type")
        cleaned.append(cleaned_item)
        debug_rows.append(
            {
                "kind": "memory_chunk",
                "id": item.get("id"),
                "run_id": item.get("run_id"),
                "fact_id": item.get("fact_id"),
                "source_type": item.get("source_type"),
                "memory_type": item.get("_memory_type"),
                "score_original": item.get("_score_original"),
                "type_weight": item.get("_type_weight"),
                "recency_weight": item.get("_recency_weight"),
                "score_final": item.get("_score_final"),
            }
        )
    return cleaned, debug_rows


def _merge_facts(
    structured_facts: list[dict[str, Any]],
    semantic_facts: list[dict[str, Any]],
    semantic_hits: list[dict[str, Any]],
    *,
    facts_limit: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    semantic_fact_scores: dict[int, float] = {}
    for hit in semantic_hits:
        fact_id = hit.get("fact_id")
        if fact_id is None:
            continue
        try:
            fid = int(fact_id)
        except Exception:
            continue
        score = max(0.0, float(hit.get("similarity") or 0.0))
        if score > semantic_fact_scores.get(fid, 0.0):
            semantic_fact_scores[fid] = score

    seen: set[tuple[str, str, str, str]] = set()
    ranked: list[dict[str, Any]] = []
    debug_rows: list[dict[str, Any]] = []

    for coll in (structured_facts, semantic_facts):
        for item in coll:
            dedupe_key = (
                str(item.get("fact_type", "")).strip().lower(),
                str(item.get("fact_status", "")).strip().lower(),
                str(item.get("title", "")).strip().lower(),
                str(item.get("component", "")).strip().lower(),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            fact_id = int(item.get("id", 0))
            semantic_score = semantic_fact_scores.get(fact_id)
            is_active = str(item.get("fact_status", "")).strip().lower() == "active"
            score_original = semantic_score if semantic_score is not None else (0.80 if is_active else 0.68)
            type_weight = _memory_type_weight("fact", str(item.get("fact_type") or ""))
            recency = _recency_weight(str(item.get("created_at") or ""))
            score_final = score_original * type_weight * recency

            row = dict(item)
            row["_fact_group"] = str(item.get("fact_type") or "fact")
            row["_score_original"] = round(score_original, 6)
            row["_type_weight"] = round(type_weight, 6)
            row["_recency_weight"] = round(recency, 6)
            row["_score_final"] = round(score_final, 6)
            ranked.append(row)

    ranked.sort(key=lambda x: float(x.get("_score_final") or 0.0), reverse=True)
    ranked = _apply_diversity(ranked, limit=max(1, facts_limit), type_key="_fact_group", max_share=0.7)

    cleaned: list[dict[str, Any]] = []
    for item in ranked:
        cleaned.append({k: v for k, v in item.items() if not k.startswith("_")})
        debug_rows.append(
            {
                "kind": "fact",
                "id": item.get("id"),
                "fact_type": item.get("fact_type"),
                "fact_status": item.get("fact_status"),
                "score_original": item.get("_score_original"),
                "type_weight": item.get("_type_weight"),
                "recency_weight": item.get("_recency_weight"),
                "score_final": item.get("_score_final"),
            }
        )
    return cleaned, debug_rows


def _merge_runs(
    structured_runs: list[dict[str, Any]],
    semantic_runs: list[dict[str, Any]],
    semantic_hits: list[dict[str, Any]],
    *,
    facts_limit: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    semantic_run_scores: dict[int, float] = {}
    for hit in semantic_hits:
        try:
            run_id = int(hit.get("run_id", 0))
        except Exception:
            continue
        score = max(0.0, float(hit.get("similarity") or 0.0))
        if score > semantic_run_scores.get(run_id, 0.0):
            semantic_run_scores[run_id] = score

    seen: set[int] = set()
    ranked: list[dict[str, Any]] = []
    debug_rows: list[dict[str, Any]] = []

    for coll in (structured_runs, semantic_runs):
        for item in coll:
            item_id = int(item["id"])
            if item_id in seen:
                continue
            seen.add(item_id)

            score_original = semantic_run_scores.get(item_id, 0.70)
            type_weight = _memory_type_weight("run_summary")
            recency = _recency_weight(str(item.get("created_at") or ""))
            score_final = score_original * type_weight * recency

            row = dict(item)
            row["_score_original"] = round(score_original, 6)
            row["_type_weight"] = round(type_weight, 6)
            row["_recency_weight"] = round(recency, 6)
            row["_score_final"] = round(score_final, 6)
            ranked.append(row)

    ranked.sort(key=lambda x: float(x.get("_score_final") or 0.0), reverse=True)
    ranked = ranked[: max(1, facts_limit)]

    cleaned: list[dict[str, Any]] = []
    for item in ranked:
        cleaned.append({k: v for k, v in item.items() if not k.startswith("_")})
        debug_rows.append(
            {
                "kind": "run_summary",
                "id": item.get("id"),
                "run_key": item.get("run_key"),
                "score_original": item.get("_score_original"),
                "type_weight": item.get("_type_weight"),
                "recency_weight": item.get("_recency_weight"),
                "score_final": item.get("_score_final"),
            }
        )
    return cleaned, debug_rows


def _build_summary(query: str, facts: list[dict[str, Any]], runs: list[dict[str, Any]], mode: str, semantic_warn: str | None) -> str:
    if not facts and not runs:
        base = f"Sem evidencias suficientes para '{query}' no modo {mode}."
        if semantic_warn and mode in {"semantic", "hybrid"}:
            base += f" Observacao: {semantic_warn}."
        return base

    top_fact_titles = [str(item.get("title", "")).strip() for item in facts[:3] if str(item.get("title", "")).strip()]
    top_run_summaries = [str(item.get("summary_short", "")).strip() for item in runs[:2] if str(item.get("summary_short", "")).strip()]
    active_count = sum(1 for item in facts if str(item.get("fact_status", "")) == "active")

    parts: list[str] = [
        f"Foram encontrados {len(facts)} facts ({active_count} ativos) e {len(runs)} runs relacionados.",
    ]
    if top_fact_titles:
        parts.append("Foco principal: " + "; ".join(top_fact_titles))
    if top_run_summaries:
        parts.append("Runs recentes relevantes: " + " | ".join(top_run_summaries))
    if semantic_warn and mode in {"semantic", "hybrid"}:
        parts.append(f"Nota semantic: {semantic_warn}.")
    return " ".join(parts)


def _detect_knowledge_gap(
    *,
    query: str,
    mode: str,
    related_facts: list[dict[str, Any]],
    related_runs: list[dict[str, Any]],
    semantic_hits: list[dict[str, Any]],
    semantic_warning: str | None,
) -> tuple[str | None, dict[str, Any]]:
    top3 = semantic_hits[:3]
    top3_types = [str(item.get("memory_type") or _canonical_memory_type(item.get("source_type"))) for item in top3]
    avg_similarity = 0.0
    if semantic_hits:
        avg_similarity = sum(max(0.0, float(item.get("similarity") or 0.0)) for item in semantic_hits) / len(semantic_hits)
    avg_similarity_threshold = float(os.getenv("PROJECT_BRAIN_GAP_AVG_SCORE_THRESHOLD", "0.42"))

    reason: str | None = None
    if not related_facts and not related_runs and not semantic_hits:
        reason = "empty_result"
    elif semantic_hits and avg_similarity < avg_similarity_threshold:
        reason = "low_average_score"
    elif len(top3_types) >= 3 and len(set(top3_types)) == 1:
        reason = "collapsed_diversity"

    context = {
        "query": query,
        "mode": mode,
        "semantic_warning": semantic_warning,
        "related_facts_count": len(related_facts),
        "related_runs_count": len(related_runs),
        "semantic_hits_count": len(semantic_hits),
        "avg_similarity": round(avg_similarity, 6) if semantic_hits else None,
        "avg_similarity_threshold": avg_similarity_threshold,
        "top3_memory_types": top3_types,
    }
    return reason, context


def _render_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("PROJECT BRAIN RESULT")
    lines.append(f"project: {payload['project']}")
    lines.append(f"query: {payload['query']}")
    lines.append(f"mode: {payload['mode']}")
    lines.append("")

    if payload.get("semantic_warning"):
        lines.append(f"semantic_warning: {payload['semantic_warning']}")
        lines.append("")

    lines.append("related facts:")
    facts = payload.get("related_facts", [])
    if not facts:
        lines.append("- (none)")
    else:
        for fact in facts:
            comp = f" [{fact['component']}]" if fact.get("component") else ""
            lines.append(f"- [{fact['fact_type']}][{fact['fact_status']}] {fact['title']}{comp}")

    lines.append("")
    lines.append("related runs:")
    runs = payload.get("related_runs", [])
    if not runs:
        lines.append("- (none)")
    else:
        for run in runs:
            lines.append(f"- {run['run_key']} | {run['run_type']} | {run['summary_short']}")

    semantic_hits = payload.get("semantic_hits", [])
    if semantic_hits:
        lines.append("")
        lines.append("semantic hits:")
        for hit in semantic_hits:
            lines.append(
                f"- sim={hit['similarity']} run_id={hit['run_id']} fact_id={hit['fact_id']} excerpt={hit['excerpt']}"
            )

    ranking_debug = payload.get("ranking_debug", [])
    if ranking_debug:
        lines.append("")
        lines.append("ranking debug:")
        for row in ranking_debug:
            lines.append(
                "- "
                f"{row.get('kind')} id={row.get('id')} "
                f"orig={row.get('score_original')} "
                f"type_w={row.get('type_weight')} "
                f"recency_w={row.get('recency_weight')} "
                f"final={row.get('score_final')}"
            )

    lines.append("")
    lines.append("summary:")
    lines.append(payload.get("summary", ""))
    return "\n".join(lines)


def query_project_brain(
    *,
    project: str,
    query: str,
    mode: str,
    facts_limit: int,
    memory_limit: int,
    fact_type: str | None,
    fact_status: str | None,
    component: str | None,
    embed_model: str,
    debug_ranking: bool,
) -> dict[str, Any]:
    with psycopg.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            structured_facts: list[dict[str, Any]] = []
            structured_runs: list[dict[str, Any]] = []
            semantic_hits: list[dict[str, Any]] = []
            semantic_facts: list[dict[str, Any]] = []
            semantic_runs: list[dict[str, Any]] = []
            semantic_warning: str | None = None

            if mode in {"structured", "hybrid"}:
                structured_facts, structured_runs = _structured_search(
                    cur,
                    project=project,
                    query=query,
                    facts_limit=max(1, facts_limit),
                    fact_type=fact_type,
                    fact_status=fact_status,
                    component=component,
                )

            if mode in {"semantic", "hybrid"}:
                semantic_hits, semantic_facts, semantic_runs, semantic_warning = _semantic_search(
                    cur,
                    project=project,
                    query=query,
                    memory_limit=max(1, memory_limit),
                    embed_model=embed_model,
                )

    fact_type_by_id = {int(item["id"]): str(item.get("fact_type") or "") for item in semantic_facts}
    ranked_semantic_hits, semantic_debug = _rank_semantic_hits(
        semantic_hits,
        memory_limit=max(1, memory_limit),
        fact_type_by_id=fact_type_by_id,
    )

    related_facts, facts_debug = _merge_facts(
        structured_facts,
        semantic_facts,
        ranked_semantic_hits,
        facts_limit=max(1, facts_limit),
    )
    related_runs, runs_debug = _merge_runs(
        structured_runs,
        semantic_runs,
        ranked_semantic_hits,
        facts_limit=max(1, facts_limit),
    )

    summary = _build_summary(
        query=query,
        facts=related_facts,
        runs=related_runs,
        mode=mode,
        semantic_warn=semantic_warning,
    )

    gap_reason, gap_context = _detect_knowledge_gap(
        query=query,
        mode=mode,
        related_facts=related_facts,
        related_runs=related_runs,
        semantic_hits=ranked_semantic_hits,
        semantic_warning=semantic_warning,
    )
    if gap_reason:
        log_knowledge_gap(query=query, reason=gap_reason, context=gap_context, source="project_brain_query")

    return {
        "status": "ok",
        "project": project,
        "query": query,
        "mode": mode,
        "filters": {
            "fact_type": fact_type,
            "fact_status": fact_status,
            "component": component,
        },
        "limits": {
            "facts_limit": facts_limit,
            "memory_limit": memory_limit,
        },
        "related_facts": related_facts[: max(1, facts_limit)],
        "related_runs": related_runs[: max(1, facts_limit)],
        "semantic_hits": ranked_semantic_hits[: max(1, memory_limit)],
        "semantic_warning": semantic_warning,
        "summary": summary,
        "memory_types_detected": sorted(
            {str(item.get("memory_type") or _canonical_memory_type(item.get("source_type"))) for item in ranked_semantic_hits}
        ),
        **(
            {"ranking_debug": (facts_debug + runs_debug + semantic_debug)}
            if debug_ranking
            else {}
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta da memoria operacional do projeto (Project Brain)")
    parser.add_argument("--project", default="livecopilot", help="nome do projeto")
    parser.add_argument("--query", required=True, help="pergunta ou query livre")
    parser.add_argument(
        "--mode",
        default="hybrid",
        choices=["structured", "semantic", "hybrid"],
        help="modo de consulta",
    )
    parser.add_argument("--facts-limit", type=int, default=10, help="limite de facts relacionados")
    parser.add_argument("--memory-limit", type=int, default=8, help="limite de hits semanticos")
    parser.add_argument("--format", default="text", choices=["text", "json"], help="formato de saida")
    parser.add_argument("--fact-type", default=None, help="filtro opcional por fact_type")
    parser.add_argument("--fact-status", default=None, help="filtro opcional por fact_status")
    parser.add_argument("--component", default=None, help="filtro opcional por component")
    parser.add_argument(
        "--debug-ranking",
        action="store_true",
        help="inclui score original, pesos e score final para auditoria de ranking",
    )
    parser.add_argument(
        "--embed-model",
        default=os.getenv("SEMANTIC_EMBED_MODEL", "text-embedding-3-small"),
        help="modelo de embedding para modo semantic/hybrid",
    )

    args = parser.parse_args()

    try:
        payload = query_project_brain(
            project=_norm(args.project) or "livecopilot",
            query=_norm(args.query),
            mode=args.mode,
            facts_limit=max(1, int(args.facts_limit)),
            memory_limit=max(1, int(args.memory_limit)),
            fact_type=_norm(args.fact_type) if args.fact_type else None,
            fact_status=_norm(args.fact_status) if args.fact_status else None,
            component=_norm(args.component) if args.component else None,
            embed_model=_norm(args.embed_model) or "text-embedding-3-small",
            debug_ranking=bool(args.debug_ranking),
        )

        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(_render_text(payload))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
