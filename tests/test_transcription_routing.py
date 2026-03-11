import unittest
from unittest.mock import patch

import app.services.transcription as transcription


class TranscriptionRoutingTests(unittest.TestCase):
    def test_local_ok_uses_local_provider(self) -> None:
        runtime = {
            "provider": "local",
            "provider_selected": "local",
            "transcription_preference": "local",
            "local_available": True,
            "local_model": "local-asr-baseline",
            "local_timeout_ms": 1200,
            "external_preferred": False,
            "external_available": True,
            "external_model": "gpt-4o-mini",
        }
        with (
            patch.object(transcription, "get_transcription_runtime", return_value=runtime),
            patch.object(transcription, "transcribe_local", return_value="texto-local"),
        ):
            payload = transcription.transcribe_with_trace("entrada")

        self.assertEqual(payload["provider_selected"], "local")
        self.assertEqual(payload["provider_used"], "local")
        self.assertFalse(payload["fallback_used"])
        self.assertEqual(payload["fallback_reason"], "")
        self.assertGreaterEqual(int(payload["transcription_latency_ms"]), 0)

    def test_local_failure_falls_back_to_external(self) -> None:
        runtime = {
            "provider": "local",
            "provider_selected": "local",
            "transcription_preference": "local",
            "local_available": False,
            "local_model": "local-asr-baseline",
            "local_timeout_ms": 1200,
            "external_preferred": False,
            "external_available": True,
            "external_model": "gpt-4o-mini",
        }
        with (
            patch.object(transcription, "get_transcription_runtime", return_value=runtime),
            patch.object(transcription, "transcribe_local", side_effect=ValueError("local_asr_unavailable")),
            patch.object(transcription, "_transcribe_external", return_value="texto-external"),
        ):
            payload = transcription.transcribe_with_trace("entrada")

        self.assertEqual(payload["provider_selected"], "local")
        self.assertEqual(payload["provider_used"], "external")
        self.assertTrue(payload["fallback_used"])
        self.assertEqual(payload["fallback_reason"], "local_unavailable")
        self.assertGreaterEqual(int(payload["transcription_latency_ms"]), 0)

    def test_local_and_external_failure_falls_back_to_mock(self) -> None:
        runtime = {
            "provider": "local",
            "provider_selected": "local",
            "transcription_preference": "local",
            "local_available": False,
            "local_model": "local-asr-baseline",
            "local_timeout_ms": 1200,
            "external_preferred": False,
            "external_available": True,
            "external_model": "gpt-4o-mini",
        }
        with (
            patch.object(transcription, "get_transcription_runtime", return_value=runtime),
            patch.object(transcription, "transcribe_local", side_effect=ValueError("local_asr_unavailable")),
            patch.object(transcription, "_transcribe_external", side_effect=ValueError("external_error")),
            patch.object(transcription, "transcribe_mock", return_value="texto-mock"),
        ):
            payload = transcription.transcribe_with_trace("entrada")

        self.assertEqual(payload["provider_selected"], "local")
        self.assertEqual(payload["provider_used"], "mock")
        self.assertTrue(payload["fallback_used"])
        self.assertEqual(payload["fallback_reason"], "local_unavailable_external_error")
        self.assertGreaterEqual(int(payload["transcription_latency_ms"]), 0)


if __name__ == "__main__":
    unittest.main()
