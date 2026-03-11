import argparse
import re
import shutil
import time
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.services.knowledge_ingest import process_knowledge_base
from app.services.knowledge_parsers import RAW_DIR, SUPPORTED_TYPES, compute_sha256, ensure_knowledge_dirs

logger = get_logger(__name__)

TEMP_DOWNLOAD_SUFFIXES = {".crdownload", ".part", ".tmp", ".download"}


def resolve_watch_dir(path: str | None) -> Path:
    raw = path or settings.downloads_watch_dir
    return Path(raw).expanduser().resolve()


def normalize_filename(name: str) -> str:
    path = Path(name)
    stem = path.stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return f"{stem or 'document'}{path.suffix.lower()}"


def build_raw_hash_index() -> dict[str, str]:
    ensure_knowledge_dirs()
    index: dict[str, str] = {}
    for path in RAW_DIR.rglob("*"):
        if path.is_file():
            index[compute_sha256(path)] = str(path.relative_to(RAW_DIR))
    return index


def _target_path_for(source_path: Path, sha256: str, normalize_names: bool) -> Path:
    target_name = normalize_filename(source_path.name) if normalize_names else source_path.name
    candidate = RAW_DIR / target_name
    if not candidate.exists():
        return candidate
    if compute_sha256(candidate) == sha256:
        return candidate
    collision_name = f"{candidate.stem}_{sha256[:10]}{candidate.suffix.lower()}"
    return candidate.with_name(collision_name)


def import_downloads_once(
    downloads_dir: Path,
    mode: str = "copy",
    normalize_names: bool = True,
    trigger_ingest: bool = True,
    chunk_size: int = 1200,
    overlap: int = 180,
) -> dict:
    ensure_knowledge_dirs()
    downloads_dir.mkdir(parents=True, exist_ok=True)
    mode = mode.lower()
    if mode not in {"copy", "move"}:
        raise ValueError("mode must be 'copy' or 'move'")

    raw_hash_index = build_raw_hash_index()
    imported = 0
    duplicates = 0
    unsupported = 0
    seen = 0
    imported_paths: list[str] = []

    for source_path in sorted(downloads_dir.iterdir()):
        if not source_path.is_file():
            continue
        seen += 1
        suffix = source_path.suffix.lower()
        if suffix in TEMP_DOWNLOAD_SUFFIXES:
            continue
        if suffix not in SUPPORTED_TYPES:
            unsupported += 1
            continue

        sha256 = compute_sha256(source_path)
        existing = raw_hash_index.get(sha256)
        if existing:
            duplicates += 1
            logger.info(
                "knowledge_download_duplicate",
                extra={"event": "knowledge_download_duplicate", "source_file": source_path.name, "existing_file": existing},
            )
            continue

        target_path = _target_path_for(source_path, sha256, normalize_names=normalize_names)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "move":
            shutil.move(str(source_path), str(target_path))
        else:
            shutil.copy2(str(source_path), str(target_path))

        raw_hash_index[sha256] = str(target_path.relative_to(RAW_DIR))
        imported += 1
        imported_paths.append(str(target_path.relative_to(RAW_DIR)))
        logger.info(
            "knowledge_download_imported",
            extra={
                "event": "knowledge_download_imported",
                "source_file": source_path.name,
                "imported_file": str(target_path.relative_to(RAW_DIR)),
                "mode": mode,
            },
        )

    ingest_summary = None
    if trigger_ingest:
        ingest_summary = process_knowledge_base(chunk_size=chunk_size, overlap=overlap)

    return {
        "watch_dir": str(downloads_dir),
        "seen": seen,
        "imported": imported,
        "duplicates": duplicates,
        "unsupported": unsupported,
        "imported_paths": imported_paths,
        "trigger_ingest": trigger_ingest,
        "ingest_summary": ingest_summary,
    }


def watch_downloads(
    downloads_dir: Path,
    mode: str = "copy",
    normalize_names: bool = True,
    trigger_ingest: bool = True,
    chunk_size: int = 1200,
    overlap: int = 180,
    poll_interval: float = 5.0,
) -> None:
    logger.info(
        "knowledge_import_watch_started",
        extra={"event": "knowledge_import_watch_started", "watch_dir": str(downloads_dir), "poll_interval": poll_interval},
    )
    while True:
        summary = import_downloads_once(
            downloads_dir=downloads_dir,
            mode=mode,
            normalize_names=normalize_names,
            trigger_ingest=trigger_ingest,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        if summary["imported"]:
            print(f"Novos arquivos importados: {summary['imported']}")
            if summary["trigger_ingest"] and summary["ingest_summary"]:
                print(f"Chunks atuais: {summary['ingest_summary']['chunk_total']}")
        time.sleep(poll_interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa downloads locais para a base de conhecimento.")
    parser.add_argument("--downloads-dir", default=settings.downloads_watch_dir, help="Pasta monitorada de downloads.")
    parser.add_argument("--mode", choices=["copy", "move"], default=settings.downloads_import_mode, help="Copia ou move os arquivos importados.")
    parser.add_argument("--normalize-names", dest="normalize_names", action="store_true", default=settings.downloads_normalize_names, help="Normaliza nomes importados.")
    parser.add_argument("--keep-names", dest="normalize_names", action="store_false", help="Preserva o nome original do arquivo.")
    parser.add_argument("--ingest", dest="trigger_ingest", action="store_true", default=settings.downloads_trigger_ingest, help="Dispara parsing e chunking após importar.")
    parser.add_argument("--no-ingest", dest="trigger_ingest", action="store_false", help="Importa sem disparar a ingestão.")
    parser.add_argument("--watch", action="store_true", help="Mantém monitoramento por polling da pasta de downloads.")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Intervalo de polling em segundos no modo watch.")
    parser.add_argument("--chunk-size", type=int, default=1200, help="Tamanho alvo de chunk ao disparar ingestão.")
    parser.add_argument("--overlap", type=int, default=180, help="Sobreposição de chunk ao disparar ingestão.")
    args = parser.parse_args()

    downloads_dir = resolve_watch_dir(args.downloads_dir)
    if args.watch:
        watch_downloads(
            downloads_dir=downloads_dir,
            mode=args.mode,
            normalize_names=args.normalize_names,
            trigger_ingest=args.trigger_ingest,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            poll_interval=args.poll_interval,
        )
        return 0

    summary = import_downloads_once(
        downloads_dir=downloads_dir,
        mode=args.mode,
        normalize_names=args.normalize_names,
        trigger_ingest=args.trigger_ingest,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )
    print(f"Pasta monitorada: {summary['watch_dir']}")
    print(f"Arquivos observados: {summary['seen']}")
    print(f"Arquivos importados: {summary['imported']}")
    print(f"Duplicatas ignoradas: {summary['duplicates']}")
    print(f"Arquivos não suportados: {summary['unsupported']}")
    if summary["trigger_ingest"] and summary["ingest_summary"]:
        ingest_summary = summary["ingest_summary"]
        print(f"Arquivos na base de conhecimento: {ingest_summary['total_found']}")
        print(f"Arquivos processados na ingestão: {ingest_summary['processed']}")
        print(f"Chunks gerados na ingestão: {ingest_summary['chunk_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
