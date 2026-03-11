import unittest

from app.services.question_bank_action import _build_action_topic
from app.services.question_bank_metadata import infer_question_metadata


class QuestionBankMetadataTests(unittest.TestCase):
    def test_kubernetes_prompt_beats_generic_python_fallback(self) -> None:
        payload = infer_question_metadata(
            source_file="CKA_Exercises_Practice.md",
            title="CKA Exercises Practice",
            prompt=(
                "A set of exercises for the Certified Kubernetes Application Developer exam. "
                "Practice with kubectl, pods, deployments, services, namespaces and cluster troubleshooting."
            ),
            choices=[],
            answer_hint="",
        )

        self.assertIn("kubernetes", payload["tags"]["technology"])
        self.assertIn("devops", payload["tags"]["domain"])
        self.assertNotIn("python", payload["tags"]["technology"])
        self.assertEqual(payload["inferred_domain"], "devops")
        self.assertEqual(payload["metadata_debug"]["matched_rules"], [])

    def test_generic_text_keeps_fallback_without_kubernetes_signal(self) -> None:
        payload = infer_question_metadata(
            source_file="generic.md",
            title="Generic Notes",
            prompt="This set of exercises reviews general study concepts and broad preparation notes.",
            choices=[],
            answer_hint="",
        )

        self.assertIn("python", payload["tags"]["technology"])
        self.assertEqual(payload["inferred_domain"], "backend")

    def test_action_topic_prefers_kubernetes_over_generic_containers(self) -> None:
        topic = _build_action_topic(
            {
                "inferred_tags": ["containers", "devops", "kubernetes"],
                "inferred_domain": "devops",
                "inferred_subtheme": "containers",
                "prompt": "Create a deployment and expose it with a service",
            }
        )

        self.assertEqual(topic, "kubernetes")


if __name__ == "__main__":
    unittest.main()
