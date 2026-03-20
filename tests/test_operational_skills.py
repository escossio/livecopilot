import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.operational_skills import (
    get_skill_by_id,
    load_operational_skills,
    match_operational_skill,
    validate_operational_skills_payload,
)


class OperationalSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.skills_path = Path(self.temp_dir.name) / "operational_skills.json"
        self.skills_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "skills": [
                        {
                            "id": "postgresql_health_check",
                            "active": True,
                            "intent": "infra_status",
                            "trigger_examples": ["como esta meu PostgreSQL?", "o banco esta saudavel?"],
                            "target": "postgresql",
                            "source": "infra_status_connector",
                            "action": {"type": "connector_call", "operation": "postgresql_health_check"},
                            "response_policy": {
                                "summary_template": "Responder com o estado atual do PostgreSQL em check read-only controlado.",
                                "detail_template": "Incluir status e latencia do check fixo.",
                            },
                            "safety": {"mode": "read_only", "approval_required": False},
                            "notes": "skill de teste",
                        },
                        {
                            "id": "project_latest_status",
                            "active": False,
                            "intent": "latest_checkpoint",
                            "trigger_examples": ["qual foi o ultimo status do projeto?"],
                            "target": "project_state",
                            "source": "project_state_connector",
                            "action": {"type": "connector_call", "operation": "project_latest_status"},
                            "response_policy": {
                                "summary_template": "Responder com o checkpoint mais recente.",
                                "detail_template": "Incluir checkpoint atual e fonte local.",
                            },
                            "safety": {"mode": "read_only", "approval_required": False},
                            "notes": "skill inativa para teste",
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.skills_patch = patch("app.services.operational_skills.OPERATIONAL_SKILLS_FILE", self.skills_path)
        self.skills_patch.start()

    def tearDown(self) -> None:
        self.skills_patch.stop()
        self.temp_dir.cleanup()

    def test_load_operational_skills(self) -> None:
        payload = load_operational_skills()

        self.assertEqual(payload["version"], 1)
        self.assertEqual(len(payload["skills"]), 2)

    def test_validate_structure_rejects_duplicate_id(self) -> None:
        with self.assertRaises(ValueError):
            validate_operational_skills_payload(
                {
                    "version": 1,
                    "skills": [
                        {
                            "id": "dup",
                            "active": True,
                            "intent": "infra_status",
                            "trigger_examples": ["a"],
                            "target": "postgresql",
                            "source": "infra_status_connector",
                            "action": {"type": "connector_call", "operation": "postgresql_health_check"},
                            "response_policy": {"summary_template": "a", "detail_template": "b"},
                            "safety": {"mode": "read_only", "approval_required": False},
                            "notes": "",
                        },
                        {
                            "id": "dup",
                            "active": True,
                            "intent": "infra_status",
                            "trigger_examples": ["b"],
                            "target": "server",
                            "source": "infra_status_connector",
                            "action": {"type": "connector_call", "operation": "server_local_health_check"},
                            "response_policy": {"summary_template": "a", "detail_template": "b"},
                            "safety": {"mode": "read_only", "approval_required": False},
                            "notes": "",
                        },
                    ],
                }
            )

    def test_match_operational_skill_by_trigger_example(self) -> None:
        payload = match_operational_skill("como esta meu postgresql?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["skill"]["id"], "postgresql_health_check")
        self.assertEqual(payload["target"], "postgresql")

    def test_match_ignores_inactive_skill(self) -> None:
        payload = match_operational_skill("qual foi o ultimo status do projeto?")

        self.assertFalse(payload["matched"])

    def test_get_skill_by_id_returns_none_for_missing_skill(self) -> None:
        payload = get_skill_by_id("skill_que_nao_existe")

        self.assertIsNone(payload)

    def test_match_mikrotik_variation_when_source_is_connector(self) -> None:
        self.skills_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "skills": [
                        {
                            "id": "mikrotik_dhcp_clients_count",
                            "active": True,
                            "intent": "network_device_count",
                            "trigger_examples": ["quem esta conectado na minha rede?"],
                            "target": "mikrotik",
                            "source": "mikrotik",
                            "action": {"type": "router_read_only", "operation": "list_dhcp_leases"},
                            "response_policy": {
                                "summary_template": "Consultar clientes DHCP no MikroTik.",
                                "detail_template": "Usar conector REST API read-only do DHCP.",
                            },
                            "safety": {"mode": "read_only", "approval_required": False},
                            "notes": "skill de teste mikrotik",
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        payload = match_operational_skill("quem esta conectado na minha rede?")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["skill"]["id"], "mikrotik_dhcp_clients_count")
        self.assertEqual(payload["source"], "mikrotik")
        self.assertEqual(payload["action"]["type"], "router_read_only")
        self.assertEqual(payload["action"]["operation"], "list_dhcp_leases")

    def test_match_operational_skill_ignores_terminal_punctuation(self) -> None:
        payload = match_operational_skill("como esta meu postgresql")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["skill"]["id"], "postgresql_health_check")


if __name__ == "__main__":
    unittest.main()
