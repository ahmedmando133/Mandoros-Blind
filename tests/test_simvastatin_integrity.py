from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "standards" / "simvastatin_workbook_dataset.json"


class SimvastatinIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
        cls.outcomes = cls.data["outcomes"]
        cls.tests = {row["test_id"]: row for row in cls.data["statistical_tests"]}

    def test_medians_keep_iqr_out_of_ci_fields(self) -> None:
        medians = [row for row in self.outcomes if str(row.get("estimate_type", "")).lower() == "median"]
        self.assertEqual(36, len(medians))
        for row in medians:
            self.assertIsNotNone(row.get("lower_value"), row["id"])
            self.assertIsNotNone(row.get("upper_value"), row["id"])
            self.assertIsNone(row.get("ci_lower"), row["id"])
            self.assertIsNone(row.get("ci_upper"), row["id"])
            self.assertIsNone(row.get("ci_level"), row["id"])

    def test_printed_n_percent_is_one_atomic_observation(self) -> None:
        rows = [row for row in self.outcomes if row.get("event_count") is not None]
        self.assertEqual(26, len(rows))
        for row in rows:
            self.assertEqual("sample_proportion", row.get("measure"), row["id"])
            self.assertEqual("participants", row.get("event_count_unit"), row["id"])
            self.assertEqual("%", row.get("percentage_unit"), row["id"])
            self.assertEqual(row.get("denominator"), row.get("event_denominator"), row["id"])

        baseline_binary = [row for row in self.data["baseline"] if row.get("event_count") is not None]
        for row in baseline_binary:
            self.assertEqual(row.get("n_baseline"), row.get("event_denominator"), row["id"])

    def test_sample_size_scopes_are_separate(self) -> None:
        arms = {row["arm_id"]: row for row in self.data["arms"]}
        self.assertEqual(32, arms["ARM_002"]["n_randomized"])
        self.assertEqual(30, arms["ARM_001"]["n_randomized"])
        self.assertIsNone(arms["ARM_002"]["n_analyzed"])
        by_id = {row["id"]: row for row in self.outcomes}
        self.assertEqual(26, by_id["OUT_0047"]["n_analyzed_timepoint"])
        self.assertEqual(25, by_id["OUT_0048"]["n_analyzed_timepoint"])
        self.assertEqual(21, by_id["OUT_0059"]["n_analyzed_timepoint"])
        self.assertEqual(20, by_id["OUT_0060"]["n_analyzed_timepoint"])
        self.assertEqual(17, by_id["OUT_0077"]["n_analyzed_timepoint"])
        self.assertEqual(10, by_id["OUT_0078"]["n_analyzed_timepoint"])

    def test_required_regression_p_values_and_methods(self) -> None:
        expected = {
            "TEST_FMLP_CHANGE": 0.034,
            "TEST_CHEM_CHANGE": 0.033,
            "TEST_NE_CHANGE": 0.001,
            "TEST_SOFA_CHANGE": 0.026,
        }
        for test_id, value in expected.items():
            row = self.tests[test_id]
            self.assertEqual(value, row["p_value"])
            self.assertTrue(row["p_eq"])
            self.assertEqual("Mann-Whitney U test", row["test_effect"])
            self.assertIsNotNone(row["source_page"])
            self.assertIsNotNone(row["source_location"])

    def test_less_than_operator_and_sofa_conflict_are_preserved(self) -> None:
        placebo_nlr = self.tests["TEST_NLR_WITHIN_PBO"]
        self.assertTrue(placebo_nlr["p_lt"])
        self.assertFalse(placebo_nlr["p_eq"])
        self.assertEqual(0.0001, placebo_nlr["p_value"])
        sofa_table = self.tests["TEST_SOFA_TABLE4_CONFLICT"]
        self.assertEqual(0.040, sofa_table["p_value"])
        self.assertEqual("CONFLICT_SOFA_P", sofa_table["conflict_id"])
        self.assertFalse(sofa_table["canonical_for_analysis"])

    def test_provenance_and_identifiers_are_complete(self) -> None:
        for collection in (self.data["baseline"], self.outcomes, self.data["statistical_tests"]):
            for row in collection:
                self.assertIsNotNone(row.get("source_page"), row.get("id") or row.get("test_id"))
                self.assertIsNotNone(row.get("source_location"), row.get("id") or row.get("test_id"))
        ids = [row["id"] for row in self.outcomes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(58, len(self.data["statistical_tests"]))

    def test_supplementary_data_were_not_invented(self) -> None:
        supplement = next(row for row in self.data["document_inventory"] if row["document_id"] == "DOC_SUPPLEMENT")
        self.assertEqual("not supplied", supplement["availability_status"])
        self.assertIsNone(supplement["sha256"])


if __name__ == "__main__":
    unittest.main()
