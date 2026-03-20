"""Gera embeddings para os chunks de um front específico."""
import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


def _collect_chunks(prefix: str, chunks_dir: Path) -> list[dict]:
    pattern = f"{prefix}__*.chunks.json"
    entries = []
    for chunk_file in sorted(chunks_dir.glob(pattern)):
        payload = json.loads(chunk_file.read_text(encoding="utf-8"))
        for chunk in payload.get("chunks", []):
            content = chunk.get("content", "").strip()
            if not content:
                continue
            entries.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "source_file": chunk.get("source_file"),
                    "title": chunk.get("title"),
                    "sequence": chunk.get("sequence"),
                    "content": content,
                }
            )
    return entries


def _write_metadata(
    metadata_path: Path,
    model: str,
    embedding_dim: int,
    chunk_count: int,
    document_count: int,
    elapsed: float,
) -> None:
    metadata = {
        "embedding_model": model,
        "embedding_dimension": embedding_dim,
        "chunk_count": chunk_count,
        "document_count": document_count,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": round(elapsed, 3),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _truncate_text(text: str, max_tokens: int = 4000) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera embeddings para chunks via OpenAI Embeddings."
    )
    parser.add_argument(
        "--source-prefix",
        default="machine_learning",
        help="Prefixo usado nos nomes dos chunk files (default: machine_learning).",
    )
    parser.add_argument(
        "--chunks-dir",
        default="data/knowledge_chunks",
        help="Diretório base dos chunk files.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/knowledge_embeddings",
        help="Destino para os embeddings gerados.",
    )
    parser.add_argument(
        "--model", default="text-embedding-3-large", help="Modelo de embeddings."
    )
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    if not chunks_dir.is_dir():
        raise SystemExit(f"Chunks dir inexistente: {chunks_dir}")
    chunks = _collect_chunks(args.source_prefix, chunks_dir)
    if not chunks:
        raise SystemExit(f"Nenhum chunk encontrado para prefixo {args.source_prefix}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY não definido; execute `source codex-supervisor/.env.secrets`."
        )

    client = OpenAI(api_key=api_key)
    output_path = Path(args.output_dir) / args.source_prefix
    output_path.mkdir(parents=True, exist_ok=True)
    embeddings_file = output_path / "embeddings.jsonl"
    metadata_file = output_path / "metadata.json"

    start = time.monotonic()
    total_dim = 0
    with embeddings_file.open("w", encoding="utf-8") as out_f:
        for chunk in chunks:
            input_text = _truncate_text(chunk["content"])
            response = client.embeddings.create(model=args.model, input=input_text)
            vector = response.data[0].embedding
            total_dim = len(vector)
            record = {
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "title": chunk["title"],
                "sequence": chunk["sequence"],
                "content": input_text,
                "embedding": vector,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
    elapsed = time.monotonic() - start
    documents = {chunk["source_file"] for chunk in chunks if chunk.get("source_file")}
    _write_metadata(
        metadata_file,
        model=args.model,
        embedding_dim=total_dim,
        chunk_count=len(chunks),
        document_count=len(documents),
        elapsed=elapsed,
    )

    print(
        f"{len(chunks)} embeddings escritos em {embeddings_file} "
        f"(docs: {len(documents)}, tempo: {round(elapsed,2)}s, dim: {total_dim})"
    )


if __name__ == "__main__":
    main()
