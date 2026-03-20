import yaml
from pathlib import Path

from app.core import config


def load_domain(name: str) -> dict:
    path = config.DOMAINS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"domain spec not found: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def list_domains() -> list[Path]:
    return sorted(config.DOMAINS_DIR.glob("*.yaml"))
