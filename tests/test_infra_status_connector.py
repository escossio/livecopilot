import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.infra_status_connector import _check_server_runtime, resolve_infra_status_query


class _FakeAudioCapture:
    def __init__(self, live: bool = False) -> None:
        self._live = live

    def is_live(self) -> bool:
        return self._live


class InfraStatusConnectorTests(unittest.TestCase):
    def _build_request(self, live: bool = False):
        return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(audio_capture=_FakeAudioCapture(live=live))))

    def test_backend_health_query_returns_backend_connector_payload(self) -> None:
        request = self._build_request(live=False)
        with (
            patch("app.services.infra_status_connector.get_transcription_runtime", return_value={"provider_selected": "external"}),
            patch("app.services.infra_status_connector.get_voice_output_runtime", return_value={"enabled_default": False}),
            patch("app.services.infra_status_connector.get_realtime_runtime", return_value={"enabled": True, "api_key_present": True}),
            patch("app.services.infra_status_connector.get_last_event_for_target", return_value=None),
            patch("app.services.infra_status_connector.append_event"),
        ):
            payload = resolve_infra_status_query(request, "o backend do Livecopilot esta saudavel?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["intent"], "livecopilot_backend_status")
        self.assertEqual(payload["knowledge_context"]["connector"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["target"], "livecopilot_backend")
        self.assertEqual(payload["knowledge_context"]["operational_memory"]["message"], "")

    def test_postgres_query_returns_scope_limited_response(self) -> None:
        request = self._build_request(live=False)
        with patch(
            "app.services.infra_status_connector._check_postgres_runtime",
            return_value={
                "status": "ok",
                "reason": "",
                "latency_ms": 18,
                "database": "livecopilot",
                "server_version": "PostgreSQL 17.8",
                "select_1_ok": True,
                "dsn_present": True,
            },
        ), patch("app.services.infra_status_connector.get_last_event_for_target", return_value=None), patch(
            "app.services.infra_status_connector.append_event"
        ):
            payload = resolve_infra_status_query(request, "como esta meu PostgreSQL?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["intent"], "infra_status")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["knowledge_context"]["connector"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["target"], "postgresql")
        self.assertTrue(payload["knowledge_context"]["select_1_ok"])

    def test_banco_saudavel_query_can_route_to_postgresql_target(self) -> None:
        request = self._build_request(live=False)
        with patch(
            "app.services.infra_status_connector._check_postgres_runtime",
            return_value={
                "status": "fail",
                "reason": "postgres_connect_failed",
                "latency_ms": 200,
                "database": "",
                "server_version": "",
                "select_1_ok": False,
                "dsn_present": True,
                "error": "timeout",
            },
        ), patch(
            "app.services.infra_status_connector.get_last_event_for_target",
            return_value={
                "timestamp": "2026-03-14T06:30:00Z",
                "kind": "infra_check",
                "target_type": "postgresql",
                "target_name": "livecopilot",
                "status": "fail",
                "summary": "check curto de PostgreSQL em livecopilot: status fail",
                "source": "infra_status_connector",
            },
        ), patch("app.services.infra_status_connector.append_event"):
            payload = resolve_infra_status_query(request, "o banco esta saudavel?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["knowledge_context"]["target"], "postgresql")
        self.assertEqual(payload["status"], "fail")
        self.assertIn("SELECT 1", payload["bullets"][1])
        self.assertIn("sem mudanca relevante", payload["bullets"][-1])

    def test_servidor_query_can_route_to_server_target(self) -> None:
        request = self._build_request(live=False)
        with patch(
            "app.services.infra_status_connector._check_server_runtime",
            return_value={
                "status": "ok",
                "reason": "server_http_runtime_ok",
                "requested_target": "agt01",
                "checked_host": "agt01",
                "reachable": True,
                "latency_ms": 3,
                "check_mode": "whitelist_http_health_status",
                "health_ok": True,
                "app_status": "ok",
                "capture_mode": "mock",
                "ws_enabled": True,
                "realtime_api_enabled": True,
                "source_urls": ["http://agt01:8000/health", "http://agt01:8000/status"],
            },
        ), patch(
            "app.services.infra_status_connector.get_last_event_for_target",
            return_value={
                "timestamp": "2026-03-14T06:30:00Z",
                "kind": "infra_check",
                "target_type": "server",
                "target_name": "agt01",
                "status": "warn",
                "summary": "check curto de servidor em agt01: status warn",
                "source": "infra_status_connector",
            },
        ), patch("app.services.infra_status_connector.append_event"):
            payload = resolve_infra_status_query(request, "como esta o servidor agt01?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["intent"], "infra_status")
        self.assertEqual(payload["knowledge_context"]["target"], "server")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["knowledge_context"]["check_mode"], "whitelist_http_health_status")
        self.assertIn("health_ok", payload["bullets"][1])
        self.assertIn("mudou de warn para ok", payload["bullets"][-1])

    def test_host_alias_query_can_route_to_server_target_with_warn_when_unmapped(self) -> None:
        request = self._build_request(live=False)
        with patch(
            "app.services.infra_status_connector._check_server_runtime",
            return_value={
                "status": "warn",
                "reason": "server_target_not_mapped",
                "requested_target": "llm",
                "checked_host": "agt01",
                "reachable": False,
                "latency_ms": 3,
                "check_mode": "whitelist_http_health_status",
            },
        ), patch("app.services.infra_status_connector.get_last_event_for_target", return_value=None), patch(
            "app.services.infra_status_connector.append_event"
        ):
            payload = resolve_infra_status_query(request, "o llm esta saudavel?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["intent"], "infra_status")
        self.assertEqual(payload["knowledge_context"]["target"], "server")
        self.assertEqual(payload["status"], "warn")
        self.assertEqual(payload["knowledge_context"]["requested_target"], "llm")

    def test_carga_do_servidor_query_can_route_to_server_target(self) -> None:
        request = self._build_request(live=False)
        with patch(
            "app.services.infra_status_connector._check_server_runtime",
            return_value={
                "status": "warn",
                "reason": "server_metrics_warn",
                "requested_target": "agt01",
                "checked_host": "agt01",
                "reachable": True,
                "uptime_seconds": 7200,
                "load_average": [5.5, 4.2, 3.1],
                "memory_total_mb": 8192,
                "memory_available_mb": 512,
                "memory_available_pct": 6.2,
                "latency_ms": 2,
            },
        ), patch(
            "app.services.infra_status_connector.get_last_event_for_target",
            return_value={
                "timestamp": "2026-03-14T06:30:00Z",
                "kind": "infra_check",
                "target_type": "server",
                "target_name": "agt01",
                "status": "warn",
                "summary": "check curto de servidor em agt01: status warn",
                "source": "infra_status_connector",
            },
        ), patch("app.services.infra_status_connector.append_event"):
            payload = resolve_infra_status_query(request, "como esta a carga do servidor?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["knowledge_context"]["target"], "server")
        self.assertEqual(payload["status"], "warn")
        self.assertIn("sem mudanca relevante", payload["bullets"][-1])

    def test_check_server_runtime_uses_whitelisted_local_source_for_agt01(self) -> None:
        with (
            patch("app.services.infra_status_connector.socket.gethostname", return_value="agt01"),
            patch(
                "app.services.infra_status_connector._read_proc_text",
                side_effect=[
                    "3600.00 0.00",
                    "0.12 0.10 0.08 1/100 12345",
                    "MemTotal:       4194304 kB\nMemAvailable:   2097152 kB\n",
                ],
            ),
        ):
            payload = _check_server_runtime("agt01")

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["checked_host"], "agt01")
        self.assertEqual(payload["check_mode"], "whitelist_local_read_only_metrics")
        self.assertEqual(payload["memory_available_pct"], 50.0)

    def test_check_server_runtime_returns_warn_for_unmapped_named_host(self) -> None:
        payload = _check_server_runtime("debian2-1")

        self.assertEqual(payload["status"], "warn")
        self.assertEqual(payload["reason"], "server_target_not_mapped")
        self.assertEqual(payload["requested_target"], "debian2-1")


if __name__ == "__main__":
    unittest.main()
