#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FACT_TYPES = {
    "decision",
    "milestone",
    "issue",
    "fix",
    "pending",
    "insight",
    "risk",
    "checkpoint",
    "hypothesis",
    "abandoned_idea",
}

FACT_STATUSES = {"active", "historical", "partial", "abandoned", "superseded"}


def _norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _must_text(args: argparse.Namespace, key: str) -> str:
    value = _norm_text(str(getattr(args, key, "")))
    if not value:
        raise ValueError(f"argumento obrigatorio ausente/vazio: --{key.replace('_', '-')}")
    return value


def _validate_fact(fact: dict[str, Any], idx: int) -> dict[str, Any]:
    fact_type = _norm_text(str(fact.get("fact_type", "")))
    fact_status = _norm_text(str(fact.get("fact_status", "")))
    title = _norm_text(str(fact.get("title", "")))
    body = _norm_text(str(fact.get("body", "")))

    if fact_type not in FACT_TYPES:
        raise ValueError(f"fact[{idx}] fact_type invalido: {fact_type}")
    if fact_status not in FACT_STATUSES:
        raise ValueError(f"fact[{idx}] fact_status invalido: {fact_status}")
    if not title:
        raise ValueError(f"fact[{idx}] title vazio")
    if not body:
        raise ValueError(f"fact[{idx}] body vazio")

    return {
        "fact_type": fact_type,
        "fact_status": fact_status,
        "title": title,
        "body": body,
        "component": _norm_text(str(fact.get("component", ""))),
        "priority": _norm_text(str(fact.get("priority", ""))),
        "source_path": _norm_text(str(fact.get("source_path", ""))),
        "source_section": _norm_text(str(fact.get("source_section", ""))),
    }


def _parse_fact_line(raw: str) -> dict[str, Any]:
    # formato: type|status|title|body|component|priority|source_path|source_section
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 4:
        raise ValueError(
            "--fact exige no minimo 4 campos: "
            "fact_type|fact_status|title|body"
        )
    while len(parts) < 8:
        parts.append("")

    return {
        "fact_type": parts[0],
        "fact_status": parts[1],
        "title": parts[2],
        "body": parts[3],
        "component": parts[4],
        "priority": parts[5],
        "source_path": parts[6],
        "source_section": parts[7],
    }


def _load_facts_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"arquivo de facts nao encontrado: {path}")
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, list):
        raise ValueError("arquivo de facts deve conter uma lista JSON")
    out: list[dict[str, Any]] = []
    for idx, fact in enumerate(parsed, start=1):
        if not isinstance(fact, dict):
            raise ValueError(f"facts_json[{idx}] precisa ser objeto")
        out.append(fact)
    return out


def _canonical_run_key(payload: dict[str, Any]) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return f"run_{digest[:24]}"


def _build_auto_checkpoint_fact(
    summary_short: str,
    checkpoint_path: str,
    status_md_path: str,
) -> dict[str, Any]:
    return {
        "fact_type": "checkpoint",
        "fact_status": "active",
        "title": f"Checkpoint da rodada: {summary_short}",
        "body": (
            "Checkpoint operacional registrado para continuidade. "
            f"Resumo: {summary_short}."
        ),
        "component": "continuity",
        "priority": "high",
        "source_path": checkpoint_path,
        "source_section": status_md_path,
    }


