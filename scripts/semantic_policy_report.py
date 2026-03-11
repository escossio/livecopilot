#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
from statistics import mean


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_ndjson(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _as_int(value, default=0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(mean(values))


def _extract_tuner_suggestions(text: str) -> list[str]:
    lines = text.splitlines()
    suggestions: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == "Sugestoes":
            in_section = True
            continue
        if in_section and stripped in {"", "Acao"}:
            if stripped == "Acao":
                break
            continue
        if in_section and stripped.startswith("- "):
            suggestions.append(stripped)
    return suggestions


def _run_tuner(python_exec: str, tuner_path: Path, telemetry: Path, policy: Path, eval_path: Path) -> tuple[list[str], str]:
    if not tuner_path.exists():
        return (["- tuner nao encontrado"], "")
    cmd = [
        python_exec,
        str(tuner_path),
        "--telemetry",
        str(telemetry),
        "--policy",
        str(policy),
        "--eval",
        str(eval_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as exc:
        return ([f"- erro ao executar tuner: {exc}"], "")
    output = (proc.stdout or "").strip()
    suggestions = _extract_tuner_suggestions(output)
    if not suggestions:
        suggestions = ["- sem sugestoes parseaveis do tuner nesta execucao"]
    return suggestions, output


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatorio operacional da semantic policy e telemetria")
    parser.add_argument("--policy", default="/lab/projects/livecopilot/config/semantic_policy.json")
    parser.add_argument("--telemetry", default="/lab/projects/livecopilot/var/semantic_telemetry.ndjson")
    parser.add_argument("--eval", default="/lab/projects/livecopilot/scripts/eval_queries.json")
    parser.add_argument("--tuner", default="/lab/projects/livecopilot/scripts/semantic_policy_tuner.py")
    args = parser.parse_args()

    policy_path = Path(args.policy)
    telemetry_path = Path(args.telemetry)
    eval_path = Path(args.eval)
    tuner_path = Path(args.tuner)

    policy = _load_json(policy_path) or {}
    telemetry_rows = _load_ndjson(telemetry_path)

    relevance_floor = policy.get("relevance_floor", "-")
    context_limit = policy.get("context_limit", "-")
    primary = policy.get("domain_signals_primary", []) if isinstance(policy.get("domain_signals_primary", []), list) else []
    adjacent = policy.get("adjacent_technical_signals", []) if isinstance(policy.get("adjacent_technical_signals", []), list) else []

    total = len(telemetry_rows)
    semantic_api = [r for r in telemetry_rows if str(r.get("backend", "")) == "semantic_api"]
    fallback_true = sum(1 for r in telemetry_rows if bool(r.get("fallback_used", False)))
    zero_context = sum(1 for r in telemetry_rows if _as_int(r.get("context_len", 0), 0) == 0)
    zero_results = sum(1 for r in telemetry_rows if _as_int(r.get("result_count", 0), 0) == 0)
    context_len_values = [_as_int(r.get("context_len", 0), 0) for r in telemetry_rows]
    result_count_values = [_as_int(r.get("result_count", 0), 0) for r in telemetry_rows]
    duration_values = [_as_int(r.get("semantic_duration_ms", 0), 0) for r in telemetry_rows]
    embedding_hits = sum(1 for r in semantic_api if bool(r.get("embedding_cache_hit", False)))
    search_hits = sum(1 for r in semantic_api if bool(r.get("search_cache_hit", False)))

    ts_first = str(telemetry_rows[0].get("ts", "")) if telemetry_rows else ""
    ts_last = str(telemetry_rows[-1].get("ts", "")) if telemetry_rows else ""

    tuner_suggestions, _ = _run_tuner(
        sys.executable,
        tuner_path,
        telemetry_path,
        policy_path,
        eval_path,
    )

    print("Semantic Policy Report")
    print(f"policy_file: {policy_path}")
    print(f"telemetry_file: {telemetry_path}")
    print(f"eval_file: {eval_path}")

    print("\nPolicy atual")
    print(f"- relevance_floor: {relevance_floor}")
    print(f"- context_limit: {context_limit}")
    print(f"- domain_signals_primary_count: {len(primary)}")
    print(f"- adjacent_technical_signals_count: {len(adjacent)}")

    print("\nTelemetria (resumo)")
    print(f"- total_rows: {total}")
    print(f"- semantic_api_rows: {len(semantic_api)}")
    print(f"- fallback_used_true: {fallback_true}")
    print(f"- zero_context_rate: {(zero_context / total * 100) if total else 0.0:.2f}%")
    print(f"- zero_result_rate: {(zero_results / total * 100) if total else 0.0:.2f}%")
    print(f"- avg_context_len: {_safe_mean(context_len_values):.2f}")
    print(f"- avg_result_count: {_safe_mean(result_count_values):.2f}")
    print(f"- avg_semantic_duration_ms: {_safe_mean(duration_values):.2f}")
    print(f"- embedding_cache_hit_rate_semantic_api: {(embedding_hits / len(semantic_api) * 100) if semantic_api else 0.0:.2f}%")
    print(f"- search_cache_hit_rate_semantic_api: {(search_hits / len(semantic_api) * 100) if semantic_api else 0.0:.2f}%")
    print(f"- window_first_ts: {ts_first}")
    print(f"- window_last_ts: {ts_last}")

    print("\nRecomendacao atual do tuner")
    for suggestion in tuner_suggestions:
        print(suggestion)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
