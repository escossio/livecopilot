"""Prompt templates for supervisor-to-codex communication."""

from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a local supervisor. Operate conservatively and report precisely what you did."
)


def build_agent_instructions(target_project: str, supervisor_home: str) -> str:
    """System instructions for the supervisor Agent."""
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Hard constraints:\n"
        f"- The target project workspace is: {target_project}\n"
        f"- This orchestrator repository is: {supervisor_home}\n"
        "- Do not treat the orchestrator repository as the target workspace.\n"
        "- Keep all supervisor state/log writes inside the orchestrator repository.\n"
        "- In this phase, prefer read-only analysis of the target project.\n"
        "- Avoid destructive or broad edits.\n"
    )


def build_supervisor_task(mission: str, next_step: str, target_project: str) -> str:
    """Build a conservative but operational task that requires MCP tool usage."""
    return (
        "Execute one conservative operational validation round with strict time discipline.\n\n"
        "Mission:\n"
        f"{mission}\n\n"
        "Current next step hint:\n"
        f"{next_step}\n\n"
        "Target project path:\n"
        f"{target_project}\n\n"
        "Mandatory operational checks (must use Codex MCP tools against the target path):\n"
        "1) Execute at most ONE focused read attempt from the next_step hint.\n"
        "2) If this read times out or fails, do not retry the same file in this round.\n"
        "3) In case of failure, try ONE lightweight root-level file as fallback (example: STATUS.md or requirements.txt).\n"
        "4) Report at least one concrete fact from successful file contents with file path.\n"
        "5) Do not edit files in this round.\n"
        "6) Keep this round short; avoid repeated exploratory loops.\n\n"
        "Required output format:\n"
        "1) What you inspected\n"
        "2) Risks/constraints noticed\n"
        "3) Evidence of tool-based inspection (commands/files actually read)\n"
        "4) Proposed next minimal step (single step)\n"
        "Do not perform aggressive edits. If tooling fails, say it explicitly."
    )


def build_continuation_context(
    *,
    mission: str,
    next_step: str,
    target_project: str,
    agent_session_id: str,
    codex_thread_id: str,
    codex_thread_id_status: str,
    codex_thread_id_source: str | None,
    explicit_continue_active: bool,
    continue_contract_mode: str,
) -> str:
    """Build continuation task context using persisted supervisor state."""
    codex_source_text = codex_thread_id_source or "unknown_source"
    continue_mode_text = (
        "explicit_thread_id_first"
        if explicit_continue_active
        else "context_fallback_only"
    )
    return (
        "Continue an existing supervisor run. This is not a new mission.\n\n"
        "Persisted continuity context:\n"
        f"- target_project_path: {target_project}\n"
        f"- agent_session_id (Agents SDK continuity): {agent_session_id}\n"
        f"- codex_thread_id (Codex-side continuity identifier): {codex_thread_id}\n"
        f"- codex_thread_id_status: {codex_thread_id_status}\n"
        f"- codex_thread_id_source: {codex_source_text}\n\n"
        f"- continuation_mode: {continue_mode_text}\n\n"
        f"- continuation_contract_mode: {continue_contract_mode}\n\n"
        "Mission (must continue from prior state, do not restart from zero):\n"
        f"{mission}\n\n"
        "Persisted next step hint from previous run:\n"
        f"{next_step}\n\n"
        "Execution rules:\n"
        "1) Continue from persisted context; do not reset history or redefine the mission.\n"
        "2) Treat agent_session_id and codex_thread_id as different identifiers with different roles.\n"
        "3) Prefer explicit continuation on Codex side via codex_thread_id; use context fallback only if explicit continue is unavailable.\n"
        "4) Use Codex MCP tools conservatively against the target path.\n"
        "5) If continuity is blocked, report exactly what is missing.\n\n"
        "Required output format:\n"
        "1) What was continued from persisted state\n"
        "2) What was inspected now\n"
        "3) Risks/constraints noticed\n"
        "4) Next minimal step"
    )
