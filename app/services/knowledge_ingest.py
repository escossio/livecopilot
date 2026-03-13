import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import get_logger
from app.services.knowledge_chunks import (
    CHUNKS_DIR,
    INDEX_DIR,
    EPUB_CHUNK_PIPELINE_VERSION,
    build_chunk_payload,
    chunk_output_path,
    load_chunk_payload,
    write_chunk_payload,
    write_index_manifest,
)
from app.services.knowledge_parsers import (
    PARSED_DIR,
    PARSED_STATUS_OK,
    RAW_DIR,
    SUPPORTED_TYPES,
    compute_sha256,
    ensure_knowledge_dirs,
    list_raw_files,
    load_parsed_payload,
    parse_file,
    parsed_output_path,
    write_parsed_payload,
)
from app.services.knowledge_tags import TAG_PIPELINE_VERSION
from app.services.semantic_min_api import ingest_knowledge_base_min
from app.services.source_prefix_resolution import (
    matches_source_prefix,
    normalize_source_prefixes,
    resolve_source_files_from_prefixes,
)

logger = get_logger(__name__)

STATE_PATH = INDEX_DIR / "knowledge_state.json"


def _has_tag_payload(payload: dict | None) -> bool:
    if not isinstance(payload, dict):
        return False
    tags = payload.get("tags")
    if not isinstance(tags, dict):
        return False
    all_tags = tags.get("all", [])
    return isinstance(all_tags, list)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"files": {}, "updated_at": None}
    try:
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}, "updated_at": None}
    if not isinstance(payload, dict):
        return {"files": {}, "updated_at": None}
    files = payload.get("files")
    if not isinstance(files, dict):
        payload["files"] = {}
    return payload


def write_state(state: dict) -> Path:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return STATE_PATH


def _needs_processing(source_path: Path, state: dict) -> tuple[bool, str]:
    relative = str(source_path.relative_to(RAW_DIR))
    sha256 = compute_sha256(source_path)
    record = state.get("files", {}).get(relative)
    parsed_path = parsed_output_path(source_path)
    chunk_path = chunk_output_path(relative)
    if not record:
        return True, sha256
    if record.get("sha256") != sha256:
        return True, sha256
    if record.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    if not parsed_path.exists() or not chunk_path.exists():
        return True, sha256
    parsed_payload = load_parsed_payload(parsed_path)
    if not _has_tag_payload(parsed_payload):
        return True, sha256
    if parsed_payload.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    chunk_payload = load_chunk_payload(chunk_path)
    if not _has_tag_payload(chunk_payload):
        return True, sha256
    if chunk_payload.get("tag_pipeline_version") != TAG_PIPELINE_VERSION:
        return True, sha256
    if source_path.suffix.lower() == ".epub":
        if int(chunk_payload.get("epub_chunk_pipeline_version", 0) or 0) != EPUB_CHUNK_PIPELINE_VERSION:
            return True, sha256
    return False, sha256


