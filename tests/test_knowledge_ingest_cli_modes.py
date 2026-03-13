import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import app.services.knowledge_ingest as knowledge_ingest


class KnowledgeIngestCliModesTests(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, str]:
        stdout = io.StringIO()
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(stdout):
            code = knowledge_ingest.main()
        return int(code), stdout.getvalue()

    def _extract_json_after_marker(self, text: str, marker: str) -> dict:
        self.assertIn(marker, text)
        tail = text.split(marker, 1)[1]
        start = tail.find("{")
        self.assertGreaterEqual(start, 0)
        payload = tail[start:].strip()
        return json.loads(payload)

    def test_dry_run_single_prefix_outputs_valid_json_contract(self) -> None:
        raw_file = knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md"

        with patch.object(knowledge_ingest, "list_raw_files", return_value=[raw_file]):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--dry-run",
                ]
            )

        self.assertEqual(code, 0)
        payload = self._extract_json_after_marker(out, "Ingestão - dry-run:")
        self.assertEqual(payload["selection_mode"], "resolved_from_source_prefix")
        self.assertEqual(payload["source_prefixes"], ["continuity_docs_selected"])
        self.assertEqual(payload["files_found_by_prefix"], {"continuity_docs_selected": 1})
        self.assertEqual(payload["total_found"], 1)
        self.assertEqual(payload["targets_sample"], ["continuity_docs_selected/docs/a.md"])

    def test_dry_run_multi_prefix_outputs_combined_counts(self) -> None:
        raw_files = [
            knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md",
            knowledge_ingest.RAW_DIR / "terraform_docs_selected_incremental/docs/b.md",
        ]

        with patch.object(knowledge_ingest, "list_raw_files", return_value=raw_files):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--source-prefix",
                    "terraform_docs_selected_incremental/",
                    "--dry-run",
                ]
            )

        self.assertEqual(code, 0)
        payload = self._extract_json_after_marker(out, "Ingestão - dry-run:")
        self.assertEqual(
            payload["source_prefixes"],
            ["continuity_docs_selected", "terraform_docs_selected_incremental"],
        )
        self.assertEqual(
            payload["files_found_by_prefix"],
            {"continuity_docs_selected": 1, "terraform_docs_selected_incremental": 1},
        )
        self.assertEqual(payload["total_found"], 2)
        self.assertEqual(len(payload["targets_sample"]), 2)

    def test_dry_run_strict_missing_prefix_fails_cleanly(self) -> None:
        with patch.object(knowledge_ingest, "list_raw_files", return_value=[]):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--source-prefix",
                    "missing/",
                    "--strict-source-prefix",
                    "--dry-run",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("strict-source-prefix habilitado e nenhum arquivo encontrado", out)

    def test_dry_run_has_zero_side_effects(self) -> None:
        raw_file = knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md"

        with (
            patch.object(knowledge_ingest, "list_raw_files", return_value=[raw_file]),
            patch.object(knowledge_ingest, "ensure_knowledge_dirs") as ensure_dirs,
            patch.object(knowledge_ingest, "load_state") as load_state,
            patch.object(knowledge_ingest, "write_state") as write_state,
            patch.object(knowledge_ingest, "write_index_manifest") as write_manifest,
            patch.object(knowledge_ingest, "parse_file") as parse_file,
            patch.object(knowledge_ingest, "write_parsed_payload") as write_parsed,
            patch.object(knowledge_ingest, "write_chunk_payload") as write_chunk,
            patch.object(knowledge_ingest, "ingest_knowledge_base_min") as ingest_semantic,
        ):
            code, _ = self._run_main(
                [
                    "knowledge_ingest",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--dry-run",
                ]
            )

        self.assertEqual(code, 0)
        ensure_dirs.assert_not_called()
        load_state.assert_not_called()
        write_state.assert_not_called()
        write_manifest.assert_not_called()
        parse_file.assert_not_called()
        write_parsed.assert_not_called()
        write_chunk.assert_not_called()
        ingest_semantic.assert_not_called()

    def test_list_targets_single_prefix_outputs_valid_json_contract(self) -> None:
        raw_file = knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md"
        state = {"files": {"continuity_docs_selected/docs/a.md": {}, "other/x.md": {}}}

        with (
            patch.object(knowledge_ingest, "list_raw_files", return_value=[raw_file]),
            patch.object(knowledge_ingest, "load_state", return_value=state),
        ):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--semantic-persist",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--list-targets",
                ]
            )

        self.assertEqual(code, 0)
        payload = self._extract_json_after_marker(out, "Persistência semântica - list-targets:")
        self.assertEqual(payload["selection_mode"], "resolved_from_source_prefix")
        self.assertEqual(payload["source_prefixes"], ["continuity_docs_selected"])
        self.assertEqual(payload["source_files_resolved_by_prefix"], {"continuity_docs_selected": 1})
        self.assertEqual(payload["source_files_resolved_total"], 1)
        self.assertEqual(payload["source_files_sample"], ["continuity_docs_selected/docs/a.md"])

    def test_list_targets_multi_prefix_outputs_combined_counts(self) -> None:
        raw_files = [
            knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md",
            knowledge_ingest.RAW_DIR / "terraform_docs_selected_incremental/docs/b.md",
        ]
        state = {
            "files": {
                "continuity_docs_selected/docs/a.md": {},
                "terraform_docs_selected_incremental/docs/b.md": {},
                "other/x.md": {},
            }
        }

        with (
            patch.object(knowledge_ingest, "list_raw_files", return_value=raw_files),
            patch.object(knowledge_ingest, "load_state", return_value=state),
        ):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--semantic-persist",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--source-prefix",
                    "terraform_docs_selected_incremental/",
                    "--list-targets",
                ]
            )

        self.assertEqual(code, 0)
        payload = self._extract_json_after_marker(out, "Persistência semântica - list-targets:")
        self.assertEqual(
            payload["source_prefixes"],
            ["continuity_docs_selected", "terraform_docs_selected_incremental"],
        )
        self.assertEqual(
            payload["source_files_resolved_by_prefix"],
            {"continuity_docs_selected": 1, "terraform_docs_selected_incremental": 1},
        )
        self.assertEqual(payload["source_files_resolved_total"], 2)

    def test_list_targets_with_semantic_source_file_keeps_explicit_mode(self) -> None:
        with patch.object(knowledge_ingest, "list_raw_files", return_value=[]):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--semantic-persist",
                    "--semantic-source-file",
                    "continuity_docs_selected/docs/a.md",
                    "--list-targets",
                ]
            )

        self.assertEqual(code, 0)
        payload = self._extract_json_after_marker(out, "Persistência semântica - list-targets:")
        self.assertEqual(payload["selection_mode"], "explicit_source_file")
        self.assertEqual(payload["source_prefixes"], [])
        self.assertEqual(payload["source_files_resolved_total"], 1)
        self.assertEqual(payload["source_files_sample"], ["continuity_docs_selected/docs/a.md"])

    def test_list_targets_strict_missing_prefix_fails_cleanly(self) -> None:
        with patch.object(knowledge_ingest, "list_raw_files", return_value=[]):
            code, out = self._run_main(
                [
                    "knowledge_ingest",
                    "--semantic-persist",
                    "--source-prefix",
                    "missing/",
                    "--strict-source-prefix",
                    "--list-targets",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("strict-source-prefix habilitado e nenhum arquivo encontrado", out)

    def test_list_targets_has_zero_side_effects(self) -> None:
        raw_file = knowledge_ingest.RAW_DIR / "continuity_docs_selected/docs/a.md"
        state = {"files": {"continuity_docs_selected/docs/a.md": {}}}

        with (
            patch.object(knowledge_ingest, "list_raw_files", return_value=[raw_file]),
            patch.object(knowledge_ingest, "load_state", return_value=state) as load_state,
            patch.object(knowledge_ingest, "ensure_knowledge_dirs") as ensure_dirs,
            patch.object(knowledge_ingest, "write_state") as write_state,
            patch.object(knowledge_ingest, "write_index_manifest") as write_manifest,
            patch.object(knowledge_ingest, "parse_file") as parse_file,
            patch.object(knowledge_ingest, "write_parsed_payload") as write_parsed,
            patch.object(knowledge_ingest, "write_chunk_payload") as write_chunk,
            patch.object(knowledge_ingest, "ingest_knowledge_base_min") as ingest_semantic,
        ):
            code, _ = self._run_main(
                [
                    "knowledge_ingest",
                    "--semantic-persist",
                    "--source-prefix",
                    "continuity_docs_selected/",
                    "--list-targets",
                ]
            )

        self.assertEqual(code, 0)
        self.assertTrue(load_state.called)
        ensure_dirs.assert_not_called()
        write_state.assert_not_called()
        write_manifest.assert_not_called()
        parse_file.assert_not_called()
        write_parsed.assert_not_called()
        write_chunk.assert_not_called()
        ingest_semantic.assert_not_called()


if __name__ == "__main__":
    unittest.main()
