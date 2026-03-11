import re
from typing import Any

SECTION_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
TARGET_SECTION_TOKENS = 1000
MAX_SECTION_TOKENS = 1200


def _estimate_tokens(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def _split_oversized_section(title: str, body: str) -> list[dict[str, Any]]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body or "") if part.strip()]
    if not paragraphs:
        return [{"title": title[:100], "content": title}]

    chunks: list[dict[str, Any]] = []
    current_parts: list[str] = []
    current_tokens = 0
    part_index = 1

    for paragraph in paragraphs:
        p_tokens = _estimate_tokens(paragraph)
        if p_tokens > MAX_SECTION_TOKENS:
            words = paragraph.split()
            start = 0
            while start < len(words):
                end = min(start + TARGET_SECTION_TOKENS, len(words))
                piece = " ".join(words[start:end]).strip()
                if piece:
                    chunk_title = f"{title} (part {part_index})"
                    chunks.append(
                        {
                            "title": chunk_title[:100],
                            "content": f"{title}\n\n{piece}",
                            "heading_level": 2,
                        }
                    )
                    part_index += 1
                start = end
            continue

        if current_parts and (current_tokens + p_tokens) > MAX_SECTION_TOKENS:
            merged = "\n\n".join(current_parts).strip()
            chunk_title = f"{title} (part {part_index})"
            chunks.append(
                {
                    "title": chunk_title[:100],
                    "content": f"{title}\n\n{merged}",
                    "heading_level": 2,
                }
            )
            part_index += 1
            current_parts = [paragraph]
            current_tokens = p_tokens
            continue

        current_parts.append(paragraph)
        current_tokens += p_tokens

    if current_parts:
        merged = "\n\n".join(current_parts).strip()
        chunk_title = f"{title} (part {part_index})"
        chunks.append(
            {
                "title": chunk_title[:100],
                "content": f"{title}\n\n{merged}",
                "heading_level": 2,
            }
        )

    return chunks


def split_markdown_by_sections(text: str) -> list[dict[str, Any]]:
    lines = (text or "").splitlines()
    headings: list[dict[str, Any]] = []
    in_code_fence = False
    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        match = SECTION_HEADING_RE.match(raw_line.rstrip())
        if not match:
            continue
        headings.append(
            {
                "line_index": idx,
                "level": len(match.group(1)),
                "title": match.group(2).strip(),
            }
        )

    if not headings:
        return []

    sections: list[dict[str, Any]] = []
    for i, heading in enumerate(headings):
        start = heading["line_index"]
        end = len(lines)
        for nxt in headings[i + 1 :]:
            if int(nxt["level"]) <= int(heading["level"]):
                end = int(nxt["line_index"])
                break

        section_text = "\n".join(lines[start:end]).strip()
        if not section_text:
            continue
        sections.append(
            {
                "title": str(heading["title"]),
                "content": section_text,
                "heading_level": int(heading["level"]),
            }
        )

    if any(int(section.get("heading_level", 0) or 0) == 2 for section in sections):
        sections = [section for section in sections if int(section.get("heading_level", 0) or 0) != 1]

    chunks: list[dict[str, Any]] = []
    for section in sections:
        title = str(section.get("title", "") or "").strip()
        section_body = str(section.get("content", "") or "").strip()
        heading_level = int(section.get("heading_level", 2) or 2)
        if not title or not section_body:
            continue
        full_text = section_body
        if _estimate_tokens(full_text) <= MAX_SECTION_TOKENS:
            chunks.append({"title": title[:100], "content": full_text, "heading_level": heading_level})
            continue
        chunks.extend(_split_oversized_section(title, section_body))

    return chunks
