import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.services.knowledge_tags import infer_tags
from app.services.question_bank_metadata import infer_question_metadata
from app.services.question_bank_parsers import QUESTION_BANK_ITEMS_DIR, ensure_question_bank_dirs

ITEM_TYPE_MULTIPLE_CHOICE = "multiple_choice"
ITEM_TYPE_OPEN_QUESTION = "open_question"
ITEM_TYPE_CHECKLIST = "checklist"
ITEM_TYPE_EXERCISE = "exercise"
ITEM_TYPE_UNKNOWN = "unknown"

CHOICE_PATTERN = re.compile(r"^\s*(?:[-*]\s+)?([A-Ha-h])[\)\].:-]\s+(.*\S)\s*$")
NUMBERED_PATTERN = re.compile(r"^\s*(\d{1,3})[\)\].:-]\s*(.*\S)?\s*$")
CHECKLIST_PATTERN = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
ANSWER_HINT_PATTERN = re.compile(r"^\s*(?:gabarito|resposta(?:\s+certa)?|answer|answer hint|hint|comentario|explicacao)\s*[:\-]\s*(.*\S)\s*$", re.IGNORECASE)
MARKDOWN_HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+")
MARKDOWN_HEADING_CAPTURE_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s+(.*\S)\s*$")
MARKDOWN_LINK_LIST_PATTERN = re.compile(r"^\s*[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*$")
QUESTION_HEADER_PATTERN = re.compile(r"^\s*(?:new\s+)?question(?:\s*#|\s*:|\s+)\s*\d+\s*$", re.IGNORECASE)
QUESTION_INLINE_PATTERN = re.compile(r"^\s*(?:new\s+)?question(?:\s*#|\s*:|\s+)\s*\d+\s*[:\-]?\s*(.*\S)?\s*$", re.IGNORECASE)
EXAM_CONTEXT_PATTERN = re.compile(
    r"\b("
    r"what\b|which\b|how\b|why\b|when\b|where\b|who\b|select\b|choose\b|true or false\b|"
    r"cite\b|describe\b|explain\b|identify\b|determine\b|implement\b|"
    r"qual\b|quais\b|como\b|por que\b|quando\b|onde\b|quem\b|selecione\b|escolha\b|"
    r"cite\b|descreva\b|explique\b|identifique\b"
    r")",
    re.IGNORECASE,
)
NOISE_PATTERNS = [
    re.compile(r"https?://", re.IGNORECASE),
    re.compile(r"\b(all exams 100% pass|download full version|exam dumps|exam questions|pdf dumps|vce dumps|study guide|testprep|pass rate|full refund|free demo)\b", re.IGNORECASE),
    re.compile(r"\b(braindump2go|killexams|passtorrent)\b", re.IGNORECASE),
    re.compile(r"\b(copyright|all rights reserved|trademarks?)\b", re.IGNORECASE),
]
NOISE_PREFIXES = (
    "vendor:",
    "exam code:",
    "exam name:",
    "version ",
    "visit ",
    "target candidate",
    "recommended aws knowledge",
    "job tasks",
)


def items_output_path(source_file: str) -> Path:
    target_name = "__".join(Path(source_file).parts) + ".items.json"
    return QUESTION_BANK_ITEMS_DIR / target_name


def load_items_payload(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(loaded, dict):
        return loaded
    return None


def write_items_payload(payload: dict) -> Path:
    ensure_question_bank_dirs()
    output_path = items_output_path(payload["source_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", (line or "").strip())


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text or ""))


def _looks_like_noise_line(line: str) -> bool:
    normalized = _normalize_line(line)
    if not normalized:
        return False
    lowered = normalized.lower()
    if lowered.startswith(NOISE_PREFIXES):
        return True
    if all(char in "-_=<>|:.!0123456789 " for char in normalized) and _word_count(normalized) < 3:
        return True
    if lowered.endswith("| page") or re.search(r"\bpage\s+\d+\b", lowered):
        return True
    return any(pattern.search(normalized) for pattern in NOISE_PATTERNS)


