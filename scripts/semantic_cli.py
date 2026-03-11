#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = os.getenv("SEMANTIC_API_BASE", "http://127.0.0.1:8099")


def _post_json(base_url: str, path: str, payload: dict):
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.getcode(), json.loads(body)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"status": "error", "error": raw or f"http {exc.code}"}
        return exc.code, parsed


def _print_error(status_code: int, payload: dict):
    msg = payload.get("error") if isinstance(payload, dict) else str(payload)
    print(f"ERROR [{status_code}]: {msg}")


def _run_search(args) -> int:
    payload = {
        "query": args.query,
        "limit": args.limit,
        "return_context": args.context,
    }
    code, data = _post_json(args.base_url, "/semantic/search", payload)
    if code >= 400 or data.get("status") != "ok":
        _print_error(code, data)
        return 1

    print(f"status: {data.get('status')}")
    print(f"query: {data.get('query')}")
    print(f"model: {data.get('model')}")
    print(f"count: {data.get('count')}")

    results = data.get("results") or []
    for i, item in enumerate(results, start=1):
        print(f"\n[{i}] similarity={item.get('similarity')} chunk_id={item.get('chunk_id')}")
        print(f"source: {item.get('source_file')}")
        print(f"title: {item.get('title')}")
        print(f"snippet: {item.get('snippet')}")

    if args.context:
        print("\ncontext:")
        print(data.get("context", ""))

    return 0


def _run_ingest(args) -> int:
    payload = {"max_chunks": args.max_chunks}
    if args.text is not None:
        payload["text"] = args.text
    if args.file is not None:
        payload["file_path"] = args.file

    code, data = _post_json(args.base_url, "/semantic/ingest-min", payload)
    if code >= 400 or data.get("status") != "ok":
        _print_error(code, data)
        return 1

    print(f"status: {data.get('status')}")
    print(f"document_id: {data.get('document_id')}")
    print(f"chunks_created: {data.get('chunks_created')}")
    print(f"chunk_ids: {', '.join(data.get('chunk_ids', []))}")
    return 0


def _build_parser(bin_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=bin_name)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"API base URL (default: {DEFAULT_BASE_URL})")

    if bin_name == "semantic-search":
        parser.add_argument("--context", action="store_true", help="inclui context no retorno")
        parser.add_argument("--limit", type=int, default=5, help="limite de resultados")
        parser.add_argument("query", help="query de busca semantica")
    elif bin_name == "semantic-ingest":
        parser.add_argument("--text", help="conteudo inline")
        parser.add_argument("--file", help="caminho do arquivo")
        parser.add_argument("--max-chunks", type=int, default=5, help="maximo de chunks")
    else:
        sub = parser.add_subparsers(dest="command", required=True)

        s = sub.add_parser("search", help="consome /semantic/search")
        s.add_argument("--context", action="store_true", help="inclui context no retorno")
        s.add_argument("--limit", type=int, default=5, help="limite de resultados")
        s.add_argument("query", help="query de busca semantica")

        i = sub.add_parser("ingest", help="consome /semantic/ingest-min")
        i.add_argument("--text", help="conteudo inline")
        i.add_argument("--file", help="caminho do arquivo")
        i.add_argument("--max-chunks", type=int, default=5, help="maximo de chunks")

    return parser


def main() -> int:
    bin_name = Path(sys.argv[0]).name
    parser = _build_parser(bin_name)
    args = parser.parse_args()

    if bin_name == "semantic-search":
        return _run_search(args)

    if bin_name == "semantic-ingest":
        if not args.text and not args.file:
            print("ERROR [400]: informe --text ou --file")
            return 1
        return _run_ingest(args)

    if args.command == "search":
        return _run_search(args)

    if not args.text and not args.file:
        print("ERROR [400]: informe --text ou --file")
        return 1
    return _run_ingest(args)


if __name__ == "__main__":
    raise SystemExit(main())
