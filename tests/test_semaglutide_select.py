from __future__ import annotations

import json
from pathlib import Path

from app.source_completeness import validate_source_inventory


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "standards" / "semaglutide_select_workbook_dataset.json"


def load_dataset():
    return json.loads(DATASET.read_text(encoding="utf-8"))


def test_select_table3_components_are_complete_and_typed():
    data = load_dataset()
    rows = data["outcomes"]
    assert sum(row.get("source_page") == 8 and row.get("dispersion") == "SE" for row in rows) == 16
    assert sum(bool(row.get("source_page") == 8 and row.get("measure") == "LOG_TRANSFORMED_RELATIVE_PERCENTAGE_CHANGE" and row.get("arm_id")) for row in rows) == 10
    assert {(row["value"], row["ci_lower"], row["ci_upper"]) for row in rows if row.get("measure") == "ODDS_RATIO"} == {
        (10.15, 9.18, 11.23),
        (8.74, 7.91, 9.65),
    }


def test_baseline_categories_and_hba1c_thresholds_are_atomic():
    data = load_dataset()
    sex_rows = [row for row in data["baseline"] if row["characteristic"] == "sex"]
    assert {row["subgroup_value"] for row in sex_rows} == {"male", "female"}
    assert len(sex_rows) == 4
    race_rows = [row for row in data["baseline"] if row["characteristic"] == "race"]
    assert all(row["subgroup_value"] for row in race_rows)
    hba1c_rows = [row for row in data["outcomes"] if row["outcome"] == "HbA1c"]
    assert hba1c_rows
    assert all("<" not in row["outcome"] and ">" not in row["outcome"] for row in hba1c_rows)
    binary_hba1c_rows = [row for row in hba1c_rows if row.get("measure") in {"sample_proportion", "ODDS_RATIO", "HAZARD_RATIO"}]
    assert binary_hba1c_rows
    assert all(row.get("threshold_value") is not None for row in binary_hba1c_rows)


def test_source_completeness_claim_is_computed_not_assumed():
    report = validate_source_inventory(load_dataset())
    assert report["inventory_independent_of_excel"] is True
    assert report["unresolved_count"] == 0
    assert report["complete_and_verified"] is True

