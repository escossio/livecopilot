from __future__ import annotations

from typing import Any


def normalize_source_prefix(raw: str) -> str:
    value = str(raw or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = value.lstrip("/")
    return value.rstrip("/")


def validate_source_prefix(raw: str) -> str:
    normalized = normalize_source_prefix(raw)
    if not normalized:
        raise ValueError("source-prefix inválido: valor vazio após normalização")
    if any(part == ".." for part in normalized.split("/")):
        raise ValueError(f"source-prefix inválido (path traversal): {raw!r}")
    return normalized


def normalize_source_prefixes(values: list[str] | None) -> list[str]:
    seen: set[str] = set()
    normalized_values: list[str] = []
    for raw in values or []:
        normalized = validate_source_prefix(raw)
        if normalized in seen:
            continue
        seen.add(normalized)
        normalized_values.append(normalized)
    return normalized_values


def matches_source_prefix(source_key: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    normalized = source_key.replace("\\", "/")
    for prefix in prefixes:
        if not prefix:
            continue
        if normalized == prefix or normalized.startswith(f"{prefix}/"):
            return True
    return False


def resolve_source_files_from_prefixes(state: dict[str, Any], prefixes: list[str]) -> tuple[list[str], dict[str, int]]:
    files = state.get("files", {})
    if not isinstance(files, dict):
        return [], {prefix: 0 for prefix in prefixes}
    counts = {prefix: 0 for prefix in prefixes}
    selected: list[str] = []
    for source_key in sorted(files.keys()):
        normalized = str(source_key).replace("\\", "/")
        matched_prefixes = [prefix for prefix in prefixes if matches_source_prefix(normalized, [prefix])]
        if not matched_prefixes:
            continue
        selected.append(normalized)
        for prefix in matched_prefixes:
            counts[prefix] += 1
    return selected, counts
