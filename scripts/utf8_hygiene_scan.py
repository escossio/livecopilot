#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _extract_sequence(chunk_id: str, fallback: int) -> int:
    import re

    text = str(chunk_id or "")
    match = re.search(r"::(\d{4})::", text)
    if match:
        return _to_int(match.group(1), fallback)
    return fallback


def _build_dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise ValueError("DSN ausente: configure DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    return dsn


def scan_utf8_hygiene(*, max_affected_rows: int = 200) -> dict[str, Any]:
    dsn = _build_dsn()
    max_rows = max(1, _to_int(max_affected_rows, 200))

    bad_rows: list[dict[str, Any]] = []
    bad_chunks_count = 0
    total_chunks_scanned = 0

    with psycopg.connect(dsn) as conn:
        conn.autocommit = False
        with conn.cursor() as list_cur, conn.cursor() as probe_cur:
            list_cur.execute(
                """
                SELECT c.id, c.document_id, c.chunk_id, c.sequence, d.source_file
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                ORDER BY c.id
                """
            )
            for chunk_pk, document_id, chunk_id, sequence, source_file in list_cur.fetchall():
                total_chunks_scanned += 1
                probe_cur.execute("SAVEPOINT utf8_scan_probe")
                try:
                    probe_cur.execute("SELECT LEFT(content, 180) FROM chunks WHERE id = %s", (chunk_pk,))
                    _ = probe_cur.fetchone()
                except psycopg.errors.CharacterNotInRepertoire as exc:
                    probe_cur.execute("ROLLBACK TO SAVEPOINT utf8_scan_probe")
                    bad_chunks_count += 1
                    if len(bad_rows) < max_rows:
                        bad_rows.append(
                            {
                                "chunk_pk": _to_int(chunk_pk),
                                "document_id": _to_int(document_id),
                                "chunk_id": str(chunk_id or ""),
                                "sequence": _extract_sequence(str(chunk_id or ""), _to_int(sequence)),
                                "source_file": str(source_file or ""),
                                "error": str(exc),
                            }
                        )
                finally:
                    probe_cur.execute("RELEASE SAVEPOINT utf8_scan_probe")

            grouped: dict[str, dict[str, Any]] = {}
            for row in bad_rows:
                source_file = str(row.get("source_file", ""))
                if source_file not in grouped:
                    grouped[source_file] = {
                        "source_file": source_file,
                        "bad_chunks": 0,
                        "example_chunk_ids": [],
                    }
                grouped[source_file]["bad_chunks"] += 1
                if len(grouped[source_file]["example_chunk_ids"]) < 5:
                    grouped[source_file]["example_chunk_ids"].append(str(row.get("chunk_id", "")))

        conn.rollback()

    grouped_rows = sorted(grouped.values(), key=lambda item: (-_to_int(item.get("bad_chunks", 0)), str(item.get("source_file", ""))))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanner": "utf8_hygiene_scan_v1",
        "read_only": True,
        "snippet_probe_sql": "LEFT(content, 180)",
        "total_chunks_scanned": total_chunks_scanned,
        "bad_chunks_count": bad_chunks_count,
        "affected_source_files_count": len(grouped_rows),
        "affected_rows": bad_rows,
        "affected_rows_returned": len(bad_rows),
        "affected_rows_truncated": bool(bad_chunks_count > len(bad_rows)),
        "grouped_by_source_file": grouped_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scanner read-only de higiene UTF-8 para chunks.content")
    parser.add_argument("--max-affected-rows", type=int, default=200, help="limite de linhas detalhadas em affected_rows")
    parser.add_argument("--output", default="", help="caminho opcional para salvar JSON")
    parser.add_argument("--pretty", action="store_true", help="imprime JSON formatado")
    args = parser.parse_args()

    payload = scan_utf8_hygiene(max_affected_rows=max(1, int(args.max_affected_rows or 1)))

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (Path(__file__).resolve().parents[1] / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
