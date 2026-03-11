import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

KNOWLEDGE_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_index" / "knowledge_manifest.json"


def _load_manifest() -> dict[str, Any]:
    if not KNOWLEDGE_MANIFEST_PATH.exists():
        return {}
    try:
        payload = json.loads(KNOWLEDGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_knowledge_tag_diagnostics(top: int = 10) -> dict[str, Any]:
    manifest = _load_manifest()
    documents = manifest.get("documents", []) if isinstance(manifest.get("documents"), list) else []

    tag_counter: Counter[str] = Counter()
    category_counter: dict[str, Counter[str]] = {
        "technology": Counter(),
        "domain": Counter(),
        "subtheme": Counter(),
    }
    suspicious_cross_support = []
    inflated_documents = []
    tag_to_documents: dict[str, list[str]] = defaultdict(list)

    for document in documents:
        if not isinstance(document, dict):
            continue
        source_file = str(document.get("source_file", ""))
        tags = document.get("tags") if isinstance(document.get("tags"), dict) else {}
        technologies = [str(tag) for tag in tags.get("technology", []) if str(tag).strip()]
        domains = [str(tag) for tag in tags.get("domain", []) if str(tag).strip()]
        subthemes = [str(tag) for tag in tags.get("subtheme", []) if str(tag).strip()]
        all_tags = [str(tag) for tag in tags.get("all", []) if str(tag).strip()]

        tag_counter.update(all_tags)
        category_counter["technology"].update(technologies)
        category_counter["domain"].update(domains)
        category_counter["subtheme"].update(subthemes)
        for tag in all_tags:
            tag_to_documents[tag].append(source_file)

        if len(all_tags) >= 10:
            inflated_documents.append(
                {
                    "source_file": source_file,
                    "tag_count": len(all_tags),
                    "technology": technologies,
                    "domain": domains,
                    "subtheme": subthemes,
                    "all_tags": all_tags,
                }
            )

        if len(technologies) >= 3 or (len(domains) >= 4 and len(subthemes) >= 2):
            suspicious_cross_support.append(
                {
                    "source_file": source_file,
                    "technology": technologies,
                    "domain": domains,
                    "subtheme": subthemes,
                    "tag_count": len(all_tags),
                }
            )

    inflated_documents.sort(key=lambda item: (-int(item["tag_count"]), item["source_file"]))
    suspicious_cross_support.sort(key=lambda item: (-int(item["tag_count"]), item["source_file"]))

    inflated_tags = []
    for tag, count in tag_counter.most_common(top):
        inflated_tags.append(
            {
                "tag": tag,
                "document_count": count,
                "sample_documents": sorted(tag_to_documents[tag])[:5],
            }
        )

    return {
        "manifest_path": str(KNOWLEDGE_MANIFEST_PATH),
        "document_count": len(documents),
        "documents_with_many_tags": inflated_documents[:top],
        "inflated_tags": inflated_tags,
        "suspicious_cross_support": suspicious_cross_support[:top],
        "category_frequency": {
            category: [{"tag": tag, "document_count": count} for tag, count in counter.most_common(top)]
            for category, counter in category_counter.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostico simples de over-tagging na knowledge base")
    parser.add_argument("--top", type=int, default=10, help="Quantidade maxima por lista")
    parser.add_argument("--pretty", action="store_true", help="Renderiza JSON identado")
    args = parser.parse_args()

    payload = build_knowledge_tag_diagnostics(top=max(1, args.top))
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
