import unittest

from app.services.source_prefix_resolution import (
    matches_source_prefix,
    normalize_source_prefix,
    normalize_source_prefixes,
    resolve_source_files_from_prefixes,
    validate_source_prefix,
)


class SourcePrefixResolutionNormalizationTests(unittest.TestCase):
    def test_normalize_simple_prefix(self) -> None:
        self.assertEqual(normalize_source_prefix("abc/def"), "abc/def")

    def test_normalize_removes_leading_dot_slash(self) -> None:
        self.assertEqual(normalize_source_prefix("./abc/def"), "abc/def")

    def test_normalize_removes_trailing_slash(self) -> None:
        self.assertEqual(normalize_source_prefix("abc/def/"), "abc/def")

    def test_normalize_empty_after_cleanup(self) -> None:
        self.assertEqual(normalize_source_prefix("./"), "")

    def test_normalize_keeps_redundant_inner_separators(self) -> None:
        self.assertEqual(normalize_source_prefix("abc//def///"), "abc//def")


class SourcePrefixResolutionValidationTests(unittest.TestCase):
    def test_validate_valid_prefix(self) -> None:
        self.assertEqual(validate_source_prefix("./abc/def/"), "abc/def")

    def test_validate_rejects_path_traversal_segment(self) -> None:
        with self.assertRaisesRegex(ValueError, "path traversal"):
            validate_source_prefix("abc/../def")

    def test_validate_rejects_empty_prefix(self) -> None:
        with self.assertRaisesRegex(ValueError, "valor vazio"):
            validate_source_prefix("./")

    def test_normalize_source_prefixes_deduplicates_preserving_order(self) -> None:
        self.assertEqual(
            normalize_source_prefixes(["./abc/", "abc", "xyz", "xyz/"]),
            ["abc", "xyz"],
        )


class SourcePrefixResolutionMatchingTests(unittest.TestCase):
    def test_matching_prefix_matches_child_file(self) -> None:
        self.assertTrue(matches_source_prefix("abc/foo.md", ["abc"]))

    def test_matching_prefix_does_not_match_partial_segment(self) -> None:
        self.assertFalse(matches_source_prefix("abcd/foo.md", ["abc"]))

    def test_matching_with_multiple_prefixes(self) -> None:
        self.assertTrue(matches_source_prefix("infra/terraform/main.tf", ["docs", "infra"]))

    def test_matching_with_nested_prefix(self) -> None:
        self.assertTrue(matches_source_prefix("abc/def/file.md", ["abc/def"]))


class SourcePrefixResolutionResolveTests(unittest.TestCase):
    def test_resolve_with_single_valid_prefix(self) -> None:
        state = {
            "files": {
                "abc/a.md": {},
                "abc/b.md": {},
                "xyz/c.md": {},
            }
        }
        resolved, counts = resolve_source_files_from_prefixes(state, ["abc"])
        self.assertEqual(resolved, ["abc/a.md", "abc/b.md"])
        self.assertEqual(counts, {"abc": 2})

    def test_resolve_with_multiple_prefixes_and_metrics(self) -> None:
        state = {
            "files": {
                "abc/a.md": {},
                "abc/sub/b.md": {},
                "infra/main.tf": {},
                "zzz/x.md": {},
            }
        }
        resolved, counts = resolve_source_files_from_prefixes(state, ["abc", "infra"])
        self.assertEqual(resolved, ["abc/a.md", "abc/sub/b.md", "infra/main.tf"])
        self.assertEqual(counts, {"abc": 2, "infra": 1})

    def test_resolve_missing_prefix_non_strict_returns_empty_selection(self) -> None:
        state = {"files": {"abc/a.md": {}, "xyz/c.md": {}}}
        resolved, counts = resolve_source_files_from_prefixes(state, ["missing"])
        self.assertEqual(resolved, [])
        self.assertEqual(counts, {"missing": 0})

    def test_resolve_missing_prefix_strict_contract_can_be_enforced_by_caller(self) -> None:
        state = {"files": {"abc/a.md": {}}}
        resolved, counts = resolve_source_files_from_prefixes(state, ["missing"])
        self.assertEqual(counts, {"missing": 0})
        with self.assertRaises(ValueError):
            if not resolved:
                raise ValueError("strict-source-prefix habilitado e nenhum source_file resolvido")

    def test_resolve_handles_non_dict_state_files(self) -> None:
        resolved, counts = resolve_source_files_from_prefixes({"files": []}, ["abc", "xyz"])
        self.assertEqual(resolved, [])
        self.assertEqual(counts, {"abc": 0, "xyz": 0})


if __name__ == "__main__":
    unittest.main()
