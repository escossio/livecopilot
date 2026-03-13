from __future__ import annotations

from typing import Any


def classify_baseline(
    *,
    max_score: float,
    avg_score: float,
    gap_if_max_below: float = 0.45,
    well_if_max_at_least: float = 0.60,
    well_if_avg_at_least: float = 0.45,
) -> str:
    if max_score < gap_if_max_below:
        return "lacuna"
    if max_score >= well_if_max_at_least and avg_score >= well_if_avg_at_least:
        return "bem_coberta"
    return "parcial"


def classify_rule_c(
    *,
    max_score: float,
    avg_score: float,
    top1_expected_official: bool,
    gap_if_max_below: float = 0.45,
    baseline_well_if_max_at_least: float = 0.60,
    baseline_well_if_avg_at_least: float = 0.45,
    rule_c_max_at_least: float = 0.55,
    rule_c_avg_at_least: float = 0.50,
) -> str:
    baseline = classify_baseline(
        max_score=max_score,
        avg_score=avg_score,
        gap_if_max_below=gap_if_max_below,
        well_if_max_at_least=baseline_well_if_max_at_least,
        well_if_avg_at_least=baseline_well_if_avg_at_least,
    )
    if baseline != "parcial":
        return baseline
    if max_score >= rule_c_max_at_least and avg_score >= rule_c_avg_at_least and top1_expected_official:
        return "bem_coberta"
    return "parcial"


def summarize_domain(rows: list[dict[str, Any]], class_key: str) -> dict[str, int]:
    return {
        "query_count": len(rows),
        "well": sum(1 for row in rows if row.get(class_key) == "bem_coberta"),
        "partial": sum(1 for row in rows if row.get(class_key) == "parcial"),
        "gap": sum(1 for row in rows if row.get(class_key) == "lacuna"),
    }


def evaluate_guardrails(
    *,
    comparison: dict[str, Any],
    target_domain: str = "terraform",
    non_target_well_gain_cap: int = 1,
    target_domain_gain_min: int = 1,
) -> dict[str, Any]:
    domain_metrics = comparison.get("domain_metrics", [])
    if not isinstance(domain_metrics, list):
        domain_metrics = []

    target = next((row for row in domain_metrics if str(row.get("domain", "")) == target_domain), None)
    target_gain = int(target.get("delta_well", 0)) if isinstance(target, dict) else 0
    non_target_gain = sum(
        max(0, int(row.get("delta_well", 0)))
        for row in domain_metrics
        if str(row.get("domain", "")) != target_domain
    )
    regressions = sum(int(row.get("well_to_partial_regressions", 0)) for row in domain_metrics)
    suspicious = sum(int(row.get("suspicious_promotions_non_official_top1", 0)) for row in domain_metrics)

    checks = [
        {
            "id": "no_well_to_partial_regressions",
            "expected": "0",
            "actual": regressions,
            "pass": regressions == 0,
        },
        {
            "id": "no_non_official_promotions",
            "expected": "0",
            "actual": suspicious,
            "pass": suspicious == 0,
        },
        {
            "id": "non_target_well_gain_cap",
            "expected": f"<={non_target_well_gain_cap}",
            "actual": non_target_gain,
            "pass": non_target_gain <= non_target_well_gain_cap,
        },
        {
            "id": "target_domain_gain_min",
            "expected": f">={target_domain_gain_min}",
            "actual": target_gain,
            "pass": target_gain >= target_domain_gain_min,
        },
    ]
    all_pass = all(bool(item.get("pass")) for item in checks)

    return {
        "target_domain": target_domain,
        "non_target_well_gain": non_target_gain,
        "target_domain_well_gain": target_gain,
        "total_regressions": regressions,
        "suspicious_non_official_promotions": suspicious,
        "checks": checks,
        "all_pass": all_pass,
    }
