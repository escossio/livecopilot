import base64
import json
import socket
import unittest
import urllib.error
from unittest.mock import patch

from app.services.mikrotik_connector import _build_rest_request, list_dhcp_leases, load_mikrotik_config, resolve_mikrotik_query


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class MikrotikConnectorTests(unittest.TestCase):
    def test_load_mikrotik_config_supports_verify_tls_false(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "MIKROTIK_BASE_URL": "https://10.0.0.1/rest",
                "MIKROTIK_USERNAME": "livecopilot_ro",
                "MIKROTIK_PASSWORD": "secret",
                "MIKROTIK_VERIFY_TLS": "false",
                "MIKROTIK_TIMEOUT": "7",
            },
            clear=False,
        ):
            payload = load_mikrotik_config()

        self.assertTrue(payload["configured"])
        self.assertEqual(payload["base_url"], "https://10.0.0.1/rest")
        self.assertFalse(payload["verify_tls"])
        self.assertEqual(payload["timeout"], 7.0)

    def test_load_mikrotik_config_supports_ca_path(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "MIKROTIK_BASE_URL": "https://router.example/rest",
                "MIKROTIK_USERNAME": "livecopilot_ro",
                "MIKROTIK_PASSWORD": "secret",
                "MIKROTIK_VERIFY_TLS": "/etc/ssl/mikrotik-ca.pem",
            },
            clear=False,
        ):
            payload = load_mikrotik_config()

        self.assertEqual(payload["verify_tls"], "/etc/ssl/mikrotik-ca.pem")

    def test_build_rest_request_uses_basic_auth_header(self) -> None:
        request = _build_rest_request("https://10.0.0.1/rest/ip/dhcp-server/lease", "livecopilot_ro", "secret")

        expected = base64.b64encode(b"livecopilot_ro:secret").decode("ascii")
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.headers["Authorization"], f"Basic {expected}")
        self.assertEqual(request.headers["Accept"], "application/json")

    def test_list_dhcp_leases_returns_normalized_rows(self) -> None:
        body = (
            b'[{"address":"192.168.88.10","mac-address":"AA:BB:CC:DD:EE:01","host-name":"notebook","status":"bound","last-seen":"10s","expires-after":"9m59s"},'
            b'{"active-address":"192.168.88.11","active-mac-address":"AA:BB:CC:DD:EE:02","host-name":"tv","status":"bound","expires-after":"4m20s"}]'
        )
        with (
            patch.dict(
                "os.environ",
                {
                    "MIKROTIK_BASE_URL": "https://10.0.0.1/rest",
                    "MIKROTIK_USERNAME": "livecopilot_ro",
                    "MIKROTIK_PASSWORD": "secret",
                    "MIKROTIK_VERIFY_TLS": "false",
                    "MIKROTIK_TIMEOUT": "5",
                },
                clear=False,
            ),
            patch("app.services.mikrotik_connector.urllib.request.urlopen", return_value=_FakeResponse(body)) as mocked_open,
        ):
            payload = list_dhcp_leases()

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["client_count"], 2)
        self.assertEqual(payload["leases"][0]["ip"], "192.168.88.10")
        self.assertEqual(payload["leases"][0]["host_name"], "notebook")
        self.assertEqual(mocked_open.call_args.kwargs["timeout"], 5.0)

    def test_list_dhcp_leases_keeps_rows_when_routeros_false_flags_are_strings(self) -> None:
        body = json.dumps(
            [
                {
                    "active-address": "10.45.0.10",
                    "active-mac-address": "64:E4:A5:00:11:22",
                    "host-name": "LGwebOSTV",
                    "status": "bound",
                    "last-seen": "9m34s",
                    "expires-after": "20m26s",
                    "server": "defconf",
                    "dynamic": "true",
                    "blocked": "false",
                    "disabled": "false",
                }
            ]
        ).encode("utf-8")
        with (
            patch.dict(
                "os.environ",
                {
                    "MIKROTIK_BASE_URL": "https://10.0.0.1/rest",
                    "MIKROTIK_USERNAME": "livecopilot_ro",
                    "MIKROTIK_PASSWORD": "secret",
                    "MIKROTIK_VERIFY_TLS": "false",
                    "MIKROTIK_TIMEOUT": "5",
                },
                clear=False,
            ),
            patch("app.services.mikrotik_connector.urllib.request.urlopen", return_value=_FakeResponse(body)),
        ):
            payload = list_dhcp_leases()

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["client_count"], 1)
        self.assertFalse(payload["leases"][0]["blocked"])
        self.assertFalse(payload["leases"][0]["disabled"])
        self.assertTrue(payload["leases"][0]["dynamic"])

    def test_list_dhcp_leases_returns_fail_on_timeout(self) -> None:
        with (
            patch.dict(
                "os.environ",
                {
                    "MIKROTIK_BASE_URL": "https://10.0.0.1/rest",
                    "MIKROTIK_USERNAME": "livecopilot_ro",
                    "MIKROTIK_PASSWORD": "secret",
                },
                clear=False,
            ),
            patch(
                "app.services.mikrotik_connector.urllib.request.urlopen",
                side_effect=urllib.error.URLError(socket.timeout("timed out")),
            ),
        ):
            payload = list_dhcp_leases()

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["reason"], "mikrotik_timeout")

    def test_list_dhcp_leases_returns_fail_on_http_error(self) -> None:
        with (
            patch.dict(
                "os.environ",
                {
                    "MIKROTIK_BASE_URL": "https://10.0.0.1/rest",
                    "MIKROTIK_USERNAME": "livecopilot_ro",
                    "MIKROTIK_PASSWORD": "secret",
                },
                clear=False,
            ),
            patch(
                "app.services.mikrotik_connector.urllib.request.urlopen",
                side_effect=urllib.error.HTTPError(
                    url="https://10.0.0.1/rest/ip/dhcp-server/lease",
                    code=403,
                    msg="forbidden",
                    hdrs=None,
                    fp=None,
                ),
            ),
        ):
            payload = list_dhcp_leases()

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["reason"], "mikrotik_auth_failed")

    def test_resolve_mikrotik_query_preserves_fail_response(self) -> None:
        with patch("app.services.mikrotik_connector.list_dhcp_leases", return_value={
            "status": "fail",
            "reason": "mikrotik_connect_failed",
            "latency_ms": 13,
            "client_count": 0,
            "leases": [],
            "base_url": "https://10.0.0.1/rest",
            "verify_tls": False,
            "error": "connection refused",
        }), patch("app.services.mikrotik_connector.append_event"):
            payload = resolve_mikrotik_query("quem esta conectado na minha rede?", "list_dhcp_leases")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["knowledge_context"]["connector"], "mikrotik_connector")
        self.assertEqual(payload["knowledge_context"]["reason"], "mikrotik_connect_failed")
        self.assertIn("connection refused", " ".join(payload["bullets"]))


if __name__ == "__main__":
    unittest.main()
