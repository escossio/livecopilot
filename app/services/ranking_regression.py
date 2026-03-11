import argparse
import json
from typing import Any

from app.services.knowledge_search import search_knowledge_chunks_with_debug
from app.services.question_bank_search import search_question_bank_items_with_debug

FROZEN_CASES: list[dict[str, Any]] = [
    {
        "id": "knowledge_kubectl_namespace",
        "engine": "knowledge",
        "query": "kubectl create namespace",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_source_contains": "Kubernetes Best Practices",
            "top1_practicality_bonus_min": 0.3,
            "top3_any_practicality_signal": ["kubectl"],
        },
    },
    {
        "id": "knowledge_helm_install_chart",
        "engine": "knowledge",
        "query": "helm install chart",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_source_contains": "Mastering Terraform",
            "top3_any_practicality_signal": ["helm"],
            "top3_forbid_practicality_signals": ["terraform-apply"],
        },
    },
    {
        "id": "knowledge_docker_compose_redis",
        "engine": "knowledge",
        "query": "docker compose up redis",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top3_any_source_contains": ["Docker_Deep_Dive", "Docker for Developers"],
            "top3_any_practicality_signal": ["docker-compose"],
        },
    },
    {
        "id": "knowledge_terraform_apply_s3",
        "engine": "knowledge",
        "query": "terraform apply s3 bucket",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_source_contains": "Terraform",
            "top3_any_practicality_signal": ["terraform-apply"],
        },
    },
    {
        "id": "knowledge_fastapi_dependency_injection",
        "engine": "knowledge",
        "query": "fastapi dependency injection",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_source_contains": "FastAPI",
        },
    },
    {
        "id": "question_bank_kubernetes_service_clusterip",
        "engine": "question_bank",
        "query": "kubernetes service clusterip",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_question_id_prefix": "f.services-",
            "top1_inferred_domain": "devops",
            "top1_practicality_bonus_min": 1.5,
        },
    },
    {
        "id": "question_bank_helm_chart_install",
        "engine": "question_bank",
        "query": "helm chart install",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_question_id_prefix": "h.helm-",
            "top1_practicality_bonus_min": 1.4,
        },
    },
    {
        "id": "question_bank_configmap_from_file",
        "engine": "question_bank",
        "query": "configmap from file",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_question_id_prefix": "d.configuration-",
            "top1_practicality_bonus_min": 1.5,
        },
    },
    {
        "id": "question_bank_liveness_probe_nginx",
        "engine": "question_bank",
        "query": "liveness probe nginx",
        "limit": 5,
        "expect": {
            "min_results": 3,
            "top1_question_id_prefix": "e.observability-",
            "top1_inferred_subtheme": "containers",
            "top1_practicality_bonus_min": 1.5,
        },
    },
    {
        "id": "question_bank_fastapi_dependency_injection",
        "engine": "question_bank",
        "query": "fastapi dependency injection",
        "limit": 5,
        "expect": {
            "expected_results": 0,
        },
    },
]


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    engine = str(case.get("engine", "")).strip()
    query = str(case.get("query", "")).strip()
    limit = int(case.get("limit", 5) or 5)
    expect = case.get("expect", {}) if isinstance(case.get("expect"), dict) else {}

    if engine == "knowledge":
        payload = search_knowledge_chunks_with_debug(query, limit=max(1, limit))
        results = payload.get("results", []) if isinstance(payload, dict) else []
    elif engine == "question_bank":
        payload = search_question_bank_items_with_debug(query, limit=max(1, limit))
        results = payload.get("results", []) if isinstance(payload, dict) else []
    else:
        return {
            "id": case.get("id", ""),
            "engine": engine,
            "query": query,
            "ok": False,
            "errors": [f"unsupported engine: {engine}"],
            "result_count": 0,
            "top1": {},
        }

    errors: list[str] = []
    top1 = results[0] if results else {}
    top3 = results[:3]

    min_results = expect.get("min_results")
    if isinstance(min_results, int) and len(results) < min_results:
        errors.append(f"expected min_results={min_results}, got {len(results)}")

    expected_results = expect.get("expected_results")
    if isinstance(expected_results, int) and len(results) != expected_results:
        errors.append(f"expected exact results={expected_results}, got {len(results)}")

    top1_source_contains = expect.get("top1_source_contains")
    if isinstance(top1_source_contains, str):
        source = str(top1.get("source_file", ""))
        if top1_source_contains not in source:
            errors.append(f"top1 source_file missing '{top1_source_contains}' (got '{source}')")

    top3_any_source_contains = expect.get("top3_any_source_contains")
    if isinstance(top3_any_source_contains, list) and top3_any_source_contains:
        sources = [str(item.get("source_file", "")) for item in top3]
        if not any(any(str(needle) in source for needle in top3_any_source_contains) for source in sources):
            errors.append(f"top3 source_file did not match any of {top3_any_source_contains}")

    top1_qid_prefix = expect.get("top1_question_id_prefix")
    if isinstance(top1_qid_prefix, str):
        qid = str(top1.get("question_id", ""))
        if not qid.startswith(top1_qid_prefix):
            errors.append(f"top1 question_id expected prefix '{top1_qid_prefix}', got '{qid}'")

    top1_domain = expect.get("top1_inferred_domain")
    if isinstance(top1_domain, str):
        got_domain = str(top1.get("inferred_domain", ""))
        if got_domain != top1_domain:
            errors.append(f"top1 inferred_domain expected '{top1_domain}', got '{got_domain}'")

    top1_subtheme = expect.get("top1_inferred_subtheme")
    if isinstance(top1_subtheme, str):
        got_subtheme = str(top1.get("inferred_subtheme", ""))
        if got_subtheme != top1_subtheme:
            errors.append(f"top1 inferred_subtheme expected '{top1_subtheme}', got '{got_subtheme}'")

    top1_practicality_bonus_min = expect.get("top1_practicality_bonus_min")
    if isinstance(top1_practicality_bonus_min, (int, float)):
        got_bonus = float(top1.get("practicality_bonus", 0.0) or 0.0)
        if got_bonus < float(top1_practicality_bonus_min):
            errors.append(
                f"top1 practicality_bonus expected >= {top1_practicality_bonus_min}, got {round(got_bonus, 3)}"
            )

    top3_any_signal = expect.get("top3_any_practicality_signal")
    if isinstance(top3_any_signal, list) and top3_any_signal:
        signals = [str(sig) for item in top3 for sig in item.get("practicality_signals", [])]
        if not any(str(needle) in signals for needle in top3_any_signal):
            errors.append(f"top3 practicality_signals missing any of {top3_any_signal}")

    top3_forbid_signals = expect.get("top3_forbid_practicality_signals")
    if isinstance(top3_forbid_signals, list) and top3_forbid_signals:
        present = sorted(
            {
                str(sig)
                for item in top3
                for sig in item.get("practicality_signals", [])
                if str(sig) in {str(s) for s in top3_forbid_signals}
            }
        )
        if present:
            errors.append(f"top3 practicality_signals contains forbidden values: {present}")

    return {
        "id": case.get("id", ""),
        "engine": engine,
        "query": query,
        "ok": len(errors) == 0,
        "errors": errors,
        "result_count": len(results),
        "top1": {
            "source_file": top1.get("source_file", ""),
            "question_id": top1.get("question_id", ""),
            "score": top1.get("score", 0.0),
            "base_score": top1.get("base_score", 0.0),
            "practicality_bonus": top1.get("practicality_bonus", 0.0),
            "practicality_signals": top1.get("practicality_signals", []),
            "inferred_domain": top1.get("inferred_domain", ""),
            "inferred_subtheme": top1.get("inferred_subtheme", ""),
        },
    }


