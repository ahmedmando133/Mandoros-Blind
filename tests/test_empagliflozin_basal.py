from __future__ import annotations

import json
import unittest
from pathlib import Path

from app.extraction_policy import evaluate_dataset
from app.source_completeness import validate_source_inventory
from app.validator import validate_workbook


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "standards" / "empagliflozin_basal_workbook_dataset.json"
SOURCE_DIR = ROOT / "data" / "private" / "empagliflozin 2"


class EmpagliflozinBasalRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    def test_primary_endpoint_tuple_is_exact(self) -> None:
        by_id = {row["id"]: row for row in self.dataset["outcomes"]}
        expected = {
            "HBA1C18_PCT_CHANGE_ARM_001": (0.0, .1, 125),
            "HBA1C18_PCT_CHANGE_ARM_002": (-.6, .1, 132),
            "HBA1C18_PCT_CHANGE_ARM_003": (-.7, .1, 117),
        }
        for identifier, (value, se, n) in expected.items():
            row = by_id[identifier]
            self.assertEqual(18, row["timepoint"])
            self.assertEqual("weeks", row["time_unit"])
            self.assertEqual("%", row["unit"])
            self.assertEqual("ADJUSTED_MEAN_CHANGE", row["measure"])
            self.assertEqual("SE", row["dispersion"])
            self.assertEqual(value, row["value"])
            self.assertEqual(se, row["dispersion_value"])
            self.assertEqual(n, row["n_analyzed"])

    def test_units_sample_scope_and_week78_insulin_are_preserved(self) -> None:
        baseline = {row["id"]: row for row in self.dataset["baseline"]}
        outcomes = {row["id"]: row for row in self.dataset["outcomes"]}
        self.assertEqual("mmol/L", baseline["BASE_FPG_ARM_001"]["unit"])
        self.assertEqual((112, 127, 110), tuple(outcomes[f"HBA1C78_PCT_CHANGE_{arm}"]["n_analyzed"] for arm in ("ARM_001", "ARM_002", "ARM_003")))
        self.assertEqual((5.5, -1.2, -.5), tuple(outcomes[f"INSULIN78_CHANGE_{arm}"]["value"] for arm in ("ARM_001", "ARM_002", "ARM_003")))

    def test_responder_percentages_and_egfr_sd_are_separate_source_findings(self) -> None:
        outcomes = {row["id"]: row for row in self.dataset["outcomes"]}
        expected_responder_percentages = {
            "RESP18_ARM_001": (5.5, 18),
            "RESP18_ARM_002": (18.0, 18),
            "RESP18_ARM_003": (19.5, 18),
            "RESP78_ARM_001": (6.7, 78),
            "RESP78_ARM_003": (17.5, 78),
        }
        for record_id, (value, week) in expected_responder_percentages.items():
            row = outcomes[record_id]
            self.assertEqual("HbA1c responder", row["outcome"])
            self.assertEqual("sample_proportion", row["estimate_type"])
            self.assertEqual(value, row["value"])
            self.assertEqual("%", row["unit"])
            self.assertEqual(week, row["timepoint"])
            self.assertTrue(row["threshold_lt"])
            self.assertFalse(row["threshold_eq"])
            self.assertFalse(row["threshold_gt"])
            self.assertEqual(7.0, row["threshold_value"])

        expected_egfr = {
            "SAFE_EGFR_ARM_001": (-6.3, 13.0, 120),
            "SAFE_EGFR_ARM_002": (-4.8, 12.1, 127),
            "SAFE_EGFR_ARM_003": (-5.7, 13.4, 117),
        }
        for record_id, (mean_change, sd, analyzed_n) in expected_egfr.items():
            row = outcomes[record_id]
            self.assertEqual(mean_change, row["value"])
            self.assertEqual("SD", row["dispersion"])
            self.assertEqual(sd, row["dispersion_value"])
            self.assertEqual(analyzed_n, row["n_analyzed"])
            self.assertEqual("mL/min/1.73m2", row["unit"])

    def test_all_table2_categories_are_present_once_per_arm(self) -> None:
        rows = [row for row in self.dataset["outcomes"] if row["id"].startswith("SAFE_T2_")]
        self.assertEqual(41 * 3, len(rows))
        self.assertEqual(len(rows), len({row["id"] for row in rows}))
        self.assertTrue(all(row["event_count"] is not None for row in rows))

    def test_sex_specific_safety_denominators_do_not_use_total_arm_n(self) -> None:
        rows = [
            row for row in self.dataset["outcomes"]
            if row["id"].startswith("SAFE_T2_") and row.get("subgroup_type") == "sex"
        ]
        self.assertEqual(12, len(rows))
        for row in rows:
            self.assertIsNone(row["n_analyzed"])
            self.assertIsNone(row["denominator"])
            self.assertIsNone(row["event_denominator"])
            self.assertEqual("sex_specific_subgroup_not_reported", row["denominator_type"])
            self.assertEqual("REQUIRES_REVIEW", row["meta_analysis_eligibility"])
            self.assertFalse(row["include_in_meta_analysis"])

    def test_source_inventory_and_policy_pass(self) -> None:
        self.assertEqual([], evaluate_dataset(self.dataset))
        report = validate_source_inventory(self.dataset)
        self.assertTrue(report["inventory_independent_of_excel"])
        self.assertTrue(report["complete_and_verified"])
        self.assertEqual("100% verified", report["claim"])

    def test_original_mandros_workbook_is_rejected_for_known_failures(self) -> None:
        report = validate_workbook(SOURCE_DIR / "empa vs placebo.pdf", SOURCE_DIR / "empa vs placebo_extracted.xlsx")
        self.assertEqual("empagliflozin-basal-dom-2015-v1", report["recognized_fixture"])
        codes = {row["code"] for row in report["issues"]}
        self.assertIn("PRIMARY_ENDPOINT_TIMEPOINT_CONTAMINATION", codes)
        self.assertIn("FPG_UNIT_MISMATCH", codes)
        self.assertIn("RESCUE_RULE_MISCLASSIFIED_AS_AGE", codes)
        self.assertIn("INCOMPLETE_TABLE2_SAFETY", codes)


if __name__ == "__main__":
    unittest.main()