def _build_auto_pending_fact(summary_short: str, checkpoint_path: str) -> dict[str, Any]:
    return {
        "fact_type": "pending",
        "fact_status": "partial",
        "title": "Revisar detalhamento canonico da rodada",
        "body": (
            "Payload gerado em modo semi-automatico. "
            f"Revisar fatos adicionais quando houver mais contexto: {summary_short}."
        ),
        "component": "continuity",
        "priority": "medium",
        "source_path": checkpoint_path,
        "source_section": "auto_generated",
    }


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    project_name = _must_text(args, "project_name")
    session_id = _must_text(args, "session_id")
    actor = _must_text(args, "actor")
    run_type = _must_text(args, "run_type")
    summary_short = _must_text(args, "summary_short")
    summary_full = _must_text(args, "summary_full")
    status_md_path = _must_text(args, "status_md_path")
    checkpoint_path = _must_text(args, "checkpoint_path")

    raw_facts: list[dict[str, Any]] = []
    for raw in args.fact_inline:
        raw_facts.append(_parse_fact_line(raw))

    if args.facts_file:
        raw_facts.extend(_load_facts_file(Path(args.facts_file)))

    facts: list[dict[str, Any]] = []
    auto_flags: list[str] = []

    checkpoint_fact = _build_auto_checkpoint_fact(summary_short, checkpoint_path, status_md_path)
    facts.append(_validate_fact(checkpoint_fact, 1))
    auto_flags.append("checkpoint_fact")

    validated_custom: list[dict[str, Any]] = []
    for idx, fact in enumerate(raw_facts, start=2):
        validated_custom.append(_validate_fact(fact, idx))

    if validated_custom:
        facts.extend(validated_custom)
    else:
        pending_fact = _build_auto_pending_fact(summary_short, checkpoint_path)
        facts.append(_validate_fact(pending_fact, 2))
        auto_flags.append("pending_fact")

    base_for_key = {
        "project_name": project_name,
        "session_id": session_id,
        "actor": actor,
        "run_type": run_type,
        "summary_short": summary_short,
        "summary_full": summary_full,
        "status_md_path": status_md_path,
        "checkpoint_path": checkpoint_path,
        "facts": facts,
    }
    run_key = _canonical_run_key(base_for_key)

    payload = {**base_for_key, "run_key": run_key}

    meta = {
        "run_key": run_key,
        "facts_count": len(facts),
        "auto_facts": auto_flags,
    }
    return payload, meta


def _resolve_output_path(args: argparse.Namespace, run_key: str) -> Path:
    if args.output:
        return Path(args.output)
    out_dir = Path(args.output_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return out_dir / f"{timestamp}_{run_key}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera payload canonico para continuity_ingest")
    parser.add_argument("--project-name", default="livecopilot")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--actor", default="codex")
    parser.add_argument("--run-type", default="implementation")
    parser.add_argument("--summary-short", required=True)
    parser.add_argument("--summary-full", required=True)
    parser.add_argument("--status-md-path", default="STATUS.md")
    parser.add_argument("--checkpoint-path", required=True)
    parser.add_argument(
        "--fact-inline",
        action="append",
        default=[],
        help=(
            "fato inline no formato "
            "fact_type|fact_status|title|body|component|priority|source_path|source_section"
        ),
    )
    parser.add_argument(
        "--facts-file",
        default=None,
        help="arquivo JSON com lista de facts canonicos",
    )
    # Compatibilidade retroativa
    parser.add_argument("--fact", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--facts-json", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=None, help="arquivo de saida do payload")
    parser.add_argument(
        "--output-dir",
        default="docs/continuity/payloads",
        help="diretorio padrao quando --output nao for informado",
    )
    parser.add_argument("--output-path-only", action="store_true", help="imprime apenas o caminho do payload")

    args = parser.parse_args()

    try:
        # Compatibilidade: flags antigas continuam aceitas
        if args.fact:
            args.fact_inline.extend(args.fact)
        if not args.facts_file and args.facts_json:
            args.facts_file = args.facts_json

        payload, meta = build_payload(args)
        out_path = _resolve_output_path(args, meta["run_key"])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if args.output_path_only:
            print(str(out_path))
            return 0

        print(
            json.dumps(
                {
                    "status": "ok",
                    "payload_path": str(out_path),
                    "run_key": meta["run_key"],
                    "facts_count": meta["facts_count"],
                    "auto_facts": meta["auto_facts"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