def run_suite() -> dict[str, Any]:
    case_results = [_run_case(case) for case in FROZEN_CASES]
    passed = sum(1 for item in case_results if bool(item.get("ok", False)))
    failed = len(case_results) - passed
    return {
        "suite": "ranking_regression_minimal",
        "total": len(case_results),
        "passed": passed,
        "failed": failed,
        "ok": failed == 0,
        "cases": case_results,
    }


def _print_human(summary: dict[str, Any]) -> None:
    print("ranking_regression_minimal")
    print(
        f"total={summary.get('total', 0)} passed={summary.get('passed', 0)} failed={summary.get('failed', 0)} ok={summary.get('ok', False)}"
    )
    for case in summary.get("cases", []):
        status = "PASS" if case.get("ok", False) else "FAIL"
        print(f"[{status}] {case.get('engine', '')} :: {case.get('query', '')}")
        if not case.get("ok", False):
            for err in case.get("errors", []):
                print(f"  - {err}")


def _main() -> int:
    parser = argparse.ArgumentParser(description="Suite minima de regressao de ranking (knowledge_search + question_bank_search)")
    parser.add_argument("--json", action="store_true", help="Imprime resultado completo em JSON")
    parser.add_argument("--pretty", action="store_true", help="Usa JSON identado quando combinado com --json")
    args = parser.parse_args()

    summary = run_suite()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
    else:
        _print_human(summary)
    return 0 if bool(summary.get("ok", False)) else 1


if __name__ == "__main__":
    raise SystemExit(_main())
