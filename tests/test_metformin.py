import json
import unittest
from collections import Counter
from pathlib import Path

from app.config import PRIVATE_DIR, STANDARDS_DIR
from app.metformin_data import expand_adherence_records, load_metformin_bundle
from app.validator import validate_workbook


class MetforminRegressionTest(unittest.TestCase):
    def test_truth_bundle_is_atomic(self):
        bundle = json.loads((STANDARDS_DIR / "metformin_truth_bundle.json").read_text(encoding="utf-8"))
        arm_ids = {arm["arm_id"] for arm in bundle["arms"]}
        self.assertEqual(bundle["study"]["randomized_total_n"], sum(arm["allocated_n"] for arm in bundle["arms"]))
        self.assertTrue(all(row["arm_id"] in arm_ids for row in bundle["outcomes"]))
        self.assertTrue(any(row["domain"] == "safety" for row in bundle["outcomes"]))
        self.assertTrue(any(row.get("threshold_value") == 10 and row.get("threshold_gt") and row.get("threshold_eq") for row in bundle["outcomes"]))

    def test_original_mandros_is_rejected(self):
        report = validate_workbook(PRIVATE_DIR / "metformin" / "source.pdf", PRIVATE_DIR / "metformin" / "mandros_input.xlsx")
        self.assertEqual(report["decision"], "REJECT")
        self.assertEqual(report["score"], 38)
        self.assertGreaterEqual(report["blocking_issue_count"], 20)
        codes = {item["code"] for item in report["issues"]}
        self.assertIn("INVALID_ARM_REFERENCE", codes)
        self.assertIn("MISSING_SAFETY_DOMAIN", codes)
        self.assertIn("PLACEBO_TIMEPOINT_VALUE_MIXUP", codes)

    def test_all_table1_adherence_records_are_preserved(self):
        table = json.loads((STANDARDS_DIR / "metformin_table1_adherence.json").read_text(encoding="utf-8"))
        records = expand_adherence_records(table)
        self.assertEqual(len(records), 119)
        levels = {row["adherence_level"] for row in records if row["adherence_level"] not in (None, "not stratified")}
        self.assertEqual(levels, {"Low adherence", "Below 50% visit adherence", "50 to 90% visit adherence", "Highly adherent"})
        for block in table["distribution_blocks"]:
            for values in block["rows"].values():
                self.assertAlmostEqual(sum(values), 100.0, delta=0.11)
        placebo_9y = [r for r in records if r["id"] == "ADH_GT5_DPP_DPPOS_9Y_COMBINED_ARM_PBO_OVERALL"][0]
        self.assertEqual(placebo_9y["value"], 27.0)
        self.assertEqual(placebo_9y["adherence_level"], "not stratified")
        bundle = load_metformin_bundle()
        self.assertEqual(len(bundle["outcomes"]), 146)
        self.assertEqual(len(bundle["statistical_tests"]), 24)
        self.assertEqual(sum(row["domain"] == "adherence" for row in bundle["outcomes"]), 110)

    def test_proportions_and_p_values_are_normalized(self):
        bundle = load_metformin_bundle()
        self.assertFalse(any(row.get("measure") == "proportion" for row in bundle["outcomes"]))
        self.assertTrue(any(row.get("measure") == "sample_proportion" for row in bundle["outcomes"]))
        self.assertTrue(all(row.get("p_value") is None for row in bundle["outcomes"]))
        self.assertTrue(all(row.get("p_value") is not None or row.get("notes") for row in bundle["statistical_tests"]))
        self.assertEqual(sum(row["test_scope"] == "between_arm_comparison" for row in bundle["statistical_tests"]), 15)
        self.assertEqual(sum(row["test_scope"] == "within_arm_subgroup" for row in bundle["statistical_tests"]), 9)
        met = next(row for row in bundle["outcomes"] if row["id"] == "EFF_WT_Y1_MET")
        pbo = next(row for row in bundle["outcomes"] if row["id"] == "EFF_WT_Y1_PBO")
        self.assertEqual(met["comparison_id"], pbo["comparison_id"])
        linked = next(row for row in bundle["statistical_tests"] if row["comparison_id"] == met["comparison_id"])
        self.assertEqual({linked["arm_a_outcome_id"], linked["arm_b_outcome_id"]}, {met["id"], pbo["id"]})
        outcome_comparisons = Counter(row["comparison_id"] for row in bundle["outcomes"] if row.get("comparison_id"))
        test_comparisons = {row["comparison_id"] for row in bundle["statistical_tests"] if row.get("comparison_id")}
        self.assertEqual(set(outcome_comparisons), test_comparisons)
        self.assertTrue(all(count == 2 for count in outcome_comparisons.values()))

    def test_operators_are_atomic(self):
        bundle = load_metformin_bundle()
        age = next(row for row in bundle["eligibility"] if row["criterion_id"] == "ELIG_001")
        self.assertEqual((age["operator_gt"], age["operator_eq"], age["operator_lt"]), (True, True, False))
        fasting = next(row for row in bundle["eligibility"] if row["criterion_id"] == "ELIG_004")
        self.assertEqual((fasting["range_min"], fasting["range_max"]), (95, 125))
        self.assertIsNone(fasting["operator_gt"])
        p_record = next(row for row in bundle["statistical_tests"] if row["comparison_id"] and row["outcome"] == "weight loss from baseline" and row["timepoint"] == 1)
        self.assertEqual((p_record["p_gt"], p_record["p_eq"], p_record["p_lt"]), (False, False, True))
        threshold = next(row for row in bundle["outcomes"] if row["id"] == "ADH_GT5_DPP_2Y_DOUBLE_BLIND_ARM_MET_high")
        self.assertEqual((threshold["threshold_gt"], threshold["threshold_eq"], threshold["threshold_lt"]), (True, False, False))


if __name__ == "__main__":
    unittest.main()

