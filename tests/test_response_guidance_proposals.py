import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.response_guidance import (
    approve_response_guidance_proposal,
    get_response_guidance_rule,
    load_response_guidance,
    list_response_guidance_proposals,
    main,
    propose_response_guidance_rule,
    reject_response_guidance_proposal,
)


class ResponseGuidanceProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.guidance_path = self.base_path / "response_guidance.json"
        self.proposals_dir = self.base_path / "response_guidance_proposals"
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
        self.proposals_patch = patch("app.services.response_guidance.RESPONSE_GUIDANCE_PROPOSALS_DIR", self.proposals_dir)
        self.guidance_patch.start()
        self.proposals_patch.start()

    def tearDown(self) -> None:
        self.proposals_patch.stop()
        self.guidance_patch.stop()
        self.temp_dir.cleanup()

    def test_create_proposal(self) -> None:
        proposal = propose_response_guidance_rule(
            proposal_id="proposal_greeting_e_ai",
            rule_id="greeting_e_ai",
            scope="livecopilot_reply",
            trigger_type="normalized_text",
            match_examples=["e ai"],
            answer="E ai. Pode mandar a pergunta.",
            bullets=["Se quiser, eu respondo em texto curto."],
            policy_notes="Saudacao curta.",
            priority=90,
        )

        self.assertEqual(proposal["status"], "pending")
        self.assertTrue((self.proposals_dir / "proposal_greeting_e_ai.json").exists())
        self.assertIsNone(get_response_guidance_rule("greeting_e_ai"))

    def test_approve_proposal_moves_rule_to_main_json(self) -> None:
        proposal = propose_response_guidance_rule(
            proposal_id="proposal_identity_operador",
            rule_id="identity_operador",
            scope="livecopilot_reply",
            trigger_type="normalized_text",
            match_examples=["quem opera voce?"],
            answer="O Livecopilot roda pelo backend unificado.",
            bullets=["A fonte canonica continua em response_guidance.json."],
            policy_notes="Resposta curta.",
            priority=90,
        )

        approved = approve_response_guidance_proposal(proposal["proposal_id"])
        saved = load_response_guidance()
        rule = get_response_guidance_rule("identity_operador")

        self.assertEqual(approved["status"], "approved")
        self.assertEqual(saved["version"], 1)
        self.assertEqual(len(saved["rules"]), 2)
        self.assertEqual(rule["created_at"], proposal["proposed_rule"]["created_at"])
        self.assertEqual(rule["updated_at"], approved["proposed_rule"]["updated_at"])
        self.assertTrue(any(self.base_path.glob("response_guidance.json.bak.*")))

    def test_reject_proposal_preserves_main_json_integrity(self) -> None:
        propose_response_guidance_rule(
            proposal_id="proposal_reject_greeting",
            rule_id="greeting_e_ai",
            scope="livecopilot_reply",
            trigger_type="normalized_text",
            match_examples=["e ai"],
            answer="E ai. Pode mandar a pergunta.",
        )

        rejected = reject_response_guidance_proposal("proposal_reject_greeting")
        saved = load_response_guidance()

        self.assertEqual(rejected["status"], "rejected")
        self.assertEqual(saved["version"], 1)
        self.assertEqual(len(saved["rules"]), 1)
        self.assertIsNone(get_response_guidance_rule("greeting_e_ai"))

    def test_reject_duplicate_rule_id_pending_proposal(self) -> None:
        propose_response_guidance_rule(
            proposal_id="proposal_one",
            rule_id="greeting_e_ai",
            scope="livecopilot_reply",
            trigger_type="normalized_text",
            match_examples=["e ai"],
            answer="E ai. Pode mandar a pergunta.",
        )

        with self.assertRaises(ValueError):
            propose_response_guidance_rule(
                proposal_id="proposal_two",
                rule_id="greeting_e_ai",
                scope="livecopilot_reply",
                trigger_type="normalized_text",
                match_examples=["fala ai"],
                answer="Fala ai.",
            )

    def test_cli_proposal_workflow(self) -> None:
        rc = main(
            [
                "propose",
                "--proposal-id",
                "proposal_cli_identity",
                "--id",
                "identity_cli",
                "--scope",
                "livecopilot_reply",
                "--trigger-type",
                "normalized_text",
                "--match-examples",
                '["quem esta no cli?"]',
                "--answer",
                "O CLI montou a proposal.",
            ]
        )
        self.assertEqual(rc, 0)

        rc = main(["list-proposals"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(list_response_guidance_proposals()), 1)

        rc = main(["show-proposal", "--proposal-id", "proposal_cli_identity"])
        self.assertEqual(rc, 0)

        rc = main(["approve", "--proposal-id", "proposal_cli_identity"])
        self.assertEqual(rc, 0)
        self.assertIsNotNone(get_response_guidance_rule("identity_cli"))


if __name__ == "__main__":
    unittest.main()
