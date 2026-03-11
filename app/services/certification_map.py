import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
CERT_MAP_DIR = BASE_DIR / "data" / "certifications"


def load_certification_map(track: str = "python") -> dict[str, Any]:
    map_path = CERT_MAP_DIR / f"{track}_cert_map.json"
    if not map_path.exists():
        raise FileNotFoundError(f"Certification map not found: {map_path}")
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Invalid certification map format")
    return payload


def iter_domains(track: str = "python") -> list[dict[str, Any]]:
    payload = load_certification_map(track)
    domains: list[dict[str, Any]] = []
    for cert in payload.get("certifications", []):
        if not isinstance(cert, dict):
            continue
        for domain in cert.get("domains", []):
            if not isinstance(domain, dict):
                continue
            domains.append(
                {
                    "track": payload.get("track", track),
                    "provider": cert.get("provider") or payload.get("provider", ""),
                    "certification": cert.get("certification", ""),
                    "level": cert.get("level", ""),
                    "domain": domain.get("domain", ""),
                    "domain_name": domain.get("name", ""),
                    "topics": domain.get("topics", []),
                }
            )
    return domains
