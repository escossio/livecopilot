#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
GAPS_FILE = ROOT_DIR / "data" / "knowledge_gaps.ndjson"
DECISIONS_FILE = ROOT_DIR / "data" / "external_search_decisions.ndjson"

INSUFFICIENCY_REASONS = {"empty_result", "low_average_score", "collapsed_diversity"}


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


def _latest_gap_for_query(query: str) -> dict[str, Any] | None:
    normalized = _normalize_query(query)
    matches = [row for row in _load_ndjson(GAPS_FILE) if _normalize_query(str(row.get("query", ""))) == normalized]
    if not matches:
        return None
    return matches[-1]


def decide_external_search(
    *,
    query: str,
    source: str,
    external_source: str | None,
    note: str | None,
) -> dict[str, Any]:
    latest_gap = _latest_gap_for_query(query)
    gap_reason = ""
    if latest_gap:
        context = latest_gap.get("context", {})
        if isinstance(context, dict):
            gap_reason = str(context.get("reason", "")).strip().lower()

    allow_external = bool(latest_gap and gap_reason in INSUFFICIENCY_REASONS)
    decision = "allow_external_complement" if allow_external else "block_external_complement"

    payload = {
        "timestamp": _now_iso(),
        "query": str(query).strip(),
        "source": str(source or "stage11_external_gate").strip() or "stage11_external_gate",
        "decision": decision,
        "criteria": "external_only_after_explicit_local_insufficiency",
        "evidence": {
            "latest_gap_found": bool(latest_gap),
            "latest_gap_timestamp": (latest_gap or {}).get("timestamp"),
            "latest_gap_reason": gap_reason or None,
            "accepted_reasons": sorted(INSUFFICIENCY_REASONS),
        },
        "external_source": (str(external_source).strip() if external_source else None),
        "note": (str(note).strip() if note else None),
    }
    _append_ndjson(DECISIONS_FILE, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate auditavel para acionamento externo complementar (Etapa 11.3).")
    parser.add_argument("--query", required=True, help="query avaliada")
    parser.add_argument("--source", default="stage11_external_gate", help="origem do acionamento")
    parser.add_argument("--external-source", default=None, help="fonte externa pretendida (opcional)")
    parser.add_argument("--note", default=None, help="observacao operacional (opcional)")
    args = parser.parse_args()

    payload = decide_external_search(
        query=args.query,
        source=args.source,
        external_source=args.external_source,
        note=args.note,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
