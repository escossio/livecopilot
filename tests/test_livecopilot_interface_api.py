import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.state import ConversationState


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

    def test_api_chat_can_route_to_project_state_connector(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "qual foi o ultimo handoff do projeto"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_connector = {
            "matched": True,
            "intent": "latest_handoff",
            "answer": "O ultimo handoff local e `docs/HANDOFF_X.md`.",
            "bullets": [
                "Resumo: publicacao concluida.",
                "Checkpoint atual: Checkpoint de preservacao.",
            ],
            "knowledge_context": {
                "query": "qual foi o ultimo handoff do projeto",
                "used_search": False,
                "search_backend": "project_state_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 3,
                "context": "handoff local mais recente",
                "sources": [
                    {"title": "STATUS.md", "source_file": "/lab/projects/livecopilot/STATUS.md"},
                ],
                "connector": "project_state_connector",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_project_state_query", return_value=fake_connector),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "qual foi o ultimo handoff do projeto",
                    "mode": "generic",
                    "conversation_id": "project-state-contract",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "project_state_connector")
        self.assertEqual(payload["answer"], fake_connector["answer"])
        self.assertEqual(payload["knowledge_context"]["connector"], "project_state_connector")
        self.assertEqual(payload["knowledge_context"]["intent"], "latest_handoff")

    def test_api_chat_operational_skill_can_route_to_postgresql_connector(self) -> None:
        fake_infra_connector = {
            "matched": True,
            "intent": "infra_status",
            "status": "ok",
            "answer": "O PostgreSQL do Livecopilot esta de pe e respondeu ao check read-only.",
            "bullets": [
                "status: ok.",
                "check: SELECT 1 read-only | latency_ms: 18.",
            ],
            "knowledge_context": {
                "query": "status do postgres",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "check read-only de PostgreSQL via DATABASE_URL com SELECT 1 e metadado fixo de runtime",
                "sources": [
                    {"title": "postgres_readonly_check", "source_file": "internal://postgresql/read_only_health"},
                ],
                "connector": "infra_status_connector",
                "target": "postgresql",
                "status": "ok",
            },
        }
        with (
            patch("app.api.routes.match_operational_skill", return_value={
                "matched": True,
                "skill": {"id": "postgresql_health_check"},
                "intent": "infra_status",
                "target": "postgresql",
                "source": "infra_status_connector",
                "action": {"type": "connector_call", "operation": "postgresql_health_check"},
                "response_policy": {"summary_template": "sum", "detail_template": "det"},
                "safety": {"mode": "read_only", "approval_required": False},
            }),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
            patch("app.api.routes.process_ingest") as process_ingest,
            patch("app.api.routes.append_event"),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "status do postgres",
                    "mode": "generic",
                    "conversation_id": "operational-skill-postgres",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "infra_status_connector")
        self.assertEqual(payload["answer"], fake_infra_connector["answer"])
        self.assertEqual(payload["knowledge_context"]["target"], "postgresql")
        self.assertEqual(payload["knowledge_context"]["routing_layer"], "operational_skills")
        self.assertEqual(payload["knowledge_context"]["skill_id"], "postgresql_health_check")
        process_ingest.assert_not_called()

    def test_api_chat_operational_skill_can_route_to_project_state_connector(self) -> None:
        fake_connector = {
            "matched": True,
            "intent": "latest_checkpoint",
            "answer": "O checkpoint mais recente registrado e `Checkpoint X`.",
            "bullets": ["Etapa atual: Etapa X."],
            "knowledge_context": {
                "query": "qual o ultimo checkpoint do projeto?",
                "used_search": False,
                "search_backend": "project_state_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "checkpoint mais recente",
                "sources": [{"title": "STATUS.md", "source_file": "/lab/projects/livecopilot/STATUS.md"}],
                "connector": "project_state_connector",
                "target": "project_state",
            },
        }
        with (
            patch("app.api.routes.match_operational_skill", return_value={
                "matched": True,
                "skill": {"id": "project_latest_status"},
                "intent": "latest_checkpoint",
                "target": "project_state",
                "source": "project_state_connector",
                "action": {"type": "connector_call", "operation": "project_latest_status"},
                "response_policy": {"summary_template": "sum", "detail_template": "det"},
                "safety": {"mode": "read_only", "approval_required": False},
            }),
            patch("app.api.routes.resolve_project_state_query", return_value=fake_connector),
            patch("app.api.routes.process_ingest") as process_ingest,
            patch("app.api.routes.append_event"),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "qual o ultimo checkpoint do projeto?",
                    "mode": "generic",
                    "conversation_id": "operational-skill-project-state",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "project_state_connector")
        self.assertEqual(payload["knowledge_context"]["routing_layer"], "operational_skills")
        self.assertEqual(payload["knowledge_context"]["skill_id"], "project_latest_status")
        process_ingest.assert_not_called()

    def test_api_chat_operational_skill_can_return_static_guidance_when_connector_not_integrated(self) -> None:
        with (
            patch("app.api.routes.match_operational_skill", return_value={
                "matched": True,
                "skill": {"id": "mikrotik_dhcp_clients_count"},
                "intent": "network_device_count",
                "target": "mikrotik",
                "source": "planned_connector",
                "action": {"type": "router_read_only", "operation": "list_dhcp_leases"},
                "response_policy": {
                    "summary_template": "Posso consultar os clientes do DHCP no MikroTik por um conector controlado.",
                    "detail_template": "A resposta deve indicar que a fonte e o DHCP do MikroTik.",
                },
                "safety": {"mode": "read_only", "approval_required": False},
            }),
            patch("app.api.routes.process_ingest") as process_ingest,
            patch("app.api.routes.append_event"),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "quantos dispositivos estao conectados na rede?",
                    "mode": "generic",
                    "conversation_id": "operational-skill-static",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "operational_skills")
        self.assertEqual(payload["knowledge_context"]["routing_layer"], "operational_skills")
        self.assertEqual(payload["knowledge_context"]["skill_id"], "mikrotik_dhcp_clients_count")
        self.assertIn("ainda sem conector operacional integrado", " ".join(payload["bullets"]).lower())
        process_ingest.assert_not_called()

    def test_api_chat_operational_skill_can_route_to_mikrotik_connector(self) -> None:
        fake_connector = {
            "matched": True,
            "intent": "network_device_count",
            "status": "ok",
            "answer": "Encontrei 3 cliente(s) ativo(s) ou utilmente identificados no servidor DHCP da sua rede.",
            "bullets": [
                "status: ok | operacao: list_dhcp_leases.",
                "client_count: 3 | latency_ms: 21.",
                "principais_clientes: notebook (ip=192.168.88.10 mac=AA:BB:CC:DD:EE:01 status=bound); tv (ip=192.168.88.11 mac=AA:BB:CC:DD:EE:02 status=bound)",
            ],
            "knowledge_context": {
                "query": "quem esta conectado na minha rede?",
                "used_search": False,
                "search_backend": "mikrotik_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 3,
                "context": "consulta read-only de leases do DHCP via MikroTik RouterOS REST API /ip/dhcp-server/lease",
                "sources": [{"title": "mikrotik_rest_dhcp_leases", "source_file": "internal://mikrotik/rest/ip/dhcp-server/lease"}],
                "connector": "mikrotik_connector",
                "target": "mikrotik",
                "status": "ok",
            },
        }
        with (
            patch("app.api.routes.match_operational_skill", return_value={
                "matched": True,
                "skill": {"id": "mikrotik_dhcp_clients_count"},
                "intent": "network_device_count",
                "target": "mikrotik",
                "source": "mikrotik",
                "action": {"type": "router_read_only", "operation": "list_dhcp_leases"},
                "response_policy": {"summary_template": "sum", "detail_template": "det"},
                "safety": {"mode": "read_only", "approval_required": False},
            }),
            patch("app.api.routes.resolve_mikrotik_query", return_value=fake_connector),
            patch("app.api.routes.process_ingest") as process_ingest,
            patch("app.api.routes.append_event"),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "quem esta conectado na minha rede?",
                    "mode": "generic",
                    "conversation_id": "operational-skill-mikrotik",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "mikrotik_connector")
        self.assertEqual(payload["answer"], fake_connector["answer"])
        self.assertEqual(payload["knowledge_context"]["routing_layer"], "operational_skills")
        self.assertEqual(payload["knowledge_context"]["skill_id"], "mikrotik_dhcp_clients_count")
        self.assertEqual(payload["knowledge_context"]["target"], "mikrotik")
        process_ingest.assert_not_called()

    def test_api_chat_falls_back_when_no_operational_skill_matches(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "como configurar probes no kubernetes"}],
            "suggestions": [
                "Use liveness e readiness probes com thresholds coerentes.",
                "Comece validando o endpoint de health.",
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
                "sources": [{"title": "kubernetes probes", "source_file": "continuity_docs_selected/docs/probes.md"}],
            },
        }
        with (
            patch("app.api.routes.match_operational_skill", return_value={"matched": False}),
            patch("app.api.routes.process_ingest", return_value=fake_snapshot) as process_ingest,
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "como configurar probes no kubernetes",
                    "mode": "generic",
                    "conversation_id": "operational-skill-fallback",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "semantic_local")
        process_ingest.assert_called_once()

    def test_realtime_respond_can_route_to_project_state_connector(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "qual foi o ultimo status do projeto"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_connector = {
            "matched": True,
            "intent": "latest_checkpoint",
            "answer": "O checkpoint mais recente registrado e `Checkpoint 2026-03-13: preservacao do estado apos publicacao HTTPS`.",
            "bullets": [
                "Etapa atual: Etapa 16 em andamento.",
                "Ultimo handoff: HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z.md.",
            ],
            "knowledge_context": {
                "query": "qual foi o ultimo status do projeto",
                "used_search": False,
                "search_backend": "project_state_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 3,
                "context": "checkpoint mais recente",
                "sources": [
                    {"title": "STATUS.md", "source_file": "/lab/projects/livecopilot/STATUS.md"},
                ],
                "connector": "project_state_connector",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_project_state_query", return_value=fake_connector),
        ):
            response = self.client.post(
                "/realtime/respond",
                json={
                    "text": "qual foi o ultimo status do projeto",
                    "mode": "generic",
                    "conversation_id": "voice-project-state-contract",
                    "voice_output_enabled": False,
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "project_state_connector")
        self.assertEqual(payload["conversation_id"], "voice-project-state-contract")
        self.assertEqual(payload["answer"], fake_connector["answer"])
        self.assertEqual(payload["knowledge_context"]["connector"], "project_state_connector")
        self.assertEqual(payload["knowledge_context"]["intent"], "latest_checkpoint")

    def test_api_chat_can_route_to_infra_status_connector(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "o backend do livecopilot esta saudavel?"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_infra_connector = {
            "matched": True,
            "intent": "livecopilot_backend_status",
            "answer": "O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente.",
            "bullets": [
                "ws_enabled: True.",
                "capture_mode: mock | capture_live: False.",
            ],
            "knowledge_context": {
                "query": "o backend do livecopilot esta saudavel?",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 2,
                "context": "health/status internos do backend principal do Livecopilot",
                "sources": [
                    {"title": "/health", "source_file": "internal://livecopilot/health"},
                ],
                "connector": "infra_status_connector",
                "target": "livecopilot_backend",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "o backend do livecopilot esta saudavel?",
                    "mode": "generic",
                    "conversation_id": "infra-contract",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["connector"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["target"], "livecopilot_backend")

    def test_api_chat_can_route_to_postgresql_infra_status_connector(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "o postgresql esta de pe?"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_infra_connector = {
            "matched": True,
            "intent": "infra_status",
            "status": "ok",
            "answer": "O PostgreSQL do Livecopilot esta de pe e respondeu ao check read-only.",
            "bullets": [
                "status: ok.",
                "check: SELECT 1 read-only | latency_ms: 18.",
            ],
            "knowledge_context": {
                "query": "o postgresql esta de pe?",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "check read-only de PostgreSQL via DATABASE_URL com SELECT 1 e metadado fixo de runtime",
                "sources": [
                    {"title": "postgres_readonly_check", "source_file": "internal://postgresql/read_only_health"},
                ],
                "connector": "infra_status_connector",
                "target": "postgresql",
                "status": "ok",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "o postgresql esta de pe?",
                    "mode": "generic",
                    "conversation_id": "infra-postgres-contract",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["target"], "postgresql")

    def test_api_chat_can_route_to_server_infra_status_connector(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "como esta o servidor agt01?"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_infra_connector = {
            "matched": True,
            "intent": "infra_status",
            "status": "ok",
            "answer": "O servidor `agt01` esta saudavel no check HTTP read-only controlado.",
            "bullets": [
                "status: ok | host: agt01.",
                "health_ok: True | app_status: ok.",
            ],
            "knowledge_context": {
                "query": "como esta o servidor agt01?",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "check HTTP read-only controlado de host permitido via /health e /status",
                "sources": [
                    {"title": "server_whitelist_http_check", "source_file": "internal://server/whitelist_health_status"},
                ],
                "connector": "infra_status_connector",
                "target": "server",
                "status": "ok",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "como esta o servidor agt01?",
                    "mode": "generic",
                    "conversation_id": "infra-server-contract",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "infra_status_connector")
        self.assertEqual(payload["knowledge_context"]["target"], "server")

    def test_api_chat_applies_response_guidance_for_greeting(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "bom dia"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {"used_search": False, "result_count": 0},
        }

        with patch("app.api.routes.process_ingest", return_value=fake_snapshot):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "bom dia",
                    "mode": "generic",
                    "conversation_id": "guidance-greeting",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "response_guidance")
        self.assertEqual(payload["knowledge_context"]["connector"], "response_guidance")
        self.assertIn("Bom dia.", payload["answer"])

    def test_api_chat_applies_response_guidance_for_unmapped_target(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "como esta o servidor llm?"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {"used_search": False, "result_count": 0},
        }
        fake_infra_connector = {
            "matched": True,
            "intent": "infra_status",
            "status": "warn",
            "answer": "O alvo de servidor `llm` nao esta mapeado neste conector; o host local disponivel e `agt01`.",
            "bullets": ["status: warn | host: agt01."],
            "knowledge_context": {
                "query": "como esta o servidor llm?",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 1,
                "context": "server unmapped",
                "sources": [{"title": "server", "source_file": "internal://server"}],
                "connector": "infra_status_connector",
                "target": "server",
                "requested_target": "llm",
                "checked_host": "agt01",
                "reason": "server_target_not_mapped",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
        ):
            response = self.client.post(
                "/api/chat",
                json={
                    "text": "como esta o servidor llm?",
                    "mode": "generic",
                    "conversation_id": "guidance-unmapped-target",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["backend"], "response_guidance")
        self.assertEqual(payload["knowledge_context"]["connector"], "response_guidance")
        self.assertIn("fonte confiavel configurada", payload["answer"])

    def test_api_voice_events_accepts_structured_payload(self) -> None:
        with patch("app.api.routes.record_voice_event", return_value="/tmp/voice-session-rt-123") as record_voice_event:
            response = self.client.post(
                "/api/voice/events",
                json={
                    "event": "transcription_completed",
                    "session_id": "rt-123",
                    "conversation_id": "rt-123",
                    "transcript_excerpt": "qual foi o ultimo status do projeto",
                    "source": "frontend",
                    "transport": "webrtc",
                    "provider_event_type": "conversation.item.input_audio_transcription.completed",
                    "ts": "2026-03-13T20:22:53Z",
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["session_dir"], "/tmp/voice-session-rt-123")
        record_voice_event.assert_called_once()
        self.assertEqual(record_voice_event.call_args.args[0], "transcription_completed")
        self.assertEqual(record_voice_event.call_args.kwargs["session_id"], "rt-123")

    def test_realtime_respond_records_voice_observability_events(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "o backend do livecopilot esta saudavel?"}],
            "suggestions": ["fallback local"],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_infra_connector = {
            "matched": True,
            "intent": "livecopilot_backend_status",
            "answer": "O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente.",
            "bullets": [
                "ws_enabled: True.",
                "capture_mode: mock | capture_live: False.",
            ],
            "knowledge_context": {
                "query": "o backend do livecopilot esta saudavel?",
                "used_search": False,
                "search_backend": "infra_status_connector",
                "context_used": False,
                "fallback_used": False,
                "semantic_api_ok": False,
                "semantic_duration_ms": 0,
                "result_count": 2,
                "context": "health/status internos do backend principal do Livecopilot",
                "sources": [
                    {"title": "/health", "source_file": "internal://livecopilot/health"},
                ],
                "connector": "infra_status_connector",
                "target": "livecopilot_backend",
            },
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.resolve_infra_status_query", return_value=fake_infra_connector),
            patch("app.api.routes.record_voice_event") as record_voice_event,
        ):
            response = self.client.post(
                "/realtime/respond",
                json={
                    "text": "o backend do livecopilot esta saudavel?",
                    "mode": "generic",
                    "conversation_id": "voice-observability",
                    "voice_output_enabled": False,
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], "infra_status_connector")
        self.assertEqual(record_voice_event.call_args_list[0].args[0], "voice_backend_request_received")
        self.assertEqual(record_voice_event.call_args_list[-1].args[0], "voice_backend_response_completed")

    def test_realtime_respond_returns_voice_output_payload_when_enabled(self) -> None:
        fake_snapshot = {
            "transcript": [{"speaker": "user", "text": "responda com audio"}],
            "suggestions": ["Resposta final em texto."],
            "quick_replies": [],
            "fillers": [],
            "term_hints": [],
            "knowledge_context": {},
        }
        fake_voice_output = {
            "voice_status": "ready",
            "voice_provider": "external",
            "voice_enabled_effective": True,
            "fallback_reason": "",
            "audio_output_available": True,
            "audio_bytes": 1234,
            "audio_base64": "ZmFrZQ==",
            "mime_type": "audio/mpeg",
            "model": "gpt-4o-mini-tts",
        }

        with (
            patch("app.api.routes.process_ingest", return_value=fake_snapshot),
            patch("app.api.routes.synthesize_voice_output_realtime_controlled", return_value=fake_voice_output) as synthesize_voice_output,
        ):
            response = self.client.post(
                "/realtime/respond",
                json={
                    "text": "responda com audio",
                    "mode": "generic",
                    "conversation_id": "voice-output-contract",
                    "voice_output_enabled": True,
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["voice_output"]["voice_status"], "ready")
        self.assertEqual(payload["voice_output"]["audio_base64"], "ZmFrZQ==")
        self.assertEqual(payload["voice_output"]["mime_type"], "audio/mpeg")
        synthesize_voice_output.assert_called_once()
        self.assertTrue(synthesize_voice_output.call_args.kwargs["enabled_override"])


if __name__ == "__main__":
    unittest.main()
