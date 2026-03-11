#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.curated_sources import (  # noqa: E402
    build_candidate_review_report,
    promote_source_candidate,
    record_candidate_review_decision,
    register_source_candidate,
)

DECISIONS_FILE = ROOT_DIR / "data" / "external_search_decisions.ndjson"
CURATION_AUDIT_FILE = ROOT_DIR / "data" / "external_persistence_curation.ndjson"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_query(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _load_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _append_ndjson(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _latest_external_decision(query: str) -> dict[str, Any] | None:
    normalized = _normalize_query(query)
    matches = [row for row in _load_ndjson(DECISIONS_FILE) if _normalize_query(str(row.get("query", ""))) == normalized]
    if not matches:
        return None
    return matches[-1]


def _require_allow_external(query: str) -> dict[str, Any]:
    latest = _latest_external_decision(query)
    if latest is None:
        raise ValueError(f"no external decision found for query: {query}")
    decision = str(latest.get("decision", "")).strip()
    if decision != "allow_external_complement":
        raise ValueError(f"external decision is not allowed for query: {query} (decision={decision or 'none'})")
    return latest


def register_external_candidate(
    *,
    query: str,
    title: str,
    artifact_path: str,
    destination: str,
    trust_level: str,
    notes: str,
) -> dict[str, Any]:
    allow_evidence = _require_allow_external(query)
    payload = register_source_candidate(
        title=title,
        source_url="",
        artifact_path=artifact_path,
        source_kind="candidate_resource",
        trust_level=trust_level,
        destination=destination,
        status="candidate",
        parser_hint="markdown_index",
        discovered_from=f"external_decision::{query}",
        notes=notes
        or f"external complement approved at {allow_evidence.get('timestamp', '')}",
        is_strong_evidence=False,
    )
    _append_ndjson(
        CURATION_AUDIT_FILE,
        {
            "timestamp": _now_iso(),
            "action": "register_external_candidate",
            "query": query,
            "candidate_id": payload.get("candidate_id"),
            "destination": destination,
            "trust_level": trust_level,
            "allow_evidence_timestamp": allow_evidence.get("timestamp"),
            "allow_evidence_decision": allow_evidence.get("decision"),
        },
    )
    return payload


def record_review(
    *,
    candidate_id: str,
    decision: str,
    notes: str,
) -> dict[str, Any]:
    payload = record_candidate_review_decision(candidate_id, decision, notes=notes)
    _append_ndjson(
        CURATION_AUDIT_FILE,
        {
            "timestamp": _now_iso(),
            "action": "record_review_decision",
            "candidate_id": candidate_id,
            "decision": decision,
            "notes": notes,
        },
    )
    return payload


def promote(
    *,
    candidate_id: str,
    confirm: bool,
) -> dict[str, Any]:
    payload = promote_source_candidate(candidate_id, confirm=confirm)
    _append_ndjson(
        CURATION_AUDIT_FILE,
        {
            "timestamp": _now_iso(),
            "action": "promote_candidate",
            "candidate_id": candidate_id,
            "promoted_to": payload.get("promoted_to"),
            "promoted_artifact_path": payload.get("promoted_artifact_path"),
            "promoted_at": payload.get("promoted_at"),
        },
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Fluxo minimo de curadoria para persistencia externa (Etapa 11.4).")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Registra candidato local para persistencia externa condicionada ao allow.")
    register.add_argument("--query", required=True)
    register.add_argument("--title", required=True)
    register.add_argument("--artifact-path", required=True)
    register.add_argument("--destination", default="knowledge", choices=["knowledge", "question_bank"])
    register.add_argument("--trust-level", default="medium_trust", choices=["high_trust", "medium_trust"])
    register.add_argument("--notes", default="")

    review = sub.add_parser("review", help="Registra decisao de revisao para candidato.")
    review.add_argument("--candidate-id", required=True)
    review.add_argument("--decision", required=True, choices=["approved", "rejected", "needs_revision"])
    review.add_argument("--notes", default="")

    promote_cmd = sub.add_parser("promote", help="Promove candidato aprovado para persistencia.")
    promote_cmd.add_argument("--candidate-id", required=True)
    promote_cmd.add_argument("--confirm", action="store_true")

    inspect_cmd = sub.add_parser("inspect", help="Inspeciona estado de revisao/promocao do candidato.")
    inspect_cmd.add_argument("--candidate-id", required=True)

    args = parser.parse_args()

    if args.command == "register":
        print(
            json.dumps(
                register_external_candidate(
                    query=args.query,
                    title=args.title,
                    artifact_path=args.artifact_path,
                    destination=args.destination,
                    trust_level=args.trust_level,
                    notes=args.notes,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "review":
        print(
            json.dumps(
                record_review(
                    candidate_id=args.candidate_id,
                    decision=args.decision,
                    notes=args.notes,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "promote":
        print(
            json.dumps(
                promote(
                    candidate_id=args.candidate_id,
                    confirm=bool(args.confirm),
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "inspect":
        print(json.dumps(build_candidate_review_report(args.candidate_id), ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
