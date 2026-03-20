import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.operational_memory import (
    append_event,
    compare_with_last_event,
    get_last_event_for_target,
    read_recent_events,
)


class OperationalMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_path = Path(self.temp_dir.name) / "operational_memory.jsonl"
        self.memory_patch = patch("app.services.operational_memory.OPERATIONAL_MEMORY_FILE", self.memory_path)
        self.memory_patch.start()

    def tearDown(self) -> None:
        self.memory_patch.stop()
        self.temp_dir.cleanup()

    def test_append_event(self) -> None:
        event = append_event(
            kind="infra_check",
            target_type="server",
            target_name="agt01",
            status="ok",
            summary="check curto de servidor em agt01: status ok",
            source="infra_status_connector",
            timestamp="2026-03-14T06:30:00Z",
        )

        self.assertEqual(event["target_name"], "agt01")
        rows = self.memory_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(rows), 1)

    def test_read_recent_events(self) -> None:
        append_event(
            kind="infra_check",
            target_type="backend",
            target_name="livecopilot_backend",
            status="ok",
            summary="check curto do backend em livecopilot_backend: status ok",
            source="infra_status_connector",
            timestamp="2026-03-14T06:30:00Z",
        )
        append_event(
            kind="voice_runtime_event",
            target_type="voice",
            target_name="session-a",
            status="info",
            summary="sessao de voz iniciou",
            source="voice_observability",
            timestamp="2026-03-14T06:31:00Z",
        )

        rows = read_recent_events(limit=1)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "voice_runtime_event")

    def test_get_last_event_for_target(self) -> None:
        append_event(
            kind="infra_check",
            target_type="postgresql",
            target_name="livecopilot",
            status="warn",
            summary="check curto de PostgreSQL em livecopilot: status warn",
            source="infra_status_connector",
            timestamp="2026-03-14T06:30:00Z",
        )
        append_event(
            kind="infra_check",
            target_type="postgresql",
            target_name="livecopilot",
            status="ok",
            summary="check curto de PostgreSQL em livecopilot: status ok",
            source="infra_status_connector",
            timestamp="2026-03-14T06:31:00Z",
        )

        event = get_last_event_for_target(kind="infra_check", target_type="postgresql", target_name="livecopilot")

        self.assertIsNotNone(event)
        self.assertEqual(event["status"], "ok")

    def test_compare_with_last_event(self) -> None:
        previous = {
            "timestamp": "2026-03-14T06:30:00Z",
            "kind": "infra_check",
            "target_type": "server",
            "target_name": "agt01",
            "status": "warn",
            "summary": "check curto de servidor em agt01: status warn",
            "source": "infra_status_connector",
        }
        current = {
            "timestamp": "2026-03-14T06:31:00Z",
            "kind": "infra_check",
            "target_type": "server",
            "target_name": "agt01",
            "status": "ok",
            "summary": "check curto de servidor em agt01: status ok",
            "source": "infra_status_connector",
        }

        comparison = compare_with_last_event(current, previous)

        self.assertTrue(comparison["changed"])
        self.assertEqual(comparison["message"], "mudou de warn para ok")

    def test_read_recent_events_skips_invalid_lines(self) -> None:
        self.memory_path.write_text(
            '{"timestamp":"2026-03-14T06:30:00Z","kind":"infra_check","target_type":"server","target_name":"agt01","status":"ok","summary":"check curto de servidor em agt01: status ok","source":"infra_status_connector"}\n'
            '{"broken": true}\n',
            encoding="utf-8",
        )

        rows = read_recent_events(limit=5)

        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