def _looks_like_noise_text(text: str) -> bool:
    normalized = _normalize_line(text)
    lowered = normalized.lower()
    if not normalized:
        return False
    if _looks_like_noise_line(normalized):
        return True
    if lowered.count("download") >= 2 or lowered.count("exam questions") >= 2:
        return True
    if lowered.count("www.") >= 2 or len(re.findall(r"\b[a-z0-9.-]+\.[a-z]{2,}\b", lowered)) >= 4:
        return True
    if "customer service" in lowered or "success guaranteed" in lowered:
        return True
    return False


def _has_exam_context(text: str) -> bool:
    normalized = _normalize_line(text)
    return bool(EXAM_CONTEXT_PATTERN.search(normalized))


def _looks_like_question_start(line: str) -> bool:
    normalized = _normalize_line(line)
    if not normalized:
        return False
    if normalized.endswith("?"):
        return True
    if QUESTION_HEADER_PATTERN.match(normalized):
        return True
    numbered_match = NUMBERED_PATTERN.match(normalized)
    if numbered_match:
        remainder = _normalize_line(numbered_match.group(2) or "")
        return bool(remainder and (_has_exam_context(remainder) or remainder.endswith("?") or _word_count(remainder) >= 5))
    inline_match = QUESTION_INLINE_PATTERN.match(normalized)
    if inline_match and _normalize_line(inline_match.group(1) or ""):
        return True
    lowered = normalized.lower()
    return lowered.startswith(("q:", "q.", "question:", "pergunta:", "questao:", "questao ")) or _has_exam_context(normalized)


def _strip_question_prefix(line: str) -> str:
    normalized = _normalize_line(line)
    normalized = re.sub(r"^(?:q[\.:]|question:|pergunta:|questao:)\s*", "", normalized, flags=re.IGNORECASE)
    inline_match = QUESTION_INLINE_PATTERN.match(normalized)
    if inline_match:
        remainder = _normalize_line(inline_match.group(1) or "")
        return remainder
    numbered_match = NUMBERED_PATTERN.match(normalized)
    if numbered_match:
        remainder = _normalize_line(numbered_match.group(2) or "")
        return remainder or normalized
    return normalized


def _empty_item(source_file: str, title: str) -> dict:
    return {
        "source_file": source_file,
        "title": title,
        "prompt_lines": [],
        "choices": [],
        "answer_hint_lines": [],
        "has_checklist_lines": False,
        "has_question_header": False,
        "has_question_mark": False,
        "has_numbering": False,
        "has_exam_context": False,
    }


