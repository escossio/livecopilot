#!/usr/bin/env python3
"""Bloqueia closure_decision se artefatos obrigatórios da frente estiverem ausentes ou divergentes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
STATUS_PATH = ROOT_DIR / "STATUS.md"
FRONT_INDEX_PATH = DOCS_DIR / "KNOWLEDGE_FRONTS_INDEX.md"
REGISTRY_PATH = ROOT_DIR / "app" / "knowledge" / "knowledge_front_registry.json"
KNOWLEDGE_EMBEDDINGS_DIR = ROOT_DIR / "data" / "knowledge_embeddings"
SEMANTIC_INDEX_DIR = ROOT_DIR / "data" / "semantic_index_experiments"


def fail(message: str) -> "None":
    print(f"PRECHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - explicit blocker path
        fail(f"Unable to read JSON file {path}: {exc}")


def find_single(pattern: str, directory: Path) -> list[Path]:
    return sorted(directory.glob(pattern))


def ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        fail(f"Missing {label}: {path}")


def ensure_contains(path: Path, needle: str, label: str) -> None:
    content = path.read_text(encoding="utf-8")
    if needle not in content:
        fail(f"{label} missing required reference: {needle}")


def normalize_front_name(front: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", front.strip().upper()).strip("_")


def locate_embeddings(front: str, registry_entry: dict[str, object]) -> Path | None:
    front_norm = front.lower()
    candidate_paths = [
        KNOWLEDGE_EMBEDDINGS_DIR / front_norm / "embeddings.jsonl",
        SEMANTIC_INDEX_DIR / front_norm / "embeddings.jsonl",
    ]
    index_path = str(registry_entry.get("index_path", "") or "").strip()
    if index_path:
        index_base = (ROOT_DIR / index_path).resolve()
        candidate_paths.append(index_base / "embeddings.jsonl")
        candidate_paths.append(index_base / "metadata.json")
    for candidate in candidate_paths:
        if candidate.is_file():
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Front closure precheck")
    parser.add_argument("front", help="Front name, e.g. MACHINE_LEARNING")
    args = parser.parse_args()

    front = normalize_front_name(args.front)
    if not front:
        fail("Invalid front name")

    front_doc = DOCS_DIR / f"FRONT_{front}.md"
    ensure_exists(front_doc, "front document")

    final_reports = find_single(f"{front}_FINAL_REPORT*.md", DOCS_DIR) + find_single(f"{front}_FINAL_REPORT_*.md", DOCS_DIR)
    if not final_reports:
        fail("Missing FINAL REPORT")

    handoffs = find_single(f"HANDOFF_*{front}*.md", DOCS_DIR)
    if not handoffs:
        fail("Missing HANDOFF")

    baseline_reports = find_single(f"{front}_SEMANTIC_BASELINE_REPORT*.md", DOCS_DIR)
    if not baseline_reports:
        fail("Missing SEMANTIC BASELINE REPORT")

    ensure_exists(STATUS_PATH, "STATUS.md")
    ensure_contains(STATUS_PATH, front, "STATUS.md")

    ensure_exists(FRONT_INDEX_PATH, "knowledge fronts index")
    ensure_contains(FRONT_INDEX_PATH, front, "knowledge fronts index")

    ensure_exists(REGISTRY_PATH, "router registry")
    registry = load_json(REGISTRY_PATH)
    if not isinstance(registry, dict):
        fail("Router registry is not a JSON object")
    fronts = registry.get("fronts", [])
    if not isinstance(fronts, list):
        fail("Router registry fronts section is invalid")

    registry_entry = None
    for entry in fronts:
        if isinstance(entry, dict) and str(entry.get("name", "")).upper() == front:
            registry_entry = entry
            break
    if registry_entry is None:
        fail("Front missing in router registry")

    if not bool(registry_entry.get("enabled_for_routing", False)):
        fail("Front not enabled for routing")

    embeddings_path = locate_embeddings(front, registry_entry)
    if embeddings_path is None:
        fail("Missing embeddings for front")

    metadata_candidates = [
        embeddings_path.with_name("metadata.json"),
        embeddings_path.parent / "metadata.json",
    ]
    if not any(candidate.is_file() for candidate in metadata_candidates):
        fail("Missing embeddings metadata for front")

    print("PRECHECK PASSED")


if __name__ == "__main__":
    main()
