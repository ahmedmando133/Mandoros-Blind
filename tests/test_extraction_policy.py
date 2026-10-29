from __future__ import annotations

import unittest
from pathlib import Path

from app.extraction_policy import apply_policy, evaluate_dataset, load_policy_bundle


ROOT = Path(__file__).resolve().parents[1]


class AutomaticExtractionPolicyTests(unittest.TestCase):
    def test_policy_bundle_is_complete_and_automatic(self) -> None:
        bundle = load_policy_bundle(ROOT)
        self.assertTrue(bundle["automatic_application"])
        self.assertEqual("mandros-blind-optimal-rct-extraction-v1", bundle["policy_id"])
        self.assertEqual("1.1.0", bundle["prompt_version"])
        self.assertEqual("1.0.0", bundle["statistics_version"])
        for item in bundle["files"].values():
            self.assertEqual(64, len(item["sha256"]))

    def test_policy_detects_known_statistical_representation_failures(self) -> None:
        dataset = {
            "arms": [{"arm_id": "ARM_A"}],
            "baseline": [],
            "outcomes": [{
                "id": "OUT_1", "arm_id": "ARM_A", "estimate_type": "median",
                "lower_value": 1, "upper_value": 3, "ci_lower": 1, "ci_upper": 3,
                "event_count": 4, "event_count_unit": "%", "source_status": "published_main_article_exact",
                "source_page": None,
            }],
            "statistical_tests": [{"test_id": "T1", "p_value": "<0.05"}],
        }
        codes = {issue["code"] for issue in evaluate_dataset(dataset)}
        self.assertIn("POLICY_IQR_DUPLICATED_AS_CI", codes)
        self.assertIn("POLICY_EVENT_COUNT_PERCENT_UNIT", codes)
        self.assertIn("POLICY_EXACT_WITHOUT_PAGE", codes)
        self.assertIn("POLICY_NONATOMIC_P_VALUE", codes)

    def test_applying_policy_never_replaces_scientific_values(self) -> None:
        dataset = {
            "arms": [{"arm_id": "ARM_A"}], "baseline": [],
            "outcomes": [{
                "id": "OUT_1", "arm_id": "ARM_A", "value": 12.5,
                "source_status": "requires_manual_review", "source_page": None,
            }],
            "statistical_tests": [], "validation_log": [],
        }
        apply_policy(dataset, ROOT)
        self.assertEqual(12.5, dataset["outcomes"][0]["value"])
        self.assertTrue(dataset["system_extraction_policy"]["automatic_application"])
        self.assertEqual("SYSTEM_EXTRACTION_SKILL", dataset["validation_log"][-1]["code"])


if __name__ == "__main__":
    unittest.main()
