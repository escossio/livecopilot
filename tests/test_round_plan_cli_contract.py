import hashlib
import json
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROUND_PLAN_SCRIPT = PROJECT_ROOT / "scripts" / "round_plan.sh"
EXISTING_PREFIX = "continuity_docs_selected/"
SECOND_PREFIX = "terraform_docs_selected_incremental/"
MISSING_PREFIX = "__prefixo_que_nao_existe__/"


class RoundPlanCliContractTests(unittest.TestCase):
    maxDiff = None

    def _run_round_plan(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(ROUND_PLAN_SCRIPT), *args],
            cwd=PROJECT_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def _snapshot_existing_state_files(self) -> dict[str, dict[str, str | int]]:
        tracked = [
            PROJECT_ROOT / "source_files",
            PROJECT_ROOT / "data" / "knowledge_state.json",
            PROJECT_ROOT / "var" / "semantic_min.db",
        ]
        snapshot: dict[str, dict[str, str | int]] = {}
        for path in tracked:
            if not path.exists():
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            stat = path.stat()
            snapshot[str(path.relative_to(PROJECT_ROOT))] = {
                "sha256": digest,
                "size": int(stat.st_size),
            }
        return snapshot

    def _assert_contract_fields(self, payload: dict) -> None:
        for field in (
            "plan_mode",
            "source_prefixes",
            "ingest_dry_run",
            "semantic_list_targets",
            "totals",
            "divergence",
        ):
            self.assertIn(field, payload)

    def test_round_plan_json_single_prefix_contract(self) -> None:
        result = self._run_round_plan(["--source-prefix", EXISTING_PREFIX, "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self._assert_contract_fields(payload)
        self.assertEqual(payload["plan_mode"], "prefix_round_preview")
        self.assertEqual(payload["source_prefixes"], ["continuity_docs_selected"])
        self.assertIn("selection_mode", payload["ingest_dry_run"])
        self.assertIn("selection_mode", payload["semantic_list_targets"])

    def test_round_plan_json_multi_prefix_contract(self) -> None:
        result = self._run_round_plan(
            [
                "--source-prefix",
                EXISTING_PREFIX,
                "--source-prefix",
                SECOND_PREFIX,
                "--json",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self._assert_contract_fields(payload)
        self.assertEqual(
            payload["source_prefixes"],
            ["continuity_docs_selected", "terraform_docs_selected_incremental"],
        )
        self.assertGreaterEqual(int(payload["totals"]["ingest_total_found"]), 0)
        self.assertGreaterEqual(int(payload["totals"]["semantic_total_source_files"]), 0)

    def test_round_plan_human_output_has_header_and_embedded_json(self) -> None:
        result = self._run_round_plan(["--source-prefix", EXISTING_PREFIX])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ROUND PLAN (prefix preview)", result.stdout)
        self.assertIn("- Prefixos:", result.stdout)
        json_start = result.stdout.find("{")
        self.assertGreaterEqual(json_start, 0)
        payload = json.loads(result.stdout[json_start:])
        self._assert_contract_fields(payload)

    def test_round_plan_missing_prefix_with_strict_fails_cleanly(self) -> None:
        result = self._run_round_plan(
            [
                "--source-prefix",
                MISSING_PREFIX,
                "--strict-source-prefix",
            ]
        )
        self.assertEqual(result.returncode, 2)
        joined = f"{result.stdout}\n{result.stderr}"
        self.assertIn("strict-source-prefix habilitado e nenhum arquivo encontrado", joined)

    def test_round_plan_json_has_no_side_effects_on_existing_state_files(self) -> None:
        before = self._snapshot_existing_state_files()
        result = self._run_round_plan(["--source-prefix", EXISTING_PREFIX, "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        _ = json.loads(result.stdout)
        after = self._snapshot_existing_state_files()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
