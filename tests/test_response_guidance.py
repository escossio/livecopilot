import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.response_guidance import (
    add_response_guidance_rule,
    get_response_guidance_rule,
    list_response_guidance_rules,
    load_response_guidance,
    main,
    resolve_response_guidance,
    save_response_guidance,
    set_response_guidance_rule_active,
    update_response_guidance_rule,
    validate_response_guidance_payload,
)


class ResponseGuidanceTests(unittest.TestCase):
    def test_guidance_file_loads_with_rules(self) -> None:
        payload = load_response_guidance()

        self.assertEqual(payload["version"], 1)
        self.assertTrue(len(payload["rules"]) >= 8)

    def test_greeting_rule_matches_bom_dia(self) -> None:
        payload = resolve_response_guidance(query="bom dia", semantic_keys=[])

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rule_id"], "greeting_bom_dia")
        self.assertIn("Bom dia.", payload["answer"])

    def test_identity_rule_matches_quem_e_voce(self) -> None:
        payload = resolve_response_guidance(query="quem é você?", semantic_keys=[])

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rule_id"], "identity_livecopilot")
        self.assertIn("Livecopilot", payload["answer"])

    def test_unmapped_target_rule_matches_semantic_key(self) -> None:
        payload = resolve_response_guidance(query="como esta o servidor llm?", semantic_keys=["unmapped_target"])

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rule_id"], "fallback_unmapped_target")
        self.assertIn("fonte confiavel", payload["answer"])

    def test_no_confident_source_rule_matches_semantic_key(self) -> None:
        payload = resolve_response_guidance(query="isso ai", semantic_keys=["no_confident_source"])

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rule_id"], "fallback_no_confident_source")
        self.assertIn("nao sei responder isso com confianca", payload["answer"])


class ResponseGuidanceMaintenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.guidance_path = Path(self.temp_dir.name) / "response_guidance.json"
        self.guidance_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "rules": [
                        {
                            "id": "fallback_unmapped_target",
                            "scope": "livecopilot_reply",
                            "trigger_type": "semantic_key",
                            "match_examples": ["unmapped_target"],
                            "preferred_response": {
                                "answer": "Ainda nao tenho uma fonte confiavel configurada para esse alvo especifico.",
                                "bullets": ["Hoje eu so respondo com seguranca para alvos explicitamente mapeados."],
                            },
                            "policy_notes": "Nao adivinhar alvo nem inventar fonte.",
                            "active": True,
                            "priority": 120,
                            "created_at": "2026-03-14T02:21:34Z",
                            "updated_at": "2026-03-14T02:21:34Z",
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.guidance_patch = patch("app.services.response_guidance.RESPONSE_GUIDANCE_FILE", self.guidance_path)
        self.guidance_patch.start()

    def tearDown(self) -> None:
        self.guidance_patch.stop()
        self.temp_dir.cleanup()

    def test_add_rule_valid(self) -> None:
        rule = add_response_guidance_rule(
            rule_id="greeting_e_ai",
            scope="livecopilot_reply",
            trigger_type="normalized_text",
            match_examples=["e ai"],
            answer="E ai. Pode mandar a pergunta.",
            bullets=["Se quiser, eu respondo em texto curto."],
            policy_notes="Saudacao curta.",
            priority=90,
        )

        self.assertEqual(rule["id"], "greeting_e_ai")
        saved = load_response_guidance()
        self.assertEqual(len(saved["rules"]), 2)

    def test_reject_invalid_rule(self) -> None:
        with self.assertRaises(ValueError):
            save_response_guidance(
                {
                    "version": 1,
                    "rules": [
                        {
                            "id": "broken_rule",
                            "scope": "livecopilot_reply",
                            "trigger_type": "normalized_text",
                            "match_examples": [],
                            "preferred_response": {"answer": "", "bullets": []},
                            "policy_notes": "",
                            "active": True,
                            "priority": 1,
                            "created_at": "2026-03-14T02:21:34Z",
                            "updated_at": "2026-03-14T02:21:34Z",
                        }
                    ],
                }
            )

    def test_prevent_duplicate_id(self) -> None:
        with self.assertRaises(ValueError):
            add_response_guidance_rule(
                rule_id="fallback_unmapped_target",
                scope="livecopilot_reply",
                trigger_type="semantic_key",
                match_examples=["another_key"],
                answer="duplicado",
            )

    def test_disable_rule(self) -> None:
        rule = set_response_guidance_rule_active("fallback_unmapped_target", False)

        self.assertFalse(rule["active"])
        self.assertFalse(get_response_guidance_rule("fallback_unmapped_target")["active"])

    def test_enable_rule(self) -> None:
        set_response_guidance_rule_active("fallback_unmapped_target", False)
        rule = set_response_guidance_rule_active("fallback_unmapped_target", True)

        self.assertTrue(rule["active"])

    def test_update_preferred_response_keeps_integrity(self) -> None:
        before = get_response_guidance_rule("fallback_unmapped_target")
        rule = update_response_guidance_rule(
            rule_id="fallback_unmapped_target",
            answer="Ainda nao tenho esse alvo mapeado com confianca.",
            bullets=["Posso te dizer os alvos disponiveis agora."],
            policy_notes="Fallback revisado.",
        )
        payload = validate_response_guidance_payload(load_response_guidance())

        self.assertEqual(rule["preferred_response"]["answer"], "Ainda nao tenho esse alvo mapeado com confianca.")
        self.assertEqual(payload["version"], 1)
        self.assertEqual(len(payload["rules"]), 1)
        self.assertNotEqual(before["updated_at"], rule["updated_at"])

    def test_cli_add_disable_enable_update_and_list(self) -> None:
        rc = main(
            [
                "add",
                "--id",
                "identity_operador",
                "--scope",
                "livecopilot_reply",
                "--trigger-type",
                "normalized_text",
                "--match-examples",
                '["quem opera voce?"]',
                "--answer",
                "O Livecopilot roda pelo backend unificado.",
                "--bullets",
                '["A fonte canonica continua em response_guidance.json."]',
            ]
        )
        self.assertEqual(rc, 0)

        rc = main(["disable", "--id", "identity_operador"])
        self.assertEqual(rc, 0)
        self.assertFalse(get_response_guidance_rule("identity_operador")["active"])

        rc = main(["enable", "--id", "identity_operador"])
        self.assertEqual(rc, 0)
        self.assertTrue(get_response_guidance_rule("identity_operador")["active"])

        rc = main(
            [
                "update",
                "--id",
                "identity_operador",
                "--answer",
                "O Livecopilot responde pelo backend unificado do projeto.",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertIn("backend unificado", get_response_guidance_rule("identity_operador")["preferred_response"]["answer"])

        rc = main(["list"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(list_response_guidance_rules()), 2)


if __name__ == "__main__":
    unittest.main()
