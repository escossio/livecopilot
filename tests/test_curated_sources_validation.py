import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.curated_sources import (
    _build_candidate_consistency,
    _main,
    build_candidate_promotion_log_report,
    build_candidate_review_report,
    build_candidate_audit_summary_report,
    build_candidate_listing_report,
    inspect_promotion_candidate,
    build_candidate_metadata_audit_report,
    build_candidate_operational_audit_report,
    build_candidate_semantic_audit_report,
    build_candidate_stats_report,
    build_target_match_inspection_report,
    build_curated_sources_report,
    build_candidate_validation_report,
    promote_source_candidate,
    reconcile_target_match_candidate,
    reclassify_candidate_destination,
    record_candidate_review_decision,
    render_candidate_listing_report,
    render_candidate_promotion_log_report,
    render_candidate_review_report,
    render_promotion_check_report,
    register_source_candidate,
)


class CuratedSourcesValidationTests(unittest.TestCase):
    def test_render_candidate_promotion_log_report_compact_with_history(self) -> None:
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "has_promotion_history": True,
            "promotion_log_count": 2,
            "promotion_log": [
                {
                    "promoted_at": "2026-02-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/old.md",
                },
                {
                    "promoted_at": "2026-03-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/example.md",
                },
            ],
        }

        payload = json.loads(render_candidate_promotion_log_report(report, compact=True))

        self.assertEqual(
            payload,
            {
                "candidate_id": "local-question-bank",
                "exists": True,
                "has_promotion_history": True,
                "promotion_log_count": 2,
                "latest_promotion": {
                    "promoted_at": "2026-03-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/example.md",
                },
            },
        )

    def test_render_candidate_promotion_log_report_compact_without_history(self) -> None:
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "has_promotion_history": False,
            "promotion_log_count": 0,
            "promotion_log": [],
        }

        payload = json.loads(render_candidate_promotion_log_report(report, compact=True))

        self.assertEqual(
            payload,
            {
                "candidate_id": "local-question-bank",
                "exists": True,
                "has_promotion_history": False,
                "promotion_log_count": 0,
            },
        )

    def test_build_candidate_promotion_log_report_handles_missing_candidate(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
        ):
            payload = build_candidate_promotion_log_report("missing-candidate")

        self.assertFalse(payload["exists"])
        self.assertFalse(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 0)
        self.assertEqual(payload["promotion_log"], [])

    def test_build_candidate_promotion_log_report_handles_candidate_without_history(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "promotion_log": [],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            payload = build_candidate_promotion_log_report("local-question-bank")

        self.assertTrue(payload["exists"])
        self.assertFalse(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 0)
        self.assertEqual(payload["promotion_log"], [])

    def test_cli_show_promotion_log_with_compact_reduces_payload(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "show-promotion-log",
            "--candidate-id",
            "local-question-bank",
            "--compact",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "has_promotion_history": True,
            "promotion_log_count": 2,
            "promotion_log": [
                {
                    "promoted_at": "2026-02-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/old.md",
                },
                {
                    "promoted_at": "2026-03-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/example.md",
                },
            ],
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.build_candidate_promotion_log_report", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {"candidate_id", "exists", "has_promotion_history", "promotion_log_count", "latest_promotion"},
        )

    def test_cli_show_promotion_log_with_compact_and_latest_only_stays_consistent(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "show-promotion-log",
            "--candidate-id",
            "local-question-bank",
            "--compact",
            "--latest-only",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "has_promotion_history": True,
            "promotion_log_count": 2,
            "promotion_log": [
                {
                    "promoted_at": "2026-02-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/old.md",
                },
                {
                    "promoted_at": "2026-03-01T00:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/example.md",
                },
            ],
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.build_candidate_promotion_log_report", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["promotion_log_count"], 2)
        self.assertEqual(payload["latest_promotion"]["promoted_artifact_path"], "data/question_bank_raw/example.md")

    def test_build_candidate_promotion_log_report_returns_full_history(self) -> None:
        promotion_log = [
            {
                "promoted_at": "2026-02-01T00:00:00+00:00",
                "promoted_to": "question_bank",
                "promoted_artifact_path": "data/question_bank_raw/old.md",
            },
            {
                "promoted_at": "2026-03-01T00:00:00+00:00",
                "promoted_to": "question_bank",
                "promoted_artifact_path": "data/question_bank_raw/example.md",
                "review_decision": "approved",
                "review_decided_at": "2026-02-28T00:00:00+00:00",
            },
        ]
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "promotion_log": promotion_log,
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            payload = build_candidate_promotion_log_report("local-question-bank")

        self.assertTrue(payload["exists"])
        self.assertTrue(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 2)
        self.assertEqual(payload["promotion_log"], promotion_log)

    def test_build_candidate_promotion_log_report_latest_only_returns_last_event(self) -> None:
        promotion_log = [
            {
                "promoted_at": "2026-02-01T00:00:00+00:00",
                "promoted_to": "question_bank",
                "promoted_artifact_path": "data/question_bank_raw/old.md",
            },
            {
                "promoted_at": "2026-03-01T00:00:00+00:00",
                "promoted_to": "question_bank",
                "promoted_artifact_path": "data/question_bank_raw/example.md",
            },
        ]
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "promotion_log": promotion_log,
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            payload = build_candidate_promotion_log_report("local-question-bank", latest_only=True)

        self.assertTrue(payload["exists"])
        self.assertTrue(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 2)
        self.assertEqual(payload["promotion_log"], [promotion_log[-1]])

    def test_build_candidate_promotion_log_report_latest_only_without_history_stays_empty(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "promotion_log": [],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            payload = build_candidate_promotion_log_report("local-question-bank", latest_only=True)

        self.assertTrue(payload["exists"])
        self.assertFalse(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 0)
        self.assertEqual(payload["promotion_log"], [])

    def test_record_candidate_review_decision_persists_fields(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "status": "candidate",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            payload = record_candidate_review_decision(
                "local-question-bank",
                "approved",
                notes="manual review ok",
            )

        self.assertEqual(payload["review_decision"], "approved")
        self.assertEqual(payload["review_notes"], "manual review ok")
        self.assertTrue(payload["review_decided_at"])
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(written_candidates[0]["review_decision"], "approved")

    def test_record_candidate_review_decision_rejects_invalid_decision(self) -> None:
        with self.assertRaisesRegex(ValueError, "decision must be one of"):
            record_candidate_review_decision("local-question-bank", "maybe")

    def test_record_candidate_review_decision_rejects_missing_candidate(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
        ):
            with self.assertRaisesRegex(ValueError, "candidate_id not found"):
                record_candidate_review_decision("missing-candidate", "approved")

    def test_record_candidate_review_decision_blocks_promoted_candidate(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "already-promoted",
                    "status": "promoted",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "already promoted"):
                record_candidate_review_decision("already-promoted", "approved")

    def test_reclassify_candidate_destination_persists_fields(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-coverage",
                    "status": "candidate",
                    "destination": "coverage_inputs",
                    "promotion_log": [],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
            patch("app.services.curated_sources.sync_destination_manifests") as sync_manifests,
        ):
            payload = reclassify_candidate_destination(
                "local-coverage",
                "knowledge",
                reason="manual reclassification after triage",
            )

        self.assertEqual(payload["destination"], "knowledge")
        self.assertEqual(payload["destination_changed_from"], "coverage_inputs")
        self.assertEqual(payload["destination_changed_reason"], "manual reclassification after triage")
        self.assertTrue(payload["destination_changed_at"])
        self.assertEqual(len(payload["destination_change_log"]), 1)
        self.assertEqual(payload["destination_change_log"][0]["destination_changed_to"], "knowledge")
        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(payload["promotion_log"], [])
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(written_candidates[0]["destination"], "knowledge")
        sync_manifests.assert_called_once()

    def test_reclassify_candidate_destination_rejects_missing_candidate(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
        ):
            with self.assertRaisesRegex(ValueError, "candidate_id not found"):
                reclassify_candidate_destination("missing-candidate", "knowledge")

    def test_reclassify_candidate_destination_blocks_promoted_candidate(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "already-promoted",
                    "status": "promoted",
                    "destination": "question_bank",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "already promoted"):
                reclassify_candidate_destination("already-promoted", "knowledge")

    def test_reclassify_candidate_destination_rejects_same_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-coverage",
                    "status": "candidate",
                    "destination": "coverage_inputs",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "already set to the requested value"):
                reclassify_candidate_destination("local-coverage", "coverage_inputs")

    def test_reclassify_candidate_destination_does_not_touch_promotion_log_or_status(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-coverage",
                    "status": "candidate",
                    "destination": "coverage_inputs",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "knowledge",
                            "promoted_artifact_path": "data/knowledge_raw/example.md",
                        }
                    ],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest"),
            patch("app.services.curated_sources.sync_destination_manifests"),
        ):
            payload = reclassify_candidate_destination("local-coverage", "knowledge")

        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(len(payload["promotion_log"]), 1)

    def test_render_candidate_review_report_compact_reduces_payload(self) -> None:
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "identity": {
                "title": "Local Question Bank",
                "destination": "question_bank",
                "status": "candidate",
                "trust_level": "medium_trust",
            },
            "artifact": {
                "artifact_path": "data/source_candidates/files/question_bank/example.md",
                "artifact_exists": True,
                "parser_hint": "markdown_index",
            },
            "review": {
                "review_decision": "approved",
                "review_decided_at": "2026-03-01T00:00:00+00:00",
                "review_notes": "manual review ok",
            },
            "promotion_history": {
                "has_promotion_history": True,
                "promotion_log_count": 2,
                "latest_promotion": {
                    "promoted_at": "2026-03-01T01:00:00+00:00",
                    "promoted_to": "question_bank",
                    "promoted_artifact_path": "data/question_bank_raw/example.md",
                },
            },
            "promotion_check": {
                "eligible": True,
                "eligibility_code": "eligible",
                "planned_target_path": "data/question_bank_raw/example.md",
                "would_copy": True,
                "target_already_matches": False,
                "has_conflict": False,
                "conflict_reason": "",
            },
            "audit_flags": ["audit_metadata:missing_notes"],
        }

        payload = json.loads(render_candidate_review_report(report, compact=True))

        self.assertEqual(
            payload,
            {
                "candidate_id": "local-question-bank",
                "exists": True,
                "title": "Local Question Bank",
                "destination": "question_bank",
                "status": "candidate",
                "trust_level": "medium_trust",
                "eligible": True,
                "eligibility_code": "eligible",
                "planned_target_path": "data/question_bank_raw/example.md",
                "would_copy": True,
                "target_already_matches": False,
                "has_conflict": False,
                "conflict_reason": "",
                "review_decision": "approved",
                "review_decided_at": "2026-03-01T00:00:00+00:00",
                "has_promotion_history": True,
                "promotion_log_count": 2,
                "audit_flags": ["audit_metadata:missing_notes"],
            },
        )

    def test_cli_review_candidate_without_compact_keeps_full_payload(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "review-candidate",
            "--candidate-id",
            "local-question-bank",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "identity": {
                "title": "Local Question Bank",
                "destination": "question_bank",
                "status": "candidate",
                "trust_level": "medium_trust",
            },
            "artifact": {
                "artifact_path": "data/source_candidates/files/question_bank/example.md",
                "artifact_exists": True,
                "parser_hint": "markdown_index",
            },
            "promotion_check": {
                "eligible": True,
                "eligibility_code": "eligible",
                "planned_target_path": "data/question_bank_raw/example.md",
                "would_copy": True,
                "target_already_matches": False,
                "has_conflict": False,
                "conflict_reason": "",
            },
            "audit_flags": [],
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.build_candidate_review_report", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertIn("identity", payload)
        self.assertIn("artifact", payload)
        self.assertIn("promotion_check", payload)

    def test_cli_review_candidate_with_compact_reduces_payload(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "review-candidate",
            "--candidate-id",
            "local-question-bank",
            "--compact",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "identity": {
                "title": "Local Question Bank",
                "destination": "question_bank",
                "status": "candidate",
                "trust_level": "medium_trust",
            },
            "artifact": {
                "artifact_path": "data/source_candidates/files/question_bank/example.md",
                "artifact_exists": True,
                "parser_hint": "markdown_index",
            },
            "promotion_check": {
                "eligible": True,
                "eligibility_code": "eligible",
                "planned_target_path": "data/question_bank_raw/example.md",
                "would_copy": True,
                "target_already_matches": False,
                "has_conflict": False,
                "conflict_reason": "",
            },
            "review": {},
            "audit_flags": ["audit_metadata:missing_notes"],
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.build_candidate_review_report", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {
                "candidate_id",
                "exists",
                "title",
                "destination",
                "status",
                "trust_level",
                "eligible",
                "eligibility_code",
                "planned_target_path",
                "would_copy",
                "target_already_matches",
                "has_conflict",
                "conflict_reason",
                "has_promotion_history",
                "promotion_log_count",
                "audit_flags",
            },
        )
        self.assertEqual(payload["eligible"], report["promotion_check"]["eligible"])
        self.assertEqual(payload["eligibility_code"], report["promotion_check"]["eligibility_code"])
        self.assertNotIn("review_decision", payload)
        self.assertNotIn("review_decided_at", payload)

    def test_build_candidate_review_report_returns_identity_artifact_and_preflight(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "discovered_from": "awesome-react",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "parser_hint": "markdown_index",
                }
            ]
        }
        promotion_check = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "planned_target_path": "data/question_bank_raw/example.md",
            "would_copy": True,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
            patch("app.services.curated_sources._collect_candidate_audit_flags", return_value=[]),
        ):
            payload = build_candidate_review_report("local-question-bank")

        self.assertTrue(payload["exists"])
        self.assertEqual(payload["identity"]["title"], "Local Question Bank")
        self.assertEqual(payload["identity"]["discovered_from"], "awesome-react")
        self.assertEqual(payload["artifact"]["artifact_path"], "data/source_candidates/files/question_bank/example.md")
        self.assertTrue(payload["artifact"]["artifact_exists"])
        self.assertIsNone(payload["review"]["review_decision"])
        self.assertFalse(payload["promotion_history"]["has_promotion_history"])
        self.assertEqual(payload["promotion_history"]["promotion_log_count"], 0)
        self.assertIsNone(payload["promotion_history"]["latest_promotion"])
        self.assertEqual(payload["promotion_check"]["eligibility_code"], "eligible")
        self.assertEqual(payload["audit_flags"], [])

    def test_build_candidate_review_report_handles_missing_candidate(self) -> None:
        promotion_check = {
            "candidate_id": "missing-candidate",
            "exists": False,
            "eligible": False,
            "eligibility_code": "candidate_not_found",
            "blocking_reason": "candidate_id not found: missing-candidate",
            "reasons": ["candidate_id not found: missing-candidate"],
            "planned_target_path": None,
            "would_copy": False,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
        ):
            payload = build_candidate_review_report("missing-candidate")

        self.assertFalse(payload["exists"])
        self.assertEqual(payload["identity"]["candidate_id"], "missing-candidate")
        self.assertIsNone(payload["review"]["review_decision"])
        self.assertFalse(payload["promotion_history"]["has_promotion_history"])
        self.assertEqual(payload["promotion_check"]["eligibility_code"], "candidate_not_found")
        self.assertEqual(payload["audit_flags"], [])

    def test_build_candidate_review_report_exposes_blocking_preflight(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "web-knowledge",
                    "title": "Web Knowledge",
                    "source_origin": "web",
                    "source_kind": "knowledge_document",
                    "trust_level": "high_trust",
                    "destination": "knowledge",
                    "status": "candidate",
                    "discovered_from": "awesome-python",
                    "parser_hint": "html",
                }
            ]
        }
        promotion_check = {
            "candidate_id": "web-knowledge",
            "exists": True,
            "eligible": False,
            "eligibility_code": "non_local_source",
            "blocking_reason": "manual promotion currently supports only local_file candidates",
            "reasons": ["manual promotion currently supports only local_file candidates"],
            "planned_target_path": None,
            "would_copy": False,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
            patch("app.services.curated_sources._collect_candidate_audit_flags", return_value=[]),
        ):
            payload = build_candidate_review_report("web-knowledge")

        self.assertFalse(payload["promotion_check"]["eligible"])
        self.assertEqual(payload["promotion_check"]["eligibility_code"], "non_local_source")
        self.assertEqual(payload["identity"]["source_origin"], "web")

    def test_build_candidate_review_report_summarizes_audit_flags(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "parser_hint": "markdown_index",
                }
            ]
        }
        promotion_check = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "planned_target_path": "data/question_bank_raw/example.md",
            "would_copy": True,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
            patch(
                "app.services.curated_sources._collect_candidate_audit_flags",
                return_value=["audit_metadata:missing_notes", "audit_operational:missing_discovered_from"],
            ),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_review_report("local-question-bank")

        self.assertEqual(
            payload["audit_flags"],
            ["audit_metadata:missing_notes", "audit_operational:missing_discovered_from"],
        )

    def test_build_candidate_review_report_exposes_review_fields_when_present(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "parser_hint": "markdown_index",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                    "review_notes": "manual review ok",
                }
            ]
        }
        promotion_check = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "planned_target_path": "data/question_bank_raw/example.md",
            "would_copy": True,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
            patch("app.services.curated_sources._collect_candidate_audit_flags", return_value=[]),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_review_report("local-question-bank")

        self.assertEqual(payload["review"]["review_decision"], "approved")
        self.assertEqual(payload["review"]["review_decided_at"], "2026-03-01T00:00:00+00:00")
        self.assertEqual(payload["review"]["review_notes"], "manual review ok")

    def test_build_candidate_review_report_summarizes_promotion_history_when_present(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "promoted",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "parser_hint": "markdown_index",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-02-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/old.md",
                        },
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                            "review_decision": "approved",
                            "review_decided_at": "2026-02-28T00:00:00+00:00",
                        },
                    ],
                }
            ]
        }
        promotion_check = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": False,
            "eligibility_code": "already_promoted",
            "planned_target_path": "data/question_bank_raw/example.md",
            "would_copy": False,
            "target_already_matches": True,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
            patch("app.services.curated_sources._collect_candidate_audit_flags", return_value=[]),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_review_report("local-question-bank")

        self.assertTrue(payload["promotion_history"]["has_promotion_history"])
        self.assertEqual(payload["promotion_history"]["promotion_log_count"], 2)
        self.assertEqual(
            payload["promotion_history"]["latest_promotion"]["promoted_artifact_path"],
            "data/question_bank_raw/example.md",
        )
        self.assertEqual(payload["promotion_history"]["latest_promotion"]["review_decision"], "approved")

    def test_render_promotion_check_report_compact_keeps_decision_fields(self) -> None:
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "blocking_reason": "",
            "reasons": [],
            "source_origin": "local_file",
            "status": "candidate",
            "destination": "question_bank",
            "artifact_path": "data/source_candidates/files/question_bank/example.md",
            "artifact_exists": True,
            "promotable_destination": True,
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_already_matches": False,
            "would_copy": True,
            "has_conflict": False,
            "conflict_reason": "",
            "review_decision": "approved",
            "review_decided_at": "2026-03-01T00:00:00+00:00",
        }

        payload = json.loads(render_promotion_check_report(report, compact=True))

        self.assertEqual(
            payload,
            {
                "candidate_id": "local-question-bank",
                "eligible": True,
                "eligibility_code": "eligible",
                "planned_target_path": "data/question_bank_raw/example.md",
                "would_copy": True,
                "target_already_matches": False,
                "has_conflict": False,
                "conflict_reason": "",
                "review_decision": "approved",
                "review_decided_at": "2026-03-01T00:00:00+00:00",
            },
        )

    def test_render_promotion_check_report_compact_keeps_exists_when_missing(self) -> None:
        report = {
            "candidate_id": "missing",
            "exists": False,
            "eligible": False,
            "eligibility_code": "candidate_not_found",
            "planned_target_path": None,
            "would_copy": False,
            "target_already_matches": False,
            "has_conflict": False,
            "conflict_reason": "",
        }

        payload = json.loads(render_promotion_check_report(report, compact=True))

        self.assertEqual(payload["exists"], False)
        self.assertEqual(payload["eligibility_code"], "candidate_not_found")

    def test_cli_check_promotion_without_compact_keeps_full_payload(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "check-promotion",
            "--candidate-id",
            "local-question-bank",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "blocking_reason": "",
            "reasons": [],
            "source_origin": "local_file",
            "status": "candidate",
            "destination": "question_bank",
            "artifact_path": "data/source_candidates/files/question_bank/example.md",
            "artifact_exists": True,
            "promotable_destination": True,
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_already_matches": False,
            "would_copy": True,
            "has_conflict": False,
            "conflict_reason": "",
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertIn("blocking_reason", payload)
        self.assertIn("reasons", payload)
        self.assertIn("artifact_path", payload)

    def test_cli_check_promotion_with_compact_reduces_payload(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "check-promotion",
            "--candidate-id",
            "local-question-bank",
            "--compact",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": True,
            "eligibility_code": "eligible",
            "blocking_reason": "",
            "reasons": [],
            "source_origin": "local_file",
            "status": "candidate",
            "destination": "question_bank",
            "artifact_path": "data/source_candidates/files/question_bank/example.md",
            "artifact_exists": True,
            "promotable_destination": True,
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_already_matches": False,
            "would_copy": True,
            "has_conflict": False,
            "conflict_reason": "",
        }
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                }
            ]
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=report),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {
                "candidate_id",
                "eligible",
                "eligibility_code",
                "planned_target_path",
                "would_copy",
                "target_already_matches",
                "has_conflict",
                "conflict_reason",
                "review_decision",
                "review_decided_at",
            },
        )
        self.assertEqual(payload["eligible"], report["eligible"])
        self.assertEqual(payload["eligibility_code"], report["eligibility_code"])
        self.assertEqual(payload["review_decision"], "approved")
        self.assertEqual(payload["review_decided_at"], "2026-03-01T00:00:00+00:00")

    def test_cli_check_promotion_with_compact_without_review_keeps_payload_stable(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "check-promotion",
            "--candidate-id",
            "local-question-bank",
            "--compact",
        ]
        report = {
            "candidate_id": "local-question-bank",
            "exists": True,
            "eligible": False,
            "eligibility_code": "review_not_approved",
            "blocking_reason": "manual promotion requires review_decision=approved",
            "reasons": ["manual promotion requires review_decision=approved"],
            "source_origin": "local_file",
            "status": "candidate",
            "destination": "question_bank",
            "artifact_path": "data/source_candidates/files/question_bank/example.md",
            "artifact_exists": True,
            "promotable_destination": True,
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_already_matches": False,
            "would_copy": True,
            "has_conflict": False,
            "conflict_reason": "",
        }
        manifest = {"candidates": [{"candidate_id": "local-question-bank"}]}

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=report),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["eligibility_code"], "review_not_approved")
        self.assertNotIn("review_decision", payload)
        self.assertNotIn("review_decided_at", payload)

    def test_warning_for_web_candidate_with_artifact_path(self) -> None:
        payload = _build_candidate_consistency(
            [
                {
                    "candidate_id": "web-with-artifact",
                    "source_origin": "web",
                    "artifact_path": "data/raw_review/example.md",
                }
            ]
        )

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["web_with_artifact_path"], ["web-with-artifact"])
        self.assertEqual(payload["warnings"]["local_file_without_artifact_path"], [])
        self.assertEqual(payload["warnings"]["missing_source_origin"], [])

    def test_warning_for_local_file_without_artifact_path(self) -> None:
        payload = _build_candidate_consistency(
            [
                {
                    "candidate_id": "local-without-artifact",
                    "source_origin": "local_file",
                }
            ]
        )

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["web_with_artifact_path"], [])
        self.assertEqual(payload["warnings"]["local_file_without_artifact_path"], ["local-without-artifact"])
        self.assertEqual(payload["warnings"]["missing_source_origin"], [])

    def test_warning_for_missing_source_origin(self) -> None:
        payload = _build_candidate_consistency(
            [
                {
                    "candidate_id": "missing-origin",
                }
            ]
        )

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["web_with_artifact_path"], [])
        self.assertEqual(payload["warnings"]["local_file_without_artifact_path"], [])
        self.assertEqual(payload["warnings"]["missing_source_origin"], ["missing-origin"])

    def test_clean_candidates_have_no_warnings(self) -> None:
        payload = _build_candidate_consistency(
            [
                {
                    "candidate_id": "web-clean",
                    "source_origin": "web",
                },
                {
                    "candidate_id": "local-clean",
                    "source_origin": "local_file",
                    "artifact_path": "data/coverage_inputs/example.pdf",
                },
            ]
        )

        self.assertEqual(payload["candidate_count"], 2)
        self.assertEqual(payload["warning_count"], 0)
        self.assertEqual(payload["warnings"]["web_with_artifact_path"], [])
        self.assertEqual(payload["warnings"]["local_file_without_artifact_path"], [])
        self.assertEqual(payload["warnings"]["missing_source_origin"], [])

    def test_validation_report_reuses_consistency_logic(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "web-with-artifact",
                    "source_origin": "web",
                    "artifact_path": "data/raw_review/example.md",
                },
                {
                    "candidate_id": "missing-origin",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_validation_report()

        self.assertEqual(payload["candidate_count"], 2)
        self.assertEqual(payload["warning_count"], 2)
        self.assertEqual(payload["web_with_artifact_path"], ["web-with-artifact"])
        self.assertEqual(payload["local_file_without_artifact_path"], [])
        self.assertEqual(payload["missing_source_origin"], ["missing-origin"])

    def test_register_source_candidate_sets_source_origin_web_for_url_flow(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
            patch("app.services.curated_sources.sync_destination_manifests"),
        ):
            payload = register_source_candidate(
                title="Example Candidate",
                source_url="https://example.com/resource",
                source_kind="candidate_resource",
                trust_level="medium_trust",
                destination="raw_review",
            )

        self.assertEqual(payload["source_origin"], "web")
        self.assertEqual(payload["status"], "candidate")
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(len(written_candidates), 1)
        self.assertEqual(written_candidates[0]["source_origin"], "web")
        self.assertEqual(written_candidates[0]["status"], "candidate")

    def test_register_source_candidate_sets_local_file_origin_for_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = root / "data" / "raw_review" / "example.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("example", encoding="utf-8")

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
                patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
                patch("app.services.curated_sources.sync_destination_manifests"),
            ):
                payload = register_source_candidate(
                    title="Local Candidate",
                    artifact_path="data/raw_review/example.md",
                    source_kind="question_bank_material",
                    trust_level="low_trust",
                    destination="raw_review",
                )

        self.assertEqual(payload["source_origin"], "local_file")
        self.assertEqual(payload["artifact_path"], "data/raw_review/example.md")
        self.assertEqual(payload["source_url"], "local://data/raw_review/example.md")
        self.assertEqual(payload["status"], "candidate")
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(written_candidates[0]["source_origin"], "local_file")
        self.assertEqual(written_candidates[0]["artifact_path"], "data/raw_review/example.md")

    def test_register_source_candidate_fails_for_missing_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("app.services.curated_sources.PROJECT_ROOT", root):
                with self.assertRaisesRegex(ValueError, "artifact_path not found"):
                    register_source_candidate(
                        title="Missing Local Candidate",
                        artifact_path="data/raw_review/missing.md",
                        source_kind="question_bank_material",
                        trust_level="low_trust",
                        destination="raw_review",
                    )

    def test_register_source_candidate_requires_url_or_artifact_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires source_url or artifact_path"):
            register_source_candidate(
                title="Invalid Candidate",
                source_kind="candidate_resource",
                trust_level="medium_trust",
                destination="raw_review",
            )

    def test_promote_source_candidate_allows_confirmed_local_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = root / "data" / "source_candidates" / "files" / "question_bank" / "example.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("example", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-question-bank",
                        "title": "Local Question Bank",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/question_bank/example.md",
                        "artifact_path": "data/source_candidates/files/question_bank/example.md",
                        "source_kind": "question_bank_material",
                        "trust_level": "medium_trust",
                        "destination": "question_bank",
                        "status": "candidate",
                        "parser_hint": "markdown_index",
                        "notes": "ready",
                        "review_decision": "approved",
                        "review_decided_at": "2026-03-01T00:00:00+00:00",
                    }
                ]
            }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
                patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
                patch("app.services.curated_sources.sync_destination_manifests"),
            ):
                payload = promote_source_candidate("local-question-bank", confirm=True)

            promoted_copy = root / "data" / "question_bank_raw" / "example.md"
            self.assertTrue(promoted_copy.exists())
            self.assertEqual(payload["status"], "promoted")
            self.assertEqual(payload["promoted_to"], "question_bank")
            self.assertEqual(payload["promoted_artifact_path"], "data/question_bank_raw/example.md")
            self.assertTrue(payload["promoted_at"])
            self.assertEqual(len(payload["promotion_log"]), 1)
            self.assertEqual(payload["promotion_log"][0]["promoted_to"], "question_bank")
            self.assertEqual(payload["promotion_log"][0]["promoted_artifact_path"], "data/question_bank_raw/example.md")
            self.assertEqual(payload["promotion_log"][0]["review_decision"], "approved")
            self.assertEqual(payload["promotion_log"][0]["review_decided_at"], "2026-03-01T00:00:00+00:00")
            written_candidates = write_manifest.call_args.args[0]
            self.assertEqual(written_candidates[0]["status"], "promoted")
            self.assertEqual(len(written_candidates[0]["promotion_log"]), 1)

    def test_promote_source_candidate_requires_explicit_confirmation(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "approved",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "requires --confirm"):
                promote_source_candidate("local-question-bank", confirm=False)

        write_manifest.assert_not_called()

    def test_promote_source_candidate_blocks_missing_review_approval(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "review_decision=approved"):
                promote_source_candidate("local-question-bank", confirm=True)

        write_manifest.assert_not_called()

    def test_promote_source_candidate_blocks_rejected_review(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "rejected",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "review_decision=approved"):
                promote_source_candidate("local-question-bank", confirm=True)

        write_manifest.assert_not_called()

    def test_promote_source_candidate_blocks_needs_revision_review(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "needs_revision",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "review_decision=approved"):
                promote_source_candidate("local-question-bank", confirm=True)

        write_manifest.assert_not_called()

    def test_promote_source_candidate_does_not_write_promotion_log_when_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "data" / "source_candidates" / "files" / "question_bank" / "example.md"
            target = root / "data" / "question_bank_raw" / "example.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("source", encoding="utf-8")
            target.write_text("different", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-question-bank",
                        "title": "Local Question Bank",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/question_bank/example.md",
                        "artifact_path": "data/source_candidates/files/question_bank/example.md",
                        "source_kind": "question_bank_material",
                        "trust_level": "medium_trust",
                        "destination": "question_bank",
                        "status": "candidate",
                        "parser_hint": "markdown_index",
                        "notes": "ready",
                        "review_decision": "approved",
                    }
                ]
            }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
                patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
            ):
                with self.assertRaisesRegex(ValueError, "different content"):
                    promote_source_candidate("local-question-bank", confirm=True)

        write_manifest.assert_not_called()

    def test_promote_source_candidate_blocks_web_candidates(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "web-knowledge",
                    "title": "Web Knowledge",
                    "source_origin": "web",
                    "source_url": "https://example.com/doc",
                    "source_kind": "knowledge_document",
                    "trust_level": "high_trust",
                    "destination": "knowledge",
                    "status": "candidate",
                    "parser_hint": "html",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "only local_file candidates"):
                promote_source_candidate("web-knowledge", confirm=True)

    def test_promote_source_candidate_blocks_non_promotable_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-raw-review",
                    "title": "Local Raw Review",
                    "source_origin": "local_file",
                    "source_url": "local://data/raw_review/example.md",
                    "artifact_path": "data/raw_review/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "low_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "destination not eligible"):
                promote_source_candidate("local-raw-review", confirm=True)

    def test_promote_source_candidate_blocks_already_promoted_candidate(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "already-promoted",
                    "title": "Already Promoted",
                    "source_origin": "local_file",
                    "source_url": "local://data/question_bank_raw/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "promoted",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            with self.assertRaisesRegex(ValueError, "already promoted"):
                promote_source_candidate("already-promoted", confirm=True)

    def test_promote_source_candidate_appends_to_existing_promotion_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = root / "data" / "source_candidates" / "files" / "knowledge" / "example.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("example", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-knowledge",
                        "title": "Local Knowledge",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/knowledge/example.md",
                        "artifact_path": "data/source_candidates/files/knowledge/example.md",
                        "source_kind": "knowledge_document",
                        "trust_level": "high_trust",
                        "destination": "knowledge",
                        "status": "candidate",
                        "parser_hint": "markdown_index",
                        "notes": "ready",
                        "review_decision": "approved",
                        "promotion_log": [
                            {
                                "promoted_at": "2026-02-01T00:00:00+00:00",
                                "promoted_to": "knowledge",
                                "promoted_artifact_path": "data/knowledge_raw/old.md",
                            }
                        ],
                    }
                ]
            }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
                patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
                patch("app.services.curated_sources.sync_destination_manifests"),
            ):
                payload = promote_source_candidate("local-knowledge", confirm=True)

        self.assertEqual(len(payload["promotion_log"]), 2)
        self.assertEqual(payload["promotion_log"][0]["promoted_artifact_path"], "data/knowledge_raw/old.md")
        self.assertEqual(payload["promotion_log"][1]["promoted_to"], "knowledge")
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(len(written_candidates[0]["promotion_log"]), 2)

    def test_check_promotion_reports_eligible_local_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = root / "data" / "source_candidates" / "files" / "question_bank" / "example.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("example", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-question-bank",
                        "title": "Local Question Bank",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/question_bank/example.md",
                        "artifact_path": "data/source_candidates/files/question_bank/example.md",
                        "source_kind": "question_bank_material",
                        "trust_level": "medium_trust",
                        "destination": "question_bank",
                        "status": "candidate",
                        "parser_hint": "markdown_index",
                        "notes": "ready",
                        "review_decision": "approved",
                    }
                ]
            }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            ):
                payload = inspect_promotion_candidate("local-question-bank")

        self.assertTrue(payload["exists"])
        self.assertTrue(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "eligible")
        self.assertTrue(payload["would_copy"])
        self.assertFalse(payload["target_already_matches"])
        self.assertFalse(payload["has_conflict"])
        self.assertEqual(payload["conflict_reason"], "")
        self.assertEqual(payload["planned_target_path"], "data/question_bank_raw/example.md")
        self.assertEqual(payload["reasons"], [])

    def test_check_promotion_blocks_missing_review_approval(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = inspect_promotion_candidate("local-question-bank")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "review_not_approved")
        self.assertIn("review_decision=approved", payload["blocking_reason"])

    def test_check_promotion_blocks_rejected_review(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "rejected",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = inspect_promotion_candidate("local-question-bank")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "review_not_approved")

    def test_check_promotion_blocks_needs_revision_review(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "needs_revision",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = inspect_promotion_candidate("local-question-bank")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "review_not_approved")

    def test_check_promotion_reports_target_already_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "data" / "source_candidates" / "files" / "question_bank" / "example.md"
            target = root / "data" / "question_bank_raw" / "example.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("same", encoding="utf-8")
            target.write_text("same", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-question-bank",
                        "title": "Local Question Bank",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/question_bank/example.md",
                        "artifact_path": "data/source_candidates/files/question_bank/example.md",
                        "source_kind": "question_bank_material",
                        "trust_level": "medium_trust",
                        "destination": "question_bank",
                        "status": "candidate",
                        "parser_hint": "markdown_index",
                        "notes": "ready",
                        "review_decision": "approved",
                    }
                ]
            }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            ):
                payload = inspect_promotion_candidate("local-question-bank")

        self.assertTrue(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "eligible")
        self.assertFalse(payload["would_copy"])
        self.assertTrue(payload["target_already_matches"])
        self.assertFalse(payload["has_conflict"])
        self.assertEqual(payload["conflict_reason"], "")

    def test_check_promotion_blocks_web_candidate(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "web-knowledge",
                    "title": "Web Knowledge",
                    "source_origin": "web",
                    "source_url": "https://example.com/doc",
                    "source_kind": "knowledge_document",
                    "trust_level": "high_trust",
                    "destination": "knowledge",
                    "status": "candidate",
                    "parser_hint": "html",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
        ):
            payload = inspect_promotion_candidate("web-knowledge")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "non_local_source")
        self.assertIn("only local_file candidates", payload["blocking_reason"])

    def test_check_promotion_blocks_non_promotable_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-raw-review",
                    "title": "Local Raw Review",
                    "source_origin": "local_file",
                    "source_url": "local://data/raw_review/example.md",
                    "artifact_path": "data/raw_review/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "low_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = inspect_promotion_candidate("local-raw-review")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "non_promotable_destination")
        self.assertIn("destination not eligible", payload["blocking_reason"])

    def test_check_promotion_blocks_missing_artifact(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-question-bank",
                    "title": "Local Question Bank",
                    "source_origin": "local_file",
                    "source_url": "local://data/source_candidates/files/question_bank/example.md",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "source_kind": "question_bank_material",
                    "trust_level": "medium_trust",
                    "destination": "question_bank",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=False),
        ):
            payload = inspect_promotion_candidate("local-question-bank")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "artifact_not_found")
        self.assertIn("artifact_path must point to an existing local file", payload["blocking_reason"])

    def test_check_promotion_blocks_target_collision_with_different_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "data" / "source_candidates" / "files" / "knowledge" / "example.md"
            target = root / "data" / "knowledge_raw" / "example.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("source", encoding="utf-8")
            target.write_text("target", encoding="utf-8")
            manifest = {
                "candidates": [
                    {
                        "candidate_id": "local-knowledge",
                        "title": "Local Knowledge",
                        "source_origin": "local_file",
                        "source_url": "local://data/source_candidates/files/knowledge/example.md",
                        "artifact_path": "data/source_candidates/files/knowledge/example.md",
                        "source_kind": "knowledge_document",
                        "trust_level": "high_trust",
                    "destination": "knowledge",
                    "status": "candidate",
                    "parser_hint": "markdown_index",
                    "notes": "ready",
                    "review_decision": "approved",
                }
            ]
        }

            with (
                patch("app.services.curated_sources.PROJECT_ROOT", root),
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            ):
                payload = inspect_promotion_candidate("local-knowledge")

        self.assertFalse(payload["eligible"])
        self.assertEqual(payload["eligibility_code"], "destination_conflict")
        self.assertFalse(payload["would_copy"])
        self.assertFalse(payload["target_already_matches"])
        self.assertTrue(payload["has_conflict"])
        self.assertEqual(payload["conflict_reason"], "destination_content_mismatch")
        self.assertIn("different content", payload["blocking_reason"])

    def test_cli_register_candidate_rejects_url_and_artifact_path_together(self) -> None:
        stderr = io.StringIO()
        argv = [
            "curated_sources",
            "register-candidate",
            "--title",
            "Invalid CLI Candidate",
            "--url",
            "https://example.com/resource",
            "--artifact-path",
            "data/raw_review/example.md",
        ]

        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                _main()

        self.assertEqual(exc.exception.code, 2)
        self.assertIn("not allowed with argument", stderr.getvalue())

    def test_cli_register_candidate_rejects_missing_url_and_artifact_path(self) -> None:
        stderr = io.StringIO()
        argv = [
            "curated_sources",
            "register-candidate",
            "--title",
            "Invalid CLI Candidate",
        ]

        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                _main()

        self.assertEqual(exc.exception.code, 2)
        self.assertIn("one of the arguments --url --artifact-path is required", stderr.getvalue())

    def test_list_candidates_filters_by_local_file_origin(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-1", "title": "Web 1", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/local-1.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(origin="local_file")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "local-1")
        self.assertEqual(payload["items"][0]["source_origin"], "local_file")
        self.assertEqual(payload["items"][0]["artifact_path"], "data/raw_review/local-1.md")

    def test_list_candidates_filters_by_destination(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "raw-1", "title": "Raw 1", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {"candidate_id": "knowledge-1", "title": "Knowledge 1", "source_origin": "web", "destination": "knowledge", "status": "candidate"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(destination="raw_review")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "raw-1")
        self.assertEqual(payload["items"][0]["destination"], "raw_review")

    def test_list_candidates_filters_by_origin_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-raw", "title": "Web Raw", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {
                    "candidate_id": "local-raw",
                    "title": "Local Raw",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/local-raw.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "local-coverage",
                    "title": "Local Coverage",
                    "source_origin": "local_file",
                    "artifact_path": "data/coverage_inputs/local-coverage.pdf",
                    "destination": "coverage_inputs",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(origin="local_file", destination="raw_review")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "local-raw")
        self.assertEqual(payload["items"][0]["source_origin"], "local_file")
        self.assertEqual(payload["items"][0]["destination"], "raw_review")

    def test_list_candidates_filters_by_query_in_title(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "react-sudheer", "title": "React Interview Questions Sudheer", "source_origin": "local_file", "destination": "raw_review", "status": "candidate"},
                {"candidate_id": "docker-cheat-sheet", "title": "Docker Cheat Sheet 2025", "source_origin": "local_file", "destination": "coverage_inputs", "status": "candidate"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(query="sudheer")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "react-sudheer")

    def test_list_candidates_filters_by_query_in_candidate_id(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "react-sudheer", "title": "React Interview Questions Sudheer", "source_origin": "local_file", "destination": "raw_review", "status": "candidate"},
                {"candidate_id": "docker-cheat-sheet", "title": "Docker Cheat Sheet 2025", "source_origin": "local_file", "destination": "coverage_inputs", "status": "candidate"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(query="docker-cheat")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["title"], "Docker Cheat Sheet 2025")

    def test_list_candidates_filters_by_query_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "react-raw", "title": "React Interview Questions", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {"candidate_id": "react-knowledge", "title": "React Core Docs", "source_origin": "web", "destination": "knowledge", "status": "candidate"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(query="react", destination="raw_review")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "react-raw")

    def test_list_candidates_filters_by_review_decision_approved(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-1",
                    "title": "Approved 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                },
                {
                    "candidate_id": "rejected-1",
                    "title": "Rejected 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "rejected",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(review_decision="approved")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "approved-1")
        self.assertEqual(payload["items"][0]["review_decision"], "approved")
        self.assertEqual(payload["items"][0]["review_decided_at"], "2026-03-01T00:00:00+00:00")

    def test_list_candidates_filters_by_review_decision_rejected(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-1",
                    "title": "Approved 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "rejected-1",
                    "title": "Rejected 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "rejected",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(review_decision="rejected")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "rejected-1")
        self.assertEqual(payload["items"][0]["review_decision"], "rejected")

    def test_list_candidates_filters_by_review_decision_none(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-1",
                    "title": "Approved 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "no-review-1",
                    "title": "No Review 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(review_decision="none")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "no-review-1")
        self.assertNotIn("review_decision", payload["items"][0])

    def test_list_candidates_filters_by_review_decision_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-qb",
                    "title": "Approved QB",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "approved-knowledge",
                    "title": "Approved Knowledge",
                    "source_origin": "local_file",
                    "destination": "knowledge",
                    "status": "candidate",
                    "review_decision": "approved",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(destination="question_bank", review_decision="approved")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "approved-qb")

    def test_list_candidates_filters_by_has_promotion_history_true(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "with-history",
                    "title": "With History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                        }
                    ],
                },
                {
                    "candidate_id": "without-history",
                    "title": "Without History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(has_promotion_history="true")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["filters"]["has_promotion_history"], "true")
        self.assertEqual(payload["items"][0]["candidate_id"], "with-history")
        self.assertTrue(payload["items"][0]["has_promotion_history"])
        self.assertEqual(payload["items"][0]["promotion_log_count"], 1)

    def test_list_candidates_filters_by_has_promotion_history_false(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "with-history",
                    "title": "With History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                        }
                    ],
                },
                {
                    "candidate_id": "without-history",
                    "title": "Without History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(has_promotion_history="false")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["filters"]["has_promotion_history"], "false")
        self.assertEqual(payload["items"][0]["candidate_id"], "without-history")
        self.assertNotIn("has_promotion_history", payload["items"][0])
        self.assertNotIn("promotion_log_count", payload["items"][0])

    def test_list_candidates_filters_by_has_promotion_history_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "qb-no-history",
                    "title": "QB No History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
                {
                    "candidate_id": "knowledge-no-history",
                    "title": "Knowledge No History",
                    "source_origin": "local_file",
                    "destination": "knowledge",
                    "status": "candidate",
                },
                {
                    "candidate_id": "qb-with-history",
                    "title": "QB With History",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                        }
                    ],
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(destination="question_bank", has_promotion_history="false")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "qb-no-history")

    def test_list_candidates_filters_by_promotion_ready_true(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-ready",
                    "title": "Approved Ready",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "approved-blocked",
                    "title": "Approved Blocked",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "no-review",
                    "title": "No Review",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "approved-ready": {"eligible": True},
                    "approved-blocked": {"eligible": False},
                }.get(candidate_id, {"eligible": False}),
            ),
        ):
            payload = build_candidate_listing_report(promotion_ready="true")

        self.assertEqual(payload["filters"]["promotion_ready"], "true")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "approved-ready")

    def test_list_candidates_filters_by_promotion_ready_false(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-ready",
                    "title": "Approved Ready",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "approved-blocked",
                    "title": "Approved Blocked",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "no-review",
                    "title": "No Review",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "approved-ready": {"eligible": True},
                    "approved-blocked": {"eligible": False},
                }.get(candidate_id, {"eligible": False}),
            ),
        ):
            payload = build_candidate_listing_report(promotion_ready="false")

        self.assertEqual(payload["filters"]["promotion_ready"], "false")
        self.assertEqual(payload["count"], 2)
        self.assertEqual(
            [item["candidate_id"] for item in payload["items"]],
            ["approved-blocked", "no-review"],
        )

    def test_list_candidates_filters_by_promotion_ready_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "qb-ready",
                    "title": "QB Ready",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "knowledge-ready",
                    "title": "Knowledge Ready",
                    "source_origin": "local_file",
                    "destination": "knowledge",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "qb-blocked",
                    "title": "QB Blocked",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "qb-ready": {"eligible": True},
                    "knowledge-ready": {"eligible": True},
                    "qb-blocked": {"eligible": False},
                }.get(candidate_id, {"eligible": False}),
            ),
        ):
            payload = build_candidate_listing_report(destination="question_bank", promotion_ready="true")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "qb-ready")

    def test_list_candidates_filters_by_eligibility_code_review_not_approved(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "no-review", "title": "No Review", "status": "candidate"},
                {"candidate_id": "approved-ready", "title": "Approved Ready", "status": "candidate", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                return_value={"eligible": True, "eligibility_code": "eligible"},
            ),
        ):
            payload = build_candidate_listing_report(eligibility_code="review_not_approved")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["filters"]["eligibility_code"], "review_not_approved")
        self.assertEqual(payload["items"][0]["candidate_id"], "no-review")
        self.assertEqual(payload["items"][0]["eligibility_code"], "review_not_approved")

    def test_list_candidates_filters_by_eligibility_code_eligible(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "approved-ready", "title": "Approved Ready", "status": "candidate", "review_decision": "approved"},
                {"candidate_id": "approved-blocked", "title": "Approved Blocked", "status": "candidate", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "approved-ready": {"eligible": True, "eligibility_code": "eligible"},
                    "approved-blocked": {"eligible": False, "eligibility_code": "artifact_not_found"},
                }[candidate_id],
            ),
        ):
            payload = build_candidate_listing_report(eligibility_code="eligible")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "approved-ready")
        self.assertEqual(payload["items"][0]["eligibility_code"], "eligible")

    def test_list_candidates_filters_by_eligibility_code_other_real_blocker(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-approved", "title": "Web Approved", "status": "candidate", "review_decision": "approved"},
                {"candidate_id": "ready-approved", "title": "Ready Approved", "status": "candidate", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "web-approved": {"eligible": False, "eligibility_code": "non_local_source"},
                    "ready-approved": {"eligible": True, "eligibility_code": "eligible"},
                }[candidate_id],
            ),
        ):
            payload = build_candidate_listing_report(eligibility_code="non_local_source")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "web-approved")
        self.assertEqual(payload["items"][0]["eligibility_code"], "non_local_source")

    def test_list_candidates_filters_by_eligibility_code_and_destination(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "qb-ready",
                    "title": "QB Ready",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                },
                {
                    "candidate_id": "knowledge-ready",
                    "title": "Knowledge Ready",
                    "destination": "knowledge",
                    "status": "candidate",
                    "review_decision": "approved",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                return_value={"eligible": True, "eligibility_code": "eligible"},
            ),
        ):
            payload = build_candidate_listing_report(destination="question_bank", eligibility_code="eligible")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "qb-ready")

    def test_list_candidates_filters_by_has_artifact_path(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-no-artifact", "title": "Web No Artifact", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {
                    "candidate_id": "local-with-artifact",
                    "title": "Local With Artifact",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/local.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(has_artifact_path=True)

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "local-with-artifact")
        self.assertIn("artifact_path", payload["items"][0])

    def test_list_candidates_filters_by_has_artifact_path_and_origin(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-no-artifact", "title": "Web No Artifact", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {
                    "candidate_id": "local-with-artifact",
                    "title": "Local With Artifact",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/local.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "local-without-artifact",
                    "title": "Local Without Artifact",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(origin="local_file", has_artifact_path=True)

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "local-with-artifact")
        self.assertEqual(payload["items"][0]["source_origin"], "local_file")

    def test_list_candidates_filters_by_has_artifact_path_and_query(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "react-sudheer",
                    "title": "React Interview Questions Sudheer",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/react.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "react-web",
                    "title": "React Interview Questions",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(query="sudheer", has_artifact_path=True)

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "react-sudheer")

    def test_list_candidates_filters_by_artifact_exists_present(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "artifact-present",
                    "title": "Artifact Present",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/present.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "artifact-missing",
                    "title": "Artifact Missing",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/missing.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "no-artifact",
                    "title": "No Artifact",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources._artifact_path_exists",
                side_effect=lambda path: path == "data/raw_review/present.md",
            ),
        ):
            payload = build_candidate_listing_report(artifact_exists="present")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "artifact-present")
        self.assertTrue(payload["items"][0]["artifact_exists"])

    def test_list_candidates_filters_by_artifact_exists_missing(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "artifact-present",
                    "title": "Artifact Present",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/present.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "artifact-missing",
                    "title": "Artifact Missing",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/missing.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "no-artifact",
                    "title": "No Artifact",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources._artifact_path_exists",
                side_effect=lambda path: path == "data/raw_review/present.md",
            ),
        ):
            payload = build_candidate_listing_report(artifact_exists="missing")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "artifact-missing")
        self.assertFalse(payload["items"][0]["artifact_exists"])

    def test_list_candidates_filters_by_artifact_exists_and_origin(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-present",
                    "title": "Local Present",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/present.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "local-missing",
                    "title": "Local Missing",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/missing.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "web-present",
                    "title": "Web Present",
                    "source_origin": "web",
                    "artifact_path": "data/raw_review/present.md",
                    "destination": "raw_review",
                    "status": "candidate",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources._artifact_path_exists",
                side_effect=lambda path: path == "data/raw_review/present.md",
            ),
        ):
            payload = build_candidate_listing_report(origin="local_file", artifact_exists="present")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["candidate_id"], "local-present")
        self.assertEqual(payload["items"][0]["source_origin"], "local_file")

    def test_candidate_stats_report_exposes_core_counts(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-1", "title": "Web 1", "source_origin": "web", "destination": "raw_review"},
                {"candidate_id": "local-1", "title": "Local 1", "source_origin": "local_file", "destination": "coverage_inputs"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["candidate_count"], 2)
        self.assertIn("by_origin", payload)
        self.assertIn("web", payload["by_origin"])
        self.assertIn("local_file", payload["by_origin"])
        self.assertEqual(payload["by_origin"]["web"], 1)
        self.assertEqual(payload["by_origin"]["local_file"], 1)
        self.assertIn("by_destination", payload)
        self.assertEqual(payload["by_destination"]["raw_review"], 1)
        self.assertEqual(payload["by_destination"]["coverage_inputs"], 1)
        self.assertIn("by_review_decision", payload)
        self.assertIn("by_promotion_history", payload)
        self.assertIn("promotion_readiness", payload)
        self.assertIn("promotion_blockers", payload)

    def test_candidate_stats_report_counts_by_review_decision(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "approved-1", "review_decision": "approved"},
                {"candidate_id": "rejected-1", "review_decision": "rejected"},
                {"candidate_id": "needs-revision-1", "review_decision": "needs_revision"},
                {"candidate_id": "none-1"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_stats_report()

        self.assertEqual(
            payload["by_review_decision"],
            {
                "approved": 1,
                "rejected": 1,
                "needs_revision": 1,
                "none": 1,
            },
        )

    def test_candidate_stats_report_counts_by_promotion_history(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "with-history",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                        }
                    ],
                },
                {"candidate_id": "without-history"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_stats_report()

        self.assertEqual(
            payload["by_promotion_history"],
            {
                "with_history": 1,
                "without_history": 1,
            },
        )

    def test_candidate_stats_report_counts_ready_for_promotion(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "approved-ready", "review_decision": "approved"},
                {"candidate_id": "approved-blocked", "review_decision": "approved"},
                {"candidate_id": "no-review"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                side_effect=lambda candidate_id: {
                    "approved-ready": {"eligible": True},
                    "approved-blocked": {"eligible": False},
                }.get(candidate_id, {"eligible": False}),
            ),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(
            payload["promotion_readiness"],
            {
                "ready": 1,
                "not_ready": 2,
            },
        )

    def test_candidate_stats_report_excludes_non_approved_candidates_from_ready(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "rejected-1", "review_decision": "rejected"},
                {"candidate_id": "needs-revision-1", "review_decision": "needs_revision"},
                {"candidate_id": "none-1"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate") as inspect_promotion,
        ):
            payload = build_candidate_stats_report()

        inspect_promotion.assert_not_called()
        self.assertEqual(
            payload["promotion_readiness"],
            {
                "ready": 0,
                "not_ready": 3,
            },
        )

    def test_candidate_stats_report_counts_approved_but_blocked_candidate_as_not_ready(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "approved-blocked", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                return_value={"eligible": False, "eligibility_code": "artifact_not_found"},
            ),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(
            payload["promotion_readiness"],
            {
                "ready": 0,
                "not_ready": 1,
            },
        )

    def test_candidate_stats_report_counts_review_not_approved_blocker(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "candidate-1"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["promotion_blockers"], {"review_not_approved": 1})

    def test_candidate_stats_report_counts_other_blocker_from_preflight(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-blocked", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                return_value={"eligible": False, "eligibility_code": "non_local_source"},
            ),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["promotion_blockers"], {"non_local_source": 1})

    def test_candidate_stats_report_excludes_ready_candidates_from_blockers(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "ready-1", "review_decision": "approved"},
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources.inspect_promotion_candidate",
                return_value={"eligible": True, "eligibility_code": "eligible"},
            ),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["promotion_blockers"], {})

    def test_candidate_stats_report_counts_all_candidates_as_none_without_review(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "candidate-1"},
                {"candidate_id": "candidate-2"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_stats_report()

        self.assertEqual(
            payload["by_review_decision"],
            {
                "approved": 0,
                "rejected": 0,
                "needs_revision": 0,
                "none": 2,
            },
        )
        self.assertEqual(
            payload["by_promotion_history"],
            {
                "with_history": 0,
                "without_history": 2,
            },
        )

    def test_candidate_stats_report_counts_artifact_presence(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "web-1", "title": "Web 1", "source_origin": "web", "destination": "raw_review"},
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "coverage_inputs",
                    "artifact_path": "data/coverage_inputs/local-1.pdf",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["with_artifact_path"], 1)
        self.assertEqual(payload["without_artifact_path"], 1)

    def test_candidate_stats_report_counts_artifact_exists_present_and_missing(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "artifact-present",
                    "title": "Artifact Present",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "artifact_path": "data/raw_review/present.md",
                },
                {
                    "candidate_id": "artifact-missing",
                    "title": "Artifact Missing",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "artifact_path": "data/raw_review/missing.md",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch(
                "app.services.curated_sources._artifact_path_exists",
                side_effect=lambda path: path == "data/raw_review/present.md",
            ),
        ):
            payload = build_candidate_stats_report()

        self.assertEqual(payload["artifact_exists"]["present"], 1)
        self.assertEqual(payload["artifact_exists"]["missing"], 1)

    def test_metadata_audit_reports_missing_notes(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "missing-notes",
                    "title": "Missing Notes",
                    "parser_hint": "html",
                    "source_kind": "candidate_resource",
                    "trust_level": "medium_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_metadata_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["missing_notes"][0]["candidate_id"], "missing-notes")

    def test_metadata_audit_reports_weak_parser_hint(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "weak-parser",
                    "title": "Weak Parser",
                    "parser_hint": "unknown",
                    "source_kind": "candidate_resource",
                    "trust_level": "medium_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "ok",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_metadata_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["weak_parser_hint"][0]["candidate_id"], "weak-parser")

    def test_metadata_audit_reports_missing_required_metadata(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "missing-required",
                    "title": "Missing Required",
                    "parser_hint": "html",
                    "notes": "ok",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_metadata_audit_report()

        self.assertEqual(payload["warning_count"], 4)
        self.assertEqual(payload["warnings"]["missing_source_kind"][0]["candidate_id"], "missing-required")
        self.assertEqual(payload["warnings"]["missing_trust_level"][0]["candidate_id"], "missing-required")
        self.assertEqual(payload["warnings"]["missing_destination"][0]["candidate_id"], "missing-required")
        self.assertEqual(payload["warnings"]["missing_status"][0]["candidate_id"], "missing-required")

    def test_metadata_audit_clean_set_has_no_warnings(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "clean",
                    "title": "Clean Candidate",
                    "parser_hint": "html",
                    "source_kind": "candidate_resource",
                    "trust_level": "medium_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "ok",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_metadata_audit_report()

        self.assertEqual(payload["warning_count"], 0)
        self.assertTrue(all(not items for items in payload["warnings"].values()))

    def test_semantic_audit_reports_local_file_without_artifact(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-without-artifact",
                    "title": "Local Without Artifact",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "trust_level": "low_trust",
                    "source_kind": "question_bank_material",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["local_file_without_artifact"][0]["candidate_id"], "local-without-artifact")

    def test_semantic_audit_reports_low_trust_destination_mismatch(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "wrong-low-trust",
                    "title": "Wrong Low Trust",
                    "source_origin": "web",
                    "destination": "question_bank_low_trust",
                    "trust_level": "medium_trust",
                    "source_kind": "question_bank_material",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["low_trust_destination_mismatch"][0]["candidate_id"], "wrong-low-trust")

    def test_semantic_audit_reports_raw_review_high_trust(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "raw-high-trust",
                    "title": "Raw High Trust",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "trust_level": "high_trust",
                    "source_kind": "knowledge_document",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["raw_review_high_trust"][0]["candidate_id"], "raw-high-trust")

    def test_semantic_audit_reports_question_material_in_knowledge(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "question-in-knowledge",
                    "title": "Question In Knowledge",
                    "source_origin": "web",
                    "destination": "knowledge",
                    "trust_level": "medium_trust",
                    "source_kind": "question_bank_material",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["question_material_in_knowledge"][0]["candidate_id"], "question-in-knowledge")

    def test_semantic_audit_reports_web_with_artifact_path(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "web-with-artifact",
                    "title": "Web With Artifact",
                    "source_origin": "web",
                    "artifact_path": "data/raw_review/web.md",
                    "destination": "raw_review",
                    "trust_level": "low_trust",
                    "source_kind": "question_bank_material",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["web_with_artifact_path"][0]["candidate_id"], "web-with-artifact")

    def test_semantic_audit_clean_set_has_no_warnings(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "clean",
                    "title": "Clean Candidate",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/clean.md",
                    "destination": "raw_review",
                    "trust_level": "low_trust",
                    "source_kind": "question_bank_material",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_semantic_audit_report()

        self.assertEqual(payload["warning_count"], 0)
        self.assertTrue(all(not items for items in payload["warnings"].values()))

    def test_operational_audit_reports_missing_discovered_from(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "missing-discovered",
                    "title": "Missing Discovered From",
                    "source_origin": "web",
                    "source_url": "https://example.com/resource",
                    "parser_hint": "html",
                    "source_kind": "candidate_resource",
                    "trust_level": "medium_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "Has notes.",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_operational_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["missing_discovered_from"], [{"candidate_id": "missing-discovered", "title": "Missing Discovered From"}])

    def test_operational_audit_reports_artifact_without_parser_hint(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "artifact-without-parser",
                    "title": "Artifact Without Parser",
                    "source_origin": "local_file",
                    "source_url": "local://data/raw_review/example.md",
                    "artifact_path": "data/raw_review/example.md",
                    "discovered_from": "manual-local",
                    "source_kind": "question_bank_material",
                    "trust_level": "low_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "Has notes.",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_operational_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["artifact_without_parser_hint"], [{"candidate_id": "artifact-without-parser", "title": "Artifact Without Parser"}])

    def test_operational_audit_reports_artifact_parser_mismatch(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "artifact-parser-mismatch",
                    "title": "Artifact Parser Mismatch",
                    "source_origin": "local_file",
                    "source_url": "local://data/raw_review/example.md",
                    "artifact_path": "data/raw_review/example.md",
                    "parser_hint": "link_only",
                    "discovered_from": "manual-local",
                    "source_kind": "question_bank_material",
                    "trust_level": "low_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "Has notes.",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_operational_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["artifact_parser_mismatch"], [{"candidate_id": "artifact-parser-mismatch", "title": "Artifact Parser Mismatch"}])

    def test_operational_audit_reports_local_url_without_artifact(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-url-no-artifact",
                    "title": "Local URL No Artifact",
                    "source_origin": "web",
                    "source_url": "local://data/raw_review/example.md",
                    "parser_hint": "markdown_index",
                    "discovered_from": "manual-local",
                    "source_kind": "candidate_resource",
                    "trust_level": "medium_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "Has notes.",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_operational_audit_report()

        self.assertEqual(payload["warning_count"], 1)
        self.assertEqual(payload["warnings"]["local_url_without_artifact"], [{"candidate_id": "local-url-no-artifact", "title": "Local URL No Artifact"}])

    def test_operational_audit_clean_set_has_no_warnings(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "clean-operational",
                    "title": "Clean Operational",
                    "source_origin": "local_file",
                    "source_url": "local://data/raw_review/example.md",
                    "artifact_path": "data/raw_review/example.md",
                    "parser_hint": "markdown_index",
                    "discovered_from": "manual-local",
                    "source_kind": "question_bank_material",
                    "trust_level": "low_trust",
                    "destination": "raw_review",
                    "status": "candidate",
                    "notes": "Has notes.",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_operational_audit_report()

        self.assertEqual(payload["warning_count"], 0)
        self.assertTrue(all(not items for items in payload["warnings"].values()))

    def test_candidate_audit_summary_includes_all_check_blocks(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
        ):
            payload = build_candidate_audit_summary_report()

        self.assertEqual(payload["candidate_count"], 26)
        self.assertIn("validate_candidates", payload["checks"])
        self.assertIn("audit_metadata", payload["checks"])
        self.assertIn("audit_semantic", payload["checks"])
        self.assertIn("audit_operational", payload["checks"])

    def test_candidate_audit_summary_sums_warning_counts(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 1}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 2}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 3}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 4}),
        ):
            payload = build_candidate_audit_summary_report()

        self.assertEqual(payload["total_warning_count"], 10)
        self.assertFalse(payload["is_clean"])

    def test_candidate_audit_summary_is_clean_when_total_is_zero(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
        ):
            payload = build_candidate_audit_summary_report()

        self.assertEqual(payload["total_warning_count"], 0)
        self.assertTrue(payload["is_clean"])

    def test_candidate_audit_summary_without_flag_preserves_current_payload(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
        ):
            payload = build_candidate_audit_summary_report()

        self.assertNotIn("nonzero_categories", payload)
        self.assertEqual(payload["total_warning_count"], 0)

    def test_candidate_audit_summary_with_flag_lists_only_nonzero_categories(self) -> None:
        with (
            patch(
                "app.services.curated_sources.build_candidate_validation_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 1,
                    "web_with_artifact_path": ["web-1"],
                    "local_file_without_artifact_path": [],
                    "missing_source_origin": [],
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_metadata_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 1,
                    "warnings": {
                        "missing_notes": [{"candidate_id": "meta-1", "title": "Meta 1"}],
                        "weak_parser_hint": [],
                    },
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_semantic_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 0,
                    "warnings": {
                        "local_file_without_artifact": [],
                        "web_with_artifact_path": [],
                    },
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_operational_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 1,
                    "warnings": {
                        "missing_discovered_from": [],
                        "artifact_parser_mismatch": [{"candidate_id": "op-1", "title": "Op 1"}],
                    },
                },
            ),
        ):
            payload = build_candidate_audit_summary_report(show_nonzero_categories=True)

        self.assertEqual(
            payload["nonzero_categories"],
            {
                "validate_candidates": ["web_with_artifact_path"],
                "audit_metadata": ["missing_notes"],
                "audit_operational": ["artifact_parser_mismatch"],
            },
        )
        self.assertNotIn("audit_semantic", payload["nonzero_categories"])

    def test_candidate_audit_summary_with_flag_is_empty_when_clean(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0, "web_with_artifact_path": [], "local_file_without_artifact_path": [], "missing_source_origin": []}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_notes": [], "weak_parser_hint": []}}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"local_file_without_artifact": [], "web_with_artifact_path": []}}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_discovered_from": [], "artifact_parser_mismatch": []}}),
        ):
            payload = build_candidate_audit_summary_report(show_nonzero_categories=True)

        self.assertEqual(payload["nonzero_categories"], {})

    def test_candidate_audit_summary_without_category_count_flag_preserves_current_payload(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0}),
        ):
            payload = build_candidate_audit_summary_report()

        self.assertNotIn("category_counts", payload)
        self.assertEqual(payload["total_warning_count"], 0)

    def test_candidate_audit_summary_with_category_counts_lists_only_nonzero_categories(self) -> None:
        with (
            patch(
                "app.services.curated_sources.build_candidate_validation_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 2,
                    "web_with_artifact_path": ["web-1", "web-2"],
                    "local_file_without_artifact_path": [],
                    "missing_source_origin": [],
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_metadata_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 1,
                    "warnings": {
                        "missing_notes": [{"candidate_id": "meta-1", "title": "Meta 1"}],
                        "weak_parser_hint": [],
                    },
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_semantic_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 0,
                    "warnings": {
                        "local_file_without_artifact": [],
                        "web_with_artifact_path": [],
                    },
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_operational_audit_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 3,
                    "warnings": {
                        "missing_discovered_from": [{"candidate_id": "op-1", "title": "Op 1"}],
                        "artifact_parser_mismatch": [{"candidate_id": "op-2", "title": "Op 2"}, {"candidate_id": "op-3", "title": "Op 3"}],
                    },
                },
            ),
        ):
            payload = build_candidate_audit_summary_report(show_category_counts=True)

        self.assertEqual(
            payload["category_counts"],
            {
                "validate_candidates": {"web_with_artifact_path": 2},
                "audit_metadata": {"missing_notes": 1},
                "audit_operational": {
                    "missing_discovered_from": 1,
                    "artifact_parser_mismatch": 2,
                },
            },
        )
        self.assertNotIn("audit_semantic", payload["category_counts"])

    def test_candidate_audit_summary_with_category_counts_is_empty_when_clean(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0, "web_with_artifact_path": [], "local_file_without_artifact_path": [], "missing_source_origin": []}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_notes": [], "weak_parser_hint": []}}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"local_file_without_artifact": [], "web_with_artifact_path": []}}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_discovered_from": [], "artifact_parser_mismatch": []}}),
        ):
            payload = build_candidate_audit_summary_report(show_category_counts=True)

        self.assertEqual(payload["category_counts"], {})

    def test_candidate_audit_summary_supports_both_category_flags_together(self) -> None:
        with (
            patch(
                "app.services.curated_sources.build_candidate_validation_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 1,
                    "web_with_artifact_path": ["web-1"],
                    "local_file_without_artifact_path": [],
                    "missing_source_origin": [],
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_metadata_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_notes": []}},
            ),
            patch(
                "app.services.curated_sources.build_candidate_semantic_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"local_file_without_artifact": []}},
            ),
            patch(
                "app.services.curated_sources.build_candidate_operational_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_discovered_from": []}},
            ),
        ):
            payload = build_candidate_audit_summary_report(
                show_nonzero_categories=True,
                show_category_counts=True,
            )

        self.assertEqual(payload["nonzero_categories"], {"validate_candidates": ["web_with_artifact_path"]})
        self.assertEqual(payload["category_counts"], {"validate_candidates": {"web_with_artifact_path": 1}})

    def test_candidate_audit_summary_sorted_category_counts_orders_by_count_then_name(self) -> None:
        with (
            patch(
                "app.services.curated_sources.build_candidate_validation_report",
                return_value={
                    "candidate_count": 26,
                    "warning_count": 5,
                    "zeta_issue": ["a"],
                    "alpha_issue": ["b", "c"],
                    "beta_issue": ["d", "e"],
                },
            ),
            patch(
                "app.services.curated_sources.build_candidate_metadata_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_notes": []}},
            ),
            patch(
                "app.services.curated_sources.build_candidate_semantic_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"local_file_without_artifact": []}},
            ),
            patch(
                "app.services.curated_sources.build_candidate_operational_audit_report",
                return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_discovered_from": []}},
            ),
        ):
            payload = build_candidate_audit_summary_report(
                show_category_counts=True,
                sort_category_counts=True,
            )

        self.assertEqual(
            list(payload["category_counts"]["validate_candidates"].items()),
            [("alpha_issue", 2), ("beta_issue", 2), ("zeta_issue", 1)],
        )

    def test_candidate_audit_summary_sorted_category_counts_stays_empty_when_clean(self) -> None:
        with (
            patch("app.services.curated_sources.build_candidate_validation_report", return_value={"candidate_count": 26, "warning_count": 0, "web_with_artifact_path": [], "local_file_without_artifact_path": [], "missing_source_origin": []}),
            patch("app.services.curated_sources.build_candidate_metadata_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_notes": [], "weak_parser_hint": []}}),
            patch("app.services.curated_sources.build_candidate_semantic_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"local_file_without_artifact": [], "web_with_artifact_path": []}}),
            patch("app.services.curated_sources.build_candidate_operational_audit_report", return_value={"candidate_count": 26, "warning_count": 0, "warnings": {"missing_discovered_from": [], "artifact_parser_mismatch": []}}),
        ):
            payload = build_candidate_audit_summary_report(
                show_category_counts=True,
                sort_category_counts=True,
            )

        self.assertEqual(payload["category_counts"], {})

    def test_render_candidate_listing_report_preserves_default_wrapper(self) -> None:
        report = {
            "count": 1,
            "filters": {"origin": "", "destination": ""},
            "items": [
                {
                    "candidate_id": "candidate-1",
                    "title": "Candidate 1",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                }
            ],
        }

        rendered = render_candidate_listing_report(report)

        self.assertIn('"count": 1', rendered)
        self.assertIn('"filters"', rendered)
        self.assertIn('"items"', rendered)

    def test_render_candidate_listing_report_supports_compact_wrapper(self) -> None:
        report = {
            "count": 1,
            "filters": {"origin": "", "destination": ""},
            "items": [
                {
                    "candidate_id": "candidate-1",
                    "title": "Candidate 1",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                }
            ],
        }

        rendered = render_candidate_listing_report(report, compact=True)
        parsed = json.loads(rendered)

        self.assertEqual(parsed["count"], 1)
        self.assertIn("items", parsed)
        self.assertNotIn("filters", parsed)

    def test_render_candidate_listing_report_supports_json_lines(self) -> None:
        report = {
            "count": 2,
            "items": [
                {
                    "candidate_id": "candidate-1",
                    "title": "Candidate 1",
                    "source_origin": "web",
                    "destination": "raw_review",
                    "status": "candidate",
                },
                {
                    "candidate_id": "candidate-2",
                    "title": "Candidate 2",
                    "source_origin": "local_file",
                    "destination": "coverage_inputs",
                    "status": "candidate",
                    "artifact_path": "data/coverage_inputs/example.pdf",
                },
            ],
        }

        rendered = render_candidate_listing_report(report, json_lines=True)
        lines = rendered.splitlines()

        self.assertEqual(len(lines), 2)
        self.assertNotIn('"count"', rendered)
        self.assertTrue(all(line.startswith("{") and line.endswith("}") for line in lines))

    def test_render_candidate_listing_report_compact_preserves_field_selection(self) -> None:
        report = {
            "count": 1,
            "filters": {"origin": "", "destination": ""},
            "items": [
                {
                    "candidate_id": "candidate-1",
                    "title": "Candidate 1",
                }
            ],
        }

        rendered = render_candidate_listing_report(report, compact=True)
        parsed = json.loads(rendered)

        self.assertEqual(parsed, {"count": 1, "items": [{"candidate_id": "candidate-1", "title": "Candidate 1"}]})

    def test_render_candidate_listing_report_json_lines_preserves_filtered_selection(self) -> None:
        manifest = {
            "candidates": [
                {"candidate_id": "react-raw", "title": "React Interview Questions", "source_origin": "web", "destination": "raw_review", "status": "candidate"},
                {"candidate_id": "docker-coverage", "title": "Docker Cheat Sheet", "source_origin": "local_file", "destination": "coverage_inputs", "status": "candidate"},
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            report = build_candidate_listing_report(query="react")

        rendered = render_candidate_listing_report(report, json_lines=True)
        lines = rendered.splitlines()

        self.assertEqual(len(lines), 1)
        self.assertIn('"candidate_id": "react-raw"', lines[0])

    def test_list_candidates_without_field_selection_preserves_full_item_shape(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "artifact_path": "data/raw_review/local-1.md",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_listing_report()

        self.assertEqual(
            set(payload["items"][0].keys()),
            {"candidate_id", "title", "source_origin", "destination", "status", "artifact_path", "artifact_exists"},
        )

    def test_list_candidates_includes_review_fields_when_present(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "artifact_path": "data/raw_review/local-1.md",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                }
            ]
        }

        with (
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources._artifact_path_exists", return_value=True),
        ):
            payload = build_candidate_listing_report()

        self.assertEqual(payload["items"][0]["review_decision"], "approved")
        self.assertEqual(payload["items"][0]["review_decided_at"], "2026-03-01T00:00:00+00:00")

    def test_list_candidates_with_field_selection_returns_only_requested_fields(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "artifact_path": "data/raw_review/local-1.md",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(fields=["candidate_id", "title"])

        self.assertEqual(payload["items"], [{"candidate_id": "local-1", "title": "Local 1"}])

    def test_list_candidates_with_field_selection_supports_review_decision(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "review_decision": "approved",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(fields=["candidate_id", "review_decision"])

        self.assertEqual(payload["items"], [{"candidate_id": "local-1", "review_decision": "approved"}])

    def test_list_candidates_with_field_selection_supports_review_decided_at(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(fields=["candidate_id", "review_decided_at"])

        self.assertEqual(
            payload["items"],
            [{"candidate_id": "local-1", "review_decided_at": "2026-03-01T00:00:00+00:00"}],
        )

    def test_list_candidates_field_selection_keeps_review_fields_with_review_filter(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "approved-1",
                    "title": "Approved 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                },
                {
                    "candidate_id": "rejected-1",
                    "title": "Rejected 1",
                    "source_origin": "local_file",
                    "destination": "question_bank",
                    "status": "candidate",
                    "review_decision": "rejected",
                },
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(
                review_decision="approved",
                fields=["candidate_id", "review_decision", "review_decided_at"],
            )

        self.assertEqual(
            payload["items"],
            [
                {
                    "candidate_id": "approved-1",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                }
            ],
        )

    def test_list_candidates_field_selection_stays_stable_without_review(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            payload = build_candidate_listing_report(fields=["candidate_id", "review_decision"])

        self.assertEqual(payload["items"], [{"candidate_id": "local-1"}])

    def test_list_candidates_field_selection_works_with_json_lines(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "local-1",
                    "title": "Local 1",
                    "source_origin": "local_file",
                    "destination": "raw_review",
                    "status": "candidate",
                    "artifact_path": "data/raw_review/local-1.md",
                }
            ]
        }

        with patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest):
            report = build_candidate_listing_report(fields=["candidate_id", "artifact_path"])

        rendered = render_candidate_listing_report(report, json_lines=True)
        parsed = json.loads(rendered)
        self.assertEqual(parsed, {"candidate_id": "local-1", "artifact_path": "data/raw_review/local-1.md"})

    def test_cli_list_candidates_rejects_invalid_field(self) -> None:
        stderr = io.StringIO()
        argv = [
            "curated_sources",
            "list-candidates",
            "--field",
            "invalid_field",
        ]

        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                _main()

        self.assertEqual(exc.exception.code, 2)
        self.assertIn("invalid choice", stderr.getvalue())

    def test_curated_sources_report_exposes_by_origin_and_consistency_warning_count(self) -> None:
        indexes_manifest = {"indexes": []}
        candidates_manifest = {
            "candidates": [
                {
                    "candidate_id": "web-clean",
                    "source_origin": "web",
                    "status": "candidate",
                    "destination": "raw_review",
                    "trust_level": "medium_trust",
                },
                {
                    "candidate_id": "local-clean",
                    "source_origin": "local_file",
                    "artifact_path": "data/raw_review/local.md",
                    "status": "candidate",
                    "destination": "raw_review",
                    "trust_level": "low_trust",
                },
                {
                    "candidate_id": "missing-origin",
                    "status": "candidate",
                    "destination": "raw_review",
                    "trust_level": "low_trust",
                },
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_indexes_manifest", return_value=indexes_manifest),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=candidates_manifest),
        ):
            payload = build_curated_sources_report()

        self.assertIn("candidate_summary", payload)
        self.assertIn("by_origin", payload["candidate_summary"])
        self.assertIn("web", payload["candidate_summary"]["by_origin"])
        self.assertIn("local_file", payload["candidate_summary"]["by_origin"])
        self.assertEqual(payload["candidate_summary"]["by_origin"]["web"], 2)
        self.assertEqual(payload["candidate_summary"]["by_origin"]["local_file"], 1)
        self.assertIn("candidate_consistency", payload)
        self.assertIn("warning_count", payload["candidate_consistency"])
        self.assertEqual(payload["candidate_consistency"]["warning_count"], 1)
        self.assertEqual(payload["candidate_consistency"]["warnings"]["missing_source_origin"], ["missing-origin"])

    def test_curated_sources_report_falls_back_missing_source_origin_to_web(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_indexes_manifest", return_value={"indexes": []}),
            patch(
                "app.services.curated_sources.load_source_candidates_manifest",
                return_value={
                    "candidates": [
                        {
                            "candidate_id": "missing-origin",
                            "status": "candidate",
                            "destination": "raw_review",
                            "trust_level": "low_trust",
                        }
                    ]
                },
            ),
        ):
            payload = build_curated_sources_report()

        self.assertEqual(payload["candidate_summary"]["by_origin"]["web"], 1)
        self.assertEqual(payload["candidate_summary"]["by_origin"]["local_file"], 0)
        self.assertEqual(payload["candidate_consistency"]["warning_count"], 1)
        self.assertEqual(payload["candidate_consistency"]["warnings"]["missing_source_origin"], ["missing-origin"])

    def test_build_target_match_inspection_report_marks_legacy_target_match(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "legacy-target-match",
                    "status": "candidate",
                    "destination": "question_bank",
                    "source_origin": "local_file",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "promotion_log": [],
                }
            ]
        }
        promotion_check = {
            "candidate_id": "legacy-target-match",
            "exists": True,
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_already_matches": True,
            "would_copy": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir) / "data" / "question_bank_raw" / "example.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("already there", encoding="utf-8")
            with (
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
                patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
                patch("app.services.curated_sources.PROJECT_ROOT", Path(tmpdir)),
            ):
                payload = build_target_match_inspection_report("legacy-target-match")

        self.assertTrue(payload["exists"])
        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(payload["destination"], "question_bank")
        self.assertEqual(payload["source_origin"], "local_file")
        self.assertTrue(payload["target_exists"])
        self.assertTrue(payload["target_already_matches"])
        self.assertFalse(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 0)
        self.assertTrue(payload["is_legacy_target_match"])

    def test_build_target_match_inspection_report_promoted_candidate_is_not_legacy(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "promoted-match",
                    "status": "promoted",
                    "destination": "knowledge",
                    "source_origin": "local_file",
                    "artifact_path": "data/source_candidates/files/knowledge/example.epub",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "knowledge",
                            "promoted_artifact_path": "data/knowledge_raw/example.epub",
                        }
                    ],
                }
            ]
        }
        promotion_check = {
            "candidate_id": "promoted-match",
            "exists": True,
            "planned_target_path": "data/knowledge_raw/example.epub",
            "target_already_matches": False,
            "would_copy": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir) / "data" / "knowledge_raw" / "example.epub"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("copied", encoding="utf-8")
            with (
                patch("app.services.curated_sources.ensure_curated_source_dirs"),
                patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
                patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
                patch("app.services.curated_sources.PROJECT_ROOT", Path(tmpdir)),
            ):
                payload = build_target_match_inspection_report("promoted-match")

        self.assertTrue(payload["target_exists"])
        self.assertTrue(payload["has_promotion_history"])
        self.assertEqual(payload["promotion_log_count"], 1)
        self.assertFalse(payload["is_legacy_target_match"])

    def test_build_target_match_inspection_report_without_target_match_is_not_legacy(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "candidate-no-match",
                    "status": "candidate",
                    "destination": "knowledge",
                    "source_origin": "local_file",
                    "artifact_path": "data/source_candidates/files/knowledge/example.epub",
                    "promotion_log": [],
                }
            ]
        }
        promotion_check = {
            "candidate_id": "candidate-no-match",
            "exists": True,
            "planned_target_path": "data/knowledge_raw/example.epub",
            "target_already_matches": False,
            "would_copy": True,
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.inspect_promotion_candidate", return_value=promotion_check),
        ):
            payload = build_target_match_inspection_report("candidate-no-match")

        self.assertFalse(payload["target_exists"])
        self.assertFalse(payload["target_already_matches"])
        self.assertFalse(payload["is_legacy_target_match"])

    def test_cli_inspect_target_match_handles_missing_candidate_stably(self) -> None:
        stdout = io.StringIO()
        argv = [
            "curated_sources",
            "inspect-target-match",
            "--candidate-id",
            "missing-candidate",
        ]
        report = {
            "candidate_id": "missing-candidate",
            "exists": False,
            "status": "",
            "destination": "",
            "source_origin": "",
            "planned_target_path": None,
            "target_exists": False,
            "target_already_matches": False,
            "has_promotion_history": False,
            "promotion_log_count": 0,
            "is_legacy_target_match": False,
        }

        with (
            patch.object(sys, "argv", argv),
            patch("app.services.curated_sources.build_target_match_inspection_report", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            _main()

        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["exists"])
        self.assertFalse(payload["is_legacy_target_match"])
        self.assertEqual(payload["candidate_id"], "missing-candidate")

    def test_reconcile_target_match_candidate_promotes_valid_legacy_case(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "legacy-target-match",
                    "status": "candidate",
                    "destination": "question_bank",
                    "source_origin": "local_file",
                    "artifact_path": "data/source_candidates/files/question_bank/example.md",
                    "review_decision": "approved",
                    "review_decided_at": "2026-03-01T00:00:00+00:00",
                    "promotion_log": [],
                }
            ]
        }
        inspection = {
            "candidate_id": "legacy-target-match",
            "exists": True,
            "status": "candidate",
            "destination": "question_bank",
            "source_origin": "local_file",
            "planned_target_path": "data/question_bank_raw/example.md",
            "target_exists": True,
            "target_already_matches": True,
            "has_promotion_history": False,
            "promotion_log_count": 0,
            "is_legacy_target_match": True,
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.build_target_match_inspection_report", return_value=inspection),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
            patch("app.services.curated_sources.sync_destination_manifests") as sync_manifests,
            patch("app.services.curated_sources.shutil.copy2") as copy2,
        ):
            payload = reconcile_target_match_candidate("legacy-target-match")

        self.assertEqual(payload["status"], "promoted")
        self.assertTrue(payload["promoted_at"])
        self.assertEqual(payload["promoted_to"], "question_bank")
        self.assertEqual(payload["promoted_artifact_path"], "data/question_bank_raw/example.md")
        self.assertEqual(len(payload["promotion_log"]), 1)
        self.assertTrue(payload["promotion_log"][0]["reconciled_from_target_match"])
        self.assertEqual(payload["promotion_log"][0]["promoted_to"], "question_bank")
        written_candidates = write_manifest.call_args.args[0]
        self.assertEqual(written_candidates[0]["status"], "promoted")
        self.assertEqual(written_candidates[0]["promotion_log"][0]["promoted_artifact_path"], "data/question_bank_raw/example.md")
        sync_manifests.assert_called_once()
        copy2.assert_not_called()

    def test_reconcile_target_match_candidate_rejects_missing_candidate(self) -> None:
        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value={"candidates": []}),
        ):
            with self.assertRaisesRegex(ValueError, "candidate_id not found"):
                reconcile_target_match_candidate("missing-candidate")

    def test_reconcile_target_match_candidate_blocks_non_legacy_case(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "not-legacy",
                    "status": "candidate",
                    "destination": "knowledge",
                    "promotion_log": [],
                }
            ]
        }
        inspection = {
            "candidate_id": "not-legacy",
            "exists": True,
            "is_legacy_target_match": False,
            "planned_target_path": "data/knowledge_raw/example.epub",
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.build_target_match_inspection_report", return_value=inspection),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "not a legacy target-match case"):
                reconcile_target_match_candidate("not-legacy")

        write_manifest.assert_not_called()

    def test_reconcile_target_match_candidate_blocks_already_promoted_candidate(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "already-promoted",
                    "status": "promoted",
                    "destination": "knowledge",
                    "promotion_log": [],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "already promoted"):
                reconcile_target_match_candidate("already-promoted")

        write_manifest.assert_not_called()

    def test_reconcile_target_match_candidate_blocks_existing_promotion_history(self) -> None:
        manifest = {
            "candidates": [
                {
                    "candidate_id": "history-present",
                    "status": "candidate",
                    "destination": "question_bank",
                    "promotion_log": [
                        {
                            "promoted_at": "2026-03-01T00:00:00+00:00",
                            "promoted_to": "question_bank",
                            "promoted_artifact_path": "data/question_bank_raw/example.md",
                        }
                    ],
                }
            ]
        }

        with (
            patch("app.services.curated_sources.ensure_curated_source_dirs"),
            patch("app.services.curated_sources.load_source_candidates_manifest", return_value=manifest),
            patch("app.services.curated_sources.write_source_candidates_manifest") as write_manifest,
        ):
            with self.assertRaisesRegex(ValueError, "already has promotion history"):
                reconcile_target_match_candidate("history-present")

        write_manifest.assert_not_called()


if __name__ == "__main__":
    unittest.main()
