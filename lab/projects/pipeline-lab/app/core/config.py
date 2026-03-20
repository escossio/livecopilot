from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DOMAINS_DIR = BASE_DIR / "domains"
RUNS_STORE = BASE_DIR / "app" / "storage" / "runs.json"
PIPELINE_STAGES = [
    "source_policy",
    "source_manifest",
    "corpus_freeze",
    "parsing",
    "chunking",
    "lexical_validation",
    "chunk_refinement",
    "semantic_baseline",
    "semantic_refinement",
    "domain_closure",
]
