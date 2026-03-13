import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.knowledge_pipeline_semantic_validate as semantic_validate


class KnowledgePipelineSemanticValidateTests(unittest.TestCase):
    def test_derive_smoke_queries_prefers_non_handoff_files(self) -> None:
        queries = semantic_validate.derive_smoke_queries(
            [
                "continuity_docs_selected/docs/HANDOFF_TERRAFORM_THRESHOLD_DIAGNOSIS_20260312T174039Z.md",
                "continuity_docs_selected/docs/UTF8_HYGIENE_SCANNER.md",
                "continuity_docs_selected/docs/SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md",
            ],
            limit=2,
        )

        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0]["expected_source_file"], "continuity_docs_selected/docs/SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md")
        self.assertEqual(queries[0]["query"], "semantic closeout checklist")
        self.assertEqual(queries[1]["query"], "utf8 hygiene scanner")

    def test_main_emits_minimum_contract_with_mocked_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_dir = Path(tmp_dir)
            round_id = "semantic-validate-contract"
            run_artifact = artifact_dir / f"knowledge_pipeline_run_{round_id}.json"
            run_artifact.write_text(
                json.dumps(
                    {
                        "config": {"source_prefixes": ["continuity_docs_selected"]},
                        "semantic": {
                            "embedding_mode_used": "mock",
                            "results": [
                                {"source_file": "continuity_docs_selected/docs/SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md"},
                                {"source_file": "continuity_docs_selected/docs/UTF8_HYGIENE_SCANNER.md"},
                            ],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            def fake_search(*, query: str, limit: int, embedding_mode: str, source_file: str | None = None) -> dict:
                mapping = {
                    "semantic closeout checklist": "continuity_docs_selected/docs/SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md",
                    "utf8 hygiene scanner": "continuity_docs_selected/docs/UTF8_HYGIENE_SCANNER.md",
                }
                resolved_source_file = mapping[query]
                similarity = 0.99 if source_file == resolved_source_file else 0.01
                return {
                    "semantic_path": "embedding_cache",
                    "search_cache_hit": False,
                    "embedding_cache_hit": False,
                    "semantic_duration_ms": 1,
                    "results": [
                        {
                            "source_file": resolved_source_file,
                            "chunk_id": "chunk::1",
                            "title": query,
                            "similarity": similarity,
                            "snippet": query,
                        }
                    ],
                }

            stdout = io.StringIO()
            argv = [
                "knowledge_pipeline_semantic_validate",
                "--round-id",
                round_id,
                "--artifact-dir",
                str(artifact_dir),
                "--source-prefix",
                "continuity_docs_selected/",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(semantic_validate, "semantic_search_with_mode", side_effect=fake_search),
                contextlib.redirect_stdout(stdout),
            ):
                code = semantic_validate.main()

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["mode"], "semantic-validate")
            self.assertEqual(payload["search_scope"], "round_scope_only")
            self.assertTrue(payload["semantic_smoke_passed"])
            self.assertEqual(payload["aggregate"]["top1_expected_prefix_count"], 2)
            self.assertEqual(payload["aggregate"]["top1_expected_source_file_count"], 2)
            self.assertEqual(payload["aggregate"]["topk_expected_source_file_count"], 2)

            artifact_path = artifact_dir / f"knowledge_pipeline_semantic_validate_{round_id}.json"
            self.assertTrue(artifact_path.exists())


if __name__ == "__main__":
    unittest.main()
