#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg

PROJECT_STATUS_STATE_PATH = Path(__file__).resolve().parents[1] / "docs" / "project_status_state.json"


def _dsn() -> str:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SEMANTIC_PG_DSN") or os.getenv("LIVECOPILOT_DB_DSN")
    if not dsn:
        raise RuntimeError("DSN ausente: defina DATABASE_URL (ou SEMANTIC_PG_DSN/LIVECOPILOT_DB_DSN)")
    return dsn


def _fetch_recent_runs(cur: Any, project: str, limit: int) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT id, run_key, session_id, actor, run_type, summary_short, checkpoint_path, created_at
        FROM project_runs
        WHERE project_name = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (project, max(1, limit)),
    )
    rows = cur.fetchall()
    return [
        {
            "id": int(row[0]),
            "run_key": row[1],
            "session_id": row[2],
            "actor": row[3],
            "run_type": row[4],
            "summary_short": row[5],
            "checkpoint_path": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
        }
        for row in rows
    ]


def _dedupe_facts(rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    facts: list[dict[str, Any]] = []
    for row in rows:
        fact_type = str(row[1])
        title = str(row[3])
        key = (fact_type, title.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        facts.append(
            {
                "id": int(row[0]),
                "fact_type": fact_type,
                "fact_status": str(row[2]),
                "title": title,
                "body": str(row[4]),
                "component": row[5],
                "priority": row[6],
                "source_path": row[7],
                "source_section": row[8],
                "run_id": int(row[9]),
                "run_key": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
            }
        )
    return facts


def _fetch_facts(
    cur: Any,
    project: str,
    fact_types: list[str],
    fact_statuses: list[str],
    limit: int,
) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            f.id,
            f.fact_type,
            f.fact_status,
            f.title,
            f.body,
            f.component,
            f.priority,
            f.source_path,
            f.source_section,
            f.run_id,
            r.run_key,
            f.created_at
        FROM project_facts f
        JOIN project_runs r ON r.id = f.run_id
        WHERE r.project_name = %s
          AND f.fact_type = ANY(%s)
          AND f.fact_status = ANY(%s)
        ORDER BY f.created_at DESC
        LIMIT %s
        """,
        (project, fact_types, fact_statuses, max(1, limit * 4)),
    )
    rows = cur.fetchall()
    deduped = _dedupe_facts(rows)
    return deduped[: max(1, limit)]


def _build_snapshot(project: str, runs_limit: int, facts_limit: int) -> dict[str, Any]:
    with psycopg.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            recent_runs = _fetch_recent_runs(cur, project, runs_limit)
            active_decisions = _fetch_facts(cur, project, ["decision"], ["active"], facts_limit)
            pending_work = _fetch_facts(cur, project, ["pending"], ["active", "partial"], facts_limit)
            active_issues = _fetch_facts(cur, project, ["issue"], ["active", "partial"], facts_limit)
            active_risks = _fetch_facts(cur, project, ["risk"], ["active", "partial"], facts_limit)
            recent_fixes = _fetch_facts(cur, project, ["fix"], ["active", "historical"], facts_limit)
            recent_milestones = _fetch_facts(cur, project, ["milestone"], ["active", "historical"], facts_limit)

    return {
        "status": "ok",
        "project": project,
        "execution_focus": _load_execution_focus(),
        "recent_runs": recent_runs,
        "active_decisions": active_decisions,
        "pending_work": pending_work,
        "active_issues": active_issues,
        "active_risks": active_risks,
        "recent_fixes": recent_fixes,
        "recent_milestones": recent_milestones,
    }


def _load_execution_focus() -> dict[str, Any]:
    try:
        payload = json.loads(PROJECT_STATUS_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(payload, dict):
        return {}

    now_payload = payload.get("now")
    if not isinstance(now_payload, dict):
        now_payload = {}

    drift_risks = payload.get("drift_risks")
    if not isinstance(drift_risks, list):
        drift_risks = []

    return {
        "mission_current": str(payload.get("mission_current", "")).strip(),
        "round_focus": str(payload.get("round_focus", "")).strip(),
        "current_stage": str(now_payload.get("current_stage", "")).strip(),
        "current_blocker": str(now_payload.get("current_blocker", "")).strip(),
        "next_step": str(now_payload.get("next_step", "")).strip(),
        "avoid_now": str(now_payload.get("avoid_now", "")).strip(),
        "drift_risks": [str(item).strip() for item in drift_risks if str(item).strip()],
    }


def _render_fact_lines(facts: list[dict[str, Any]]) -> list[str]:
    if not facts:
        return ["- (none)"]
    lines: list[str] = []
    for fact in facts:
        comp = f" [{fact['component']}]" if fact.get("component") else ""
        pri = f" (priority={fact['priority']})" if fact.get("priority") else ""
        lines.append(f"- {fact['title']}{comp}{pri}")
    return lines


def _render_runs_lines(runs: list[dict[str, Any]]) -> list[str]:
    if not runs:
        return ["- (none)"]
    lines: list[str] = []
    for run in runs:
        lines.append(
            f"- {run['run_key']} | {run['run_type']} | {run['summary_short']}"
        )
    return lines


def _render_text(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("PROJECT CONTINUITY ACTION BRIEF")
    lines.append(f"project: {snapshot['project']}")
    lines.append("")

    focus = snapshot.get("execution_focus", {}) if isinstance(snapshot.get("execution_focus"), dict) else {}
    recent_runs = snapshot.get("recent_runs", [])
    active_issues = snapshot.get("active_issues", [])
    active_risks = snapshot.get("active_risks", [])
    pending_work = snapshot.get("pending_work", [])
    recent_milestones = snapshot.get("recent_milestones", [])

    latest_run = recent_runs[0] if recent_runs else {}
    latest_progress = str(latest_run.get("summary_short", "")).strip() if isinstance(latest_run, dict) else ""
    if not latest_progress and recent_milestones:
        latest_progress = str(recent_milestones[0].get("title", "")).strip()

    blocker = str(focus.get("current_blocker", "")).strip()
    if not blocker and active_issues:
        blocker = str(active_issues[0].get("title", "")).strip()
    elif not blocker and active_risks:
        blocker = str(active_risks[0].get("title", "")).strip()
    elif not blocker and pending_work:
        blocker = str(pending_work[0].get("title", "")).strip()

    lines.append("focus da rodada:")
    lines.append(f"- {focus.get('round_focus', '(nao definido)') or '(nao definido)'}")
    lines.append("etapa atual:")
    lines.append(f"- {focus.get('current_stage', '(nao definido)') or '(nao definido)'}")
    lines.append("ultimo progresso relevante:")
    lines.append(f"- {latest_progress or '(nao identificado)'}")
    lines.append("bloqueio/trava atual:")
    lines.append(f"- {blocker or '(sem bloqueio explicito)'}")
    lines.append("proximo passo recomendado:")
    lines.append(f"- {focus.get('next_step', '(nao definido)') or '(nao definido)'}")
    lines.append("evitar agora:")
    lines.append(f"- {focus.get('avoid_now', '(nao definido)') or '(nao definido)'}")
    lines.append("")

    lines.append("riscos de deriva (top3):")
    drift_risks = focus.get("drift_risks", [])
    if isinstance(drift_risks, list) and drift_risks:
        for risk in drift_risks[:3]:
            lines.append(f"- {risk}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("operational memory (compact):")
    lines.append("recent runs:")
    lines.extend(_render_runs_lines(recent_runs[:3]))
    lines.append("")
    lines.append("active decisions:")
    lines.extend(_render_fact_lines(snapshot["active_decisions"][:3]))
    lines.append("")
    lines.append("pending work:")
    lines.extend(_render_fact_lines(pending_work[:3]))
    lines.append("")
    lines.append("active issues:")
    lines.extend(_render_fact_lines(active_issues[:3]))
    lines.append("")
    lines.append("active risks:")
    lines.extend(_render_fact_lines(active_risks[:3]))
    lines.append("")
    lines.append("recent milestones:")
    lines.extend(_render_fact_lines(recent_milestones[:3]))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera snapshot de continuidade para bootstrap de contexto")
    parser.add_argument("--project", default="livecopilot")
    parser.add_argument("--runs-limit", type=int, default=5)
    parser.add_argument("--facts-limit", type=int, default=10)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--output",
        default=None,
        help="caminho opcional para salvar snapshot em arquivo (txt/json)",
    )
    args = parser.parse_args()

    try:
        snapshot = _build_snapshot(
            project=args.project,
            runs_limit=max(1, args.runs_limit),
            facts_limit=max(1, args.facts_limit),
        )
        rendered = (
            json.dumps(snapshot, ensure_ascii=False, indent=2)
            if args.format == "json"
            else _render_text(snapshot)
        )

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
            print(f"[continuity-bootstrap] snapshot salvo em: {output_path}", file=sys.stderr)

        print(rendered)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
