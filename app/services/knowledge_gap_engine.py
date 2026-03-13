import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.semantic_min_api import semantic_search

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "auditable_domains.json"
DEFAULT_HISTORICAL_AUDITS = [
    PROJECT_ROOT / "docs" / "coverage" / "semantic_coverage_audit_aws_iam_after_20260312.json",
    PROJECT_ROOT / "docs" / "coverage" / "semantic_coverage_audit_iam_after_aws5_20260311.json",
    PROJECT_ROOT / "docs" / "coverage" / "semantic_coverage_audit_docker_after_20260312.json",
    PROJECT_ROOT / "docs" / "coverage" / "semantic_coverage_audit_terraform_after_20260312.json",
    PROJECT_ROOT / "docs" / "coverage" / "semantic_coverage_audit_observability_after_20260312.json",
]


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {}


def _classify(*, max_score: float, avg_score: float, thresholds: dict[str, Any]) -> str:
    gap_if_max_below = _to_float(thresholds.get("gap_if_max_below", 0.45))
    well_if_max = _to_float(thresholds.get("well_covered_if_max_at_least", 0.6))
    well_if_avg = _to_float(thresholds.get("well_covered_requires_avg_at_least", 0.45))

    if max_score < gap_if_max_below:
        return "lacuna"
    if max_score >= well_if_max and avg_score >= well_if_avg:
        return "bem_coberta"
    return "parcial"


def _load_historical_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in DEFAULT_HISTORICAL_AUDITS:
        payload = _read_json(path)
        if not payload:
            continue

        rows = []
        if isinstance(payload.get("rows"), list):
            rows = payload.get("rows", [])
        elif isinstance(payload.get("results"), list):
            rows = payload.get("results", [])

        for row in rows:
            if not isinstance(row, dict):
                continue
            query = str(row.get("question", "")).strip()
            if not query:
                continue
            key = query.lower()
            if key in index:
                continue

            coverage_class = str(row.get("coverage_class", "") or row.get("classification", "")).strip() or "lacuna"
            results = row.get("results")
            if not isinstance(results, list):
                results = row.get("top_k") if isinstance(row.get("top_k"), list) else []
            raw_top_k = row.get("top_k", 5)
            top_k_value = 5
            if isinstance(raw_top_k, int):
                top_k_value = raw_top_k
            elif isinstance(raw_top_k, list):
                top_k_value = len(raw_top_k)
            else:
                try:
                    top_k_value = int(raw_top_k or 5)
                except Exception:
                    top_k_value = 5

            index[key] = {
                "query": query,
                "top_k": top_k_value,
                "count": int(row.get("count") or row.get("top_k_count") or len(results)),
                "max_score": round(_to_float(row.get("max_score", 0.0)), 6),
                "avg_score": round(_to_float(row.get("avg_score", 0.0)), 6),
                "top_source_file": str(row.get("top_source_file", "")),
                "coverage_class": coverage_class,
                "results": results,
                "fallback_mode": "historical_audit_artifact",
            }
    return index


def _recommend_action(gap_count: int, partial_count: int, avg_max: float) -> str:
    if gap_count > 0:
        return "executar recorte oficial seletivo e ingestao canônica para subtemas com lacuna"
    if partial_count > 0:
        return "expandir recorte direcionado + persistencia semantica incremental"
    if avg_max < 0.62:
        return "auditar qualidade de chunking/queries e reforcar fontes oficiais de alta aderencia"
    return "manter cobertura e monitorar regressao"


def _priority_score(*, weight: float, total: int, gap_count: int, partial_count: int, avg_max: float) -> float:
    if total <= 0:
        return round(100.0 * max(weight, 1.0), 3)
    gap_ratio = gap_count / total
    partial_ratio = partial_count / total
    quality_penalty = max(0.0, 0.6 - avg_max)
    raw = (gap_ratio * 1.0) + (partial_ratio * 0.55) + (quality_penalty * 1.2)
    return round(min(100.0, max(0.0, raw * 100.0 * max(weight, 0.1))), 3)


