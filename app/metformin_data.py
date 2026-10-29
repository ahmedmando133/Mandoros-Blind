from __future__ import annotations

import json
from typing import Any

from .config import STANDARDS_DIR


def load_metformin_bundle() -> dict[str, Any]:
    bundle = json.loads((STANDARDS_DIR / "metformin_truth_bundle.json").read_text(encoding="utf-8"))
    table = json.loads((STANDARDS_DIR / "metformin_table1_adherence.json").read_text(encoding="utf-8"))
    normalized = [*[_normalize_outcome(row) for row in bundle["outcomes"]], *expand_adherence_records(table)]
    bundle["outcomes"], bundle["statistical_tests"] = _separate_statistical_tests(normalized)
    return bundle


def _operator_flags(operator: str | None, value: Any) -> dict[str, bool | None]:
    if operator is None and value is None:
        return {"gt": None, "eq": None, "lt": None}
    return {"gt": operator == ">", "eq": operator == "=", "lt": operator == "<"}


def _normalize_outcome(row: dict[str, Any]) -> dict[str, Any]:
    record = dict(row)
    if record.get("measure") == "proportion":
        record["measure"] = "sample_proportion"
    p_flags = _operator_flags(record.pop("p_operator", None), record.get("p_value"))
    record.update({"p_gt": p_flags["gt"], "p_eq": p_flags["eq"], "p_lt": p_flags["lt"]})
    for key in ("period_id", "threshold_value", "threshold_unit", "threshold_gt", "threshold_eq", "threshold_lt",
                "subgroup_type", "subgroup_value", "adherence_level", "adherence_min_value", "adherence_min_unit",
                "adherence_min_inclusive", "adherence_max_value", "adherence_max_unit", "adherence_max_inclusive",
                "visit_pill_min_value", "visit_pill_min_unit", "visit_pill_gt", "visit_pill_eq", "visit_pill_lt",
                "adherence_special_rule", "analysis_population", "applicability_status"):
        record.setdefault(key, None)
    return record


_PAIRING_FIELDS = (
    "domain", "outcome", "period_id", "timepoint", "time_unit", "measure",
    "threshold_value", "threshold_unit", "threshold_gt", "threshold_eq", "threshold_lt",
    "subgroup_type", "subgroup_value", "adherence_level", "analysis_population",
)


def _pairing_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(record.get(key) for key in _PAIRING_FIELDS)


def _clear_p_value(record: dict[str, Any]) -> None:
    record.update({"p_gt": None, "p_eq": None, "p_lt": None, "p_value": None})