def process_knowledge_base(
    chunk_size: int = 1200,
    overlap: int = 180,
    source_prefixes: list[str] | None = None,
    strict_source_prefix: bool = False,
    dry_run: bool = False,
) -> dict:
    normalized_prefixes = normalize_source_prefixes(source_prefixes)

    all_raw_files = list_raw_files()
    files_found_by_prefix: dict[str, int] = {}
    if normalized_prefixes:
        for prefix in normalized_prefixes:
            files_found_by_prefix[prefix] = sum(
                1
                for path in all_raw_files
                if matches_source_prefix(str(path.relative_to(RAW_DIR)).replace("\\", "/"), [prefix])
            )

    raw_files = [
        path
        for path in all_raw_files
        if matches_source_prefix(str(path.relative_to(RAW_DIR)).replace("\\", "/"), normalized_prefixes)
    ]

    if strict_source_prefix and normalized_prefixes and not raw_files:
        joined = ", ".join(normalized_prefixes)
        raise ValueError(f"strict-source-prefix habilitado e nenhum arquivo encontrado para: {joined}")

    selected_targets = sorted(str(path.relative_to(RAW_DIR)).replace("\\", "/") for path in raw_files)
    if dry_run:
        return {
            "dry_run": True,
            "selection_mode": "resolved_from_source_prefix" if normalized_prefixes else "default",
            "total_found": len(raw_files),
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "unsupported": 0,
            "chunk_total": 0,
            "source_prefixes": normalized_prefixes,
            "files_found_by_prefix": files_found_by_prefix,
            "selected_targets": selected_targets,
            "manifest_path": "",
            "state_path": str(STATE_PATH),
        }

    ensure_knowledge_dirs()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()

    active_sources = {str(path.relative_to(RAW_DIR)) for path in raw_files}

    if normalized_prefixes:
        stale_sources = [
            source_key
            for source_key in state.get("files", {})
            if matches_source_prefix(source_key, normalized_prefixes) and source_key not in active_sources
        ]
    else:
        stale_sources = [source_key for source_key in state.get("files", {}) if source_key not in active_sources]

    for source_key in stale_sources:
        record = state["files"].pop(source_key, {})
        for path_key in ("parsed_path", "chunk_path"):
            raw_path = record.get(path_key)
            if not raw_path:
                continue
            path = Path(str(raw_path))
            if path.exists():
                path.unlink()

    expected_parsed_paths = {parsed_output_path(path) for path in raw_files}
    expected_chunk_paths = {chunk_output_path(str(path.relative_to(RAW_DIR))) for path in raw_files}
    if normalized_prefixes:
        scoped_state_sources = [
            source_key for source_key in state.get("files", {}) if matches_source_prefix(source_key, normalized_prefixes)
        ]
        scoped_expected_parsed = {
            Path(str(state["files"].get(source_key, {}).get("parsed_path", "")))
            for source_key in scoped_state_sources
            if state["files"].get(source_key, {}).get("parsed_path")
        }
        scoped_expected_chunk = {
            Path(str(state["files"].get(source_key, {}).get("chunk_path", "")))
            for source_key in scoped_state_sources
            if state["files"].get(source_key, {}).get("chunk_path")
        }
        for artifact in PARSED_DIR.glob("*.json"):
            if artifact in scoped_expected_parsed and artifact not in expected_parsed_paths:
                artifact.unlink()
        for artifact in CHUNKS_DIR.glob("*.json"):
            if artifact in scoped_expected_chunk and artifact not in expected_chunk_paths:
                artifact.unlink()
    else:
        for artifact in PARSED_DIR.glob("*.json"):
            if artifact not in expected_parsed_paths:
                artifact.unlink()
        for artifact in CHUNKS_DIR.glob("*.json"):
            if artifact not in expected_chunk_paths:
                artifact.unlink()

    total_found = len(raw_files)
    processed = 0
    skipped = 0
    errors = 0
    unsupported = 0
    chunk_total = 0

    for source_path in raw_files:
        should_process, sha256 = _needs_processing(source_path, state)
        source_key = str(source_path.relative_to(RAW_DIR))
        if not should_process:
            skipped += 1
            existing_chunk = load_chunk_payload(chunk_output_path(source_key))
            if existing_chunk:
                chunk_total += int(existing_chunk.get("chunk_count", 0) or 0)
            continue

        parsed_payload = parse_file(source_path)
        previous_record = state.setdefault("files", {}).get(source_key, {})
        new_parsed_path = parsed_output_path(source_path)
        new_chunk_path = chunk_output_path(source_key)
        for path_key, new_path in (("parsed_path", new_parsed_path), ("chunk_path", new_chunk_path)):
            raw_path = previous_record.get(path_key)
            if raw_path and Path(str(raw_path)) != new_path:
                old_path = Path(str(raw_path))
                if old_path.exists():
                    old_path.unlink()

        parsed_path = write_parsed_payload(parsed_payload)
        processed += 1

        state.setdefault("files", {})[source_key] = {
            "sha256": sha256,
            "tag_pipeline_version": TAG_PIPELINE_VERSION,
            "parsed_path": str(parsed_path),
            "chunk_path": str(new_chunk_path),
            "status": parsed_payload.get("status", ""),
            "file_type": parsed_payload.get("file_type", ""),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        if source_path.suffix.lower() not in SUPPORTED_TYPES:
            unsupported += 1
            continue

        if parsed_payload.get("status") != PARSED_STATUS_OK:
            errors += 1
            continue

        chunk_payload = build_chunk_payload(parsed_payload, chunk_size=chunk_size, overlap=overlap)
        write_chunk_payload(chunk_payload)
        state["files"][source_key]["chunk_count"] = int(chunk_payload.get("chunk_count", 0) or 0)
        chunk_total += int(chunk_payload.get("chunk_count", 0) or 0)

        logger.info(
            "knowledge_file_processed",
            extra={
                "event": "knowledge_file_processed",
                "source_file": source_key,
                "status": parsed_payload.get("status", ""),
                "chunk_count": chunk_payload.get("chunk_count", 0),
            },
        )

    documents = []
    chunk_documents = []
    for source_key, record in sorted(state.get("files", {}).items()):
        parsed_path = Path(str(record.get("parsed_path", "")))
        parsed_payload = load_parsed_payload(parsed_path)
        if parsed_payload:
            documents.append(parsed_payload)
        chunk_payload = load_chunk_payload(chunk_output_path(source_key))
        if chunk_payload:
            chunk_documents.append(chunk_payload)

    write_state(state)
    manifest_path = write_index_manifest(documents, chunk_documents)

    return {
        "dry_run": False,
        "selection_mode": "resolved_from_source_prefix" if normalized_prefixes else "default",
        "total_found": total_found,
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
        "unsupported": unsupported,
        "chunk_total": chunk_total,
        "source_prefixes": normalized_prefixes,
        "files_found_by_prefix": files_found_by_prefix,
        "selected_targets": selected_targets,
        "manifest_path": str(manifest_path),
        "state_path": str(STATE_PATH),
    }


def _sample_targets(targets: list[str], limit: int = 50) -> tuple[list[str], bool]:
    normalized = [str(item) for item in targets]
    if len(normalized) <= limit:
        return normalized, False
    return normalized[:limit], True


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão local de base de conhecimento.")
    parser.add_argument("--chunk-size", type=int, default=1200, help="Tamanho alvo de cada chunk em caracteres.")
    parser.add_argument("--overlap", type=int, default=180, help="Sobreposição leve entre chunks em caracteres.")
    parser.add_argument(
        "--source-prefix",
        action="append",
        default=[],
        help=(
            "Filtra ingestão por prefixo relativo a data/knowledge_raw (repetível). "
            "Ex.: --source-prefix continuity_docs_selected/"
        ),
    )
    parser.add_argument(
        "--strict-source-prefix",
        action="store_true",
        help="Falha a execução quando prefixos são informados e nenhum arquivo é encontrado.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas lista os arquivos de ingestão que seriam selecionados, sem alterar estado/manifests.",
    )
    parser.add_argument(
        "--semantic-persist",
        action="store_true",
        help="Persistir documentos/chunks no schema semântico usando a trilha mínima canônica.",
    )
    parser.add_argument(
        "--semantic-limit-docs",
        type=int,
        default=1,
        help="Quantidade máxima de documentos para persistência semântica nesta execução.",
    )
    parser.add_argument(
        "--semantic-max-chunks-per-doc",
        type=int,
        default=8,
        help="Quantidade máxima de chunks por documento na persistência semântica mínima.",
    )
    parser.add_argument(
        "--semantic-source-file",
        action="append",
        default=[],
        help="Filtra por source_file específico (repetível) para a persistência semântica.",
    )
    parser.add_argument(
        "--semantic-embedding-mode",
        choices=["auto", "openai", "mock"],
        default="auto",
        help="Modo de embedding da persistência semântica (auto usa OpenAI quando disponível).",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help=(
            "Em conjunto com --semantic-persist, apenas lista os source_files que seriam persistidos "
            "sem gerar embeddings nem alterar banco/estado."
        ),
    )
    args = parser.parse_args()

    if args.list_targets and not args.semantic_persist:
        print("Erro: --list-targets requer --semantic-persist")
        return 2

    try:
        summary = process_knowledge_base(
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            source_prefixes=args.source_prefix,
            strict_source_prefix=bool(args.strict_source_prefix),
            dry_run=bool(args.dry_run or args.list_targets),
        )
    except ValueError as exc:
        print(f"Erro: {exc}")
        return 2

    if args.dry_run:
        sample, truncated = _sample_targets(list(summary.get("selected_targets", [])))
        dry_run_payload = {
            "mode": "dry_run",
            "selection_mode": summary.get("selection_mode", "default"),
            "source_prefixes": summary.get("source_prefixes", []),
            "files_found_by_prefix": summary.get("files_found_by_prefix", {}),
            "total_found": int(summary.get("total_found", 0) or 0),
            "targets_sample": sample,
            "targets_sample_truncated": bool(truncated),
            "targets_sample_size": len(sample),
        }
        print("Ingestão - dry-run:")
        print(json.dumps(dry_run_payload, ensure_ascii=False, indent=2))
        if not args.semantic_persist:
            return 0
        if not args.list_targets:
            print("Modo dry-run: persistência semântica não executada (use --list-targets para apenas listar alvos).")
            return 0

    print(f"Arquivos encontrados: {summary['total_found']}")
    print(f"Arquivos processados: {summary['processed']}")
    print(f"Arquivos ignorados: {summary['skipped']}")
    print(f"Erros de parsing: {summary['errors']}")
    print(f"Arquivos não suportados: {summary['unsupported']}")
    print(f"Chunks gerados: {summary['chunk_total']}")
    if summary.get("source_prefixes"):
        print(f"Prefixos de origem: {', '.join(summary['source_prefixes'])}")
        if summary.get("files_found_by_prefix"):
            print("Contagem por prefixo:")
            for prefix, count in summary["files_found_by_prefix"].items():
                print(f"- {prefix}: {count}")
    if summary.get("manifest_path"):
        print(f"Manifesto: {summary['manifest_path']}")
    elif args.dry_run or args.list_targets:
        print("Manifesto: (não gerado em modo somente listagem)")
    if args.semantic_persist:
        explicit_semantic_sources = [str(item).strip() for item in (args.semantic_source_file or []) if str(item).strip()]
        resolved_semantic_sources = explicit_semantic_sources
        semantic_resolution_meta: dict[str, object] = {
            "selection_mode": "explicit_source_file" if explicit_semantic_sources else "default",
            "source_prefixes": [],
            "source_files_resolved_total": len(explicit_semantic_sources),
            "source_files_resolved_by_prefix": {},
        }

        if not explicit_semantic_sources and summary.get("source_prefixes"):
            state_for_persist = load_state()
            prefixes = list(summary.get("source_prefixes", []))
            resolved, counts = resolve_source_files_from_prefixes(state_for_persist, prefixes)
            resolved_semantic_sources = resolved
            semantic_resolution_meta = {
                "selection_mode": "resolved_from_source_prefix",
                "source_prefixes": prefixes,
                "source_files_resolved_total": len(resolved),
                "source_files_resolved_by_prefix": counts,
            }
            print("Persistência semântica - resolução por prefixo:")
            print(f"- Prefixos normalizados: {', '.join(prefixes)}")
            print(f"- Source files resolvidos: {len(resolved)}")
            print("- Contagem por prefixo:")
            for prefix in prefixes:
                print(f"  - {prefix}: {int(counts.get(prefix, 0))}")

            if not resolved:
                if args.strict_source_prefix:
                    joined = ", ".join(prefixes)
                    print(f"Erro: strict-source-prefix habilitado e nenhum source_file resolvido para persistência: {joined}")
                    return 2
                semantic_summary = {
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "documents_selected": 0,
                    "documents_processed": 0,
                    "documents_validated": 0,
                    "documents_failed": 0,
                    "chunks_persisted": 0,
                    "sources_with_error": [],
                    "duplicate_source_checksum_rows": [],
                    "selection_mode": "resolved_from_source_prefix",
                    "source_prefixes": prefixes,
                    "source_files_resolved_total": 0,
                    "source_files_resolved_by_prefix": counts,
                    "note": "Nenhum source_file resolvido pelos prefixos; persistência semântica não executada.",
                }
                print("Persistência semântica:")
                print(json.dumps(semantic_summary, ensure_ascii=False, indent=2))
                return 0

        if args.list_targets:
            sample, truncated = _sample_targets(list(resolved_semantic_sources))
            list_targets_payload = {
                "mode": "list_targets",
                "selection_mode": str(semantic_resolution_meta.get("selection_mode", "default")),
                "source_prefixes": semantic_resolution_meta.get("source_prefixes", []),
                "source_files_resolved_total": int(semantic_resolution_meta.get("source_files_resolved_total", 0)),
                "source_files_resolved_by_prefix": semantic_resolution_meta.get("source_files_resolved_by_prefix", {}),
                "source_files_sample": sample,
                "source_files_sample_truncated": bool(truncated),
                "source_files_sample_size": len(sample),
                "note": (
                    "Sem filtros explícitos: a seleção final depende do limit_docs no fluxo real."
                    if str(semantic_resolution_meta.get("selection_mode", "default")) == "default"
                    else ""
                ),
            }
            print("Persistência semântica - list-targets:")
            print(json.dumps(list_targets_payload, ensure_ascii=False, indent=2))
            return 0

        semantic_summary = ingest_knowledge_base_min(
            limit_docs=max(1, int(args.semantic_limit_docs)),
            max_chunks_per_doc=max(1, int(args.semantic_max_chunks_per_doc)),
            source_files=resolved_semantic_sources,
            embedding_mode=args.semantic_embedding_mode,
        )
        semantic_summary["selection_mode"] = str(semantic_resolution_meta.get("selection_mode", "default"))
        semantic_summary["source_prefixes"] = semantic_resolution_meta.get("source_prefixes", [])
        semantic_summary["source_files_resolved_total"] = int(semantic_resolution_meta.get("source_files_resolved_total", 0))
        semantic_summary["source_files_resolved_by_prefix"] = semantic_resolution_meta.get(
            "source_files_resolved_by_prefix", {}
        )
        print("Persistência semântica:")
        print(json.dumps(semantic_summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