def _audit_query(
    query: str,
    top_k: int,
    thresholds: dict[str, Any],
    historical_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    try:
        result = semantic_search(query=query, limit=top_k)
    except Exception as exc:
        fallback = historical_index.get(query.lower())
        if fallback:
            out = dict(fallback)
            out["top_k"] = top_k
            out["fallback_reason"] = str(exc)
            return out
        return {
            "query": query,
            "top_k": top_k,
            "count": 0,
            "max_score": 0.0,
            "avg_score": 0.0,
            "top_source_file": "",
            "coverage_class": "lacuna",
            "results": [],
            "error": str(exc),
        }

    rows = result.get("results") if isinstance(result.get("results"), list) else []
    scores = [_to_float(item.get("similarity", 0.0)) for item in rows]
    max_score = max(scores) if scores else 0.0
    avg_score = (sum(scores) / len(scores)) if scores else 0.0
    coverage_class = _classify(max_score=max_score, avg_score=avg_score, thresholds=thresholds)
    top_source_file = str(rows[0].get("source_file", "")) if rows else ""

    return {
        "query": query,
        "top_k": top_k,
        "count": len(rows),
        "max_score": round(max_score, 6),
        "avg_score": round(avg_score, 6),
        "top_source_file": top_source_file,
        "coverage_class": coverage_class,
        "results": rows,
    }


def run_domain_audit(
    *,
    domain: dict[str, Any],
    top_k: int,
    thresholds: dict[str, Any],
    historical_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    domain_id = str(domain.get("id", "")).strip()
    domain_name = str(domain.get("name", domain_id)).strip() or domain_id
    weight = _to_float(domain.get("weight", 1.0))

    subthemes_raw = domain.get("subthemes", [])
    subthemes: dict[str, str] = {}
    if isinstance(subthemes_raw, list):
        for item in subthemes_raw:
            if isinstance(item, dict):
                sub_id = str(item.get("id", "")).strip()
                if sub_id:
                    subthemes[sub_id] = str(item.get("name", sub_id)).strip() or sub_id

    rows: list[dict[str, Any]] = []
    per_subtheme_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "well": 0,
            "partial": 0,
            "gap": 0,
            "avg_max": 0.0,
            "avg_avg": 0.0,
            "query_count": 0,
        }
    )

    queries = domain.get("queries", []) if isinstance(domain.get("queries"), list) else []
    for item in queries:
        if not isinstance(item, dict):
            continue
        query = str(item.get("query", "")).strip()
        if not query:
            continue
        subtheme_id = str(item.get("subtheme", "")).strip()
        audit = _audit_query(query=query, top_k=top_k, thresholds=thresholds, historical_index=historical_index)
        audit["subtheme"] = subtheme_id
        rows.append(audit)

        bucket = per_subtheme_stats[subtheme_id]
        bucket["query_count"] += 1
        bucket["avg_max"] += _to_float(audit.get("max_score", 0.0))
        bucket["avg_avg"] += _to_float(audit.get("avg_score", 0.0))
        cls = str(audit.get("coverage_class", ""))
        if cls == "bem_coberta":
            bucket["well"] += 1
        elif cls == "parcial":
            bucket["partial"] += 1
        else:
            bucket["gap"] += 1

    total = len(rows)
    well_count = sum(1 for row in rows if row.get("coverage_class") == "bem_coberta")
    partial_count = sum(1 for row in rows if row.get("coverage_class") == "parcial")
    gap_count = sum(1 for row in rows if row.get("coverage_class") == "lacuna")

    avg_max = round(sum(_to_float(row.get("max_score", 0.0)) for row in rows) / total, 6) if total else 0.0
    avg_avg = round(sum(_to_float(row.get("avg_score", 0.0)) for row in rows) / total, 6) if total else 0.0

    weak_subthemes = []
    subtheme_rows: list[dict[str, Any]] = []
    for sub_id, stats in per_subtheme_stats.items():
        qcount = int(stats["query_count"] or 0)
        s_avg_max = round((_to_float(stats["avg_max"]) / qcount), 6) if qcount else 0.0
        s_avg_avg = round((_to_float(stats["avg_avg"]) / qcount), 6) if qcount else 0.0
        sub_row = {
            "subtheme": sub_id,
            "name": subthemes.get(sub_id, sub_id),
            "well": int(stats["well"]),
            "partial": int(stats["partial"]),
            "gap": int(stats["gap"]),
            "avg_max": s_avg_max,
            "avg_avg": s_avg_avg,
            "query_count": qcount,
        }
        subtheme_rows.append(sub_row)
        if int(stats["gap"]) > 0 or int(stats["partial"]) > int(stats["well"]):
            weak_subthemes.append(sub_id)

    subtheme_rows.sort(key=lambda x: (-int(x.get("gap", 0)), -int(x.get("partial", 0)), str(x.get("subtheme", ""))))
    weak_subthemes = sorted(set([item for item in weak_subthemes if item]))

    priority_score = _priority_score(
        weight=weight,
        total=total,
        gap_count=gap_count,
        partial_count=partial_count,
        avg_max=avg_max,
    )

    return {
        "domain": domain_id,
        "domain_name": domain_name,
        "weight": weight,
        "subthemes": subtheme_rows,
        "total_queries": total,
        "well": well_count,
        "partial": partial_count,
        "gap": gap_count,
        "avg_max": avg_max,
        "avg_avg": avg_avg,
        "priority_score": priority_score,
        "weak_subthemes": weak_subthemes,
        "recommended_next_action": _recommend_action(gap_count, partial_count, avg_max),
        "rows": rows,
    }


def run_engine(*, config_path: Path, domain_ids: list[str], top_k: int) -> dict[str, Any]:
    cfg = _read_json(config_path)
    default_top_k = int(cfg.get("default_top_k", 5) or 5)
    thresholds = cfg.get("thresholds") if isinstance(cfg.get("thresholds"), dict) else {}
    domains = cfg.get("domains") if isinstance(cfg.get("domains"), list) else []

    selected = []
    domain_filter = {item.strip() for item in domain_ids if item and item.strip()}
    for item in domains:
        if not isinstance(item, dict):
            continue
        d_id = str(item.get("id", "")).strip()
        if not d_id:
            continue
        if domain_filter and d_id not in domain_filter:
            continue
        selected.append(item)

    historical_index = _load_historical_index()
    resolved_top_k = max(1, int(top_k or default_top_k))
    domain_results = [
        run_domain_audit(
            domain=item,
            top_k=resolved_top_k,
            thresholds=thresholds,
            historical_index=historical_index,
        )
        for item in selected
    ]
    domain_results.sort(key=lambda row: (-_to_float(row.get("priority_score", 0.0)), str(row.get("domain", ""))))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "top_k": resolved_top_k,
        "thresholds": thresholds,
        "domains": domain_results,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="knowledge_gap_engine v1")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="auditable domains config")
    parser.add_argument("--domain", action="append", default=[], help="filter by domain id (repeatable)")
    parser.add_argument("--top-k", type=int, default=0, help="top-k per query (defaults to config)")
    parser.add_argument("--output", default="", help="optional output json path")
    parser.add_argument("--pretty", action="store_true", help="pretty print")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (PROJECT_ROOT / config_path).resolve()

    payload = run_engine(config_path=config_path, domain_ids=args.domain, top_k=max(0, int(args.top_k or 0)))

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = (PROJECT_ROOT / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()
