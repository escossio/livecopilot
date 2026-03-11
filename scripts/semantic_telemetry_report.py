#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _avg(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatorio de telemetria semantica com foco em hit rate de cache")
    parser.add_argument(
        "--file",
        default="/lab/projects/livecopilot/var/semantic_telemetry.ndjson",
        help="caminho do arquivo NDJSON",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Arquivo nao encontrado: {path}")
        return 1

    records = []
    with path.open("r", encoding="utf-8") as fp:
        for line_no, line in enumerate(fp, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Linha ignorada (JSON invalido): {line_no}")

    total_queries = len(records)
    semantic_api_records = [r for r in records if str(r.get("backend", "")) == "semantic_api"]
    semantic_api = len(semantic_api_records)
    fallback_or_other = total_queries - semantic_api

    cache_hits = sum(1 for r in semantic_api_records if bool(r.get("embedding_cache_hit", False)))
    cache_misses = semantic_api - cache_hits
    hit_rate = (cache_hits / semantic_api) if semantic_api else 0.0

    openai_calls = sum(1 for r in semantic_api_records if bool(r.get("openai_called", False)))
    estimated_openai_calls_saved = cache_hits

    semantic_duration_values = [_safe_int(r.get("semantic_duration_ms"), 0) for r in records]
    duration_cache_hit = [
        _safe_int(r.get("semantic_duration_ms"), 0)
        for r in semantic_api_records
        if bool(r.get("embedding_cache_hit", False))
    ]
    duration_cache_miss = [
        _safe_int(r.get("semantic_duration_ms"), 0)
        for r in semantic_api_records
        if not bool(r.get("embedding_cache_hit", False))
    ]
    context_values = [_safe_int(r.get("context_len"), 0) for r in records]
    result_count_zero = sum(1 for r in records if _safe_int(r.get("result_count"), 0) == 0)
    fallback_used_true = sum(1 for r in records if bool(r.get("fallback_used", False)))

    report = {
        "file": str(path),
        "total_queries": total_queries,
        "semantic_api": semantic_api,
        "fallback_or_other": fallback_or_other,
        "embedding_cache_hits": cache_hits,
        "embedding_cache_misses": cache_misses,
        "embedding_cache_hit_rate": round(hit_rate, 4),
        "openai_calls": openai_calls,
        "estimated_openai_calls_saved": estimated_openai_calls_saved,
        "avg_semantic_duration_ms": round(_avg(semantic_duration_values), 2),
        "avg_duration_ms_cache_hit": round(_avg(duration_cache_hit), 2),
        "avg_duration_ms_cache_miss": round(_avg(duration_cache_miss), 2),
        "avg_context_len": round(_avg(context_values), 2),
        "queries_result_count_zero": result_count_zero,
        "queries_fallback_used_true": fallback_used_true,
    }
    if records:
        report["window_first_ts"] = str(records[0].get("ts", ""))
        report["window_last_ts"] = str(records[-1].get("ts", ""))

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
