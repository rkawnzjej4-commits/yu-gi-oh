"""Synthetic records only: these are not verified Yu-Gi-Oh! cards or evidence."""

import copy
import unittest

from tools.audit_catalog import audit


def fixture():
    return {
        "schema_version": 1,
        "cutoff": "2012-03-31",
        "snapshot": {
            "id": "synthetic-test-only",
            "rules_verified_at": "2026-11-02",
            "rules_source_url": "https://example.invalid/rules",
            "engine_sha256": "a" * 64,
            "scripts_sha256": "b" * 64,
            "card_data_sha256": "c" * 64,
        },
        "cards": [{
            "card_id": "synthetic-not-a-card",
            "name_ja": "テスト専用",
            "eligibility": {
                "status": "verified", "territory": "JP-OCG",
                "first_release_date": "2012-03-31",
                "evidence_url": "https://example.invalid/release",
                "verified_at": "2026-11-02",
            },
            "text": {
                "status": "verified", "source_url": "https://example.invalid/text",
                "verified_at": "2026-11-02", "sha256": "d" * 64,
            },
            "implementation": {
                "status": "verified", "snapshot_id": "synthetic-test-only",
                "text_sha256": "d" * 64,
                "tests": [{"id": "synthetic-effect", "result": "passed"}],
            },
        }],
    }


class CatalogTests(unittest.TestCase):
    def test_cutoff_is_inclusive(self):
        self.assertEqual(audit(fixture())["supported_count"], 1)

    def test_april_first_is_excluded_even_with_verified_script(self):
        catalog = fixture()
        catalog["cards"][0]["eligibility"]["first_release_date"] = "2012-04-01"
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_tcg_date_is_insufficient(self):
        catalog = fixture()
        catalog["cards"][0]["eligibility"]["territory"] = "TCG"
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_eligible_but_unimplemented_is_blocked(self):
        catalog = fixture()
        catalog["cards"][0]["implementation"]["status"] = "unimplemented"
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_unverified_release_is_blocked(self):
        catalog = fixture()
        catalog["cards"][0]["eligibility"]["status"] = "pending"
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_updated_text_invalidates_effect_approval(self):
        catalog = fixture()
        catalog["cards"][0]["text"]["sha256"] = "e" * 64
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_new_snapshot_invalidates_approval(self):
        catalog = fixture()
        catalog["snapshot"]["id"] = "new-bundle"
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_skipped_failed_and_zero_tests_do_not_pass(self):
        for tests in ([], [{"id": "case", "result": "skipped"}],
                      [{"id": "case", "result": "failed"}]):
            with self.subTest(tests=tests):
                catalog = fixture()
                catalog["cards"][0]["implementation"]["tests"] = tests
                self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_missing_official_verification_blocks_all_cards(self):
        catalog = fixture()
        catalog["snapshot"]["rules_verified_at"] = None
        self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_late_reprint_does_not_change_first_release(self):
        catalog = fixture()
        catalog["cards"][0]["eligibility"]["reprint_date"] = "2025-01-01"
        self.assertEqual(audit(catalog)["supported_count"], 1)

    def test_duplicate_identity_is_an_error(self):
        catalog = fixture()
        catalog["cards"].append(copy.deepcopy(catalog["cards"][0]))
        with self.assertRaises(ValueError):
            audit(catalog)

    def test_invalid_dates_and_missing_evidence_block(self):
        for field, value in (("first_release_date", "2012-02-30"),
                             ("first_release_date", None), ("evidence_url", None)):
            with self.subTest(field=field, value=value):
                catalog = fixture()
                catalog["cards"][0]["eligibility"][field] = value
                self.assertEqual(audit(catalog)["supported_count"], 0)

    def test_empty_catalog_does_not_validate_cards(self):
        result = audit({"schema_version": 1, "cutoff": "2012-03-31",
                        "snapshot": None, "cards": []})
        self.assertEqual(result["supported_count"], 0)
        self.assertTrue(result["snapshot_issues"])

    def test_malformed_sections_are_errors(self):
        catalog = fixture()
        catalog["cards"][0]["implementation"] = []
        with self.assertRaises(ValueError):
            audit(catalog)


if __name__ == "__main__":
    unittest.main()
