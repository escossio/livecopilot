import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    raise SystemExit("requests is required to run the crawler")

ROOT_DIR = Path(__file__).resolve().parents[2]
MANIFEST_MAP = {
    "azure": ROOT_DIR / "docs" / "AZURE_SOURCE_MANIFEST.json",
    "reactjs": ROOT_DIR / "docs" / "REACTJS_SOURCE_MANIFEST.json",
    "aws": ROOT_DIR / "docs" / "AWS_SOURCE_MANIFEST.json",
    "machine_learning": ROOT_DIR / "docs" / "MACHINE_LEARNING_SOURCE_MANIFEST.json",
}
TARGET_MAP = {
    "azure": ROOT_DIR / "data" / "knowledge_raw" / "azure",
    "reactjs": ROOT_DIR / "data" / "knowledge_raw" / "reactjs",
    "aws": ROOT_DIR / "data" / "knowledge_raw" / "aws",
    "machine_learning": ROOT_DIR / "data" / "knowledge_raw" / "machine_learning",
}


def slugify(value: str) -> str:
    normalized = "".join(
        ch if ch.isalnum() else "_" for ch in value.strip().lower()
    )
    return "_".join(filter(None, normalized.split("_")))


def download_url(url: str, timeout: int = 30) -> bytes:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def file_exists(path: Path) -> bool:
    return path.exists()


def main(front: str) -> None:
    manifest_path = MANIFEST_MAP.get(front)
    if not manifest_path or not manifest_path.exists():
        raise SystemExit(f"manifest not found for front '{front}'")

    target_dir = TARGET_MAP[front]
    target_dir.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    if isinstance(manifest, dict):
        entries = manifest.get("sources", [])
    else:
        entries = manifest

    allowed_domains = {
        urlparse(entry["url"]).netloc.lower() for entry in entries
    }
    downloaded = 0

    logging.info("Starting crawl for front %s", front)

    for entry in entries:
        url = entry["url"]
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain not in allowed_domains:
            logging.warning("Skipping url outside allowed domains: %s", url)
            continue

        category = entry.get("category", "MISC")
        category_dir = "_".join(
            token.lower()
            for token in category.replace("/", " ").split()
            if token
        )
        if not category_dir:
            category_dir = "misc"
        dest_dir = target_dir / category_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        name = entry.get("name", parsed.path.strip("/").split("/")[-1] or "page")
        filename = f"{slugify(name)}.html"
        html_path = dest_dir / filename
        metadata_path = dest_dir / f"{slugify(name)}.metadata.json"

        if file_exists(html_path) and file_exists(metadata_path):
            logging.info("Already downloaded: %s", url)
            continue

        logging.info("Downloading %s", url)
        try:
            content = download_url(url)
        except Exception as exc:  # pragma: no cover
            logging.error("Failed to download %s: %s", url, exc)
            continue

        html_path.write_bytes(content)

        metadata = {
            "url": url,
            "domain": domain,
            "download_timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "content_hash": hashlib.sha256(content).hexdigest(),
            "content_type": "html",
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        logging.info("Saved %s (%d bytes)", html_path.name, len(content))
        downloaded += 1

    logging.info("Crawl completed for front %s (%d pages)", front, downloaded)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    parser = argparse.ArgumentParser(description="Materialize corpus from a front manifest")
    parser.add_argument("front", choices=MANIFEST_MAP.keys(), help="front name (azure, reactjs, aws)")
    args = parser.parse_args()
    main(args.front)