def _extract_markdown_index_items(source_file: str, title: str, content: str) -> list[dict]:
    raw_lines = [line.rstrip() for line in content.splitlines()]
    intro_lines: list[str] = []
    index_entries: list[dict[str, str]] = []
    in_contents = False
    contents_level = 0

    for raw_line in raw_lines:
        line = _normalize_line(raw_line)
        if not line:
            continue
        heading_match = MARKDOWN_HEADING_CAPTURE_PATTERN.match(raw_line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            heading_text = _normalize_line(heading_match.group(2))
            lowered_heading = heading_text.lower()
            if "contents" in lowered_heading or "table of contents" in lowered_heading:
                in_contents = True
                contents_level = heading_level
                continue
            if in_contents and heading_level <= contents_level:
                break
            if not in_contents and heading_level <= 2:
                continue

        if not in_contents:
            if not _looks_like_noise_line(line) and len(intro_lines) < 4:
                intro_lines.append(line)
            continue

        link_match = MARKDOWN_LINK_LIST_PATTERN.match(raw_line)
        if link_match:
            entry_title = _normalize_line(link_match.group(1))
            entry_target = _normalize_line(link_match.group(2))
            if entry_title:
                index_entries.append({"title": entry_title, "target": entry_target})

    if len(index_entries) < 2:
        return []

    intro_text = " ".join(
        line
        for line in intro_lines
        if line and not line.startswith("#") and "can i pr?" not in line.lower()
    ).strip()

    items: list[dict] = []
    stem = Path(source_file).stem
    for index, entry in enumerate(index_entries, start=1):
        entry_title = entry["title"]
        prompt_parts = [f"Exercise track: {entry_title}."]
        if intro_text:
            prompt_parts.append(intro_text)
        if entry.get("target"):
            prompt_parts.append(f"Source section: {entry['target']}.")
        prompt = " ".join(part for part in prompt_parts if part).strip()
        metadata = infer_question_metadata(
            source_file=source_file,
            title=f"{title} - {entry_title}",
            prompt=prompt,
            choices=[],
            answer_hint="",
        )
        inferred_tags = metadata.get("tags", {})
        items.append(
            {
                "question_id": f"{stem}-{index:03d}",
                "source_file": source_file,
                "title": entry_title,
                "prompt": prompt,
                "choices": [],
                "answer_hint": None,
                "inferred_tags": inferred_tags.get("all", []),
                "inferred_domain": metadata.get("inferred_domain"),
                "inferred_subtheme": metadata.get("inferred_subtheme"),
                "difficulty_hint": metadata.get("difficulty_hint"),
                "item_type": ITEM_TYPE_EXERCISE,
                "metadata_debug": metadata.get("metadata_debug", {}),
                "parsed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return items


def _extract_markdown_lab_items(source_file: str, title: str, content: str) -> list[dict]:
    raw_lines = [line.rstrip() for line in content.splitlines()]
    current_h2 = ""
    current_h3 = ""
    current_block: list[str] = []
    sections: list[tuple[str, str, list[str]]] = []

    def split_sparse_long_heading(exercise_title: str) -> list[str]:
        normalized_title = _normalize_line(exercise_title)
        if _word_count(normalized_title) < 20:
            return [normalized_title]

        clauses = [
            clause.strip(" .")
            for clause in re.split(r"\.\s+", normalized_title)
            if _word_count(clause) >= 4
        ]
        if len(clauses) < 2:
            return [normalized_title]
        if len(clauses) <= 3:
            return clauses
        return [clauses[0], " ".join(clauses[1:3]), " ".join(clauses[3:])]

    def flush_section() -> None:
        nonlocal current_block, current_h3
        if not current_h3:
            current_block = []
            return
        body_lines = [line.strip() for line in current_block if line.strip()]
        body_text = "\n".join(body_lines).strip()
        if _word_count(current_h3) >= 4 and _word_count(body_text) >= 6:
            sections.append((current_h2, current_h3, body_lines))
        current_block = []

    for raw_line in raw_lines:
        heading_match = MARKDOWN_HEADING_CAPTURE_PATTERN.match(raw_line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            heading_text = _normalize_line(heading_match.group(2))
            lowered_heading = heading_text.lower()

            if heading_level <= 2:
                flush_section()
                current_h3 = ""
                if heading_level == 2 and lowered_heading not in {"contents", "table of contents"}:
                    current_h2 = heading_text
                continue

            if heading_level >= 3:
                flush_section()
                if lowered_heading in {"show", "solution", "solutions"}:
                    current_h3 = ""
                    continue
                current_h3 = heading_text
                continue

        if current_h3:
            current_block.append(raw_line)

    flush_section()
    if len(sections) < 2:
        return []

    if len(sections) <= 3:
        expanded_sections: list[tuple[str, str, list[str]]] = []
        for section_title, exercise_title, body_lines in sections:
            body_word_count = _word_count(" ".join(body_lines))
            split_titles = split_sparse_long_heading(exercise_title)
            if body_word_count >= 80 and len(split_titles) > 1:
                expanded_sections.extend((section_title, split_title, body_lines) for split_title in split_titles)
            else:
                expanded_sections.append((section_title, exercise_title, body_lines))
        sections = expanded_sections

    if len(sections) >= 40:
        compacted_sections: list[tuple[str, str, list[str]]] = []
        index = 0
        while index < len(sections):
            current_section = sections[index]
            if index + 1 < len(sections):
                next_section = sections[index + 1]
                current_word_count = _word_count(current_section[1]) + _word_count(" ".join(current_section[2]))
                next_word_count = _word_count(next_section[1]) + _word_count(" ".join(next_section[2]))
                if (
                    current_section[0] == next_section[0]
                    and current_word_count <= 35
                    and next_word_count <= 35
                ):
                    compacted_sections.append(
                        (
                            current_section[0],
                            f"{current_section[1]} / {next_section[1]}",
                            current_section[2] + [""] + next_section[2],
                        )
                    )
                    index += 2
                    continue
            compacted_sections.append(current_section)
            index += 1
        sections = compacted_sections

    stem = Path(source_file).stem
    items: list[dict] = []
    for index, (section_title, exercise_title, body_lines) in enumerate(sections, start=1):
        prompt_parts = []
        if section_title:
            prompt_parts.append(f"Section: {section_title}.")
        prompt_parts.append(f"Exercise: {exercise_title}.")
        body_text = _normalize_line(" ".join(body_lines))
        if body_text:
            prompt_parts.append(body_text[:1200])
        prompt = " ".join(part for part in prompt_parts if part).strip()
        metadata = infer_question_metadata(
            source_file=source_file,
            title=f"{title} - {exercise_title}",
            prompt=prompt,
            choices=[],
            answer_hint="",
        )
        inferred_tags = metadata.get("tags", {})
        item_title = exercise_title if not section_title else f"{section_title} - {exercise_title}"
        items.append(
            {
                "question_id": f"{stem}-{index:03d}",
                "source_file": source_file,
                "title": item_title,
                "prompt": prompt,
                "choices": [],
                "answer_hint": None,
                "inferred_tags": inferred_tags.get("all", []),
                "inferred_domain": metadata.get("inferred_domain"),
                "inferred_subtheme": metadata.get("inferred_subtheme"),
                "difficulty_hint": metadata.get("difficulty_hint"),
                "item_type": ITEM_TYPE_EXERCISE,
                "metadata_debug": metadata.get("metadata_debug", {}),
                "parsed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return items


def _candidate_debug_text(item: dict) -> str:
    return " ".join(
        part
        for part in [
            " ".join(item.get("prompt_lines", [])),
            " ".join(item.get("choices", [])),
            " ".join(item.get("answer_hint_lines", [])),
        ]
        if part
    ).strip()


def _should_keep_item(item: dict, prompt: str, choices: list[str], answer_hint: str) -> tuple[bool, str]:
    word_count = _word_count(prompt)
    has_strong_prompt = prompt.endswith("?") or item.get("has_question_mark") or item.get("has_exam_context")
    has_structure = item.get("has_question_header") or item.get("has_numbering") or bool(choices) or bool(answer_hint)

    if _looks_like_noise_text(prompt):
        return False, "noise_text"

    if choices and word_count >= 3:
        return True, "multiple_choice"
    if answer_hint and has_strong_prompt and word_count >= 4:
        return True, "answer_hint_with_prompt"
    if item.get("has_checklist_lines") and has_structure and word_count >= 4:
        return True, "checklist"
    if has_strong_prompt and has_structure and word_count >= 4:
        return True, "strong_open_question"
    if prompt.endswith("?") and word_count >= 5:
        return True, "question_mark_open"
    if item.get("has_numbering") and item.get("has_exam_context") and word_count >= 5:
        return True, "numbered_exam_question"
    return False, "weak_editorial_or_noise"


def _finalize_item(item: dict, index: int) -> tuple[Optional[dict], Optional[dict]]:
    prompt = " ".join(part for part in item.get("prompt_lines", []) if part).strip()
    choices = [choice for choice in item.get("choices", []) if choice]
    answer_hint = " ".join(part for part in item.get("answer_hint_lines", []) if part).strip()
    if not prompt and not choices:
        return None, None

    keep, reason = _should_keep_item(item, prompt=prompt, choices=choices, answer_hint=answer_hint)
    if not keep:
        dropped = _candidate_debug_text(item)
        return None, {
            "reason": reason,
            "content": dropped[:240],
        }

    if choices:
        item_type = ITEM_TYPE_MULTIPLE_CHOICE
    elif item.get("has_checklist_lines") and len(item.get("prompt_lines", [])) > 1:
        item_type = ITEM_TYPE_CHECKLIST
    elif prompt:
        item_type = ITEM_TYPE_OPEN_QUESTION
    else:
        item_type = ITEM_TYPE_UNKNOWN

    metadata = infer_question_metadata(
        source_file=item["source_file"],
        title=item["title"],
        prompt=prompt,
        choices=choices,
        answer_hint=answer_hint,
    )
    inferred_tags = metadata.get("tags", {})

    difficulty_hint = None
    tag_input = " ".join([item.get("title", ""), prompt, " ".join(choices), answer_hint])
    lowered = tag_input.lower()
    if any(term in lowered for term in ("advanced", "avancado", "hard", "dificil")):
        difficulty_hint = "advanced"
    elif any(term in lowered for term in ("intermediate", "intermediario", "medium")):
        difficulty_hint = "intermediate"
    elif any(term in lowered for term in ("basic", "beginner", "facil", "easy", "iniciante")):
        difficulty_hint = "basic"
    elif metadata.get("difficulty_hint"):
        difficulty_hint = str(metadata.get("difficulty_hint"))

    question_id = f"{Path(item['source_file']).stem}-{index:03d}"
    return (
        {
            "question_id": question_id,
            "source_file": item["source_file"],
            "title": item["title"],
            "prompt": prompt,
            "choices": choices,
            "answer_hint": answer_hint or None,
            "inferred_tags": inferred_tags.get("all", []),
            "inferred_domain": metadata.get("inferred_domain"),
            "inferred_subtheme": metadata.get("inferred_subtheme"),
            "difficulty_hint": difficulty_hint,
            "item_type": item_type,
            "metadata_debug": metadata.get("metadata_debug", {}),
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        },
        None,
    )


def extract_question_items(parsed_payload: dict) -> dict:
    ensure_question_bank_dirs()
    source_file = str(parsed_payload.get("source_file", ""))
    title = str(parsed_payload.get("title", ""))
    content = str(parsed_payload.get("content", ""))
    lines = [_normalize_line(line) for line in content.splitlines()]
    items: list[dict] = []
    current: Optional[dict] = None
    candidate_count = 0
    dropped_count = 0
    dropped_examples: list[dict] = []
    skipped_noise_examples: list[str] = []

    def start_item(initial_line: str = "") -> None:
        nonlocal current
        current = _empty_item(source_file=source_file, title=title)
        if initial_line:
            current["prompt_lines"].append(initial_line)
            current["has_question_mark"] = initial_line.endswith("?")
            current["has_exam_context"] = _has_exam_context(initial_line)

    def flush_item() -> None:
        nonlocal candidate_count, current, dropped_count
        if current is None:
            return
        candidate_count += 1
        finalized, dropped = _finalize_item(current, len(items) + 1)
        if finalized:
            items.append(finalized)
        elif dropped:
            dropped_count += 1
            if len(dropped_examples) < 8:
                dropped_examples.append(dropped)
        current = None

    for index, line in enumerate(lines):
        next_nonempty_line = ""
        for future_line in lines[index + 1 :]:
            if future_line:
                next_nonempty_line = future_line
                break

        if not line:
            if current is None:
                continue
            if next_nonempty_line and (
                CHOICE_PATTERN.match(next_nonempty_line)
                or ANSWER_HINT_PATTERN.match(next_nonempty_line)
                or (current["prompt_lines"] and not current["choices"] and not current["answer_hint_lines"])
            ):
                continue
            flush_item()
            continue

        if current is None and MARKDOWN_HEADING_PATTERN.match(line):
            continue

        if _looks_like_noise_line(line):
            if len(skipped_noise_examples) < 8:
                skipped_noise_examples.append(line[:240])
            continue

        answer_match = ANSWER_HINT_PATTERN.match(line)
        if answer_match:
            if current is None:
                start_item()
            current["answer_hint_lines"].append(_normalize_line(answer_match.group(1)))
            continue

        choice_match = CHOICE_PATTERN.match(line)
        if choice_match:
            if current is None:
                continue
            label = choice_match.group(1).upper()
            text = _normalize_line(choice_match.group(2))
            current["choices"].append(f"{label}) {text}")
            continue

        if QUESTION_HEADER_PATTERN.match(line):
            if current is not None and (current["prompt_lines"] or current["choices"]):
                flush_item()
            start_item()
            current["has_question_header"] = True
            current["has_exam_context"] = True
            continue

        numbered_match = NUMBERED_PATTERN.match(line)
        if numbered_match:
            remainder = _normalize_line(numbered_match.group(2) or "")
            if current is not None and (current["prompt_lines"] or current["choices"]):
                flush_item()
            start_item(_strip_question_prefix(line if not remainder else remainder))
            current["has_numbering"] = True
            continue

        if _looks_like_question_start(line):
            if current is not None and current["prompt_lines"] and not current["choices"] and not current["answer_hint_lines"]:
                current["prompt_lines"].append(_strip_question_prefix(line))
                current["has_question_mark"] = current["has_question_mark"] or line.endswith("?")
                current["has_exam_context"] = True
                continue
            if current is not None and (current["prompt_lines"] or current["choices"]):
                flush_item()
            start_item(_strip_question_prefix(line))
            current["has_question_mark"] = line.endswith("?")
            current["has_exam_context"] = _has_exam_context(line)
            continue

        checklist_match = CHECKLIST_PATTERN.match(line)
        if checklist_match:
            if current is None:
                continue
            current["has_checklist_lines"] = True
            current["prompt_lines"].append(_normalize_line(checklist_match.group(1)))
            continue

        if current is None:
            continue
        current["prompt_lines"].append(line)
        if line.endswith("?"):
            current["has_question_mark"] = True
        if _has_exam_context(line):
            current["has_exam_context"] = True

    flush_item()

    if not items and content.strip():
        markdown_index_items = _extract_markdown_index_items(
            source_file=source_file,
            title=title,
            content=content,
        )
        if markdown_index_items:
            items.extend(markdown_index_items)

    if not items and content.strip():
        markdown_lab_items = _extract_markdown_lab_items(
            source_file=source_file,
            title=title,
            content=content,
        )
        if markdown_lab_items:
            items.extend(markdown_lab_items)

    if not items and content.strip():
        fallback_metadata = infer_question_metadata(
            source_file=source_file,
            title=title,
            prompt=content[:1200].strip(),
            choices=[],
            answer_hint="",
        )
        fallback_tags = fallback_metadata.get("tags", infer_tags(source_file=source_file, title=title, content=content))
        items.append(
            {
                "question_id": f"{Path(source_file).stem}-001",
                "source_file": source_file,
                "title": title,
                "prompt": content[:1200].strip(),
                "choices": [],
                "answer_hint": None,
                "inferred_tags": fallback_tags.get("all", []),
                "inferred_domain": fallback_metadata.get("inferred_domain"),
                "inferred_subtheme": fallback_metadata.get("inferred_subtheme"),
                "difficulty_hint": fallback_metadata.get("difficulty_hint"),
                "item_type": ITEM_TYPE_UNKNOWN,
                "metadata_debug": fallback_metadata.get("metadata_debug", {}),
                "parsed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return {
        "source_file": source_file,
        "title": title,
        "pipeline": "question_bank",
        "item_count": len(items),
        "items": items,
        "filter_debug": {
            "line_count": len(lines),
            "candidate_count": max(candidate_count, len(items)),
            "kept_count": len(items),
            "dropped_count": dropped_count,
            "dropped_examples": dropped_examples,
            "skipped_noise_examples": skipped_noise_examples,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
