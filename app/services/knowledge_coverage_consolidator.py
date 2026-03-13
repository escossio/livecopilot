import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COVERAGE_DIR = PROJECT_ROOT / "docs" / "coverage"

DOMAIN_ARTIFACTS = {
    "aws_iam": {
        "name": "AWS IAM",
        "compare": "semantic_coverage_audit_iam_compare_after_aws5_20260311.json",
        "persist": "semantic_persist_aws5_validation_20260311.json",
    },
    "docker": {
        "name": "Docker",
        "compare": "semantic_coverage_audit_docker_compare_before_after_20260312.json",
        "persist": "semantic_persist_docker79_validation_20260312.json",
    },
    "terraform": {
        "name": "Terraform",
        "compare": "semantic_coverage_audit_terraform_compare_before_after_20260312.json",
        "persist": "semantic_persist_terraform43_validation_20260312.json",
    },
    "observability": {
        "name": "Observability",
        "compare": "semantic_coverage_audit_observability_compare_before_after_20260312.json",
        "persist": "semantic_persist_observability35_validation_20260312.json",
    },
    "kubernetes": {
        "name": "Kubernetes",
        "compare": "semantic_coverage_audit_kubernetes_compare_before_after_20260312T154518Z.json",
        "persist": "kubernetes_semantic_persist_validation_20260312T154518Z.json",
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}
    return {}


def _zero_aggregate() -> dict[str, Any]:
    return {
        "well_covered_count": 0,
        "partial_count": 0,
        "gap_count": 0,
        "global_avg_of_max_score": 0.0,
        "global_avg_of_avg_score": 0.0,
    }


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _class_to_bucket(label: str) -> str:
    normalized = str(label or "").strip().lower()
    if normalized in {"bem_coberta", "well", "well_covered"}:
        return "well"
    if normalized in {"parcial", "partial"}:
        return "partial"
    return "gap"


def _aggregate_from_rows(rows: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    agg = _zero_aggregate()
    if not rows:
        return agg

    max_scores: list[float] = []
    avg_scores: list[float] = []
    for row in rows:
        cls = _class_to_bucket(str(row.get(f"{prefix}_classification", "")))
        if cls == "well":
            agg["well_covered_count"] += 1
        elif cls == "partial":
            agg["partial_count"] += 1
        else:
            agg["gap_count"] += 1
        max_scores.append(_to_float(row.get(f"{prefix}_max_score", 0.0)))
        avg_scores.append(_to_float(row.get(f"{prefix}_avg_score", 0.0)))

    agg["global_avg_of_max_score"] = round(sum(max_scores) / len(max_scores), 6)
    agg["global_avg_of_avg_score"] = round(sum(avg_scores) / len(avg_scores), 6)
    return agg


def _extract_before_after(compare_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    notes: dict[str, Any] = {}

    if isinstance(compare_payload.get("before_aggregate"), dict) and isinstance(compare_payload.get("after_aggregate"), dict):
        before = compare_payload.get("before_aggregate", _zero_aggregate())
        after = compare_payload.get("after_aggregate", _zero_aggregate())
        delta = compare_payload.get("aggregate_delta") if isinstance(compare_payload.get("aggregate_delta"), dict) else {}
        if not delta:
            delta = {
                "well_covered_count": int(after.get("well_covered_count", 0)) - int(before.get("well_covered_count", 0)),
                "partial_count": int(after.get("partial_count", 0)) - int(before.get("partial_count", 0)),
                "gap_count": int(after.get("gap_count", 0)) - int(before.get("gap_count", 0)),
                "global_avg_of_max_score": round(
                    _to_float(after.get("global_avg_of_max_score")) - _to_float(before.get("global_avg_of_max_score")), 6
                ),
                "global_avg_of_avg_score": round(
                    _to_float(after.get("global_avg_of_avg_score")) - _to_float(before.get("global_avg_of_avg_score")), 6
                ),
            }
        return before, after, delta, notes

    if isinstance(compare_payload.get("aggregate_after"), dict):
        rows = [row for row in compare_payload.get("rows", []) if isinstance(row, dict)]
        comparable_rows = [row for row in rows if bool(row.get("before_available"))]
        before = _aggregate_from_rows(comparable_rows, "before")
        after = _aggregate_from_rows(comparable_rows, "after")
        delta = {
            "well_covered_count": int(after.get("well_covered_count", 0)) - int(before.get("well_covered_count", 0)),
            "partial_count": int(after.get("partial_count", 0)) - int(before.get("partial_count", 0)),
            "gap_count": int(after.get("gap_count", 0)) - int(before.get("gap_count", 0)),
            "global_avg_of_max_score": round(
                _to_float(after.get("global_avg_of_max_score")) - _to_float(before.get("global_avg_of_max_score")), 6
            ),
            "global_avg_of_avg_score": round(
                _to_float(after.get("global_avg_of_avg_score")) - _to_float(before.get("global_avg_of_avg_score")), 6
            ),
        }
        notes["subset_mode"] = True
        notes["comparable_questions"] = len(comparable_rows)
        notes["total_questions_after"] = int(compare_payload.get("aggregate_after", {}).get("total_questions", len(rows)))
        return before, after, delta, notes

    return _zero_aggregate(), _zero_aggregate(), _zero_aggregate(), {"error": "unsupported_compare_schema"}


def _gain_classification(before: dict[str, Any], after: dict[str, Any], delta: dict[str, Any], notes: dict[str, Any]) -> str:
    comparable_questions = int(notes.get("comparable_questions", 0) or 0)
    if notes.get("subset_mode") and comparable_questions <= 1:
        if _to_float(delta.get("global_avg_of_max_score", 0.0)) > 0:
            return "inconclusivo_com_sinal_positivo"
        return "inconclusivo"

    before_gap = int(before.get("gap_count", 0) or 0)
    after_gap = int(after.get("gap_count", 0) or 0)
    delta_max = _to_float(delta.get("global_avg_of_max_score", 0.0))

    if before_gap > 0 and after_gap == 0 and delta_max >= 0.1:
        return "estrutural_forte"
    if before_gap > after_gap and delta_max >= 0.05:
        return "estrutural"
    if delta_max >= 0.03:
        return "marginal_positivo"
    if delta_max <= -0.03:
        return "regressao"
    return "estavel"


def build_consolidated_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    for domain_id, meta in DOMAIN_ARTIFACTS.items():
        compare_path = COVERAGE_DIR / meta["compare"]
        persist_path = COVERAGE_DIR / meta["persist"]

        compare = _read_json(compare_path)
        persist = _read_json(persist_path)

        before, after, delta, notes = _extract_before_after(compare)

        docs_selected = int(
            persist.get("documents_selected")
            or persist.get("source_files_count_requested")
            or persist.get("sources_total")
            or (persist.get("persist_summary", {}).get("documents_selected") if isinstance(persist.get("persist_summary"), dict) else 0)
            or 0
        )
        chunks_persisted = int(
            persist.get("chunks_persisted")
            or (persist.get("persist_summary", {}).get("chunks_persisted") if isinstance(persist.get("persist_summary"), dict) else 0)
            or 0
        )

        row = {
            "domain": domain_id,
            "domain_name": meta["name"],
            "documents_selected": docs_selected,
            "chunks_persisted": chunks_persisted,
            "before": {
                "well": int(before.get("well_covered_count", 0) or 0),
                "partial": int(before.get("partial_count", 0) or 0),
                "gap": int(before.get("gap_count", 0) or 0),
                "avg_max": round(_to_float(before.get("global_avg_of_max_score", 0.0)), 6),
                "avg_avg": round(_to_float(before.get("global_avg_of_avg_score", 0.0)), 6),
            },
            "after": {
                "well": int(after.get("well_covered_count", 0) or 0),
                "partial": int(after.get("partial_count", 0) or 0),
                "gap": int(after.get("gap_count", 0) or 0),
                "avg_max": round(_to_float(after.get("global_avg_of_max_score", 0.0)), 6),
                "avg_avg": round(_to_float(after.get("global_avg_of_avg_score", 0.0)), 6),
            },
            "delta": {
                "well": int(delta.get("well_covered_count", 0) or 0),
                "partial": int(delta.get("partial_count", 0) or 0),
                "gap": int(delta.get("gap_count", 0) or 0),
                "avg_max": round(_to_float(delta.get("global_avg_of_max_score", 0.0)), 6),
                "avg_avg": round(_to_float(delta.get("global_avg_of_avg_score", 0.0)), 6),
            },
            "gain_classification": _gain_classification(before, after, delta, notes),
            "notes": notes,
            "artifact_refs": {
                "compare": str(compare_path.relative_to(PROJECT_ROOT)),
                "persist": str(persist_path.relative_to(PROJECT_ROOT)),
            },
        }
        rows.append(row)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consolidated_domain_comparison",
        "domains": rows,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Consolidated report for IAM/Docker/Terraform/Observability rounds")
    parser.add_argument(
        "--output",
        default=str(COVERAGE_DIR / "domain_coverage_consolidated_20260312.json"),
        help="output json path",
    )
    parser.add_argument("--pretty", action="store_true", help="pretty print output")
    args = parser.parse_args()

    payload = build_consolidated_report()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (PROJECT_ROOT / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"status": "ok", "output": str(output_path), "domain_count": len(payload.get("domains", []))}, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()
