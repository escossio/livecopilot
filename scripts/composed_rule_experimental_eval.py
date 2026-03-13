#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.semantic_classification_experimental import (
    classify_baseline,
    classify_rule_c,
    evaluate_guardrails,
    summarize_domain,
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid JSON object: {path}")
    return payload


def _resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def _is_enabled(env_var_name: str, cli_flag: bool) -> bool:
    if cli_flag:
        return True
    raw = str(os.getenv(env_var_name, "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_rows_with_classes(rows: list[dict[str, Any]], include_rule_c: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        enriched = dict(row)
        max_score = float(enriched.get("max_score", 0.0) or 0.0)
        avg_score = float(enriched.get("avg_score", 0.0) or 0.0)
        top1_expected_official = bool(enriched.get("top1_expected_official", False))
        enriched["baseline_class"] = classify_baseline(max_score=max_score, avg_score=avg_score)
        if include_rule_c:
            enriched["experimental_rule_c_class"] = classify_rule_c(
                max_score=max_score,
                avg_score=avg_score,
                top1_expected_official=top1_expected_official,
            )
        out.append(enriched)
    return out


def _build_baseline_payload(rows: list[dict[str, Any]], *, generated_at: str, signals_file: str) -> dict[str, Any]:
    domains = sorted({str(row.get("domain", "")) for row in rows if row.get("domain")})
    domain_metrics = []
    for domain in domains:
        drows = [row for row in rows if row.get("domain") == domain]
        baseline = summarize_domain(drows, "baseline_class")
        domain_metrics.append({"domain": domain, "baseline": baseline})
    baseline_global = summarize_domain(rows, "baseline_class")
    return {
        "generated_at": generated_at,
        "signals_file": signals_file,
        "mode": "baseline",
        "baseline_rule": "well if max>=0.60 and avg>=0.45; gap if max<0.45",
        "domains": domains,
        "baseline_global": baseline_global,
        "domain_metrics": domain_metrics,
    }


def _build_rule_c_payload(rows: list[dict[str, Any]], *, generated_at: str, signals_file: str) -> dict[str, Any]:
    domains = sorted({str(row.get("domain", "")) for row in rows if row.get("domain")})
    domain_metrics = []
    for domain in domains:
        drows = [row for row in rows if row.get("domain") == domain]
        exp = summarize_domain(drows, "experimental_rule_c_class")
        domain_metrics.append({"domain": domain, "experimental_rule_c": exp})
    exp_global = summarize_domain(rows, "experimental_rule_c_class")
    return {
        "generated_at": generated_at,
        "signals_file": signals_file,
        "mode": "rule_c",
        "experimental_rule_c": "baseline OR (max>=0.55 and avg>=0.50 and top1_expected_official)",
        "domains": domains,
        "experimental_global": exp_global,
        "domain_metrics": domain_metrics,
    }


def _build_compare_payload(rows: list[dict[str, Any]], *, generated_at: str, signals_file: str) -> dict[str, Any]:
    domains = sorted({str(row.get("domain", "")) for row in rows if row.get("domain")})
    domain_metrics = []
    for domain in domains:
        drows = [row for row in rows if row.get("domain") == domain]
        baseline = summarize_domain(drows, "baseline_class")
        experimental = summarize_domain(drows, "experimental_rule_c_class")
        partial_to_well = sum(
            1
            for row in drows
            if row.get("baseline_class") == "parcial" and row.get("experimental_rule_c_class") == "bem_coberta"
        )
        well_to_partial = sum(
            1
            for row in drows
            if row.get("baseline_class") == "bem_coberta" and row.get("experimental_rule_c_class") == "parcial"
        )
        suspicious_promotions = sum(
            1
            for row in drows
            if row.get("baseline_class") == "parcial"
            and row.get("experimental_rule_c_class") == "bem_coberta"
            and not bool(row.get("top1_expected_official", False))
        )
        promoted_queries = [
            {
                "query": row.get("query", ""),
                "max_score": row.get("max_score", 0.0),
                "avg_score": row.get("avg_score", 0.0),
                "top1_source_file": row.get("top1_source_file", ""),
            }
            for row in drows
            if row.get("baseline_class") == "parcial" and row.get("experimental_rule_c_class") == "bem_coberta"
        ]
        domain_metrics.append(
            {
                "domain": domain,
                "baseline": baseline,
                "experimental_rule_c": experimental,
                "delta_well": experimental["well"] - baseline["well"],
                "partial_to_well": partial_to_well,
                "well_to_partial_regressions": well_to_partial,
                "suspicious_promotions_non_official_top1": suspicious_promotions,
                "promoted_queries": promoted_queries,
            }
        )

    baseline_global = summarize_domain(rows, "baseline_class")
    experimental_global = summarize_domain(rows, "experimental_rule_c_class")
    return {
        "generated_at": generated_at,
        "signals_file": signals_file,
        "mode": "compare",
        "domains": domains,
        "baseline_rule": "well if max>=0.60 and avg>=0.45; gap if max<0.45",
        "experimental_rule_c": "baseline OR (max>=0.55 and avg>=0.50 and top1_expected_official)",
        "baseline_global": baseline_global,
        "experimental_global": experimental_global,
        "global_delta": {
            "well": experimental_global["well"] - baseline_global["well"],
            "partial": experimental_global["partial"] - baseline_global["partial"],
            "gap": experimental_global["gap"] - baseline_global["gap"],
        },
        "domain_metrics": domain_metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline experimental evaluation for composed Rule C.")
    parser.add_argument(
        "--mode",
        choices=["baseline", "rule_c", "compare", "guardrails"],
        default="baseline",
        help="Execution mode. Default keeps baseline behavior only.",
    )
    parser.add_argument(
        "--signals-file",
        default="",
        help="Path to consolidated signals JSON. Required for baseline/rule_c/compare.",
    )
    parser.add_argument(
        "--comparison-file",
        default="",
        help="Path to comparison JSON generated in compare mode. Required for guardrails mode.",
    )
    parser.add_argument(
        "--output-prefix",
        default="docs/coverage/rule_c_experimental",
        help="Output prefix relative to project root.",
    )
    parser.add_argument(
        "--enable-rule-c",
        action="store_true",
        help="Explicitly enable Rule C in rule_c/compare modes.",
    )
    parser.add_argument(
        "--experimental-env-var",
        default="LIVECOPILOT_EXPERIMENTAL_RULE_C",
        help="Environment variable name used as experimental feature flag.",
    )
    parser.add_argument("--target-domain", default="terraform")
    parser.add_argument("--non-target-well-gain-cap", type=int, default=1)
    parser.add_argument("--target-domain-gain-min", type=int, default=1)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_prefix = _resolve_path(args.output_prefix)

    if args.mode == "guardrails":
        if not args.comparison_file:
            raise ValueError("--comparison-file is required in guardrails mode")
        comparison_path = _resolve_path(args.comparison_file)
        comparison = _read_json(comparison_path)
        guardrails_core = evaluate_guardrails(
            comparison=comparison,
            target_domain=args.target_domain,
            non_target_well_gain_cap=max(0, int(args.non_target_well_gain_cap)),
            target_domain_gain_min=max(0, int(args.target_domain_gain_min)),
        )
        guardrails = {"generated_at": generated_at, "rule_under_test": "Rule C experimental", **guardrails_core}
        if guardrails["all_pass"]:
            decision_label = "rule_c_ready_for_promotion_preparation"
            recommendation = (
                "Regra C passa guardrails; preparar PR experimental com bateria ampliada antes de promover."
            )
        elif int(guardrails["target_domain_well_gain"]) <= 0:
            decision_label = "rule_c_not_worth_promotion"
            recommendation = "Regra C nao melhora dominio alvo; manter baseline."
        else:
            decision_label = "rule_c_keep_experimental_only"
            recommendation = "Regra C melhora parcialmente, mas falha guardrails; manter em experimento."
        decision = {
            "generated_at": generated_at,
            "decision": decision_label,
            "target_domain": args.target_domain,
            "terraform_delta_well": guardrails["target_domain_well_gain"],
            "non_target_well_gain": guardrails["non_target_well_gain"],
            "total_regressions": guardrails["total_regressions"],
            "suspicious_non_official_promotions": guardrails["suspicious_non_official_promotions"],
            "guardrails_all_pass": guardrails["all_pass"],
            "recommendation": recommendation,
        }
        guardrails_path = Path(f"{output_prefix}_guardrails_{generated_at}.json")
        decision_path = Path(f"{output_prefix}_decision_{generated_at}.json")
        _write_json(guardrails_path, guardrails)
        _write_json(decision_path, decision)
        summary = {
            "mode": "guardrails",
            "comparison_file": str(comparison_path.relative_to(PROJECT_ROOT)),
            "guardrails_file": str(guardrails_path.relative_to(PROJECT_ROOT)),
            "decision_file": str(decision_path.relative_to(PROJECT_ROOT)),
            "decision": decision_label,
            "guardrails_all_pass": guardrails["all_pass"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    if not args.signals_file:
        raise ValueError("--signals-file is required in baseline/rule_c/compare modes")
    signals_path = _resolve_path(args.signals_file)
    payload = _read_json(signals_path)
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("signals file must contain list at 'rows'")

    mode_requires_rule_c = args.mode in {"rule_c", "compare"}
    include_rule_c = mode_requires_rule_c
    if mode_requires_rule_c and not _is_enabled(args.experimental_env_var, args.enable_rule_c):
        raise PermissionError(
            f"Rule C experimental is disabled. Use --enable-rule-c or set {args.experimental_env_var}=1"
        )

    enriched_rows = _build_rows_with_classes(rows, include_rule_c=include_rule_c)
    signals_file_rel = str(signals_path.relative_to(PROJECT_ROOT))

    if args.mode == "baseline":
        baseline_payload = _build_baseline_payload(
            enriched_rows,
            generated_at=generated_at,
            signals_file=signals_file_rel,
        )
        baseline_path = Path(f"{output_prefix}_baseline_only_{generated_at}.json")
        _write_json(baseline_path, baseline_payload)
        summary = {
            "mode": "baseline",
            "baseline_file": str(baseline_path.relative_to(PROJECT_ROOT)),
            "well": baseline_payload["baseline_global"]["well"],
            "partial": baseline_payload["baseline_global"]["partial"],
            "gap": baseline_payload["baseline_global"]["gap"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    if args.mode == "rule_c":
        rule_c_payload = _build_rule_c_payload(
            enriched_rows,
            generated_at=generated_at,
            signals_file=signals_file_rel,
        )
        rule_c_path = Path(f"{output_prefix}_rule_c_only_{generated_at}.json")
        _write_json(rule_c_path, rule_c_payload)
        summary = {
            "mode": "rule_c",
            "experimental_file": str(rule_c_path.relative_to(PROJECT_ROOT)),
            "well": rule_c_payload["experimental_global"]["well"],
            "partial": rule_c_payload["experimental_global"]["partial"],
            "gap": rule_c_payload["experimental_global"]["gap"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    # compare mode
    comparison_payload = _build_compare_payload(
        enriched_rows,
        generated_at=generated_at,
        signals_file=signals_file_rel,
    )
    comparison_path = Path(f"{output_prefix}_baseline_vs_rule_c_{generated_at}.json")
    _write_json(comparison_path, comparison_payload)

    guardrails_core = evaluate_guardrails(
        comparison=comparison_payload,
        target_domain=args.target_domain,
        non_target_well_gain_cap=max(0, int(args.non_target_well_gain_cap)),
        target_domain_gain_min=max(0, int(args.target_domain_gain_min)),
    )
    guardrails = {"generated_at": generated_at, "rule_under_test": "Rule C experimental", **guardrails_core}
    if guardrails["all_pass"]:
        decision_label = "rule_c_ready_for_promotion_preparation"
        recommendation = "Regra C passa guardrails; preparar PR experimental com bateria ampliada antes de promover."
    elif int(guardrails["target_domain_well_gain"]) <= 0:
        decision_label = "rule_c_not_worth_promotion"
        recommendation = "Regra C nao melhora dominio alvo; manter baseline."
    else:
        decision_label = "rule_c_keep_experimental_only"
        recommendation = "Regra C melhora parcialmente, mas falha guardrails; manter em experimento."
    decision = {
        "generated_at": generated_at,
        "decision": decision_label,
        "target_domain": args.target_domain,
        "terraform_delta_well": guardrails["target_domain_well_gain"],
        "non_target_well_gain": guardrails["non_target_well_gain"],
        "total_regressions": guardrails["total_regressions"],
        "suspicious_non_official_promotions": guardrails["suspicious_non_official_promotions"],
        "guardrails_all_pass": guardrails["all_pass"],
        "recommendation": recommendation,
    }

    guardrails_path = Path(f"{output_prefix}_guardrails_{generated_at}.json")
    decision_path = Path(f"{output_prefix}_decision_{generated_at}.json")
    _write_json(guardrails_path, guardrails)
    _write_json(decision_path, decision)

    summary = {
        "mode": "compare",
        "comparison_file": str(comparison_path.relative_to(PROJECT_ROOT)),
        "guardrails_file": str(guardrails_path.relative_to(PROJECT_ROOT)),
        "decision_file": str(decision_path.relative_to(PROJECT_ROOT)),
        "decision": decision_label,
        "guardrails_all_pass": guardrails["all_pass"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
