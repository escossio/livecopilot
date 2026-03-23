#!/usr/bin/env python3
"""Checagem de regressao contra a baseline protegida do Livecopilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASELINE_PATH = Path("/lab/projects/livecopilot/docs/LIVECOPILOT_GUARDRAIL_BASELINE.md")
DEFAULT_BASELINE_JSON = Path("/lab/projects/livecopilot/docs/LIVECOPILOT_GUARDRAIL_BASELINE.json")


def load_baseline_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    prompts = [
        "Sobre python",
        "No Linux?",
        "o que é docker?",
        "como rodar um container nginx?",
        "docker -> kubernetes -> deploy",
        "responde mais humano",
        "responde mais direto",
        "faz em passo a passo",
        "usa hipótese + teste",
    ]
    baseline = {
        "prompts": prompts,
        "acceptable_labels": ["OK"],
        "must_not_labels": ["FALLBACK_DISFARCADO", "DRIFT_DE_DOMINIO", "IDIOMA_ERRADO"],
        "min_round_health_score": 1.0,
    }
    path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    return baseline


def load_run(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_steps(run: dict) -> dict[str, dict]:
    steps = run.get("steps", [])
    mapping = {}
    for step in steps:
        if isinstance(step, dict):
            question = str(step.get("question", "") or "").strip()
            if question:
                mapping[question] = step
    return mapping


def index_events(run: dict) -> dict[str, dict]:
    events = run.get("newEvents", [])
    mapping = {}
    if not isinstance(events, list):
        return mapping
    for event in events:
        if isinstance(event, dict):
            prompt = str(event.get("query", "") or "").strip()
            if prompt:
                mapping[prompt] = event
    return mapping


def label_of(step: dict) -> str:
    quality = step.get("quality", {}) if isinstance(step, dict) else {}
    if isinstance(quality, dict):
        return str(quality.get("quality_label", "") or "").strip() or "DESCONHECIDO"
    return "DESCONHECIDO"


def build_report(run: dict, baseline: dict) -> dict:
    steps_by_question = index_steps(run)
    events_by_question = index_events(run)
    prompt_reports = []
    failures = []
    ok_count = 0
    protected = baseline.get("prompts", [])
    acceptable = set(baseline.get("acceptable_labels", ["OK"]))
    forbidden = set(baseline.get("must_not_labels", []))
    for prompt in protected:
        step = steps_by_question.get(prompt, {})
        event = events_by_question.get(prompt, {})
        label = str(event.get("quality_label", "") or "").strip() or label_of(step)
        passed = label in acceptable and label not in forbidden
        if passed:
            ok_count += 1
        else:
            failures.append({"prompt": prompt, "label": label, "answer": step.get("answer", ""), "response_preview": event.get("response_preview", "")})
        prompt_reports.append({"prompt": prompt, "label": label, "passed": passed, "answer": step.get("answer", ""), "response_preview": event.get("response_preview", "")})
    total = len(protected) or 1
    round_health_score = round(ok_count / total, 3)
    pass_fail = "PASS" if ok_count == total and round_health_score >= float(baseline.get("min_round_health_score", 1.0)) else "FAIL"
    delta = {
        "protected_prompts": total,
        "ok": ok_count,
        "failures": len(failures),
        "round_health_score": round_health_score,
    }
    return {
        "result": pass_fail,
        "delta": delta,
        "prompts": prompt_reports,
        "failures": failures,
        "baseline": baseline,
        "run_id": run.get("runId", ""),
        "source_run": run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardrail check do Livecopilot")
    parser.add_argument("--run-json", required=True, help="caminho para o JSON da rodada")
    parser.add_argument("--baseline-json", default=str(DEFAULT_BASELINE_JSON), help="caminho para a baseline json")
    parser.add_argument("--output", default="", help="opcional: caminho para salvar a saida")
    args = parser.parse_args()

    baseline = load_baseline_json(Path(args.baseline_json))
    run = load_run(Path(args.run_json))
    report = build_report(run, baseline)

    output_text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    print(output_text)
    return 0 if report["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