def _separate_statistical_tests(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Store each inferential test once and link arm outcomes through comparison_id."""
    outcomes = [dict(record) for record in records]
    for record in outcomes:
        record.setdefault("comparison_id", None)

    statistical_tests: list[dict[str, Any]] = []
    test_only_ids: set[str] = set()

    for record in outcomes:
        if record.get("measure") != "global_p_value":
            continue
        statistical_tests.append({
            "test_id": record["id"],
            "comparison_id": None,
            "test_scope": "within_arm_subgroup",
            "domain": record["domain"],
            "outcome": "distribution across adherence categories",
            "threshold_gt": None,
            "threshold_eq": None,
            "threshold_lt": None,
            "threshold_value": None,
            "threshold_unit": None,
            "period_id": record.get("period_id"),
            "timepoint": record.get("timepoint"),
            "time_unit": record.get("time_unit"),
            "arm_a_id": None,
            "arm_b_id": None,
            "arm_id": record.get("arm_id"),
            "arm_a_outcome_id": None,
            "arm_b_outcome_id": None,
            "subgroup_factor": record.get("subgroup_type"),
            "p_gt": record.get("p_gt"),
            "p_eq": record.get("p_eq"),
            "p_lt": record.get("p_lt"),
            "p_value": record.get("p_value"),
            "source_page": record.get("source_page"),
            "notes": record.get("applicability_status"),
        })
        test_only_ids.add(record["id"])

    paired_test_ids: set[str] = set()
    for record in outcomes:
        if record["id"] in test_only_ids or record.get("p_value") is None:
            continue
        candidates = [
            other for other in outcomes
            if other["id"] not in test_only_ids
            and other["id"] != record["id"]
            and other.get("arm_id") != record.get("arm_id")
            and _pairing_key(other) == _pairing_key(record)
        ]
        if len(candidates) != 1:
            raise ValueError(f"Expected one comparator outcome for {record['id']}; found {len(candidates)}")
        comparator = candidates[0]
        ordered_ids = sorted((record["id"], comparator["id"]))
        comparison_id = f"CMP_{ordered_ids[0]}__{ordered_ids[1]}"
        if comparison_id in paired_test_ids:
            continue
        paired_test_ids.add(comparison_id)
        record["comparison_id"] = comparison_id
        comparator["comparison_id"] = comparison_id
        statistical_tests.append({
            "test_id": f"TEST_{comparison_id}",
            "comparison_id": comparison_id,
            "test_scope": "between_arm_comparison",
            "domain": record["domain"],
            "outcome": record["outcome"],
            "threshold_gt": record.get("threshold_gt"),
            "threshold_eq": record.get("threshold_eq"),
            "threshold_lt": record.get("threshold_lt"),
            "threshold_value": record.get("threshold_value"),
            "threshold_unit": record.get("threshold_unit"),
            "period_id": record.get("period_id"),
            "timepoint": record.get("timepoint"),
            "time_unit": record.get("time_unit"),
            "arm_a_id": record.get("arm_id"),
            "arm_b_id": comparator.get("arm_id"),
            "arm_id": None,
            "arm_a_outcome_id": record["id"],
            "arm_b_outcome_id": comparator["id"],
            "subgroup_factor": record.get("subgroup_type"),
            "p_gt": record.get("p_gt"),
            "p_eq": record.get("p_eq"),
            "p_lt": record.get("p_lt"),
            "p_value": record.get("p_value"),
            "source_page": record.get("source_page"),
            "notes": "Reported once for the linked between-arm comparison.",
        })
        _clear_p_value(record)
        _clear_p_value(comparator)

    actual_outcomes = [record for record in outcomes if record["id"] not in test_only_ids]
    return actual_outcomes, statistical_tests


def _level_fields(level_id: str) -> dict[str, Any]:
    common = {
        "adherence_min_value": None, "adherence_min_unit": "% of visits", "adherence_min_inclusive": None,
        "adherence_max_value": None, "adherence_max_unit": "% of visits", "adherence_max_inclusive": None,
        "visit_pill_min_value": 80, "visit_pill_min_unit": "% of prescribed pills",
        "visit_pill_gt": True, "visit_pill_eq": True, "visit_pill_lt": False,
        "adherence_special_rule": None,
    }
    if level_id == "low":
        common["adherence_special_rule"] = "never met visit-level pill-taking threshold"
    elif level_id == "lt50":
        common.update({"adherence_min_value": 0, "adherence_min_inclusive": False, "adherence_max_value": 50, "adherence_max_inclusive": False})
    elif level_id == "ge50_lt90":
        common.update({"adherence_min_value": 50, "adherence_min_inclusive": True, "adherence_max_value": 90, "adherence_max_inclusive": False})
    elif level_id == "high":
        common.update({"adherence_min_value": 90, "adherence_min_inclusive": True})
    return common


def _blank_threshold() -> dict[str, Any]:
    return {"threshold_value": None, "threshold_unit": None, "threshold_gt": None, "threshold_eq": None, "threshold_lt": None}


def _blank_p() -> dict[str, Any]:
    return {"p_gt": None, "p_eq": None, "p_lt": None, "p_value": None}


def expand_adherence_records(table: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    levels = table["levels"]
    source_page = table["source_page"]
    for block in table["distribution_blocks"]:
        for scope_key, values in block["rows"].items():
            subgroup_type, subgroup_value = scope_key.split("|", 1)
            for level, value in zip(levels, values, strict=True):
                records.append({
                    "id": f"ADH_DIST_{block['period_id']}_{block['arm_id']}_{subgroup_type}_{_slug(subgroup_value)}_{level['id']}",
                    "domain": "adherence", "outcome": "distribution across adherence categories",
                    "period_id": block["period_id"], "timepoint": block["timepoint"], "time_unit": block["time_unit"],
                    "arm_id": block["arm_id"], "measure": "sample_proportion", "value": value, "unit": "%",
                    "dispersion": None, "dispersion_value": None, **_blank_p(), **_blank_threshold(),
                    "subgroup_type": subgroup_type, "subgroup_value": subgroup_value, "adherence_level": level["label"],
                    **_level_fields(level["id"]), "analysis_population": block["analysis_population"],
                    "applicability_status": "reported", "source_page": source_page,
                })
    threshold = {"threshold_value": 5, "threshold_unit": "% weight loss", "threshold_gt": True, "threshold_eq": False, "threshold_lt": False}
    for block in table["weight_loss_blocks"]:
        for level, value in zip(levels, block["values_by_level"], strict=True):
            records.append({
                "id": f"ADH_GT5_{block['period_id']}_{block['arm_id']}_{level['id']}", "domain": "adherence",
                "outcome": "participants meeting weight-loss threshold by adherence category", "period_id": block["period_id"],
                "timepoint": block["timepoint"], "time_unit": block["time_unit"], "arm_id": block["arm_id"],
                "measure": "sample_proportion", "value": value, "unit": "%", "dispersion": None, "dispersion_value": None,
                **_blank_p(), **threshold, "subgroup_type": "overall", "subgroup_value": "Overall",
                "adherence_level": level["label"], **_level_fields(level["id"]),
                "analysis_population": block["analysis_population"], "applicability_status": "reported", "source_page": source_page,
            })
    placebo = table["placebo_combined"]
    common = {
        "period_id": placebo["period_id"], "timepoint": placebo["timepoint"], "time_unit": placebo["time_unit"],
        "arm_id": placebo["arm_id"], "dispersion": None, "dispersion_value": None, **_blank_p(),
        "subgroup_type": "overall", "subgroup_value": "Overall", "analysis_population": placebo["analysis_population"],
        "source_page": source_page,
    }
    records.append({
        "id": "ADH_DIST_DPP_DPPOS_9Y_COMBINED_ARM_PBO_NOT_APPLICABLE", "domain": "adherence",
        "outcome": "distribution across adherence categories", "measure": "applicability_status", "value": None, "unit": None,
        **_blank_threshold(), "adherence_level": None, **_level_fields("none"),
        "applicability_status": placebo["adherence_applicability"], **common,
    })
    records.append({
        "id": "ADH_GT5_DPP_DPPOS_9Y_COMBINED_ARM_PBO_OVERALL", "domain": "adherence",
        "outcome": "participants meeting weight-loss threshold; not stratified by adherence", "measure": "sample_proportion",
        "value": placebo["overall_percent_with_gt5_weight_loss"], "unit": "%", **threshold,
        "adherence_level": "not stratified", **_level_fields("none"), "applicability_status": "reported_overall_only", **common,
    })
    for test in table["statistical_tests"]:
        flags = _operator_flags(test["p_operator"], test["p_value"])
        records.append({
            "id": test["id"], "domain": "adherence", "outcome": "adherence distribution statistical test",
            "period_id": test["period_id"], "timepoint": 2 if test["period_id"].startswith("DPP_2Y") else 9,
            "time_unit": "years", "arm_id": test["arm_id"], "measure": "global_p_value", "value": None, "unit": None,
            "dispersion": None, "dispersion_value": None, "p_gt": flags["gt"], "p_eq": flags["eq"], "p_lt": flags["lt"],
            "p_value": test["p_value"], **_blank_threshold(), "subgroup_type": test["scope"],
            "subgroup_value": "global comparison", "adherence_level": None, **_level_fields("none"),
            "analysis_population": None, "applicability_status": test["reported_text"] or "reported", "source_page": source_page,
        })
    return records


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.upper()).strip("_")
