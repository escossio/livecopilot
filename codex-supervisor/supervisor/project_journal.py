"""Project-local checkpoint/status journal for target repositories."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

JOURNAL_DIRNAME = ".supervisor"
CHECKPOINTS_SUBDIR = "checkpoints"


def ensure_project_journal_dir(target_project_path: str | Path) -> Path:
    """Ensure project-local journal directories exist inside target project."""
    root = _resolve_target_root(target_project_path)
    journal_dir = _safe_path(root, JOURNAL_DIRNAME)
    checkpoints_dir = _safe_path(root, JOURNAL_DIRNAME, CHECKPOINTS_SUBDIR)
    journal_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    return journal_dir


def append_project_checkpoint(target_project_path: str | Path, record: dict[str, Any]) -> Path:
    """Append one project checkpoint entry as markdown file."""
    root = _resolve_target_root(target_project_path)
    ensure_project_journal_dir(root)
    timestamp_token = _timestamp_token(record.get("timestamp_utc"))
    mode_token = _slug(str(record.get("mode") or "unknown"))
    checkpoint_path = _safe_path(
        root,
        JOURNAL_DIRNAME,
        CHECKPOINTS_SUBDIR,
        f"{timestamp_token}_{mode_token}.md",
    )
    checkpoint_path.write_text(_render_checkpoint_markdown(record), encoding="utf-8")
    return checkpoint_path


def update_or_create_status_md(target_project_path: str | Path, record: dict[str, Any]) -> Path:
    """Prepend a compact supervisor update block to STATUS.md in target project."""
    root = _resolve_target_root(target_project_path)
    status_path = _safe_path(root, "STATUS.md")
    block = _render_status_update_block(record)

    if status_path.exists():
        existing = status_path.read_text(encoding="utf-8").strip()
        if existing:
            content = f"{block}\n\n{existing}\n"
        else:
            content = _render_status_template(block)
    else:
        content = _render_status_template(block)

    status_path.write_text(content, encoding="utf-8")
    return status_path


def _resolve_target_root(target_project_path: str | Path) -> Path:
    root = Path(target_project_path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"target project path not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"target project path is not a directory: {root}")
    return root


def _safe_path(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"refusing to write outside target project: {candidate}"
        ) from exc
    return candidate


def _timestamp_token(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "unknown_time"
    cleaned = re.sub(r"[^0-9A-Za-z]+", "", raw)
    return cleaned[:32] or "unknown_time"


def _slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "unknown"


def _render_checkpoint_markdown(record: dict[str, Any]) -> str:
    summary = _compact_final_output(record.get("final_output"))
    next_step = _safe_inline_text(record.get("next_step"), max_chars=800)
    lines = [
        "# Supervisor Checkpoint",
        "",
        f"- Timestamp UTC: {record.get('timestamp_utc') or 'n/a'}",
        f"- Mode: {record.get('mode') or 'n/a'}",
        f"- Deploy Profile: {record.get('deploy_profile') or 'n/a'}",
        f"- Decision: {record.get('decision') or 'n/a'}",
        f"- Status: {record.get('status') or 'n/a'}",
        f"- Agent Session ID: {record.get('agent_session_id') or 'n/a'}",
        f"- Codex Thread ID: {record.get('codex_thread_id') or 'n/a'}",
        "",
        "## Final Output (resumo curto)",
        "```text",
        summary,
        "```",
        "",
        "## Next Step",
        next_step or "n/a",
    ]

    last_action_link = _safe_inline_text(
        record.get("supervisor_last_action_path"), max_chars=400
    )
    checkpoint_link = _safe_inline_text(
        record.get("supervisor_checkpoint_path"), max_chars=400
    )
    if last_action_link or checkpoint_link:
        lines.extend(
            [
                "",
                "## Supervisor State Links",
                f"- last_action: {last_action_link or 'n/a'}",
                f"- checkpoint: {checkpoint_link or 'n/a'}",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _render_status_update_block(record: dict[str, Any]) -> str:
    summary = _compact_final_output(record.get("final_output"))
    next_step = _safe_inline_text(record.get("next_step"), max_chars=600)
    return "\n".join(
        [
            f"## Supervisor Update ({record.get('timestamp_utc') or 'n/a'})",
            f"- mode: {record.get('mode') or 'n/a'}",
            f"- deploy_profile: {record.get('deploy_profile') or 'n/a'}",
            f"- decision: {record.get('decision') or 'n/a'}",
            f"- status: {record.get('status') or 'n/a'}",
            f"- agent_session_id: {record.get('agent_session_id') or 'n/a'}",
            f"- codex_thread_id: {record.get('codex_thread_id') or 'n/a'}",
            f"- final_output_summary: {summary.replace(chr(10), ' | ')}",
            f"- next_step: {next_step or 'n/a'}",
            f"- supervisor_last_action: {record.get('supervisor_last_action_path') or 'n/a'}",
            f"- supervisor_checkpoint: {record.get('supervisor_checkpoint_path') or 'n/a'}",
        ]
    ).strip()


def _render_status_template(update_block: str) -> str:
    return "\n".join(
        [
            "# STATUS",
            "",
            "Arquivo de status operacional do projeto, atualizado pelo codex-supervisor.",
            "",
            update_block,
            "",
        ]
    )


def _compact_final_output(value: Any, *, max_lines: int = 10, max_chars: int = 1500) -> str:
    text = _redact_secrets(str(value or "").strip())
    if not text:
        return "(empty final output)"
    lines = text.splitlines()
    truncated_lines = lines[:max_lines]
    normalized = [line.strip()[:300] for line in truncated_lines]
    if len(lines) > max_lines:
        normalized.append("... (truncated)")
    compact = "\n".join(normalized).strip()
    if len(compact) > max_chars:
        return compact[:max_chars].rstrip() + "... (truncated)"
    return compact


def _safe_inline_text(value: Any, *, max_chars: int) -> str:
    text = _redact_secrets(str(value or "").strip())
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "... (truncated)"
    return text


def _redact_secrets(text: str) -> str:
    redacted = re.sub(
        r"(?i)\b(openai_api_key|supervisor_api_token)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        text,
    )
    redacted = re.sub(r"(?i)\bbearer\s+[A-Za-z0-9._-]{8,}\b", "Bearer <redacted>", redacted)
    redacted = re.sub(r"\bsk-[A-Za-z0-9]{10,}\b", "sk-<redacted>", redacted)
    return redacted
