import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "config" / "knowledge_source_catalog.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {}


def recommend_sources(*, catalog_path: Path, domain: str, subtheme: str = "", limit: int = 5) -> dict[str, Any]:
    catalog = _read_json(catalog_path)
    domains = catalog.get("domains") if isinstance(catalog.get("domains"), dict) else {}

    domain_key = str(domain or "").strip()
    if not domain_key:
        return {
            "status": "error",
            "error": "domain is required",
        }

    domain_entry = domains.get(domain_key)
    if not isinstance(domain_entry, dict):
        return {
            "status": "error",
            "error": f"domain not found in catalog: {domain_key}",
        }

    subtheme_key = str(subtheme or "").strip()
    subtheme_entry = {}
    if subtheme_key:
        subthemes = domain_entry.get("subthemes") if isinstance(domain_entry.get("subthemes"), dict) else {}
        entry = subthemes.get(subtheme_key)
        if isinstance(entry, dict):
            subtheme_entry = entry

    sources: list[dict[str, Any]] = []
    if isinstance(subtheme_entry.get("sources"), list):
        sources.extend([item for item in subtheme_entry["sources"] if isinstance(item, dict)])

    if len(sources) < max(1, limit) and isinstance(domain_entry.get("sources"), list):
        sources.extend([item for item in domain_entry["sources"] if isinstance(item, dict)])

    deduped: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for item in sources:
        url = str(item.get("url", "")).strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(item)
        if len(deduped) >= max(1, limit):
            break

    domain_name = str(domain_entry.get("name", domain_key)).strip() or domain_key
    recorte_hint = str(
        subtheme_entry.get("recorte_hint")
        or domain_entry.get("default_recorte_hint")
        or f"Montar recorte seletivo oficial para {domain_name}."
    ).strip()

    next_slice = f"Proximo recorte sugerido para {domain_name}"
    if subtheme_key:
        next_slice += f" ({subtheme_key})"
    next_slice += f": {recorte_hint}"

    return {
        "status": "ok",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_path": str(catalog_path),
        "domain": domain_key,
        "domain_name": domain_name,
        "subtheme": subtheme_key or None,
        "recommended_sources": deduped,
        "recommended_next_slice": next_slice,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="knowledge_source_recommender v1")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH), help="catalog path")
    parser.add_argument("--domain", required=True, help="domain id")
    parser.add_argument("--subtheme", default="", help="optional subtheme id")
    parser.add_argument("--limit", type=int, default=5, help="max sources")
    parser.add_argument("--output", default="", help="optional output json path")
    parser.add_argument("--pretty", action="store_true", help="pretty print")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    if not catalog_path.is_absolute():
        catalog_path = (PROJECT_ROOT / catalog_path).resolve()

    payload = recommend_sources(
        catalog_path=catalog_path,
        domain=args.domain,
        subtheme=args.subtheme,
        limit=max(1, int(args.limit or 1)),
    )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (PROJECT_ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()
