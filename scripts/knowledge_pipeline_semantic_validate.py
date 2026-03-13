#!/usr/bin/env python3
import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.knowledge_ingest import load_state
from app.services.semantic_min_api import semantic_search_with_mode
from app.services.source_prefix_resolution import normalize_source_prefixes, resolve_source_files_from_prefixes


ARTIFACT_PREFIX = "knowledge_pipeline_semantic_validate"
GENERIC_QUERY_TOKENS = {
    "handoff",
    "round",
    "selected",
    "docs",
    "doc",
    "content",
    "incremental",
    "operational",
    "validation",
    "report",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json invalido: {path}")
    return payload


def _clean_query_text(source_file: str) -> str:
    stem = Path(source_file).stem
    normalized = re.sub(r"\d{8}T\d{6}Z", " ", stem, flags=re.IGNORECASE)
    normalized = normalized.replace("_", " ").replace("-", " ")
    tokens = [token.lower() for token in normalized.split() if token.strip()]
    filtered = [token for token in tokens if token not in GENERIC_QUERY_TOKENS and len(token) >= 3]
    if filtered:
        return " ".join(filtered[:6])
    if tokens:
        return " ".join(tokens[:6])
    return Path(source_file).name.lower()


def derive_smoke_queries(source_files: list[str], limit: int = 5) -> list[dict[str, Any]]:
    prioritized = sorted(
        {item for item in source_files if item},
        key=lambda item: (item.upper().startswith("HANDOFF_") or "/HANDOFF_" in item.upper(), item),
    )
    queries: list[dict[str, Any]] = []
    seen_queries: set[str] = set()
    for source_file in prioritized:
        query = _clean_query_text(source_file)
        if not query or query in seen_queries:
            continue
        queries.append(
            {
                "query": query,
                "expected_source_file": source_file,
                "derivation": "source_file_stem",
            }
        )
        seen_queries.add(query)
        if len(queries) >= max(1, limit):
            break
    return queries


def _load_queryset(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_queries = payload.get("queries", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_queries, list):
        raise ValueError("queryset invalido: esperado list ou objeto com chave 'queries'")

    queries: list[dict[str, Any]] = []
    for item in raw_queries:
        if isinstance(item, str):
            clean = item.strip()
            if clean:
                queries.append({"query": clean, "expected_source_file": None, "derivation": "queryset_string"})
            continue
        if isinstance(item, dict):
            query = str(item.get("query", "")).strip()
            if not query:
                continue
            queries.append(
                {
                    "query": query,
                    "expected_source_file": str(item.get("expected_source_file") or "").strip() or None,
                    "derivation": str(item.get("derivation") or "queryset_file"),
                }
            )
    return queries


def _source_files_from_run(run_payload: dict[str, Any]) -> list[str]:
    semantic_results = run_payload.get("semantic", {}).get("results", [])
    if not isinstance(semantic_results, list):
        return []
    resolved = []
    for item in semantic_results:
        if not isinstance(item, dict):
            continue
        source_file = str(item.get("source_file", "")).strip()
        if source_file:
            resolved.append(source_file)
    return sorted(set(resolved))


def _starts_with_expected_prefix(source_file: str, prefixes: list[str]) -> bool:
    return any(source_file.startswith(prefix) for prefix in prefixes)


def summarize_semantic_smoke_results(
    *,
    prefixes: list[str],
    results: list[dict[str, Any]],
    top_k: int,
) -> dict[str, Any]:
    total_queries = len(results)
    top1_expected_prefix_count = sum(1 for item in results if item.get("top1_expected_prefix"))
    topk_expected_prefix_count = sum(1 for item in results if item.get("topk_expected_prefix"))
    top1_expected_source_file_count = sum(1 for item in results if item.get("top1_expected_source_file"))
    topk_expected_source_file_count = sum(1 for item in results if item.get("expected_source_file_in_topk"))
    required_top1_expected_source_file_hits = max(1, math.ceil(total_queries / 2)) if total_queries else 0
    semantic_smoke_passed = bool(
        total_queries
        and topk_expected_source_file_count == total_queries
        and top1_expected_source_file_count >= required_top1_expected_source_file_hits
    )
    return {
        "source_prefixes": prefixes,
        "top_k": top_k,
        "total_queries": total_queries,
        "queries_with_results": sum(1 for item in results if item.get("result_count", 0) > 0),
        "top1_expected_prefix_count": top1_expected_prefix_count,
        "topk_expected_prefix_count": topk_expected_prefix_count,
        "top1_expected_source_file_count": top1_expected_source_file_count,
        "topk_expected_source_file_count": topk_expected_source_file_count,
        "required_top1_expected_source_file_hits": required_top1_expected_source_file_hits,
        "semantic_smoke_passed": semantic_smoke_passed,
    }


def _search_within_scope(
    *,
    query: str,
    source_files: list[str],
    top_k: int,
    embedding_mode: str,
) -> dict[str, Any]:
    ranked: list[dict[str, Any]] = []
    semantic_paths: list[str] = []
    search_cache_hit = False
    embedding_cache_hit = False
    total_duration_ms = 0

    for source_file in source_files:
        payload = semantic_search_with_mode(
            query=query,
            limit=1,
            source_file=source_file,
            embedding_mode=embedding_mode,
        )
        semantic_paths.append(str(payload.get("semantic_path", "")))
        search_cache_hit = search_cache_hit or bool(payload.get("search_cache_hit", False))
        embedding_cache_hit = embedding_cache_hit or bool(payload.get("embedding_cache_hit", False))
        total_duration_ms += int(payload.get("semantic_duration_ms", 0) or 0)
        results = payload.get("results", [])
        if not isinstance(results, list) or not results:
            continue
        best = dict(results[0])
        best["source_file"] = source_file
        ranked.append(best)

    ranked.sort(key=lambda item: float(item.get("similarity", 0.0) or 0.0), reverse=True)
    return {
        "results": ranked[:top_k],
        "semantic_path": "round_scope_only",
        "semantic_paths_observed": sorted(set(path for path in semantic_paths if path)),
        "search_cache_hit": search_cache_hit,
        "embedding_cache_hit": embedding_cache_hit,
        "semantic_duration_ms": total_duration_ms,
    }


def build_semantic_validation_artifact(
    *,
    round_id: str,
    artifact_dir: Path,
    source_prefixes: list[str],
    queryset_file: Path | None,
) -> dict[str, Any]:
    normalized_prefixes = normalize_source_prefixes(source_prefixes)
    run_artifact = artifact_dir / f"knowledge_pipeline_run_{round_id}.json"
    if not run_artifact.exists():
        raise FileNotFoundError(f"artefato de run nao encontrado: {run_artifact}")

    run_payload = _load_json(run_artifact)
    run_prefixes = list(run_payload.get("config", {}).get("source_prefixes", []))
    if run_prefixes and run_prefixes != normalized_prefixes:
        raise ValueError(
            f"prefixos divergentes do run artifact: run={run_prefixes} request={normalized_prefixes}"
        )

    source_files = _source_files_from_run(run_payload)
    source_files_by_prefix: dict[str, int] = {}
    if not source_files:
        state = load_state()
        source_files, source_files_by_prefix = resolve_source_files_from_prefixes(state, normalized_prefixes)
    else:
        for prefix in normalized_prefixes:
            source_files_by_prefix[prefix] = sum(1 for item in source_files if item.startswith(prefix))

    if queryset_file is not None:
        queries = _load_queryset(queryset_file)
        query_derivation_mode = "explicit_queryset_file"
    else:
        queries = derive_smoke_queries(source_files)
        query_derivation_mode = "source_file_stem"

    if not queries:
        raise ValueError("nenhuma query de smoke foi derivada para o escopo informado")

    embedding_mode = str(run_payload.get("semantic", {}).get("embedding_mode_used") or "auto").strip().lower()
    if embedding_mode not in {"openai", "mock"}:
        embedding_mode = "auto"

    top_k = 5
    query_results: list[dict[str, Any]] = []
    for query_meta in queries:
        query = str(query_meta.get("query", "")).strip()
        expected_source_file = query_meta.get("expected_source_file")
        payload = _search_within_scope(
            query=query,
            source_files=source_files,
            top_k=top_k,
            embedding_mode=embedding_mode,
        )
        results = payload.get("results", [])
        if not isinstance(results, list):
            results = []
        top1_source_file = str(results[0].get("source_file", "")).strip() if results else ""
        topk_source_files = [str(item.get("source_file", "")).strip() for item in results if str(item.get("source_file", "")).strip()]
        expected_hit_position = None
        if expected_source_file:
            for idx, source_file in enumerate(topk_source_files, start=1):
                if source_file == expected_source_file:
                    expected_hit_position = idx
                    break

        query_results.append(
            {
                "query": query,
                "expected_source_file": expected_source_file,
                "query_derivation": str(query_meta.get("derivation") or query_derivation_mode),
                "result_count": len(results),
                "top1_source_file": top1_source_file,
                "top1_similarity": float(results[0].get("similarity", 0.0)) if results else 0.0,
                "top1_expected_prefix": bool(top1_source_file and _starts_with_expected_prefix(top1_source_file, normalized_prefixes)),
                "top1_expected_source_file": bool(expected_source_file and top1_source_file == expected_source_file),
                "topk_expected_prefix": any(_starts_with_expected_prefix(source_file, normalized_prefixes) for source_file in topk_source_files),
                "expected_source_file_in_topk": expected_hit_position is not None,
                "expected_source_file_hit_position": expected_hit_position,
                "semantic_path": str(payload.get("semantic_path", "")),
                "semantic_paths_observed": payload.get("semantic_paths_observed", []),
                "search_cache_hit": bool(payload.get("search_cache_hit", False)),
                "embedding_cache_hit": bool(payload.get("embedding_cache_hit", False)),
                "semantic_duration_ms": int(payload.get("semantic_duration_ms", 0) or 0),
                "topk": results,
            }
        )

    aggregate = summarize_semantic_smoke_results(prefixes=normalized_prefixes, results=query_results, top_k=top_k)
    artifact = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": "knowledge_pipeline_v2_semantic_validate",
        "mode": "semantic-validate",
        "round_id": round_id,
        "source_prefixes": normalized_prefixes,
        "search_scope": "round_scope_only",
        "query_derivation_mode": query_derivation_mode,
        "queryset_file": str(queryset_file) if queryset_file else "",
        "embedding_mode_used_for_search": embedding_mode,
        "artifacts": {
            "run_artifact": str(run_artifact),
            "semantic_validate_artifact": str(artifact_dir / f"{ARTIFACT_PREFIX}_{round_id}.json"),
        },
        "scope": {
            "source_files_total": len(source_files),
            "source_files_by_prefix": source_files_by_prefix,
            "source_files_sample": source_files[:20],
        },
        "queries": queries,
        "results": query_results,
        "aggregate": aggregate,
        "semantic_smoke_passed": bool(aggregate.get("semantic_smoke_passed", False)),
    }
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic validate V2 for knowledge pipeline rounds.")
    parser.add_argument("--round-id", required=True, help="Round id ja executado no knowledge pipeline.")
    parser.add_argument(
        "--source-prefix",
        action="append",
        default=[],
        help="Prefixo relativo a data/knowledge_raw (repetivel).",
    )
    parser.add_argument(
        "--artifact-dir",
        default=str(ROOT_DIR / "docs" / "coverage"),
        help="Diretorio onde os artefatos da rodada ficam salvos.",
    )
    parser.add_argument(
        "--queryset-file",
        default="",
        help="Arquivo JSON opcional com queryset explicito.",
    )
    args = parser.parse_args()

    prefixes = normalize_source_prefixes(args.source_prefix)
    if not prefixes:
        print("Erro: semantic-validate exige pelo menos um --source-prefix explicito.")
        return 2

    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    queryset_file = Path(args.queryset_file).expanduser() if str(args.queryset_file).strip() else None

    try:
        artifact = build_semantic_validation_artifact(
            round_id=args.round_id,
            artifact_dir=artifact_dir,
            source_prefixes=prefixes,
            queryset_file=queryset_file,
        )
    except Exception as exc:
        print(f"Erro: {exc}")
        return 2

    artifact_path = artifact_dir / f"{ARTIFACT_PREFIX}_{args.round_id}.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
