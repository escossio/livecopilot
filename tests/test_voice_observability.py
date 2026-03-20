import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.voice_observability import record_voice_event


class VoiceObservabilityTests(unittest.TestCase):
    def test_record_voice_event_creates_session_trace_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            voice_observability_dir = tmp_path / "var_voice_observability"
            voice_events_file = voice_observability_dir / "voice_events.ndjson"
            voice_session_root = tmp_path / "logs" / "voice_sessions"
            voice_session_index_file = voice_session_root / "session_index.json"

            with (
                patch("app.services.voice_observability.VOICE_OBSERVABILITY_DIR", voice_observability_dir),
                patch("app.services.voice_observability.VOICE_EVENTS_FILE", voice_events_file),
                patch("app.services.voice_observability.VOICE_SESSION_ROOT", voice_session_root),
                patch("app.services.voice_observability.VOICE_SESSION_INDEX_FILE", voice_session_index_file),
            ):
                session_dir = record_voice_event(
                    "voice_session_started",
                    session_id="rt-xyz",
                    conversation_id="rt-xyz",
                    source="frontend",
                    transport="webrtc",
                    ts="2026-03-13T20:33:15Z",
                    started_at="2026-03-13T20:33:15Z",
                    url="https://livecopilot.escossio.dev.br",
                    model="gpt-realtime-mini",
                    voice="alloy",
                    secure_context=True,
                    media_devices=True,
                    get_user_media=True,
                    user_agent="test-agent",
                    response_summary="sessao iniciada",
                )
                record_voice_event(
                    "transcription_completed",
                    session_id="rt-xyz",
                    conversation_id="rt-xyz",
                    source="frontend",
                    ts="2026-03-13T20:33:16Z",
                    transcript_excerpt="voce esta me escutando?",
                )
                record_voice_event(
                    "voice_backend_response_completed",
                    session_id="rt-xyz",
                    conversation_id="rt-xyz",
                    source="backend",
                    ts="2026-03-13T20:33:17Z",
                    http_status=200,
                    backend="infra_status_connector",
                    response_summary="O backend principal do Livecopilot esta saudavel.",
                )

            session_path = Path(session_dir)
            self.assertTrue(session_path.is_dir())
            self.assertTrue((session_path / "session_meta.json").exists())
            self.assertTrue((session_path / "frontend_events.jsonl").exists())
            self.assertTrue((session_path / "backend_events.jsonl").exists())
            self.assertTrue((session_path / "transcripts.jsonl").exists())
            self.assertTrue((session_path / "responses.jsonl").exists())
            self.assertTrue((session_path / "summary.md").exists())

            meta = json.loads((session_path / "session_meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["session_id"], "rt-xyz")
            self.assertEqual(meta["model"], "gpt-realtime-mini")
            self.assertEqual(meta["voice"], "alloy")

            transcript_rows = [
                json.loads(line)
                for line in (session_path / "transcripts.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(transcript_rows[0]["text"], "voce esta me escutando?")

            response_rows = [
                json.loads(line)
                for line in (session_path / "responses.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(response_rows[0]["backend"], "infra_status_connector")

            summary = (session_path / "summary.md").read_text(encoding="utf-8")
            self.assertIn("session_id: `rt-xyz`", summary)
            self.assertIn("ultimo evento bem-sucedido", summary)


if __name__ == "__main__":
    unittest.main()
