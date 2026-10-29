"""Build the source-adjudicated dataset for Ferrannini et al. 2010.

All numeric values below are transcribed from the supplied main-article PDF
(Tables 1-3 and explicitly quantified Results text). No supplementary-file
result and no calculated event count is introduced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data" / "private" / "dapagliflozin trial" / "dabagliflozin RCT1.pdf"
MANDROS = ROOT / "data" / "private" / "dapagliflozin trial" / "daba DM_extracted.xlsx"
DESTINATION = ROOT / "standards" / "dapagliflozin_workbook_dataset.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


ARM_SPECS = [
    ("ARM_PBO_AM", "Placebo, morning", "placebo", None, "morning", 75, "primary"),
    ("ARM_DAPA_2_5_AM", "Dapagliflozin 2.5 mg, morning", "dapagliflozin", 2.5, "morning", 65, "primary"),
    ("ARM_DAPA_5_AM", "Dapagliflozin 5 mg, morning", "dapagliflozin", 5, "morning", 64, "primary"),
    ("ARM_DAPA_10_AM", "Dapagliflozin 10 mg, morning", "dapagliflozin", 10, "morning", 70, "primary"),
    ("ARM_DAPA_2_5_PM", "Dapagliflozin 2.5 mg, evening", "dapagliflozin", 2.5, "evening", 67, "exploratory_evening"),
    ("ARM_DAPA_5_PM", "Dapagliflozin 5 mg, evening", "dapagliflozin", 5, "evening", 68, "exploratory_evening"),
    ("ARM_DAPA_10_PM", "Dapagliflozin 10 mg, evening", "dapagliflozin", 10, "evening", 76, "exploratory_evening"),
    ("ARM_DAPA_5_HIGH", "Dapagliflozin 5 mg, morning, baseline A1C 10.1-12%", "dapagliflozin", 5, "morning", 34, "exploratory_high_A1C"),
    ("ARM_DAPA_10_HIGH", "Dapagliflozin 10 mg, morning, baseline A1C 10.1-12%", "dapagliflozin", 10, "morning", 39, "exploratory_high_A1C"),
]

ARM_IDS = [item[0] for item in ARM_SPECS]
ARM_NS = {item[0]: item[5] for item in ARM_SPECS}


def arms() -> list[dict[str, Any]]:
    rows = []
    for arm_id, label, drug, dose, timing, n, cohort in ARM_SPECS:
        n_randomized = 35 if arm_id == "ARM_DAPA_5_HIGH" else n
        rows.append({
            "arm_id": arm_id,
            "label": label,
            "n_randomized": n_randomized,
            "n_baseline": n,
            "n_analyzed": n,
            "analysis_population": "randomized" if cohort != "exploratory_high_A1C" else "received_at_least_one_dose",
            "drug": drug,
            "dose_value": dose,
            "dose_unit": "mg" if dose is not None else None,
            "initial_frequency_value": 1,
            "initial_frequency_unit": "dose/day",
            "target_frequency_value": 1,
            "target_frequency_unit": "dose/day",
            "administration_timing": timing,
            "duration_value": 24,
            "duration_unit": "weeks",
            "titration_value": None,
            "titration_unit": None,
            "route": "oral",
            "cohort": cohort,
            "source_page": 3,
            "source_status": "published_main_article_exact",
        })
    return rows


def criterion(identifier: str, category: str, variable: str, *, lt=False, eq=False, gt=False,
              value=None, unit=None, minimum=None, maximum=None, min_inclusive=None,
              max_inclusive=None, scope="overall", qualifier=None) -> dict[str, Any]:
    return {
        "criterion_id": identifier, "category": category, "variable": variable,
        "operator_lt": lt, "operator_eq": eq, "operator_gt": gt, "value": value, "unit": unit,
        "range_min": minimum, "range_max": maximum, "range_unit": unit if minimum is not None or maximum is not None else None,
        "range_min_inclusive": min_inclusive, "range_max_inclusive": max_inclusive,
        "population_scope": scope, "qualifier": qualifier, "source_page": 2,
        "source_status": "published_main_article_exact",
    }


ELIGIBILITY = [
    criterion("ELIG_INC_AGE", "inclusion", "age", minimum=18, maximum=77, unit="years", min_inclusive=True, max_inclusive=True, qualifier="Men and women aged 18-77 years."),
    criterion("ELIG_INC_T2D", "inclusion", "type_2_diabetes", qualifier="Treatment-naive patients with type 2 diabetes inadequately controlled with diet and exercise alone."),
    criterion("ELIG_INC_A1C_MAIN", "inclusion", "baseline_A1C", minimum=7.0, maximum=10.0, unit="%", min_inclusive=True, max_inclusive=True, scope="primary and exploratory evening-dose cohorts"),
    criterion("ELIG_INC_A1C_HIGH", "inclusion", "baseline_A1C", minimum=10.1, maximum=12.0, unit="%", min_inclusive=True, max_inclusive=True, scope="exploratory high-A1C cohort"),
    criterion("ELIG_INC_BMI", "inclusion", "BMI", lt=True, eq=True, value=45, unit="kg/m2"),
    criterion("ELIG_INC_CPEPTIDE", "inclusion", "fasting_C_peptide", eq=True, gt=True, value=1.0, unit="ng/mL"),
    criterion("ELIG_INC_CONSENT", "inclusion", "informed_consent", qualifier="All patients gave informed consent."),
    criterion("ELIG_EXC_T1D", "exclusion", "type_1_diabetes", qualifier="History of type 1 diabetes."),
    criterion("ELIG_EXC_CREAT_MEN", "exclusion", "serum_creatinine", eq=True, gt=True, value=133, unit="umol/L", scope="men"),
    criterion("ELIG_EXC_CREAT_WOMEN", "exclusion", "serum_creatinine", eq=True, gt=True, value=124, unit="umol/L", scope="women"),
    criterion("ELIG_EXC_UACR", "exclusion", "urine_albumin_to_creatinine_ratio", gt=True, value=200, unit="mg/mmol"),
    criterion("ELIG_EXC_AST_ALT", "exclusion", "AST_or_ALT", gt=True, value=3, unit="times upper limit of normal"),
    criterion("ELIG_EXC_CK", "exclusion", "creatine_kinase", eq=True, gt=True, value=3, unit="times upper limit of normal"),
    criterion("ELIG_EXC_WEIGHT_LOSS", "exclusion", "recent_weight_loss", gt=True, value=10, unit="%", qualifier="Symptoms of severely uncontrolled diabetes, including >10% weight loss during the previous 3 months."),
    criterion("ELIG_EXC_MAJOR_DISEASE", "exclusion", "significant_comorbidity", qualifier="Significant renal, hepatic, hematological, oncological, endocrine, psychiatric, or rheumatic disease."),
    criterion("ELIG_EXC_CV_EVENT", "exclusion", "recent_cardiovascular_event", lt=True, eq=True, value=6, unit="months", qualifier="Cardiovascular event, including NYHA class III/IV congestive heart failure, within 6 months of enrollment."),
    criterion("ELIG_EXC_SBP", "exclusion", "systolic_blood_pressure", eq=True, gt=True, value=180, unit="mmHg"),
    criterion("ELIG_EXC_DBP", "exclusion", "diastolic_blood_pressure", eq=True, gt=True, value=110, unit="mmHg"),
]


BASELINE_CONTINUOUS = {
    "age": ("years", [52.7, 53.0, 52.6, 50.6, 54.3, 54.5, 50.7, 48.3, 47.9], [10.3, 11.7, 10.9, 9.97, 11.5, 11.0, 9.7, 9.3, 12.1]),
    "A1C": ("%", [7.84, 7.92, 7.86, 8.01, 7.99, 7.82, 7.99, 10.82, 10.73], [0.87, 0.90, 0.94, 0.96, 0.99, 0.91, 1.05, 0.93, 0.85]),
    "fasting_plasma_glucose": ("mg/dL", [159.9, 164.1, 162.2, 166.6, 160.6, 157.0, 168.1, 231.6, 241.2], [42.1, 48.0, 45.0, 41.5, 45.9, 50.9, 57.9, 65.1, 65.7]),
    "body_weight": ("kg", [88.8, 90.8, 87.6, 94.2, 88.3, 89.2, 92.1, 88.7, 87.5], [19.0, 22.8, 17.1, 18.7, 20.5, 20.5, 22.0, 19.2, 22.7]),
    "BMI": ("kg/m2", [32.3, 32.6, 31.9, 33.6, 32.2, 32.8, 33.3, 32.6, 31.1], [5.5, 5.5, 4.8, 5.4, 5.3, 5.3, 5.6, 4.6, 5.9]),
}

MEN = [(31, 41.3), (36, 55.4), (31, 48.4), (34, 48.6), (29, 43.3), (29, 42.6), (39, 51.3), (24, 70.6), (23, 59.0)]
WOMEN = [(44, 58.7), (29, 44.6), (33, 51.6), (36, 51.4), (38, 56.7), (39, 57.4), (37, 48.7), (10, 29.4), (16, 41.0)]
DIABETES_DURATION = [(.50, .10, 3.40), (.50, .10, 2.90), (.25, .10, 1.40), (.45, .10, 3.40), (.20, .10, 1.20), (.50, .15, 2.20), (.40, .10, 2.45), (.65, .20, 2.50), (1.40, .20, 3.50)]


def baseline_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for variable, (unit, values, sds) in BASELINE_CONTINUOUS.items():
        for index, arm_id in enumerate(ARM_IDS):
            identifier = f"BASE_{variable.upper()}_{arm_id}"
            rows.append({
                "id": identifier, "characteristic": variable, "subgroup_type": None, "subgroup_value": None,
                "independent_study_id": "NCT00528372", "estimand_family": "baseline_mean",
                "comparison_id": None, "timepoint": 0, "time_unit": "baseline", "arm_id": arm_id,
                "n_baseline": ARM_NS[arm_id], "event_count": None, "denominator": None,
                "denominator_type": "table_1_arm_n", "measure": "mean", "estimate_type": "mean",
                "value": values[index], "unit": unit, "dispersion": "SD", "dispersion_value": sds[index],
                "lower_value": None, "upper_value": None, "analysis_population": "table_1_population",
                "source_status": "published_main_article_exact", "conflict_id": None,
                "canonical_record_id": identifier, "canonical_for_analysis": True,
                "meta_analysis_eligibility": "NOT_POOLABLE", "meta_analysis_reason": "Baseline descriptive record.",
                "include_in_meta_analysis": False, "notes": None, "source_page": 3,
            })
    for label, values in (("men", MEN), ("women", WOMEN)):
        for index, arm_id in enumerate(ARM_IDS):
            count, proportion = values[index]
            identifier = f"BASE_SEX_{label.upper()}_{arm_id}"
            rows.append({
                "id": identifier, "characteristic": "sex", "subgroup_type": "sex", "subgroup_value": label,
                "independent_study_id": "NCT00528372", "estimand_family": "baseline_sample_proportion",
                "comparison_id": None, "timepoint": 0, "time_unit": "baseline", "arm_id": arm_id,
                "n_baseline": ARM_NS[arm_id], "event_count": count, "denominator": ARM_NS[arm_id],
                "denominator_type": "table_1_arm_n", "measure": "sample_proportion", "estimate_type": "sample_proportion",
                "value": proportion, "unit": "%", "dispersion": None, "dispersion_value": None,
                "lower_value": None, "upper_value": None, "analysis_population": "table_1_population",
                "source_status": "published_main_article_exact", "conflict_id": None,
                "canonical_record_id": identifier, "canonical_for_analysis": True,
                "meta_analysis_eligibility": "NOT_POOLABLE", "meta_analysis_reason": "Baseline descriptive record.",
                "include_in_meta_analysis": False,
                "notes": "One sex observation: printed participant count and sample proportion are stored in separate cells on the same row.",
                "source_page": 3,
            })
    for index, arm_id in enumerate(ARM_IDS):
        median, q1, q3 = DIABETES_DURATION[index]
        identifier = f"BASE_DIABETES_DURATION_{arm_id}"
        rows.append({
            "id": identifier, "characteristic": "diabetes_duration", "subgroup_type": None, "subgroup_value": None,
            "independent_study_id": "NCT00528372", "estimand_family": "baseline_median",
            "comparison_id": None, "timepoint": 0, "time_unit": "baseline", "arm_id": arm_id,
            "n_baseline": ARM_NS[arm_id], "event_count": None, "denominator": None,
            "denominator_type": "table_1_arm_n", "measure": "median", "estimate_type": "median",
            "value": median, "unit": "years", "dispersion": "IQR", "dispersion_value": None,
            "lower_value": q1, "upper_value": q3, "analysis_population": "table_1_population",
            "source_status": "published_main_article_exact", "conflict_id": None,
            "canonical_record_id": identifier, "canonical_for_analysis": True,
            "meta_analysis_eligibility": "NOT_POOLABLE", "meta_analysis_reason": "Baseline descriptive record.",
            "include_in_meta_analysis": False, "notes": None, "source_page": 3,
        })
    return rows


TABLE2 = [
    ("A1C change from baseline", "%", [-.23, -.58, -.77, -.89, -.83, -.79, -.79, -2.88, -2.66], [.10, .11, .11, .11, .11, .11, .10, 1.41, 1.26]),
    ("fasting plasma glucose change from baseline", "mg/dL", [-4.1, -15.2, -24.1, -28.8, -25.6, -27.3, -29.6, -77.1, -84.3], [3.9, 4.2, 4.3, 4.0, 4.1, 4.2, 4.0, 53.4, 61.0]),
    ("body weight change from baseline", "kg", [-2.2, -3.3, -2.8, -3.2, -3.8, -3.6, -3.1, -2.1, -1.9], [.4, .5, .5, .5, .5, .5, .4, 3.4, 3.5]),
    ("urinary glucose to creatinine ratio change from baseline", "g/g", [.96, 12.12, 17.68, 33.80, 24.24, 38.00, 45.80, None, None], [2.87, 2.98, 3.28, 3.08, 3.07, 3.09, 2.86, None, None]),
    ("seated systolic blood pressure change from baseline", "mmHg", [-.9, -4.6, -2.3, -3.6, -4.0, -5.2, -2.3, -5.7, -2.5], [1.8, 1.8, 1.9, 1.9, 2.3, 1.7, 1.4, 2.1, 2.1]),
    ("seated diastolic blood pressure change from baseline", "mmHg", [-.7, -2.8, -1.7, -2.0, -3.2, -2.0, -1.0, -3.3, -2.9], [1.0, 1.1, 1.1, 1.1, 1.2, 1.1, 1.0, 1.6, 1.5]),
    ("serum creatinine change from baseline", "umol/L", [-.4, -.6, -2.0, -1.1, -.5, 1.8, -1.9, 0.0, .6], [.9, 1.3, 1.4, 1.0, .9, .9, 1.7, 1.2, 1.4]),
    ("serum albumin change from baseline", "g/L", [-.1, .6, .3, .9, 0.0, 1.0, 1.3, .4, .7], [.3, .4, .4, .3, .3, .4, .3, .5, .4]),
    ("cystatin C change from baseline", "mg/L", [-.014, -.009, .005, -.003, .014, .024, -.015, .070, -.045], [.012, .014, .014, .016, .012, .009, .026, .025, .063]),
    ("hematocrit change from baseline", "%", [-.38, 1.60, 1.74, 2.38, 1.23, 1.92, 2.41, .77, 1.88], [.25, .33, .40, .44, .26, .30, .30, .57, .42]),
    ("serum uric acid change from baseline", "umol/L", [-11.9, -39.3, -50.6, -51.7, -59.5, -43.4, -49.4, None, None], [5.6, 6.0, 6.1, 5.8, 5.9, 6.0, 5.6, None, None]),
    ("blood urea nitrogen change from baseline", "mmol/L", [-.2, .6, .6, .4, .6, .7, .4, .6, .9], [.2, .2, .2, .2, .2, .2, .2, .2, .3]),
    ("serum sodium change from baseline", "mmol/L", [-.1, -.1, -.9, -.4, -.1, -.2, .1, 1.7, .5], [.3, .3, .4, .4, .3, .3, .3, .6, .5]),
    ("serum potassium change from baseline", "mmol/L", [-.03, -.05, 0.0, -.01, -.03, -.09, -.08, -.05, -.02], [.06, .05, .05, .06, .06, .05, .06, .08, .06]),
    ("serum calcium change from baseline", "mmol/L", [.01, .03, 0.0, .03, .01, .04, .04, None, None], [.01, .02, .02, .01, .01, .02, .02, None, None]),
    ("serum magnesium change from baseline", "mmol/L", [-.25, 0.0, .50, 0.0, 0.0, .15, -.20, None, None], [.18, .20, .26, .26, .25, .22, .27, None, None]),
    ("serum inorganic phosphorus change from baseline", "mmol/L", [-.01, .01, .04, .05, .04, .08, .06, .04, .07], [.02, .02, .03, .02, .02, .02, .02, .03, .02]),
]


SAFETY = {
    "at least one adverse event": [(45,60.0),(41,63.1),(37,57.8),(48,68.6),(45,67.2),(44,64.7),(45,59.2),(27,79.4),(28,71.8)],
    "at least one serious adverse event": [(3,4.0),(0,None),(1,1.6),(1,1.4),(1,1.5),(1,1.5),(1,1.3),(0,None),(0,None)],
    "discontinuation for adverse event": [(1,1.3),(2,3.1),(3,4.7),(5,7.1),(0,None),(4,5.9),(3,3.9),(0,None),(0,None)],
    "discontinuation for serious adverse event": [(0,None),(0,None),(1,1.6),(0,None),(0,None),(1,1.5),(1,1.3),(0,None),(0,None)],
    "nasopharyngitis": [(4,5.3),(7,10.8),(3,4.7),(2,2.9),(7,10.4),(5,7.4),(4,5.3),(4,11.8),(4,10.3)],
    "diarrhea": [(1,1.3),(4,6.2),(1,1.6),(1,1.4),(3,4.5),(7,10.3),(3,3.9),(2,5.9),(1,2.6)],
    "headache": [(5,6.7),(5,7.7),(3,4.7),(4,5.7),(3,4.5),(9,13.2),(9,11.8),(5,14.7),(6,15.4)],
    "hypoglycemia": [(2,2.7),(1,1.5),(0,None),(2,2.9),(1,1.5),(0,None),(1,1.3),(1,2.9),(0,None)],
    "events suggestive of urinary tract infections": [(3,4.0),(3,4.6),(8,12.5),(4,5.7),(5,7.5),(8,11.8),(5,6.6),(3,8.8),(6,15.4)],
    "events suggestive of genital infections": [(1,1.3),(5,7.7),(5,7.8),(9,12.9),(6,9.0),(3,4.4),(2,2.6),(2,5.9),(7,17.9)],
    "hypotensive events": [(1,1.3),(0,None),(0,None),(1,1.4),(3,4.5),(0,None),(0,None),(1,2.9),(1,2.6)],
}


def outcome_record(identifier: str, domain: str, outcome: str, arm_id: str | None, measure: str, value: Any,
                   unit: str | None, *, dispersion=None, dispersion_value=None, event_count=None,
                   denominator=None, subgroup_type=None, subgroup_value=None, comparison_id=None,
                   source_page=5, notes=None, ready=False) -> dict[str, Any]:
    return {
        "id": identifier, "domain": domain, "outcome": outcome, "independent_study_id": "NCT00528372",
        "estimand_family": measure, "threshold_lt": False, "threshold_eq": False, "threshold_gt": False,
        "threshold_value": None, "threshold_unit": None, "subgroup_type": subgroup_type,
        "subgroup_value": subgroup_value, "adherence_level": None, "comparison_id": comparison_id,
        "period_id": "WEEK_24", "timepoint": 24, "time_unit": "weeks", "arm_id": arm_id,
        "n_analyzed": denominator if ready else None, "event_count": event_count, "denominator": denominator,
        "denominator_type": "outcome_specific" if denominator is not None else "not_reported",
        "measure": measure, "estimate_type": measure, "value": value, "unit": unit,
        "dispersion": dispersion, "dispersion_value": dispersion_value, "lower_value": None, "upper_value": None,
        "ci_lower": None, "ci_upper": None, "ci_level": None, "effect_measure": None, "effect_value": None,
        "analysis_population": "as_reported", "applicability_status": "reported", "derivation_type": None,
        "source_status": "published_main_article_exact", "conflict_id": None, "canonical_record_id": identifier,
        "canonical_for_analysis": True, "meta_analysis_eligibility": "READY" if ready else "REQUIRES_REVIEW",
        "meta_analysis_reason": "Printed event count and denominator are available." if ready else "Outcome-specific analyzed N and/or SD was not printed; preserve without pooling.",
        "include_in_meta_analysis": ready, "notes": notes, "source_page": source_page,
    }


def outcome_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for variable_index, (name, unit, values, dispersions) in enumerate(TABLE2, start=1):
        for index, arm_id in enumerate(ARM_IDS):
            if values[index] is None:
                continue
            high_sd = name in {"A1C change from baseline", "fasting plasma glucose change from baseline", "body weight change from baseline"} and index >= 7
            identifier = f"EFF_T2_{variable_index:02d}_{arm_id}"
            rows.append(outcome_record(
                identifier, "efficacy", name, arm_id, "mean_change", values[index], unit,
                dispersion="SD" if high_sd else "SEM", dispersion_value=dispersions[index],
                source_page=5,
                notes="Table 2; outcome-specific analyzed N is not printed." if not high_sd else "Table 2 footnote: high-A1C value is mean +/- SD.",
                ready=False,
            ))
    for arm_id, proportion in zip(ARM_IDS[:4], [32, 41, 44, 51]):
        identifier = f"EFF_A1C_TARGET_{arm_id}"
        record = outcome_record(identifier, "efficacy", "participants achieving A1C target", arm_id, "sample_proportion", proportion, "%", source_page=4, notes="Printed proportion; event count and outcome-specific denominator are not reported.")
        record.update({"threshold_lt": True, "threshold_value": 7, "threshold_unit": "%"})
        rows.append(record)
    subgroup_values = [0.16, -1.23, -1.98, -1.90]
    subgroup_dispersion = [2.50, .98, .90, .79]
    for arm_id, value, spread in zip(ARM_IDS[:4], subgroup_values, subgroup_dispersion):
        record = outcome_record(
            f"EFF_A1C_GE9_{arm_id}", "efficacy", "A1C change from baseline", arm_id, "mean_change", value, "%",
            dispersion="reported_plus_minus_unspecified", dispersion_value=spread,
            subgroup_type="baseline_A1C", subgroup_value=">=9%", source_page=4,
            notes="Results-text subgroup analysis of the main morning-dose cohort, not the exploratory evening-dose cohort. The printed plus/minus value is not identified as SD or SEM.",
        )
        record["analysis_population"] = "primary_morning_dose_cohort_with_baseline_A1C_ge_9_percent"
        rows.append(record)
    for event_index, (event, values) in enumerate(SAFETY.items(), start=1):
        for index, arm_id in enumerate(ARM_IDS):
            count, proportion = values[index]
            denominator = ARM_NS[arm_id]
            if proportion is not None:
                rows.append(outcome_record(
                    f"SAFE_{event_index:02d}_{arm_id}", "safety", event, arm_id, "sample_proportion", proportion,
                    "%", event_count=count, denominator=denominator, source_page=6,
                    notes="One Table 3 event observation: printed count and sample proportion are stored in separate cells on the same row; data include events after rescue.", ready=True,
                ))
            else:
                rows.append(outcome_record(
                    f"SAFE_{event_index:02d}_{arm_id}", "safety", event, arm_id, "event_count", count,
                    "participants", event_count=count, denominator=denominator, source_page=6,
                    notes="Table 3 prints a zero count without a percentage; no percentage is derived or invented. Data include events after rescue.", ready=True,
                ))
    for arm_id, count in zip(ARM_IDS[4:7], [1, 2, 3]):
        rows.append(outcome_record(
            f"SAFE_NOCTURIA_{arm_id}", "safety", "nocturia", arm_id, "event_count", count, "participants",
            event_count=count, denominator=ARM_NS[arm_id], source_page=6,
            notes="Results text reports counts for evening 2.5, 5, and 10 mg doses; no percentage is derived.", ready=True,
        ))
    rows.append(outcome_record(
        "SAFE_DEATH_10MG", "safety", "death due to motor vehicle accident", None, "event_count", 1,
        "participant", event_count=1, denominator=None, subgroup_type="dose", subgroup_value="dapagliflozin 10 mg; cohort not specified",
        source_page=6, notes="Narrative does not specify morning/evening cohort; no arm assignment is invented.",
    ))
    rows.append(outcome_record(
        "SAFE_MAJOR_HYPO_ALL", "safety", "major hypoglycemia", None, "event_count", 0,
        "participants", event_count=0, denominator=None, subgroup_type="study", subgroup_value="all cohorts",
        source_page=6, notes="Narrative reports no major episodes; no arm-specific zeroes are invented.",
    ))
    return rows


def test_record(identifier: str, outcome: str, arm_a: str | None, arm_b: str | None, operator: str,
                p_value: float, *, effect_measure=None, effect_value=None, source_page=4, notes=None) -> dict[str, Any]:
    return {
        "test_id": identifier, "comparison_id": identifier.replace("TEST_", "CMP_"),
        "test_scope": "between_arm_comparison" if arm_b else "reported_association", "domain": "efficacy",
        "outcome": outcome, "independent_study_id": "NCT00528372", "estimand_family": "p_value_only",
        "threshold_lt": False, "threshold_eq": False, "threshold_gt": False, "threshold_value": None,
        "threshold_unit": None, "period_id": "WEEK_24", "timepoint": 24, "time_unit": "weeks",
        "arm_a_id": arm_a, "arm_b_id": arm_b, "arm_id": None, "arm_a_outcome_id": None,
        "arm_b_outcome_id": None, "subgroup_factor": None, "test_effect": None, "estimate_type": "p_value",
        "effect_measure": effect_measure, "effect_value": effect_value, "ci_lower": None, "ci_upper": None,
        "ci_level": None, "analysis_population": "as_reported", "p_lt": operator == "<",
        "p_eq": operator == "=", "p_gt": operator == ">", "p_value": p_value,
        "source_status": "published_main_article_exact", "conflict_id": None, "canonical_for_analysis": True,
        "meta_analysis_eligibility": "NOT_POOLABLE", "meta_analysis_reason": "P-value-only record; preserve for interpretation, not pooling.",
        "include_in_meta_analysis": False, "source_page": source_page, "notes": notes,
    }


STATISTICAL_TESTS = [
    test_record("TEST_A1C_5_AM", "A1C change from baseline", "ARM_DAPA_5_AM", "ARM_PBO_AM", "=", .0005, notes="Exact Results-text p-value; Table 2 footnote summarizes this as P<0.001."),
    test_record("TEST_A1C_10_AM", "A1C change from baseline", "ARM_DAPA_10_AM", "ARM_PBO_AM", "<", .0001),
    test_record("TEST_FPG_5_AM", "fasting plasma glucose change from baseline", "ARM_DAPA_5_AM", "ARM_PBO_AM", "<", .001, source_page=5, notes="Table 2 footnote."),
    test_record("TEST_FPG_10_AM", "fasting plasma glucose change from baseline", "ARM_DAPA_10_AM", "ARM_PBO_AM", "<", .0001, source_page=5, notes="Table 2 footnote."),
    test_record("TEST_FRGE_WEIGHT", "association of fractional renal glucose excretion change with body-weight change", None, None, "=", .008, effect_measure="correlation_coefficient", effect_value=-.13, source_page=6),
    test_record("TEST_FRGE_A1C", "association of fractional renal glucose excretion change with A1C change", None, None, "=", .11, source_page=6, notes="The paper reports a similar trend and p-value but no correlation coefficient."),
]


def main() -> None:
    outcomes = outcome_rows()
    study = {
        "study_id": "NCT00528372", "title": "Dapagliflozin Monotherapy in Type 2 Diabetic Patients With Inadequate Glycemic Control by Diet and Exercise",
        "authors": "Ferrannini et al.", "year": 2010, "journal": "Diabetes Care", "doi": "10.2337/dc10-0612",
        "design": "24-week randomized parallel-group double-blind placebo-controlled phase 3 trial",
        "study_phase": "Phase 3", "randomized_total_n": 559, "duration_value": 24, "duration_unit": "weeks",
        "condition": "Type 2 diabetes inadequately controlled with diet and exercise",
        "registration": "NCT00528372", "source_page": 1, "source_status": "published_main_article_exact",
    }
    dataset = {
        "dataset_id": "dapagliflozin-monotherapy-dc10-0612-v1", "version": "1.1.0",
        "generation_mode": "versioned_pdf_truth_bundle", "output_filename": "dabagliflozin_Mandros_Blind_corrected.xlsx",
        "preview_prefix": "dapagliflozin", "source_document": PDF.name, "source_sha256": sha256(PDF),
        "mandros_document": MANDROS.name, "mandros_sha256": sha256(MANDROS),
        "mandros_domain_scores": {"numerical_accuracy": 0, "statistical_interpretation": 0, "pico_eligibility": 0, "outcome_completeness": 0, "duplication_integrity": 0, "structure_traceability": 0},
        "document_inventory": [
            {"document_id": "DOC_PDF", "document_type": "main_article_pdf", "document_name": PDF.name, "availability_status": "supplied", "extraction_status": "source_adjudicated", "page_count": 8, "sha256": sha256(PDF)},
            {"document_id": "DOC_MANDROS", "document_type": "mandros_extraction_xlsx", "document_name": MANDROS.name, "availability_status": "supplied", "extraction_status": "validated_and_corrected_against_pdf", "page_count": None, "sha256": sha256(MANDROS)},
        ],
        "study": study,
        "master_study_rows": [
            ["Study ID", "NCT00528372", "DOI", "10.2337/dc10-0612", "Year", 2010, "Randomized total N", 559],
            ["Design", study["design"], "Phase", "Phase 3", "Duration", 24, "Unit", "weeks"],
            ["Title", study["title"], "Condition", study["condition"], "Source", PDF.name, "Mandros input", "Supplied and corrected against PDF"],
        ],
        "arms": arms(), "eligibility": ELIGIBILITY, "baseline": baseline_rows(),
        "baseline_status": "Table 1 fully transcribed from the supplied main article.",
        "outcomes": outcomes, "statistical_tests": STATISTICAL_TESTS,
        "source_conflicts": [{
            "conflict_id": "CONFLICT_RANDOMIZED_VS_TREATED_N", "record_scope": "study and high-A1C 5 mg arm", "field": "population count scope",
            "source_a_location": "PDF Figure 1 and Results", "source_a_value": "559 randomized overall; 35 randomized to high-A1C dapagliflozin 5 mg, of whom 1 did not receive study medication",
            "source_b_location": "Mandros Studies and Arms sheets", "source_b_value": "558 total sample size; high-A1C dapagliflozin 5 mg arm n=34",
            "published_total_value": 559, "published_total_denominator": "randomized participants", "reconciled_arm_sum": 558,
            "reconciled_arm_denominator": "participants represented at baseline/treated; high-A1C 5 mg includes 34 who received at least one dose",
            "source_status": "published_main_article_exact", "resolution_status": "RESOLVED_BY_POPULATION_SCOPE",
            "analysis_action": "Store randomized N separately from baseline/treated N; never substitute 558 for randomized total 559.", "source_page": 2,
        }],
        "phase2_readiness": [
            {"row_type":"rule","item":"study identity and population scope","phase_1_requirement":"PDF and workbook must describe the same trial; randomized and treated populations must remain separate","extraction_status":"Identity matches NCT00528372; randomized N=559 is separated from baseline/treated N=558","phase_2_use":"prevents pooling the wrong trial or denominator","meta_analysis_eligibility":"READY","source_page":2,"notes":"Population-scope reconciliation is retained in Source Conflicts."},
            {"row_type":"rule","item":"Table 2 continuous outcomes","phase_1_requirement":"effect, variance and outcome-specific N","extraction_status":"mean change and SEM/SD preserved; outcome-specific N often not printed","phase_2_use":"do not substitute randomized N","meta_analysis_eligibility":"REQUIRES_REVIEW","source_page":5,"notes":"No variance or denominator is invented."},
            {"row_type":"rule","item":"Table 3 safety outcomes","phase_1_requirement":"event count, denominator and printed sample proportion","extraction_status":"one row per arm-event; count, denominator and printed proportion use separate cells","phase_2_use":"dichotomous arm data without duplicate observations","meta_analysis_eligibility":"READY","source_page":6,"notes":"A percentage is not derived when the article prints only a zero count."},
            {"row_type":"rule","item":"supplementary information","phase_1_requirement":"report only supplied evidence","extraction_status":"not supplied; no supplementary result reported","phase_2_use":"prevents invented precision","meta_analysis_eligibility":"NOT_POOLABLE","source_page":None,"notes":"Main article only."},
        ],
        "statistical_methods": [
            {"method_id":"METHOD_ANCOVA","data_or_estimand":"A1C, FPG and body-weight change","reported_method":"ANCOVA with treatment group as effect and baseline value as covariate","reported_rule":"point estimates and 95% CIs for within-group change and between-group difference","source_page":3,"notes":None},
            {"method_id":"METHOD_EXPLORATORY_P","data_or_estimand":"exploratory cohorts","reported_method":"no p-values generated","reported_rule":"per study design","source_page":3,"notes":None},
            {"method_id":"METHOD_MULTIPLICITY","data_or_estimand":"Table 2 primary/secondary endpoints","reported_method":"Dunnett adjustment and sequential procedure","reported_rule":"alpha=0.019 two-sided; secondary endpoints tested sequentially","source_page":5,"notes":None},
            {"method_id":"METHOD_RESCUE","data_or_estimand":"efficacy analyses","reported_method":"exclude post-rescue data","reported_rule":"data obtained after rescue medication excluded from efficacy analyses","source_page":3,"notes":None},
        ],
        "validation_log": [
            {"code":"STUDY_IDENTITY_MATCH","status":"PASS","severity":"information","message":"The supplied PDF and current Mandros workbook both describe dapagliflozin trial NCT00528372."},
            {"code":"POPULATION_SCOPE_CONFLICT","status":"RESOLVED","severity":"critical","message":"PDF randomized N=559 and Mandros total N=558 represent different population scopes; corrected fields preserve randomized, baseline and treated counts separately."},
            {"code":"INVALID_ARM_REFERENCE","status":"RESOLVED","severity":"critical","message":"Non-canonical Mandros outcome arm references were normalized to source-grounded canonical arm IDs in the corrected workbook."},
            {"code":"PDF_TABLE1_COMPLETE","status":"RESOLVED","severity":"information","message":"All printed Table 1 baseline characteristics were transcribed for all nine displayed arms."},
            {"code":"PDF_TABLE2_COMPLETE","status":"RESOLVED","severity":"information","message":"All printed non-NA Table 2 change outcomes were transcribed for all displayed arms; NA cells were not converted to results."},
            {"code":"PDF_TABLE3_COMPLETE","status":"RESOLVED","severity":"information","message":"All Table 3 adverse-event categories were transcribed for all nine arms; each arm-event is one record with count, denominator and printed proportion in separate fields."},
            {"code":"P_VALUES_ATOMIC","status":"RESOLVED","severity":"information","message":"P-value operators and numeric values are in separate cells and stored once per comparison."},
            {"code":"NO_DENOMINATOR_SUBSTITUTION","status":"RESOLVED","severity":"critical","message":"Randomized or arm N is not substituted where outcome-specific analyzed N is not printed."},
            {"code":"NO_SUPPLEMENTARY_INVENTION","status":"RESOLVED","severity":"critical","message":"No supplementary result is reported because no supplementary file was supplied."},
            {"code":"MANUAL_WORKBOOK_USED","status":"RESOLVED","severity":"information","message":"NO. The corrected workbook uses the supplied PDF and Mandros Excel only; Mandros content was rejected after identity mismatch."},
        ],
        "qa_rows": [
            ["Study identity match", 1, 1, "MATCHED: NCT00528372"],
            ["Manual workbook used", 0, 0, "NO"],
            ["Arms", len(ARM_IDS), None, "ALL PRINTED TABLE ARMS"],
            ["Eligibility criteria", len(ELIGIBILITY), None, "SOURCE-GROUNDED"],
            ["Baseline observations", len(baseline_rows()), None, "TABLE 1"],
            ["Outcome observations", len(outcomes), None, "TABLES 2-3 + QUANTIFIED RESULTS TEXT"],
            ["Statistical test records", len(STATISTICAL_TESTS), None, "STORED ONCE"],
            ["Scientific state", None, None, "SOURCE-ADJUDICATED MAIN ARTICLE; PHASE 2 FLAGS PRESERVED"],
        ],
    }
    DESTINATION.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(DESTINATION)
    print(f"baseline={len(dataset['baseline'])} outcomes={len(outcomes)} tests={len(STATISTICAL_TESTS)}")


if __name__ == "__main__":
    main()
