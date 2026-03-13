import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_SCRIPT = PROJECT_ROOT / "scripts" / "knowledge_pipeline.sh"
EXISTING_PREFIX = "continuity_docs_selected/"


@unittest.skipUnless(shutil.which("bash"), "bash nao disponivel")
class KnowledgePipelineCliContractTests(unittest.TestCase):
    maxDiff = None

    def _run_pipeline(self, args: list[str], artifact_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(PIPELINE_SCRIPT), *args, "--artifact-dir", str(artifact_dir)],
            cwd=PROJECT_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_plan_mode_emits_wrapped_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_dir = Path(tmp_dir)
            round_id = "test-plan-contract"
            result = self._run_pipeline(
                [
                    "--mode",
                    "plan",
                    "--round-id",
                    round_id,
                    "--source-prefix",
                    EXISTING_PREFIX,
                ],
                artifact_dir,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["pipeline"], "knowledge_pipeline_v1")
            self.assertEqual(payload["mode"], "plan")
            self.assertEqual(payload["round_id"], round_id)
            self.assertEqual(payload["plan"]["source_prefixes"], ["continuity_docs_selected"])

            artifact_path = artifact_dir / f"knowledge_pipeline_plan_{round_id}.json"
            self.assertTrue(artifact_path.exists())
            saved = json.loads(artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["plan"]["plan_mode"], "prefix_round_preview")

    def test_validate_mode_consumes_existing_run_artifact_and_emits_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_dir = Path(tmp_dir)
            round_id = "test-validate-contract"
            run_artifact = artifact_dir / f"knowledge_pipeline_run_{round_id}.json"
            run_artifact.write_text(
                json.dumps(
                    {
                        "pipeline": "knowledge_pipeline_v1",
                        "mode": "run",
                        "round_id": round_id,
                        "config": {
                            "source_prefixes": ["continuity_docs_selected"],
                        },
                        "ingest": {
                            "total_found": 12,
                            "processed": 0,
                        },
                        "semantic": {
                            "source_files_resolved_total": 12,
                            "documents_selected": 12,
                            "documents_processed": 12,
                            "chunks_persisted": 39,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = self._run_pipeline(
                [
                    "--mode",
                    "validate",
                    "--round-id",
                    round_id,
                    "--source-prefix",
                    EXISTING_PREFIX,
                ],
                artifact_dir,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["pipeline"], "knowledge_pipeline_v1")
            self.assertEqual(payload["mode"], "validate")
            self.assertEqual(payload["round_id"], round_id)
            self.assertIn("checks", payload)
            self.assertIn("utf8_summary", payload)

            validate_artifact = artifact_dir / f"knowledge_pipeline_validate_{round_id}.json"
            utf8_artifact = artifact_dir / f"knowledge_pipeline_validate_utf8_{round_id}.json"
            self.assertTrue(validate_artifact.exists())
            self.assertTrue(utf8_artifact.exists())


if __name__ == "__main__":
    unittest.main()
