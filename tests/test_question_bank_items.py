import unittest
from pathlib import Path

from app.services.question_bank_items import extract_question_items
from app.services.question_bank_parsers import QUESTION_BANK_RAW_DIR, list_question_bank_raw_files


class QuestionBankItemsTests(unittest.TestCase):
    def test_markdown_contents_generates_multiple_exercise_items(self) -> None:
        payload = extract_question_items(
            {
                "source_file": "CKA_Exercises_Practice.md",
                "title": "CKA Exercises Practice",
                "content": "\n".join(
                    [
                        "# CKAD Exercises",
                        "",
                        "Hands-on Kubernetes exercises for CKA/CKAD preparation.",
                        "Practice with kubectl, pods, services and namespaces.",
                        "",
                        "## Contents",
                        "",
                        "- [Core Concepts - 13%](a.core_concepts.md)",
                        "- [Pod design - 20%](c.pod_design.md)",
                        "- [Services and networking - 13%](f.services.md)",
                    ]
                ),
            }
        )

        self.assertEqual(payload["item_count"], 3)
        self.assertEqual(
            [item["title"] for item in payload["items"]],
            ["Core Concepts - 13%", "Pod design - 20%", "Services and networking - 13%"],
        )
        self.assertTrue(all(item["item_type"] == "exercise" for item in payload["items"]))
        self.assertTrue(all(item["inferred_domain"] == "devops" for item in payload["items"]))
        self.assertTrue(all("kubernetes" in item["inferred_tags"] for item in payload["items"]))
        self.assertTrue(all("python" not in item["inferred_tags"] for item in payload["items"]))

    def test_markdown_without_structure_keeps_single_fallback_item(self) -> None:
        payload = extract_question_items(
            {
                "source_file": "generic_notes.md",
                "title": "Generic Notes",
                "content": "This set of exercises reviews broad study concepts without sections or explicit tasks.",
            }
        )

        self.assertEqual(payload["item_count"], 1)
        self.assertEqual(payload["items"][0]["item_type"], "unknown")
        self.assertEqual(payload["items"][0]["question_id"], "generic_notes-001")

    def test_markdown_lab_sections_generate_multiple_exercise_items(self) -> None:
        payload = extract_question_items(
            {
                "source_file": "ckad_exercises/a.core_concepts.md",
                "title": "a.core concepts",
                "content": "\n".join(
                    [
                        "# Core Concepts (13%)",
                        "",
                        "## Namespaces",
                        "",
                        "### Create a namespace called 'mynamespace' and a pod with image nginx called nginx on this namespace",
                        "",
                        "Use kubectl create namespace and kubectl run to create the namespace and pod.",
                        "",
                        "### Create the pod that was just described using YAML",
                        "",
                        "Generate YAML with dry-run and create it with kubectl apply.",
                        "",
                        "## Networking",
                        "",
                        "### Get nginx pod's ip created in previous step, use a temp busybox image to wget its '/'",
                        "",
                        "Inspect pod IPs and call the endpoint from a busybox pod for verification.",
                    ]
                ),
            }
        )

        self.assertEqual(payload["item_count"], 3)
        self.assertTrue(all(item["item_type"] == "exercise" for item in payload["items"]))
        self.assertTrue(all(item["inferred_domain"] == "devops" for item in payload["items"]))
        self.assertTrue(all("kubernetes" in item["inferred_tags"] for item in payload["items"]))
        self.assertEqual(
            [item["title"] for item in payload["items"]],
            [
                "Namespaces - Create a namespace called 'mynamespace' and a pod with image nginx called nginx on this namespace",
                "Namespaces - Create the pod that was just described using YAML",
                "Networking - Get nginx pod's ip created in previous step, use a temp busybox image to wget its '/'",
            ],
        )

    def test_dense_markdown_lab_sections_compact_short_siblings(self) -> None:
        sections: list[str] = ["# Dense Lab", "", "## Pod Design", ""]
        for index in range(1, 41):
            sections.extend(
                [
                    f"### Short exercise number {index} for pods",
                    "",
                    f"Run pod task {index} with kubectl and verify the result.",
                    "",
                ]
            )

        payload = extract_question_items(
            {
                "source_file": "ckad_exercises/dense_lab.md",
                "title": "Dense Lab",
                "content": "\n".join(sections),
            }
        )

        self.assertEqual(payload["item_count"], 20)
        self.assertTrue(all(item["item_type"] == "exercise" for item in payload["items"]))
        self.assertTrue(all(item["inferred_domain"] == "devops" for item in payload["items"]))
        self.assertTrue(all("kubernetes" in item["inferred_tags"] for item in payload["items"]))
        self.assertTrue(all(" / " in item["title"] for item in payload["items"]))

    def test_sparse_long_heading_splits_into_multiple_exercises(self) -> None:
        payload = extract_question_items(
            {
                "source_file": "ckad_exercises/b.multi_container_pods.md",
                "title": "Multi-container Pods",
                "content": "\n".join(
                    [
                        "# Multi-container Pods (10%)",
                        "",
                        "### Create a pod with an nginx container exposed on port 80. Add a busybox init container which downloads a page. Make a volume of type emptyDir and mount it in both containers. When done, get the IP of the created pod and run wget from a busybox pod.",
                        "",
                        "Use kubectl to create the pod YAML, configure the init container and verify the endpoint from a second pod.",
                        "Copy the generated manifest, add the initContainer, mount the shared volume, apply the pod, get the pod IP and validate the response from another busybox pod.",
                        "Keep the exercise as a single long section so the markdown fallback needs to split the heading instead of relying on extra headings.",
                        "",
                        "```bash",
                        "kubectl run box --image=nginx --restart=Never --port=80 --dry-run=client -o yaml > pod-init.yaml",
                        "kubectl get po -o wide",
                        "kubectl run box-test --image=busybox --restart=Never -it --rm -- /bin/sh -c \"wget -O- $(kubectl get pod box -o jsonpath='{.status.podIP}')\"",
                        "```",
                        "",
                        "### Create another pod with two containers and inspect the second container",
                        "",
                        "Use kubectl exec to inspect the second container after the pod starts.",
                    ]
                ),
            }
        )

        self.assertEqual(payload["item_count"], 4)
        self.assertTrue(all(item["item_type"] == "exercise" for item in payload["items"]))
        self.assertTrue(all(item["inferred_domain"] == "devops" for item in payload["items"]))
        self.assertTrue(all("kubernetes" in item["inferred_tags"] for item in payload["items"]))
        self.assertEqual(
            [item["title"] for item in payload["items"][:3]],
            [
                "Create a pod with an nginx container exposed on port 80",
                "Add a busybox init container which downloads a page Make a volume of type emptyDir and mount it in both containers",
                "When done, get the IP of the created pod and run wget from a busybox pod",
            ],
        )

    def test_list_question_bank_raw_files_ignores_operational_backups(self) -> None:
        test_dir = QUESTION_BANK_RAW_DIR / "tmp_test_ignore_backups"
        valid_path = test_dir / "valid_lab.md"
        backup_path = test_dir / "valid_lab.md.pre-ckad-modules-20260302T174755Z.backup.md"

        test_dir.mkdir(parents=True, exist_ok=True)
        valid_path.write_text("# valid\n", encoding="utf-8")
        backup_path.write_text("# backup\n", encoding="utf-8")
        try:
            discovered = {path.relative_to(QUESTION_BANK_RAW_DIR).as_posix() for path in list_question_bank_raw_files()}
            self.assertIn("tmp_test_ignore_backups/valid_lab.md", discovered)
            self.assertNotIn("tmp_test_ignore_backups/valid_lab.md.pre-ckad-modules-20260302T174755Z.backup.md", discovered)
        finally:
            for path in (valid_path, backup_path):
                if path.exists():
                    path.unlink()
            if test_dir.exists():
                test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
