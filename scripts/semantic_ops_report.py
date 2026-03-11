#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


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


def _run_json_script(cmd: list[str]) -> dict:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception:
        return {}
    if proc.returncode != 0:
        return {}
    try:
        data = json.loads((proc.stdout or "").strip())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _extract_tuner_suggestions(output: str) -> list[str]:
    lines = output.splitlines()
    out: list[str] = []
    in_section = False
    for raw in lines:
        line = raw.strip()
        if line == "Sugestoes":
            in_section = True
            continue
        if in_section and line == "Acao":
            break
        if in_section and line.startswith("- "):
            out.append(line)
    return out


def _run_tuner(python_exec: str, tuner_path: Path, telemetry_path: Path, policy_path: Path, eval_path: Path) -> list[str]:
    if not tuner_path.exists():
        return ["- tuner nao encontrado"]
    cmd = [
        python_exec,
        str(tuner_path),
        "--telemetry",
        str(telemetry_path),
        "--policy",
        str(policy_path),
        "--eval",
        str(eval_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as exc:
        return [f"- erro ao executar tuner: {exc}"]
    suggestions = _extract_tuner_suggestions(proc.stdout or "")
    if not suggestions:
        return ["- sem sugestoes parseaveis do tuner nesta execucao"]
    return suggestions


def main() -> int:
    parser = argparse.ArgumentParser(description="Resumo operacional semantico (telemetria + policy + cache)")
    parser.add_argument("--telemetry", default="/lab/projects/livecopilot/var/semantic_telemetry.ndjson")
    parser.add_argument("--policy", default="/lab/projects/livecopilot/config/semantic_policy.json")
    parser.add_argument("--eval", default="/lab/projects/livecopilot/scripts/eval_queries.json")
    parser.add_argument("--telemetry-report", default="/lab/projects/livecopilot/scripts/semantic_telemetry_report.py")
    parser.add_argument("--tuner", default="/lab/projects/livecopilot/scripts/semantic_policy_tuner.py")
    args = parser.parse_args()

    telemetry_path = Path(args.telemetry)
    policy_path = Path(args.policy)
    eval_path = Path(args.eval)
    telemetry_report_path = Path(args.telemetry_report)
    tuner_path = Path(args.tuner)

    policy = _load_json(policy_path)
    telemetry_rows = _load_ndjson(telemetry_path)
    telemetry_report = _run_json_script(
        [sys.executable, str(telemetry_report_path), "--file", str(telemetry_path)]
    )

    semantic_rows = [r for r in telemetry_rows if str(r.get("backend", "")) == "semantic_api"]
    search_hits = sum(1 for r in semantic_rows if bool(r.get("search_cache_hit", False)))
    search_hit_rate = (search_hits / len(semantic_rows) * 100.0) if semantic_rows else 0.0

    tuner_suggestions = _run_tuner(sys.executable, tuner_path, telemetry_path, policy_path, eval_path)

    print("Semantic Ops Report")
    print(f"telemetry_file: {telemetry_path}")
    print(f"policy_file: {policy_path}")
    print(f"eval_file: {eval_path}")

    print("\nPolicy")
    print(f"- relevance_floor: {policy.get('relevance_floor', '-')}")
    print(f"- context_limit: {policy.get('context_limit', '-')}")
    primary = policy.get("domain_signals_primary", [])
    adjacent = policy.get("adjacent_technical_signals", [])
    print(f"- domain_signals_primary_count: {len(primary) if isinstance(primary, list) else 0}")
    print(f"- adjacent_technical_signals_count: {len(adjacent) if isinstance(adjacent, list) else 0}")

    print("\nCache & Telemetry")
    print(f"- total_queries: {telemetry_report.get('total_queries', len(telemetry_rows))}")
    print(f"- semantic_api_rows: {telemetry_report.get('semantic_api', len(semantic_rows))}")
    print(f"- embedding_cache_hit_rate: {float(telemetry_report.get('embedding_cache_hit_rate', 0.0)) * 100:.2f}%")
    print(f"- search_cache_hit_rate: {search_hit_rate:.2f}%")
    print(f"- openai_calls: {telemetry_report.get('openai_calls', 0)}")
    print(f"- estimated_openai_calls_saved: {telemetry_report.get('estimated_openai_calls_saved', 0)}")
    print(f"- avg_semantic_duration_ms: {telemetry_report.get('avg_semantic_duration_ms', 0.0)}")
    print(f"- window_last_ts: {telemetry_report.get('window_last_ts', '')}")

    print("\nTuner Recommendation")
    for item in tuner_suggestions:
        print(item)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
