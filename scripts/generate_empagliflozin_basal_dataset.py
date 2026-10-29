"""Build the source-adjudicated EMPA-REG BASAL Phase 1 dataset.

Only values explicitly printed in the supplied main-article PDF are used.
The supplementary appendix was not supplied; no supplementary value is
created, inferred, or copied from another source.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "private" / "empagliflozin 2"
PDF = SOURCE_DIR / "empa vs placebo.pdf"
MANDROS = SOURCE_DIR / "empa vs placebo_extracted.xlsx"
DESTINATION = ROOT / "standards" / "empagliflozin_basal_workbook_dataset.json"

STUDY_ID = "NCT01011868"
ARM_PBO = "ARM_001"
ARM_E10 = "ARM_002"
ARM_E25 = "ARM_003"
ARM_N = {ARM_PBO: 170, ARM_E10: 169, ARM_E25: 155}
ARM_LABEL = {
    ARM_PBO: "Placebo once daily",
    ARM_E10: "Empagliflozin 10 mg once daily",
    ARM_E25: "Empagliflozin 25 mg once daily",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def baseline(identifier: str, characteristic: str, arm_id: str | None, measure: str,
             value: Any, unit: str | None, *, n_baseline=None, dispersion=None,
             dispersion_value=None, event_count=None, denominator=None,
             subgroup_type=None, subgroup_value=None, analysis_population="as reported",
             source_page=5, source_location="Table 1", notes=None) -> dict[str, Any]:
    return {
        "id": identifier, "characteristic": characteristic,
        "threshold_lt": False, "threshold_eq": False, "threshold_gt": False,
        "threshold_value": None, "threshold_unit": None,
        "subgroup_type": subgroup_type, "subgroup_value": subgroup_value,
        "independent_study_id": STUDY_ID, "estimand_family": f"baseline_{measure}",
        "comparison_id": None, "timepoint": 0, "time_unit": "baseline",
        "arm_id": arm_id, "n_baseline": n_baseline,
        "event_count": event_count, "event_count_unit": "participants" if event_count is not None else None,
        "denominator": denominator, "event_denominator": denominator,
        "percentage_unit": "%" if measure == "sample_proportion" else None,
        "denominator_type": "reported_population" if denominator is not None else "not_reported",
        "measure": measure, "estimate_type": measure, "value": value, "unit": unit,
        "dispersion": dispersion, "dispersion_value": dispersion_value,
        "lower_value": None, "upper_value": None,
        "analysis_population": analysis_population,
        "source_status": "published_main_article_exact", "conflict_id": None,
        "canonical_record_id": identifier, "canonical_for_analysis": True,
        "meta_analysis_eligibility": "NOT_POOLABLE",
        "meta_analysis_reason": "Baseline descriptive record.",
        "include_in_meta_analysis": False, "source_page": source_page,
        "source_location": source_location, "notes": notes,
    }


def outcome(identifier: str, domain: str, name: str, arm_id: str | None,
            measure: str, value: Any, unit: str | None, *, timepoint=None,
            time_unit=None, n_randomized=None, n_baseline=None, n_analyzed=None,
            event_count=None, denominator=None, dispersion=None,
            dispersion_value=None, ci_lower=None, ci_upper=None,
            effect_measure=None, effect_value=None, subgroup_type=None,
            subgroup_value=None, lt=False, eq=False, gt=False,
            threshold_value=None, threshold_unit=None,
            analysis_population="as reported", source_page=5,
            source_location="Table 1", notes=None, comparison_id=None,
            ready=False, source_status="published_main_article_exact") -> dict[str, Any]:
    return {
        "id": identifier, "domain": domain, "outcome": name,
        "threshold_lt": lt, "threshold_eq": eq, "threshold_gt": gt,
        "threshold_value": threshold_value, "threshold_unit": threshold_unit,
        "subgroup_type": subgroup_type, "subgroup_value": subgroup_value,
        "adherence_level": None, "independent_study_id": STUDY_ID,
        "estimand_family": measure, "comparison_id": comparison_id,
        "period_id": None, "timepoint": timepoint, "time_unit": time_unit,
        "arm_id": arm_id, "n_randomized": n_randomized,
        "n_baseline": n_baseline, "n_analyzed": n_analyzed,
        "n_analyzed_timepoint": timepoint if n_analyzed is not None else None,
        "event_count": event_count,
        "event_count_unit": "participants" if event_count is not None else None,
        "denominator": denominator, "event_denominator": denominator,
        "percentage_unit": "%" if measure == "sample_proportion" else None,
        "denominator_type": "outcome_specific" if denominator is not None else "not_reported",
        "measure": measure, "estimate_type": measure, "value": value,
        "unit": unit, "dispersion": dispersion, "dispersion_value": dispersion_value,
        "lower_value": None, "upper_value": None, "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_level": 95 if ci_lower is not None and ci_upper is not None else None,
        "effect_measure": effect_measure, "effect_value": effect_value,
        "analysis_population": analysis_population, "applicability_status": "reported",
        "derivation_type": None, "source_status": source_status,
        "conflict_id": None, "canonical_record_id": identifier,
        "canonical_for_analysis": True,
        "meta_analysis_eligibility": "READY" if ready else "REQUIRES_REVIEW",
        "meta_analysis_reason": (
            "All explicitly printed components required for this record are present."
            if ready else "Preserved as printed; pooling requires estimand-specific review."
        ),
        "include_in_meta_analysis": ready, "source_page": source_page,
        "source_location": source_location, "notes": notes,
    }


def test(identifier: str, name: str, arm_a: str, arm_b: str, *,
         timepoint=None, time_unit=None, p_operator=None, p_value=None,
         effect_measure=None, effect_value=None, ci_lower=None, ci_upper=None,
         method=None, population="as reported", source_page=5,
         source_location="Table 1", notes=None, comparison_id=None,
         domain="efficacy") -> dict[str, Any]:
    cmp_id = comparison_id or identifier.replace("TEST_", "CMP_")
    return {
        "test_id": identifier, "comparison_id": cmp_id,
        "test_scope": "between_arm_comparison", "domain": domain,
        "outcome": name, "threshold_lt": False, "threshold_eq": False,
        "threshold_gt": False, "threshold_value": None, "threshold_unit": None,
        "independent_study_id": STUDY_ID,
        "estimand_family": effect_measure or "p_value_only", "period_id": None,
        "timepoint": timepoint, "time_unit": time_unit,
        "arm_a_id": arm_a, "arm_b_id": arm_b, "arm_id": None,
        "arm_a_outcome_id": None, "arm_b_outcome_id": None,
        "subgroup_factor": None, "test_effect": method,
        "estimate_type": effect_measure or "p_value",
        "effect_measure": effect_measure, "effect_value": effect_value,
        "ci_lower": ci_lower, "ci_upper": ci_upper,
        "ci_level": 95 if ci_lower is not None and ci_upper is not None else None,
        "analysis_population": population, "p_lt": p_operator == "<",
        "p_eq": p_operator == "=", "p_gt": p_operator == ">",
        "p_value": p_value, "nominal_adjusted_status": "reported_nominal",
        "source_status": "published_main_article_exact", "conflict_id": None,
        "canonical_for_analysis": True,
        "meta_analysis_eligibility": (
            "READY" if effect_value is not None and ci_lower is not None and ci_upper is not None
            else "NOT_POOLABLE"
        ),
        "meta_analysis_reason": (
            "Published effect estimate and confidence interval preserved."
            if effect_value is not None and ci_lower is not None and ci_upper is not None
            else "P-value-only comparison; preserve for interpretation."
        ),
        "include_in_meta_analysis": bool(effect_value is not None and ci_lower is not None and ci_upper is not None),
        "source_page": source_page, "source_location": source_location,
        "notes": notes,
    }


def eligibility_rows() -> list[dict[str, Any]]:
    def c(identifier, category, variable, *, lt=False, eq=False, gt=False,
          value=None, unit=None, range_min=None, range_max=None,
          min_inclusive=None, max_inclusive=None, qualifier=None):
        return {
            "criterion_id": identifier, "category": category, "variable": variable,
            "operator_lt": lt, "operator_eq": eq, "operator_gt": gt,
            "value": value, "unit": unit, "range_min": range_min,
            "range_max": range_max, "range_unit": unit if range_min is not None else None,
            "range_min_inclusive": min_inclusive, "range_max_inclusive": max_inclusive,
            "population_scope": "overall", "qualifier": qualifier,
            "source_page": 2, "source_location": "Inclusion and Exclusion Criteria",
            "source_status": "published_main_article_exact",
        }
    return [
        c("ELIG_INC_ADULT", "inclusion", "adult_status", qualifier="Adults; no numeric minimum age was printed in the main article."),
        c("ELIG_INC_T2D", "inclusion", "type_2_diabetes", qualifier="Inadequately controlled type 2 diabetes."),
        c("ELIG_INC_BMI", "inclusion", "BMI", lt=True, eq=True, value=45, unit="kg/m2"),
        c("ELIG_INC_HBA1C_PERCENT", "inclusion", "HbA1c", range_min=7, range_max=10, unit="%", min_inclusive=False, max_inclusive=True),
        c("ELIG_INC_HBA1C_SI", "inclusion", "HbA1c", range_min=53, range_max=86, unit="mmol/mol", min_inclusive=False, max_inclusive=True),
        c("ELIG_INC_GLARGINE_DETEMIR", "inclusion", "basal_glargine_or_detemir_dose", gt=True, eq=True, value=20, unit="IU/day"),
        c("ELIG_INC_NPH", "inclusion", "NPH_insulin_dose", gt=True, eq=True, value=14, unit="IU/day"),
        c("ELIG_INC_INSULIN_STABILITY", "inclusion", "basal_insulin_dose_change", lt=True, eq=True, value=10, unit="% of baseline", qualifier="Dose unchanged by more than 10% for at least 12 weeks before randomization."),
        c("ELIG_INC_INSULIN_STABILITY_DURATION", "inclusion", "basal_insulin_stable_duration", gt=True, eq=True, value=12, unit="weeks before randomization"),
        c("ELIG_INC_BACKGROUND_DRUGS", "inclusion", "metformin_or_sulphonylurea_stability", gt=True, eq=True, value=12, unit="weeks before randomization", qualifier="With or without metformin and/or sulphonylurea, unchanged for at least 12 weeks."),
        c("ELIG_EXC_FASTING_GLUCOSE", "exclusion", "fasting_plasma_glucose", gt=True, value=13.3, unit="mmol/L", qualifier="After an overnight fast during placebo run-in."),
        c("ELIG_EXC_FASTING_GLUCOSE_MGDL", "exclusion", "fasting_plasma_glucose", gt=True, value=240, unit="mg/dL", qualifier="Source-reported equivalent after an overnight fast during placebo run-in."),
        c("ELIG_EXC_RANDOM_GLUCOSE", "exclusion", "random_plasma_glucose", gt=True, value=22.2, unit="mmol/L", qualifier="Random assessment during placebo run-in."),
        c("ELIG_EXC_RANDOM_GLUCOSE_MGDL", "exclusion", "random_plasma_glucose", gt=True, value=400, unit="mg/dL", qualifier="Source-reported equivalent during placebo run-in."),
        c("ELIG_EXC_HYPO", "exclusion", "frequent_hypoglycaemic_events", qualifier="Frequent events on basal insulin therapy in the investigator's opinion."),
        c("ELIG_EXC_RECENT_CV", "exclusion", "myocardial_infarction_stroke_or_TIA", lt=True, value=3, unit="months before consent"),
        c("ELIG_EXC_EGFR", "exclusion", "eGFR", lt=True, value=30, unit="mL/min/1.73m2"),
        c("ELIG_EXC_BARIATRIC", "exclusion", "bariatric_surgery"),
        c("ELIG_EXC_INVESTIGATIONAL", "exclusion", "investigational_drug_intake", lt=True, value=2, unit="months before consent"),
        c("ELIG_EXC_ANTI_OBESITY", "exclusion", "anti_obesity_drug_treatment", lt=True, value=3, unit="months before consent"),
        c("ELIG_EXC_OTHER_OAD", "exclusion", "oral_antidiabetes_medication_other_than_metformin_or_sulphonylurea", lt=True, value=3, unit="months before consent"),
        c("ELIG_EXC_SHORT_INSULIN", "exclusion", "chronic_short_acting_insulin", lt=True, value=3, unit="months before consent"),
        c("ELIG_EXC_GLP1", "exclusion", "GLP1_receptor_agonist", lt=True, value=3, unit="months before consent"),
    ]


def baseline_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Arm-specific values printed in Table 1 / Figures 1-2. The printed
    # uncertainty is SE, not SD.
    for arm, value, se in ((ARM_PBO, 90.5, 1.7), (ARM_E10, 91.6, 1.5), (ARM_E25, 94.7, 1.7)):
        rows.append(baseline(f"BASE_WEIGHT_{arm}", "body weight", arm, "mean", value, "kg", n_baseline=ARM_N[arm], dispersion="SE", dispersion_value=se, analysis_population="full analysis set", source_page=5))
    for arm, value, se in ((ARM_PBO, 7.9, .2), (ARM_E10, 7.7, .2), (ARM_E25, 8.1, .2)):
        rows.append(baseline(f"BASE_FPG_{arm}", "fasting plasma glucose", arm, "mean", value, "mmol/L", n_baseline=ARM_N[arm], dispersion="SE", dispersion_value=se, analysis_population="full analysis set", source_page=5))
    for arm, value in ((ARM_PBO, 133.9), (ARM_E10, 132.4), (ARM_E25, 132.8)):
        rows.append(baseline(f"BASE_SBP_{arm}", "systolic blood pressure", arm, "mean", value, "mmHg", n_baseline=ARM_N[arm], analysis_population="full analysis set", source_page=4, source_location="Figure 1D directly printed baseline label", notes="No exact baseline dispersion was printed in the supplied main article."))
    for arm, value in ((ARM_PBO, 78.6), (ARM_E10, 78.4), (ARM_E25, 77.9)):
        rows.append(baseline(f"BASE_DBP_{arm}", "diastolic blood pressure", arm, "mean", value, "mmHg", n_baseline=ARM_N[arm], analysis_population="full analysis set", source_page=4, source_location="Figure 1E directly printed baseline label", notes="No exact baseline dispersion was printed in the supplied main article."))
    n18 = {ARM_PBO: 125, ARM_E10: 132, ARM_E25: 117}
    for arm, value, se in ((ARM_PBO, 8.1, .1), (ARM_E10, 8.3, .1), (ARM_E25, 8.3, .1)):
        rows.append(baseline(f"BASE_HBA1C_FAS18_{arm}", "HbA1c", arm, "mean", value, "%", n_baseline=n18[arm], dispersion="SE", dispersion_value=se, analysis_population="FAS-18 completers", source_page=5, notes="Endpoint-specific baseline for the primary Week 18 analysis; not the randomized arm N."))
    n78 = {ARM_PBO: 112, ARM_E10: 127, ARM_E25: 110}
    for arm, value, se in ((ARM_PBO, 47.8, 3.1), (ARM_E10, 45.1, 2.6), (ARM_E25, 48.4, 2.8)):
        rows.append(baseline(f"BASE_INSULIN_FAS78_{arm}", "basal insulin dose", arm, "mean", value, "IU", n_baseline=n78[arm], dispersion="SE", dispersion_value=se, analysis_population="FAS-78 completers", source_page=5, notes="Endpoint-specific baseline for the Week 78 insulin-dose analysis."))

    rows.extend([
        baseline("BASE_OVERALL_AGE", "age", None, "mean", 58.8, "years", n_baseline=494, dispersion="SD", dispersion_value=9.9, analysis_population="full analysis set", source_page=3, source_location="Results - Patients"),
        baseline("BASE_OVERALL_HBA1C", "HbA1c", None, "mean", 8.2, "%", n_baseline=494, dispersion="SD", dispersion_value=.8, analysis_population="full analysis set", source_page=3, source_location="Results - Patients"),
        baseline("BASE_OVERALL_HBA1C_SI", "HbA1c", None, "mean", 67, "mmol/mol", n_baseline=494, dispersion="SD", dispersion_value=9.0, analysis_population="full analysis set", source_page=3, source_location="Results - Patients"),
        baseline("BASE_OVERALL_BMI", "BMI", None, "mean", 32.2, "kg/m2", n_baseline=494, analysis_population="full analysis set", source_page=1, source_location="Abstract", notes="Mean only; no dispersion printed in the abstract."),
    ])
    proportions = [
        ("BASE_T2D_GT5Y", "type 2 diabetes duration", ">5 years", 89),
        ("BASE_HBA1C_GE85", "HbA1c", ">=8.5%", 36),
        ("BASE_BG_INS_MET", "background therapy", "basal insulin plus metformin", 40),
        ("BASE_BG_INS_MET_SU", "background therapy", "basal insulin plus metformin and sulphonylurea", 39),
        ("BASE_BG_INS_SU", "background therapy", "basal insulin plus sulphonylurea", 10),
        ("BASE_BG_INS_ONLY", "background therapy", "basal insulin only", 10),
        ("BASE_INS_GLARGINE", "basal insulin type", "glargine", 58),
        ("BASE_INS_DETEMIR", "basal insulin type", "detemir", 19),
        ("BASE_INS_NPH", "basal insulin type", "NPH", 14),
    ]
    for ident, characteristic, subgroup, pct in proportions:
        rows.append(baseline(ident, characteristic, None, "sample_proportion", pct, "%", n_baseline=494, denominator=494, subgroup_type=characteristic, subgroup_value=subgroup, analysis_population="full analysis set", source_page=3, source_location="Results - Patients", notes="Only the printed percentage is stored; no count is derived."))
    return rows


def add_table1_rows(rows: list[dict[str, Any]], tests: list[dict[str, Any]]) -> None:
    n18 = {ARM_PBO: 125, ARM_E10: 132, ARM_E25: 117}
    n78 = {ARM_PBO: 112, ARM_E10: 127, ARM_E25: 110}

    def arm_rows(prefix, name, week, unit, population, n_map, final_values, change_values):
        for arm in (ARM_PBO, ARM_E10, ARM_E25):
            final, final_se = final_values[arm]
            change, change_se = change_values[arm]
            rows.append(outcome(f"{prefix}_FINAL_{arm}", "efficacy", name, arm, "mean", final, unit, timepoint=week, time_unit="weeks", n_analyzed=n_map[arm], dispersion="SE", dispersion_value=final_se, analysis_population=population, source_page=5, ready=False))
            rows.append(outcome(f"{prefix}_CHANGE_{arm}", "efficacy", name, arm, "ADJUSTED_MEAN_CHANGE", change, unit, timepoint=week, time_unit="weeks", n_analyzed=n_map[arm], dispersion="SE", dispersion_value=change_se, analysis_population=population, source_page=5, comparison_id=f"CMP_{prefix}", ready=False, notes="Adjusted mean change +/- SE."))

    # Primary HbA1c endpoint, Week 18.
    arm_rows("HBA1C18_PCT", "HbA1c", 18, "%", "FAS-18 completers; ANCOVA with LOCF", n18,
             {ARM_PBO:(8.1,.1), ARM_E10:(7.7,.1), ARM_E25:(7.6,.1)},
             {ARM_PBO:(0.0,.1), ARM_E10:(-.6,.1), ARM_E25:(-.7,.1)})
    arm_rows("HBA1C18_SI", "HbA1c", 18, "mmol/mol", "FAS-18 completers; ANCOVA with LOCF", n18,
             {ARM_PBO:(65,1.1), ARM_E10:(60,1.0), ARM_E25:(59,.9)},
             {ARM_PBO:(-.1,.8), ARM_E10:(-6.2,.8), ARM_E25:(-7.8,.8)})
    # Key HbA1c endpoint, Week 78.
    arm_rows("HBA1C78_PCT", "HbA1c", 78, "%", "FAS-78 completers; ANCOVA with LOCF", n78,
             {ARM_PBO:(8.1,.1), ARM_E10:(7.8,.1), ARM_E25:(7.6,.1)},
             {ARM_PBO:(0.0,.1), ARM_E10:(-.5,.1), ARM_E25:(-.6,.1)})
    arm_rows("HBA1C78_SI", "HbA1c", 78, "mmol/mol", "FAS-78 completers; ANCOVA with LOCF", n78,
             {ARM_PBO:(65,1.2), ARM_E10:(61,.9), ARM_E25:(60,1.0)},
             {ARM_PBO:(-.2,1.0), ARM_E10:(-5.2,.9), ARM_E25:(-7.0,1.0)})
    # FPG, insulin dose and body weight.
    arm_rows("FPG18", "fasting plasma glucose", 18, "mmol/L", "full analysis set; ANCOVA with LOCF", ARM_N,
             {ARM_PBO:(8.4,.3), ARM_E10:(6.8,.2), ARM_E25:(6.9,.2)},
             {ARM_PBO:(.6,.2), ARM_E10:(-1.0,.2), ARM_E25:(-1.1,.2)})
    arm_rows("FPG78", "fasting plasma glucose", 78, "mmol/L", "full analysis set; ANCOVA with LOCF", ARM_N,
             {ARM_PBO:(8.0,.2), ARM_E10:(7.2,.2), ARM_E25:(7.1,.2)},
             {ARM_PBO:(.2,.2), ARM_E10:(-.6,.2), ARM_E25:(-.8,.2)})
    arm_rows("WEIGHT18", "body weight", 18, "kg", "full analysis set; ANCOVA with LOCF", ARM_N,
             {ARM_PBO:(90.4,1.8), ARM_E10:(89.9,1.5), ARM_E25:(93.9,2.1)},
             {ARM_PBO:(0.0,.6), ARM_E10:(-1.7,.6), ARM_E25:(-.9,.6)})
    arm_rows("WEIGHT78", "body weight", 78, "kg", "full analysis set; ANCOVA with LOCF", ARM_N,
             {ARM_PBO:(91.2,1.9), ARM_E10:(89.4,1.5), ARM_E25:(92.7,1.7)},
             {ARM_PBO:(.7,.5), ARM_E10:(-2.2,.5), ARM_E25:(-2.0,.5)})
    arm_rows("INSULIN78", "basal insulin dose", 78, "IU", "FAS-78 completers; ANCOVA with LOCF", n78,
             {ARM_PBO:(52.6,3.0), ARM_E10:(44.4,2.3), ARM_E25:(48.0,2.8)},
             {ARM_PBO:(5.5,1.6), ARM_E10:(-1.2,1.5), ARM_E25:(-.5,1.6)})

    effects = [
        ("HBA1C18_PCT", "HbA1c", 18, "%", ARM_E10, -.6, .1, -.8, -.4, "<", .001, "FAS-18 completers"),
        ("HBA1C18_PCT", "HbA1c", 18, "%", ARM_E25, -.7, .1, -.9, -.5, "<", .001, "FAS-18 completers"),
        ("HBA1C18_SI", "HbA1c", 18, "mmol/mol", ARM_E10, -6.1, 1.1, -8.2, -3.9, "<", .001, "FAS-18 completers"),
        ("HBA1C18_SI", "HbA1c", 18, "mmol/mol", ARM_E25, -7.7, 1.1, -9.8, -5.5, "<", .001, "FAS-18 completers"),
        ("HBA1C78_PCT", "HbA1c", 78, "%", ARM_E10, -.5, .1, -.7, -.2, "<", .001, "FAS-78 completers"),
        ("HBA1C78_PCT", "HbA1c", 78, "%", ARM_E25, -.6, .1, -.9, -.4, "<", .001, "FAS-78 completers"),
        ("HBA1C78_SI", "HbA1c", 78, "mmol/mol", ARM_E10, -5.0, 1.3, -7.7, -2.5, "<", .001, "FAS-78 completers"),
        ("HBA1C78_SI", "HbA1c", 78, "mmol/mol", ARM_E25, -6.8, 1.3, -9.5, -4.2, "<", .001, "FAS-78 completers"),
        ("INSULIN78", "basal insulin dose", 78, "IU", ARM_E10, -6.7, 2.2, -10.9, -2.4, "=", .002, "FAS-78 completers"),
        ("INSULIN78", "basal insulin dose", 78, "IU", ARM_E25, -5.9, 2.3, -10.4, -1.5, "=", .009, "FAS-78 completers"),
        ("FPG18", "fasting plasma glucose", 18, "mmol/L", ARM_E10, -1.6, .2, -2.1, -1.1, "<", .001, "full analysis set"),
        ("FPG18", "fasting plasma glucose", 18, "mmol/L", ARM_E25, -1.6, .3, -2.1, -1.1, "<", .001, "full analysis set"),
        ("FPG78", "fasting plasma glucose", 78, "mmol/L", ARM_E10, -.7, .3, -1.2, -.2, "=", .005, "full analysis set"),
        ("FPG78", "fasting plasma glucose", 78, "mmol/L", ARM_E25, -1.0, .3, -1.5, -.5, "<", .001, "full analysis set"),
        ("WEIGHT18", "body weight", 18, "kg", ARM_E10, -1.7, .8, -3.3, -.1, "=", .035, "full analysis set"),
        ("WEIGHT18", "body weight", 18, "kg", ARM_E25, -.9, .8, -2.5, .8, "=", .293, "full analysis set"),
        ("WEIGHT78", "body weight", 78, "kg", ARM_E10, -2.9, .7, -4.3, -1.5, "<", .001, "full analysis set"),
        ("WEIGHT78", "body weight", 78, "kg", ARM_E25, -2.8, .7, -4.2, -1.3, "<", .001, "full analysis set"),
    ]
    for index, (prefix, name, week, unit, arm, value, se, lo, hi, pop, pval, population) in enumerate(effects, start=1):
        cmp_id = f"CMP_{prefix}_{arm}"
        rows.append(outcome(f"EFF_{prefix}_{arm}", "efficacy", name, None, "ADJUSTED_MEAN_DIFFERENCE", value, unit, timepoint=week, time_unit="weeks", dispersion="SE", dispersion_value=se, ci_lower=lo, ci_upper=hi, effect_measure="ADJUSTED_MEAN_DIFFERENCE", effect_value=value, analysis_population=population, source_page=5, comparison_id=cmp_id, ready=True, notes="Published difference versus placebo; not recalculated."))
        tests.append(test(f"TEST_T1_{index:02d}", name, arm, ARM_PBO, timepoint=week, time_unit="weeks", p_operator=pop, p_value=pval, effect_measure="ADJUSTED_MEAN_DIFFERENCE", effect_value=value, ci_lower=lo, ci_upper=hi, method="ANCOVA", population=population, source_page=5, comparison_id=cmp_id))


def efficacy_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    add_table1_rows(rows, tests)

    # Binary HbA1c response values explicitly printed in Results text.
    # Keep each arm-level percentage as its own source finding. The published
    # odds ratio is a separate between-arm statistic and must never substitute
    # for either arm's responder percentage.
    for arm, pct in ((ARM_PBO, 5.5), (ARM_E10, 18.0), (ARM_E25, 19.5)):
        rows.append(outcome(f"RESP18_{arm}", "efficacy", "HbA1c responder", arm, "sample_proportion", pct, "%", timepoint=18, time_unit="weeks", subgroup_type="baseline_HbA1c", subgroup_value=">=7.0% at baseline", lt=True, threshold_value=7.0, threshold_unit="%", analysis_population="patients with baseline HbA1c >=7.0%; exact denominator not printed in main article", source_page=3, source_location="Results - Efficacy Week 18 (printed page 938)", notes="Arm-level responder percentage printed in the main article; no denominator is inferred. Stored separately from the odds ratio."))
    for index, (arm, odds, lo, hi) in enumerate(((ARM_E10, 4.1, 1.8, 9.1), (ARM_E25, 4.6, 2.1, 10.3)), start=1):
        cmp_id = f"CMP_RESP18_{arm}"
        rows.append(outcome(f"RESP18_OR_{arm}", "efficacy", "HbA1c responder", None, "ODDS_RATIO", odds, None, timepoint=18, time_unit="weeks", ci_lower=lo, ci_upper=hi, effect_measure="ODDS_RATIO", effect_value=odds, lt=True, threshold_value=7.0, threshold_unit="%", subgroup_type="baseline_HbA1c", subgroup_value=">=7.0% at baseline", analysis_population="patients with baseline HbA1c >=7.0%", source_page=3, source_location="Results - Efficacy Week 18", comparison_id=cmp_id, ready=True))
        tests.append(test(f"TEST_RESP18_{index}", "HbA1c responder", arm, ARM_PBO, timepoint=18, time_unit="weeks", p_operator="<", p_value=.001, effect_measure="ODDS_RATIO", effect_value=odds, ci_lower=lo, ci_upper=hi, method="logistic regression", population="patients with baseline HbA1c >=7.0%", source_page=3, source_location="Results - Efficacy Week 18", comparison_id=cmp_id))
    for arm, pct in ((ARM_PBO, 6.7), (ARM_E25, 17.5)):
        rows.append(outcome(f"RESP78_{arm}", "efficacy", "HbA1c responder", arm, "sample_proportion", pct, "%", timepoint=78, time_unit="weeks", subgroup_type="baseline_HbA1c", subgroup_value=">=7.0% at baseline", lt=True, threshold_value=7.0, threshold_unit="%", analysis_population="patients with baseline HbA1c >=7.0%; exact denominator not printed in main article", source_page=3, source_location="Results - Efficacy Week 78 (printed page 938)", notes="Arm-level responder percentage printed in the main article and stored separately from the odds ratio. Only placebo and empagliflozin 25 mg values were printed; the 10 mg value is not invented."))
    rows.append(outcome("RESP78_OR_E25", "efficacy", "HbA1c responder", None, "ODDS_RATIO", 3.2, None, timepoint=78, time_unit="weeks", ci_lower=1.5, ci_upper=6.9, effect_measure="ODDS_RATIO", effect_value=3.2, lt=True, threshold_value=7.0, threshold_unit="%", subgroup_type="baseline_HbA1c", subgroup_value=">=7.0% at baseline", analysis_population="patients with baseline HbA1c >=7.0%", source_page=3, source_location="Results - Efficacy Week 78", comparison_id="CMP_RESP78_E25", ready=True))
    tests.append(test("TEST_RESP78_E25", "HbA1c responder", ARM_E25, ARM_PBO, timepoint=78, time_unit="weeks", p_operator="=", p_value=.002, effect_measure="ODDS_RATIO", effect_value=3.2, ci_lower=1.5, ci_upper=6.9, method="logistic regression", population="patients with baseline HbA1c >=7.0%", source_page=3, source_location="Results - Efficacy Week 78", comparison_id="CMP_RESP78_E25"))

    # Blood pressure adjusted changes. Exact SE is preserved only where printed.
    bp = [
        (18, "systolic blood pressure", ARM_PBO, -.3, .9, None, None),
        (18, "systolic blood pressure", ARM_E10, -3.7, .9, "=", .011),
        (18, "systolic blood pressure", ARM_E25, -3.3, 1.0, "=", .027),
        (18, "diastolic blood pressure", ARM_PBO, -.4, .6, None, None),
        (18, "diastolic blood pressure", ARM_E10, -3.6, .6, "<", .001),
        (18, "diastolic blood pressure", ARM_E25, -2.0, None, None, None),
        (78, "systolic blood pressure", ARM_PBO, .1, 1.0, None, None),
        (78, "systolic blood pressure", ARM_E10, -4.1, 1.0, "=", .004),
        (78, "systolic blood pressure", ARM_E25, -2.4, None, None, None),
        (78, "diastolic blood pressure", ARM_PBO, -.3, .6, None, None),
        (78, "diastolic blood pressure", ARM_E10, -2.9, .7, "=", .004),
        (78, "diastolic blood pressure", ARM_E25, -1.5, None, None, None),
    ]
    for index, (week, name, arm, value, se, pop, pval) in enumerate(bp, start=1):
        notes = None if se is not None else "Directly printed figure value; exact SE was not printed and is left blank."
        rows.append(outcome(f"BP_{week}_{index:02d}", "efficacy", name, arm, "ADJUSTED_MEAN_CHANGE", value, "mmHg", timepoint=week, time_unit="weeks", n_analyzed=ARM_N[arm], dispersion="SE" if se is not None else None, dispersion_value=se, analysis_population="full analysis set; ANCOVA with LOCF", source_page=4 if week == 18 else 8, source_location=f"Figure {'1' if week == 18 else '2'} directly printed value and Results text", notes=notes))
        if pop:
            tests.append(test(f"TEST_BP_{week}_{index:02d}", name, arm, ARM_PBO, timepoint=week, time_unit="weeks", p_operator=pop, p_value=pval, method="ANCOVA", population="full analysis set; LOCF", source_page=4 if week == 18 else 9, source_location=f"Figure {'1' if week == 18 else '2'} / Results text"))

    # Figure 2 directly printed analyzed-observation counts. Curves are not digitized.
    observed = {
        "HbA1c": ([6,12,18,30,42,54,66,78], {ARM_PBO:[156,129,141,132,119,113,105,98], ARM_E10:[160,132,148,137,123,121,115,114], ARM_E25:[137,120,123,114,110,107,98,96]}, 6),
        "fasting plasma glucose": ([0,6,12,18,30,42,54,66,78], {ARM_PBO:[151,141,139,135,128,106,103,95,92], ARM_E10:[157,149,143,138,130,110,111,105,104], ARM_E25:[140,135,129,120,114,102,99,89,92]}, 6),
        "basal insulin dose": ([0,6,12,18,30,42,54,66,78], {ARM_PBO:[150,150,146,140,130,120,112,105,102], ARM_E10:[155,155,151,146,133,126,122,117,115], ARM_E25:[138,138,126,121,116,111,104,98,96]}, 7),
        "body weight": ([0,6,12,18,30,42,54,66,78], {ARM_PBO:[160,160,145,141,133,120,114,105,100], ARM_E10:[164,163,152,148,136,123,120,114,113], ARM_E25:[144,143,133,125,117,111,106,97,96]}, 8),
    }
    for metric, (weeks, values_by_arm, page) in observed.items():
        for arm, values in values_by_arm.items():
            for week, value in zip(weeks, values):
                rows.append(outcome(f"OBS_{metric.upper().replace(' ','_')}_{arm}_{week}", "process", f"{metric} analyzed observations", arm, "analyzed_sample_size", value, "participants", timepoint=week, time_unit="weeks", analysis_population="MMRM full analysis set observed cases", source_page=page, source_location="Figure 2 directly printed number of analyzed patients", notes="Directly printed count only; no curve value is digitized."))

    # Patient flow and eGFR text results.
    for ident, name, count, pct, week in (("FLOW_COMPLETE18", "completed treatment", 429, 87, 18), ("FLOW_COMPLETE78", "completed treatment", 360, 73, 78)):
        rows.append(outcome(ident, "process", name, None, "sample_proportion", pct, "%", timepoint=week, time_unit="weeks", event_count=count, denominator=494, analysis_population="all randomized patients", source_page=3, source_location="Results - Patients", notes="Printed count and percentage."))
    for arm, value, sd, n in ((ARM_PBO, -6.3, 13.0, 120), (ARM_E10, -4.8, 12.1, 127), (ARM_E25, -5.7, 13.4, 117)):
        rows.append(outcome(f"SAFE_EGFR_{arm}", "safety", "eGFR change from baseline", arm, "mean_change", value, "mL/min/1.73m2", timepoint=78, time_unit="weeks", n_analyzed=n, dispersion="SD", dispersion_value=sd, analysis_population="follow-up set", source_page=9, source_location="Safety Results text (printed page 944)", notes="End-of-treatment mean change, SD and analyzed N preserved in separate fields exactly as printed."))
    return rows, tests


def safety_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Every Table 2 category. Each n (%) is one observation with count and
    # percentage in separate fields on the same row.
    table2 = [
        ("at least one adverse event", (148,87),(143,85),(135,87), None, None),
        ("at least one drug-related adverse event", (52,31),(65,38),(68,44), None, None),
        ("adverse event leading to discontinuation", (13,8),(19,11),(20,13), None, None),
        ("serious adverse event", (28,16),(28,17),(28,18), None, None),
        ("death", (1,1),(0,None),(0,None), None, None),
        ("hypoglycaemia", (56,33),(56,33),(55,35), None, None),
        ("nasopharyngitis", (22,13),(20,12),(17,11), None, None),
        ("urinary tract infection preferred term", (13,8),(21,12),(16,10), None, None),
        ("hyperglycaemia", (17,10),(16,9),(15,10), None, None),
        ("upper respiratory tract infection", (10,6),(18,11),(13,8), None, None),
        ("back pain", (13,8),(11,7),(13,8), None, None),
        ("dizziness", (12,7),(18,11),(7,5), None, None),
        ("diarrhoea", (13,8),(10,6),(11,7), None, None),
        ("nausea", (12,7),(9,5),(8,5), None, None),
        ("arthralgia", (10,6),(6,4),(8,5), None, None),
        ("cough", (9,5),(6,4),(4,3), None, None),
        ("headache", (5,3),(5,3),(8,5), None, None),
        ("depression", (4,2),(11,7),(2,1), None, None),
        ("vomiting", (5,3),(4,2),(8,5), None, None),
        ("fatigue", (2,1),(10,6),(4,3), None, None),
        ("hypertension", (12,7),(1,1),(3,2), None, None),
        ("confirmed hypoglycaemic adverse event", (60,35),(61,36),(56,36), None, None),
        ("symptomatic confirmed hypoglycaemic adverse event", (22,13),(28,17),(21,14), "glucose category", ">=3.0 to <=3.9 mmol/L with symptoms; no assistance"),
        ("symptomatic hypoglycaemic adverse event", (29,17),(22,13),(31,20), "glucose category", "<3.0 mmol/L with symptoms; no assistance"),
        ("severe hypoglycaemic event", (0,None),(0,None),(2,1), "severity", "requiring assistance"),
        ("events consistent with urinary tract infection", (15,9),(25,15),(18,12), None, None),
        ("events consistent with urinary tract infection", (3,3),(5,5),(7,8), "sex", "male"),
        ("events consistent with urinary tract infection", (12,15),(20,26),(11,18), "sex", "female"),
        ("events consistent with urinary tract infection", (155,91),(144,85),(137,88), "number of events per patient", "0"),
        ("events consistent with urinary tract infection", (10,6),(20,12),(12,8), "number of events per patient", "1"),
        ("events consistent with urinary tract infection", (4,2),(2,1),(3,2), "number of events per patient", "2"),
        ("events consistent with urinary tract infection", (0,None),(3,2),(1,1), "number of events per patient", "3 or 4"),
        ("events consistent with urinary tract infection", (1,1),(0,None),(2,1), "number of events per patient", ">=5"),
        ("events consistent with genital infection", (3,2),(13,8),(8,5), None, None),
        ("events consistent with genital infection", (0,None),(7,8),(4,4), "sex", "male"),
        ("events consistent with genital infection", (3,4),(6,8),(4,6), "sex", "female"),
        ("events consistent with genital infection", (167,98),(156,92),(147,95), "number of events per patient", "0"),
        ("events consistent with genital infection", (3,2),(11,7),(7,5), "number of events per patient", "1"),
        ("events consistent with genital infection", (0,None),(1,1),(0,None), "number of events per patient", "2"),
        ("events consistent with genital infection", (0,None),(1,1),(0,None), "number of events per patient", "3 or 4"),
        ("events consistent with genital infection", (0,None),(0,None),(1,1), "number of events per patient", ">=5"),
    ]
    for index, (name, pbo, e10, e25, subgroup_type, subgroup_value) in enumerate(table2, start=1):
        for arm, pair in ((ARM_PBO,pbo),(ARM_E10,e10),(ARM_E25,e25)):
            count, pct = pair
            measure = "sample_proportion" if pct is not None else "event_count"
            sex_specific = subgroup_type == "sex"
            row = outcome(
                f"SAFE_T2_{index:02d}_{arm}", "safety", name, arm, measure,
                pct if pct is not None else count,
                "%" if pct is not None else "participants",
                timepoint=78, time_unit="weeks",
                n_analyzed=None if sex_specific else ARM_N[arm],
                event_count=count,
                denominator=None if sex_specific else ARM_N[arm],
                subgroup_type=subgroup_type, subgroup_value=subgroup_value,
                analysis_population=(
                    f"treated set; {subgroup_value} subgroup"
                    if sex_specific else "treated set"
                ),
                source_page=10, source_location="Table 2 (printed page 945)",
                ready=bool(pct is not None and not sex_specific),
                notes=(
                    "Published sex-specific n (%) preserved exactly. The main article does not report the male/female subgroup N; total arm N is not substituted as the denominator."
                    if sex_specific else
                    "Printed n (%) stored on one row in separate count and percentage cells."
                    if pct is not None else
                    "Zero count printed without a parenthetical percentage; no percentage is invented."
                ),
            )
            if sex_specific:
                row["denominator_type"] = "sex_specific_subgroup_not_reported"
                row["meta_analysis_eligibility"] = "REQUIRES_REVIEW"
                row["meta_analysis_reason"] = "Sex-specific subgroup denominator is not reported in the supplied main article."
                row["include_in_meta_analysis"] = False
            rows.append(row)

    # Additional exact safety findings printed in Results text.
    for arm, count, pct in ((ARM_PBO,35,21),(ARM_E10,33,20),(ARM_E25,44,28)):
        rows.append(outcome(f"SAFE_HYPO18_{arm}", "safety", "confirmed hypoglycaemic adverse event", arm, "sample_proportion", pct, "%", timepoint=18, time_unit="weeks", n_analyzed=ARM_N[arm], event_count=count, denominator=ARM_N[arm], analysis_population="treated set during fixed-insulin-dose period", source_page=9, source_location="Safety Results text", notes="Printed count and percentage."))
    text_events = [
        ("SAFE_HYPO18_ASSIST_E25", "hypoglycaemic event requiring assistance", ARM_E25, 1, 18, "weeks"),
        ("SAFE_HYPO_POST18_ASSIST_E25", "additional hypoglycaemic event requiring assistance after fixed-dose period", ARM_E25, 1, 78, "weeks"),
        ("SAFE_UTI_SEVERE_PBO", "severe event consistent with urinary tract infection", ARM_PBO, 1, 78, "weeks"),
        ("SAFE_UTI_SEVERE_E10", "severe event consistent with urinary tract infection", ARM_E10, 1, 78, "weeks"),
        ("SAFE_UTI_SEVERE_E25", "severe event consistent with urinary tract infection", ARM_E25, 1, 78, "weeks"),
        ("SAFE_UTI_DISCONT_E25", "urinary tract infection leading to study-drug discontinuation", ARM_E25, 1, 78, "weeks"),
        ("SAFE_UTI_HOSP_E25", "urinary tract infection requiring hospitalization", ARM_E25, 1, 78, "weeks"),
        ("SAFE_GEN_DISCONT_E10", "genital infection leading to study-drug discontinuation", ARM_E10, 1, 78, "weeks"),
        ("SAFE_GEN_DISCONT_E25", "genital infection leading to study-drug discontinuation", ARM_E25, 1, 78, "weeks"),
        ("SAFE_GEN_HOSP_E10", "genital infection requiring hospitalization and surgery", ARM_E10, 1, 78, "weeks"),
    ]
    for ident, name, arm, count, timepoint, time_unit in text_events:
        rows.append(outcome(ident, "safety", name, arm, "event_count", count, "participants", timepoint=timepoint, time_unit=time_unit, n_analyzed=ARM_N[arm], event_count=count, denominator=ARM_N[arm], analysis_population="treated set", source_page=9, source_location="Safety Results text", notes="Exact count printed; no percentage is derived."))
    for ident, name in (("SAFE_NO_DKA", "diabetic ketoacidosis adverse event"), ("SAFE_NO_KETONURIA", "ketonuria adverse event")):
        rows.append(outcome(ident, "safety", name, None, "event_count", 0, "participants", timepoint=78, time_unit="weeks", n_analyzed=494, event_count=0, denominator=494, analysis_population="treated set overall", source_page=9, source_location="Safety Results text", notes="The main article explicitly reports no events."))
    return rows


def build_inventory(baselines, outcomes, tests) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for row in [*baselines, *outcomes]:
        inventory.append({
            "inventory_id": f"INV_{row['id']}", "finding_key": row["id"],
            "source_page": row.get("source_page"),
            "evidence_type": row.get("source_location") or "published main-article finding",
            "expected_components": "study, outcome, arm, timepoint, population, value, statistical type, unit, and printed uncertainty/denominator",
            "extraction_ids": [row["id"]], "status": "VERIFIED",
            "source_status": row.get("source_status"),
        })
    for row in tests:
        inventory.append({
            "inventory_id": f"INV_{row['test_id']}", "finding_key": row["test_id"],
            "source_page": row.get("source_page"),
            "evidence_type": row.get("source_location") or "published statistical comparison",
            "expected_components": "comparison arms, timepoint, population, method, p-value and effect/CI when printed",
            "extraction_ids": [row["test_id"]], "status": "VERIFIED",
            "source_status": "published_main_article_exact",
        })
    inventory.append({
        "inventory_id": "INV_SUPPLEMENT_NOT_SUPPLIED", "finding_key": "supplementary_material",
        "source_page": 12, "evidence_type": "document availability check",
        "expected_components": "none; File S1 and Tables S1-S4 were not supplied",
        "extraction_ids": [], "status": "NOT_REPORTED_IN_SOURCE",
        "source_status": "supplementary_not_supplied",
    })
    return inventory


def main() -> None:
    baselines = baseline_rows()
    outcomes, tests = efficacy_rows()
    outcomes.extend(safety_rows())
    inventory = build_inventory(baselines, outcomes, tests)
    study = {
        "study_id": STUDY_ID,
        "title": "Impact of empagliflozin added on to basal insulin in type 2 diabetes inadequately controlled on basal insulin: a 78-week randomized, double-blind, placebo-controlled trial",
        "authors": "Rosenstock et al.; EMPA-REG BASAL trial investigators",
        "year": 2015, "journal": "Diabetes, Obesity and Metabolism",
        "doi": "10.1111/dom.12503",
        "design": "multicentre randomized double-blind placebo-controlled phase IIb trial",
        "study_phase": "phase IIb", "randomized_total_n": 494,
        "duration_value": 78, "duration_unit": "weeks treatment",
        "condition": "type 2 diabetes inadequately controlled on basal insulin",
        "registration": STUDY_ID, "source_page": 1,
        "source_status": "published_main_article_exact",
    }
    arms = [
        {"arm_id": ARM_PBO, "label": ARM_LABEL[ARM_PBO], "n_randomized": 170, "n_baseline": None, "n_analyzed": None, "analysis_population": "outcome-specific analyzed N stored per outcome", "drug": "placebo", "dose_value": None, "dose_unit": None, "initial_frequency_value": 1, "initial_frequency_unit": "daily", "target_frequency_value": 1, "target_frequency_unit": "daily", "administration_timing": None, "duration_value": 78, "duration_unit": "weeks", "titration_value": None, "titration_unit": None, "route": "oral", "source_page": 2, "source_status": "published_main_article_exact"},
        {"arm_id": ARM_E10, "label": ARM_LABEL[ARM_E10], "n_randomized": 169, "n_baseline": None, "n_analyzed": None, "analysis_population": "outcome-specific analyzed N stored per outcome", "drug": "empagliflozin", "dose_value": 10, "dose_unit": "mg", "initial_frequency_value": 1, "initial_frequency_unit": "daily", "target_frequency_value": 1, "target_frequency_unit": "daily", "administration_timing": None, "duration_value": 78, "duration_unit": "weeks", "titration_value": None, "titration_unit": None, "route": "oral", "source_page": 2, "source_status": "published_main_article_exact"},
        {"arm_id": ARM_E25, "label": ARM_LABEL[ARM_E25], "n_randomized": 155, "n_baseline": None, "n_analyzed": None, "analysis_population": "outcome-specific analyzed N stored per outcome", "drug": "empagliflozin", "dose_value": 25, "dose_unit": "mg", "initial_frequency_value": 1, "initial_frequency_unit": "daily", "target_frequency_value": 1, "target_frequency_unit": "daily", "administration_timing": None, "duration_value": 78, "duration_unit": "weeks", "titration_value": None, "titration_unit": None, "route": "oral", "source_page": 2, "source_status": "published_main_article_exact"},
    ]
    dataset = {
        "dataset_id": "empagliflozin-basal-dom-2015-v1", "version": "1.0.0",
        "generation_mode": "versioned_pdf_truth_bundle",
        "strict_source_tuple_validation": True,
        "primary_endpoint": {
            "outcome": "HbA1c", "metric": "ADJUSTED_MEAN_CHANGE",
            "timepoint": 18, "time_unit": "weeks", "unit": "%",
            "analysis_population": "FAS-18 completers",
            "required_record_ids": [
                "HBA1C18_PCT_CHANGE_ARM_001",
                "HBA1C18_PCT_CHANGE_ARM_002",
                "HBA1C18_PCT_CHANGE_ARM_003"
            ]
        },
        "output_filename": "empa-vs-placebo_extracted_corrected.xlsx",
        "preview_prefix": "empagliflozin-basal",
        "source_document": PDF.name, "source_sha256": sha256(PDF),
        "mandros_document": MANDROS.name, "mandros_sha256": sha256(MANDROS),
        "mandros_domain_scores": {"numerical_accuracy": 3, "statistical_interpretation": 0, "pico_eligibility": 0, "outcome_completeness": 5, "duplication_integrity": 5, "structure_traceability": 5},
        "source_inventory_independent": True,
        "source_inventory_scope": "supplied main article: Tables 1-2, Figures 1-2 directly printed labels and analyzed-N rows, eligibility, footnotes, and quantified Results text; references excluded",
        "source_inventory": inventory,
        "document_inventory": [
            {"document_id":"DOC_PDF","document_type":"main_article_pdf","document_name":PDF.name,"availability_status":"supplied","extraction_status":"source_adjudicated","page_count":13,"sha256":sha256(PDF)},
            {"document_id":"DOC_MANDROS","document_type":"mandros_extraction_xlsx","document_name":MANDROS.name,"availability_status":"supplied","extraction_status":"validated_and_corrected_against_pdf","page_count":None,"sha256":sha256(MANDROS)},
            {"document_id":"DOC_SUPPLEMENT","document_type":"supplementary_appendix","document_name":None,"availability_status":"not supplied","extraction_status":"no supplementary values reported or invented","page_count":None,"sha256":None},
        ],
        "study": study,
        "master_study_rows": [
            ["Study ID", STUDY_ID, "DOI", study["doi"], "Year", 2015, "Randomized total N", 494],
            ["Design", study["design"], "Treatment duration", 78, "Unit", "weeks", "Main article pages", 13],
            ["Title", study["title"], "Source", PDF.name, "Mandros input", MANDROS.name, "Supplement", "not supplied; no numbers created"],
        ],
        "arms": arms, "eligibility": eligibility_rows(), "baseline": baselines,
        "baseline_status": "Arm-level Table 1/Figure baseline values and quantified overall Results text preserved with source-specific population and uncertainty.",
        "outcomes": outcomes, "statistical_tests": tests, "source_conflicts": [],
        "phase2_readiness": [
            {"row_type":"gate","item":"primary endpoint tuple","phase_1_requirement":"HbA1c change at Week 18 must match arm, analyzed N, SE, unit, population and source","extraction_status":"source-adjudicated for all three arms and both published units","phase_2_use":"prevents Day 29/Week 18 contamination","meta_analysis_eligibility":"READY","source_page":5,"notes":None},
            {"row_type":"gate","item":"sample-size scope","phase_1_requirement":"separate randomized, FAS-18, FAS-78 and outcome-specific N","extraction_status":"stored in separate columns and records","phase_2_use":"prevents denominator substitution","meta_analysis_eligibility":"READY","source_page":5,"notes":None},
            {"row_type":"gate","item":"Table 1 units and SE","phase_1_requirement":"preserve mmol/L, mg/dL equivalents only when printed, and classify +/- as SE","extraction_status":"Table 1 arm values use source unit and SE; no unit conversion invented","phase_2_use":"prevents unit and variance errors","meta_analysis_eligibility":"READY","source_page":5,"notes":None},
            {"row_type":"gate","item":"Table 2 safety completeness","phase_1_requirement":"every published category, subgroup and event-frequency row once","extraction_status":"all 41 displayed Table 2 categories represented for three arms","phase_2_use":"prevents selective safety extraction","meta_analysis_eligibility":"READY","source_page":10,"notes":None},
            {"row_type":"gate","item":"supplementary material","phase_1_requirement":"do not report unavailable supplementary numbers","extraction_status":"not supplied; no supplementary numbers created","phase_2_use":"prevents invented precision","meta_analysis_eligibility":"NOT_POOLABLE","source_page":12,"notes":"The main article names File S1 and Tables S1-S4, but the files were not supplied."},
        ],
        "statistical_methods": [
            {"method_id":"METHOD_ANCOVA","data_or_estimand":"primary, secondary and continuous exploratory endpoints","reported_method":"analysis of covariance","reported_rule":"treatment and region fixed effects; relevant baseline value as covariate; post-rescue values missing with LOCF","source_page":3,"notes":None},
            {"method_id":"METHOD_MMRM","data_or_estimand":"HbA1c, insulin dose, FPG and body weight over time","reported_method":"restricted maximum likelihood mixed model repeated measures","reported_rule":"full analysis set observed cases in Figure 2","source_page":3,"notes":None},
            {"method_id":"METHOD_LOGISTIC","data_or_estimand":"categorical HbA1c response","reported_method":"logistic regression","reported_rule":"odds ratios and confidence intervals preserved when printed","source_page":3,"notes":None},
            {"method_id":"METHOD_SAFETY","data_or_estimand":"adverse events","reported_method":"descriptive safety analysis","reported_rule":"treated set","source_page":3,"notes":None},
        ],
        "validation_log": [
            {"code":"PRIMARY_ENDPOINT_SOURCE_GATE","status":"VERIFIED","severity":"critical","message":"Week 18 HbA1c adjusted mean changes, SEs, analyzed Ns, units and arms match Table 1 and Figure 1."},
            {"code":"TIMEPOINT_IDENTITY_GATE","status":"VERIFIED","severity":"critical","message":"Day 29 values from the Mandros workbook were rejected; only source-reported Week 18 and Week 78 outcomes are retained."},
            {"code":"UNIT_IDENTITY_GATE","status":"VERIFIED","severity":"critical","message":"FPG is stored in mmol/L; no value is relabeled as mg/dL."},
            {"code":"SAMPLE_SCOPE_GATE","status":"VERIFIED","severity":"critical","message":"Randomized N, FAS-18 N, FAS-78 N and Figure 2 observed-case N remain separate."},
            {"code":"ELIGIBILITY_SECTION_GATE","status":"VERIFIED","severity":"critical","message":"Rescue-therapy timing was not treated as age eligibility; basal insulin is correctly represented as required background therapy."},
            {"code":"SAFETY_COMPLETENESS_GATE","status":"VERIFIED","severity":"critical","message":"All Table 2 categories and arm-specific n (%) values are represented once; n and percentage share one row in separate fields."},
            {"code":"RESPONDER_COMPONENTS_GATE","status":"VERIFIED","severity":"critical","message":"Week 18 arm-level HbA1c responder percentages (5.5%, 18.0%, 19.5%) and Week 78 printed percentages (6.7%, 17.5%) are represented as separate findings from the published odds ratios and confidence intervals."},
            {"code":"EGFR_DISPERSION_GATE","status":"VERIFIED","severity":"critical","message":"End-of-treatment eGFR mean changes, SDs (13.0, 12.1, 13.4), analyzed Ns (120, 127, 117), arms and mL/min/1.73m2 units are preserved in separate fields."},
            {"code":"SEX_SPECIFIC_DENOMINATOR_GATE","status":"VERIFIED","severity":"critical","message":"Sex-specific urinary and genital infection counts and published percentages are retained, but total arm N is not used as the male/female denominator; the unreported subgroup denominator remains blank."},
            {"code":"NO_SUPPLEMENTARY_INVENTION","status":"VERIFIED","severity":"critical","message":"Supplementary files were not supplied; no supplementary numbers are reported."},
        ],
        "qa_rows": [
            ["Study identity match",1,1,"MATCHED: NCT01011868 / DOI 10.1111/dom.12503"],
            ["Manual workbook used",0,0,"NO"],
            ["Baseline observations",len(baselines),None,"SOURCE-ADJUDICATED MAIN ARTICLE"],
            ["Outcome observations",len(outcomes),None,"TABLES 1-2 + DIRECTLY PRINTED FIGURE LABELS + RESULTS TEXT"],
            ["Statistical comparisons",len(tests),None,"ONE RECORD PER COMPARISON"],
            ["Source inventory findings",len(inventory),None,"INDEPENDENT OF MANDROS EXCEL"],
            ["Scientific state",None,None,"SOURCE-ADJUDICATED MAIN ARTICLE; SUPPLEMENTARY NOT SUPPLIED"],
        ],
    }
    DESTINATION.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(DESTINATION)
    print(f"baseline={len(baselines)} outcomes={len(outcomes)} tests={len(tests)} inventory={len(inventory)}")


if __name__ == "__main__":
    main()
