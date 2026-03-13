import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class LivecopilotInterfaceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def test_api_chat_returns_livecopilot_response_contract(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "como configurar probes no kubernetes"}],
            "suggestions": [
                "Use liveness e readiness probes com thresholds coerentes.",
                "Comece validando o endpoint de health.",
                "Evite timeouts agressivos no primeiro deploy.",
            ],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {
                "used_search": True,
                "query": "como configurar probes no kubernetes",
                "result_count": 2,
                "context": "docs de probes",
                "search_backend": "semantic_local",
                "fallback_used": False,
                "context_used": True,
                "semantic_api_ok": True,
                "semantic_duration_ms": 12,
                "sources": [
                    {"title": "kubernetes probes", "source_file": "continuity_docs_selected/docs/probes.md"},
                ],
            },
        }

        with patch("app.api.routes.process_ingest", return_value=fake_snapshot):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "como configurar probes no kubernetes",
                    "mode": "generic",
                    "conversation_id": "chat-contract",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["channel"], "text")
        self.assertEqual(payload["conversation_id"], "chat-contract")
        self.assertIn("answer", payload)
        self.assertIn("bullets", payload)
        self.assertIn("knowledge_context", payload)
        self.assertIn("snapshot", payload)
        self.assertEqual(payload["knowledge_context"]["search_backend"], "semantic_local")

    def test_api_realtime_session_returns_ephemeral_contract(self) -> None:
        fake_runtime = {
            "enabled": True,
            "provider": "openai_realtime",
            "webrtc_url": "https://api.openai.com/v1/realtime/calls",
            "model": "gpt-realtime-mini",
            "voice": "alloy",
            "language": "pt",
            "transcription_model": "gpt-4o-mini-transcribe",
        }
        fake_created = {
            "client_secret": "rt_secret_123",
            "expires_at": 1234567890,
            "webrtc_url": "https://api.openai.com/v1/realtime/calls",
            "model": "gpt-realtime-mini",
            "voice": "alloy",
            "language": "pt",
            "transcription_model": "gpt-4o-mini-transcribe",
            "provider": "openai_realtime",
            "session": {"type": "realtime", "model": "gpt-realtime-mini"},
        }

        with (
            patch("app.api.routes.get_realtime_runtime", return_value=fake_runtime),
            patch("app.api.routes.create_realtime_client_secret", return_value=fake_created),
        ):
            response = self.client.post("/api/realtime/session", json={"mode": "generic"})

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["channel"], "voice")
        self.assertEqual(payload["provider"], "openai_realtime")
        self.assertEqual(payload["client_secret"], "rt_secret_123")
        self.assertEqual(payload["webrtc_url"], "https://api.openai.com/v1/realtime/calls")
        self.assertEqual(payload["model"], "gpt-realtime-mini")
        self.assertEqual(payload["session"]["type"], "realtime")


if __name__ == "__main__":
    unittest.main()
