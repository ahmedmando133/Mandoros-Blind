"""Generate the source-grounded Mandros extraction workbook for Häring et al. 2013 (RCT3)."""

from __future__ import annotations

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pathlib import Path

def create_workbook(output_path: Path) -> None:
    wb = openpyxl.Workbook()
    # remove default sheet
    wb.remove(wb.active)

    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="17324D", end_color="17324D", fill_type="solid")
    data_font = Font(name="Segoe UI", size=9)

    def style_sheet(ws, headers, rows):
        ws.append(headers)
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for row_data in rows:
            ws.append(row_data)

        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = data_font

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    # 1. Studies
    study_headers = [
        "study_id", "title", "authors", "publication_year", "journal", "doi",
        "study_design", "study_phase", "total_sample_size", "duration_value",
        "duration_unit", "condition_studied"
    ]
    study_rows = [
        [
            "RCT_EMPA_METSU_2013",
            "Empagliflozin as Add-on to Metformin Plus Sulfonylurea in Patients With Type 2 Diabetes",
            "Hans-Ulrich Häring, Ludwig Merker, Elke Seewaldt-Becker, Marc Weimer, Thomas Meinicke, Hans J. Woerle, Uli C. Broedl; EMPA-REG METSU trial investigators",
            2013,
            "Diabetes Care",
            "10.2337/dc12-2673",
            "Randomized, double-blind, placebo-controlled trial",
            "Phase 3",
            666,
            24,
            "weeks",
            "Type 2 diabetes mellitus inadequately controlled on metformin plus sulfonylurea"
        ]
    ]
    ws_studies = wb.create_sheet("Studies")
    style_sheet(ws_studies, study_headers, study_rows)

    # 2. Arms
    arm_headers = [
        "arm_id", "study_id", "arm_name", "intervention_type", "drug_name",
        "dose_value", "dose_unit", "frequency_number", "frequency_unit",
        "sample_size_allocated", "sample_size_analyzed", "source_page"
    ]
    arm_rows = [
        ["ARM_PLACEBO", "RCT_EMPA_METSU_2013", "Placebo", "placebo", "Placebo", 0, "mg", 1, "daily", 225, 225, 4],
        ["ARM_EMPA_10MG", "RCT_EMPA_METSU_2013", "Empagliflozin 10 mg", "active_comparator", "Empagliflozin", 10, "mg", 1, "daily", 225, 225, 4],
        ["ARM_EMPA_25MG", "RCT_EMPA_METSU_2013", "Empagliflozin 25 mg", "active_comparator", "Empagliflozin", 25, "mg", 1, "daily", 216, 216, 4],
        ["ARM_EMPA_25MG_OL", "RCT_EMPA_METSU_2013", "Open-label empagliflozin 25 mg", "open_label", "Empagliflozin", 25, "mg", 1, "daily", 101, 101, 4]
    ]
    ws_arms = wb.create_sheet("Arms")
    style_sheet(ws_arms, arm_headers, arm_rows)

    # 3. Eligibility
    elig_headers = [
        "criterion_id", "study_id", "criterion_type", "domain", "criterion_name",
        "min_operator (>=)", "min_value", "max_operator (<=)", "max_value", "unit",
        "less_than (<)", "equal (=)", "greater_than (>)", "between", "value",
        "raw_source_text", "source_page", "variable_role", "applicable_population", "assessment_stage"
    ]
    elig_rows = [
        ["ELIG_001", "RCT_EMPA_METSU_2013", "inclusion", "demographic", "age", ">=", 18, None, None, "years", None, None, None, None, 18, "aged >=18 years", 1, "INCLUSION_CRITERION", "overall", "eligibility_assessment"],
        ["ELIG_002", "RCT_EMPA_METSU_2013", "inclusion", "laboratory", "HbA1c", ">=", 7.0, "<=", 10.0, "%", None, None, None, "7.0-10.0", "7.0-10.0", "inadequately controlled on metformin and sulfonylurea (HbA1c >=7 to <=10%)", 1, "INCLUSION_CRITERION", "overall", "eligibility_assessment"],
        ["ELIG_003", "RCT_EMPA_METSU_2013", "inclusion", "demographic", "BMI", None, None, "<=", 45, "kg/m2", None, None, None, None, 45, "BMI <=45 kg/m2", 2, "INCLUSION_CRITERION", "overall", "eligibility_assessment"],
        ["ELIG_004", "RCT_EMPA_METSU_2013", "inclusion", "treatment", "stable background therapy", None, None, None, None, None, None, None, None, None, "stable dose", "stable dose of metformin (>=1,500 mg/day or maximum tolerated dose) plus sulfonylurea", 2, "INCLUSION_CRITERION", "overall", "eligibility_assessment"],
        ["ELIG_005", "RCT_EMPA_METSU_2013", "exclusion", "renal", "eGFR", None, None, None, None, "mL/min/1.73 m2", "<", None, None, None, 30, "moderate or severe renal impairment (eGFR <30 mL/min/1.73 m2)", 2, "EXCLUSION_CRITERION", "overall", "eligibility_assessment"],
        ["ELIG_006", "RCT_EMPA_METSU_2013", "exclusion", "hepatic", "liver enzymes", None, None, None, None, "ULN", None, None, ">", None, 3, "serum levels of ALT, AST, or alkaline phosphatase >3-fold the ULN", 2, "EXCLUSION_CRITERION", "overall", "eligibility_assessment"],
    ]
    ws_elig = wb.create_sheet("Eligibility")
    style_sheet(ws_elig, elig_headers, elig_rows)

    # 4. Outcomes
    outcome_headers = [
        "outcome_id", "study_id", "arm_id", "race", "gender", "is_baseline",
        "domain", "parameter_name", "statistical_type", "metric_type",
        "Timepoint (value)", "Timepoint (unit)", "sample_size", "analysis_population",
        "mean", "sd", "se", "dispersion_type", "median", "iqr_lower", "iqr_upper",
        "change_value", "change_sd", "ratio", "ratio_ci_lower", "ratio_ci_upper",
        "events", "total", "percentage", "unit", "effect_measure", "effect_value",
        "ci_lower", "ci_upper", "p_value", "is_primary", "source_page", "source_location",
        "raw_source_text", "variable_role", "estimate_type", "original_timepoint_label",
        "assessment_stage", "timepoint_type", "source_evidence", "is_between_group_diff",
        "derivation_type", "digitization_uncertainty"
    ]

    outcomes = []
    oid = 1
    def add_out(**kwargs):
        nonlocal oid
        row = [
            f"OUT_{oid:03d}", "RCT_EMPA_METSU_2013", kwargs.get("arm_id"), kwargs.get("race"), kwargs.get("gender"), kwargs.get("is_baseline", False),
            kwargs.get("domain", "efficacy"), kwargs.get("param", ""), kwargs.get("stat_type", "continuous"), kwargs.get("metric", "mean_sd"),
            kwargs.get("tp_val", 24), kwargs.get("tp_unit", "weeks"), kwargs.get("sample_size"), kwargs.get("pop", "FAS"),
            kwargs.get("mean"), kwargs.get("sd"), kwargs.get("se"), kwargs.get("disp_type", "SD" if "sd" in kwargs else ("SE" if "se" in kwargs else None)),
            kwargs.get("median"), kwargs.get("iqr_lower"), kwargs.get("iqr_upper"),
            kwargs.get("change_val"), kwargs.get("change_sd"), kwargs.get("ratio"), kwargs.get("r_ci_l"), kwargs.get("r_ci_u"),
            kwargs.get("events"), kwargs.get("total"), kwargs.get("pct"), kwargs.get("unit", ""),
            kwargs.get("eff_measure"), kwargs.get("eff_val"), kwargs.get("ci_l"), kwargs.get("ci_u"), kwargs.get("p_val"),
            kwargs.get("is_primary", "NO"), kwargs.get("page", 4), kwargs.get("location", "Table 1, Page 4"),
            kwargs.get("raw_text", ""), kwargs.get("role", "EFFICACY_OUTCOME"), kwargs.get("est_type", "MEAN"),
            kwargs.get("orig_tp", "Week 24"), kwargs.get("stage", "follow_up"), kwargs.get("tp_type", "point_in_time"),
            kwargs.get("evidence", ""), kwargs.get("is_diff", "NO"), kwargs.get("deriv", "directly_reported"), None
        ]
        outcomes.append(row)
        oid += 1

    # --- Baseline Characteristics (Table 1, Page 4) ---
    arms_baseline = [
        ("ARM_PLACEBO", 225, 56.9, 9.2, 76.2, 16.9, 27.9, 4.9, 8.15, 0.83, 8.42, 1.99, 9.46, 1.69, 128.8, 14.3, 78.3, 8.6, 86.9, 20.1),
        ("ARM_EMPA_10MG", 225, 57.0, 9.2, 77.1, 18.3, 28.3, 5.4, 8.07, 0.81, 8.38, 1.82, 9.45, 1.61, 128.7, 13.9, 78.4, 9.6, 86.5, 21.8),
        ("ARM_EMPA_25MG", 216, 57.4, 9.3, 77.5, 18.8, 28.3, 5.5, 8.10, 0.83, 8.69, 1.87, 9.59, 2.10, 129.3, 14.2, 79.0, 8.4, 88.3, 22.6),
        ("ARM_EMPA_25MG_OL", 101, 53.4, 10.5, 76.4, 18.2, 28.7, 5.5, 11.18, 1.25, 11.12, 3.37, 12.94, 3.52, 126.4, 12.4, 78.3, 8.8, 93.1, 23.7),
    ]

    for arm_id, n, age_m, age_sd, wt_m, wt_sd, bmi_m, bmi_sd, hba1c_m, hba1c_sd, fpg_m, fpg_sd, mdg_m, mdg_sd, sbp_m, sbp_sd, dbp_m, dbp_sd, egfr_m, egfr_sd in arms_baseline:
        add_out(arm_id=arm_id, is_baseline=True, domain="demographic", param="Age", mean=age_m, sd=age_sd, unit="years", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"Age (years): {age_m} ({age_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="anthropometric", param="Body weight", mean=wt_m, sd=wt_sd, unit="kg", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"Body weight (kg): {wt_m} ({wt_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="anthropometric", param="BMI", mean=bmi_m, sd=bmi_sd, unit="kg/m2", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"BMI (kg/m2): {bmi_m} ({bmi_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="glycemic", param="HbA1c", mean=hba1c_m, sd=hba1c_sd, unit="%", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"HbA1c (%): {hba1c_m} ({hba1c_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="glycemic", param="FPG", mean=fpg_m, sd=fpg_sd, unit="mmol/L", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"FPG (mmol/L): {fpg_m} ({fpg_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="glycemic", param="MDG", mean=mdg_m, sd=mdg_sd, unit="mmol/L", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"MDG (mmol/L): {mdg_m} ({mdg_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="cardiovascular", param="SBP", mean=sbp_m, sd=sbp_sd, unit="mmHg", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"SBP (mmHg): {sbp_m} ({sbp_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="cardiovascular", param="DBP", mean=dbp_m, sd=dbp_sd, unit="mmHg", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"DBP (mmHg): {dbp_m} ({dbp_sd})")
        add_out(arm_id=arm_id, is_baseline=True, domain="renal", param="eGFR", mean=egfr_m, sd=egfr_sd, unit="mL/min/1.73 m2", sample_size=n, tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"eGFR: {egfr_m} ({egfr_sd})")

    # Sex and Race baseline counts
    sex_baseline = [
        ("ARM_PLACEBO", 112, 113, 225),
        ("ARM_EMPA_10MG", 113, 112, 225),
        ("ARM_EMPA_25MG", 114, 102, 216),
        ("ARM_EMPA_25MG_OL", 54, 47, 101),
    ]
    for arm_id, m_cnt, f_cnt, tot in sex_baseline:
        add_out(arm_id=arm_id, is_baseline=True, gender="Male", domain="demographic", param="Sex: Male", stat_type="dichotomous", metric="count_percentage", events=m_cnt, total=tot, pct=round(m_cnt/tot*100, 1), unit="participants", tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"Male: {m_cnt} ({round(m_cnt/tot*100)}%)")
        add_out(arm_id=arm_id, is_baseline=True, gender="Female", domain="demographic", param="Sex: Female", stat_type="dichotomous", metric="count_percentage", events=f_cnt, total=tot, pct=round(f_cnt/tot*100, 1), unit="participants", tp_val=0, tp_unit="weeks", orig_tp="Baseline", location="Table 1, Page 4", raw_text=f"Female: {f_cnt} ({round(f_cnt/tot*100)}%)")

    # --- Primary & Secondary Efficacy Endpoints (Page 3-5) ---
    # HbA1c Change from baseline at Week 24 (Primary Endpoint)
    add_out(arm_id="ARM_PLACEBO", is_primary="YES", domain="glycemic", param="Change from baseline in HbA1c", change_val=-0.17, se=0.05, unit="%", sample_size=225, tp_val=24, page=3, location="Results Section 3, Page 3", raw_text="adjusted mean (SE) changes of -0.17% (0.05) for placebo", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_10MG", is_primary="YES", domain="glycemic", param="Change from baseline in HbA1c", change_val=-0.82, se=0.05, unit="%", sample_size=225, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-0.64, ci_l=-0.77, ci_u=-0.51, p_val="<0.001", page=3, location="Results Section 3, Page 3", raw_text="-0.82% (0.05) for empagliflozin 10 mg (difference vs placebo: -0.64% [95% CI -0.77 to -0.51]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_25MG", is_primary="YES", domain="glycemic", param="Change from baseline in HbA1c", change_val=-0.77, se=0.05, unit="%", sample_size=216, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-0.59, ci_l=-0.73, ci_u=-0.46, p_val="<0.001", page=3, location="Results Section 3, Page 3", raw_text="-0.77% (0.05) for empagliflozin 25 mg (difference vs placebo: -0.59% [95% CI -0.73 to -0.46]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")

    # HbA1c < 7.0% at Week 24
    add_out(arm_id="ARM_PLACEBO", domain="glycemic", param="Patients reaching HbA1c < 7.0%", stat_type="dichotomous", metric="count_percentage", pct=9.3, unit="%", sample_size=225, tp_val=24, page=3, location="Results Section 3, Page 3", raw_text="reached HbA1c < 7.0% at week 24: placebo 9.3%")
    add_out(arm_id="ARM_EMPA_10MG", domain="glycemic", param="Patients reaching HbA1c < 7.0%", stat_type="dichotomous", metric="count_percentage", pct=26.3, unit="%", sample_size=225, tp_val=24, eff_measure="odds_ratio", eff_val=3.85, ci_l=2.17, ci_u=6.85, p_val="<0.001", page=3, location="Results Section 3, Page 3", raw_text="reached HbA1c < 7.0% at week 24: empagliflozin 10 mg (26.3%); OR vs placebo 3.85 (95% CI 2.17-6.85); P < 0.001")
    add_out(arm_id="ARM_EMPA_25MG", domain="glycemic", param="Patients reaching HbA1c < 7.0%", stat_type="dichotomous", metric="count_percentage", pct=32.2, unit="%", sample_size=216, tp_val=24, eff_measure="odds_ratio", eff_val=5.22, ci_l=2.95, ci_u=9.24, p_val="<0.001", page=3, location="Results Section 3, Page 3", raw_text="reached HbA1c < 7.0% at week 24: empagliflozin 25 mg (32.2%); OR vs placebo 5.22 (95% CI 2.95-9.24); P < 0.001")

    # Body weight change at Week 24
    add_out(arm_id="ARM_PLACEBO", domain="anthropometric", param="Change from baseline in body weight", change_val=-0.39, se=0.15, unit="kg", sample_size=225, tp_val=24, page=4, location="Results Section 3, Page 4", raw_text="-0.39 kg (0.15) with placebo", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_10MG", domain="anthropometric", param="Change from baseline in body weight", change_val=-2.16, se=0.15, unit="kg", sample_size=225, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-1.76, ci_l=-2.19, ci_u=-1.34, p_val="<0.001", page=4, location="Results Section 3, Page 4", raw_text="-2.16 kg (0.15) with empagliflozin 10 mg (difference vs placebo: -1.76 kg [95% CI -2.19 to -1.34]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_25MG", domain="anthropometric", param="Change from baseline in body weight", change_val=-2.39, se=0.16, unit="kg", sample_size=216, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-1.99, ci_l=-2.43, ci_u=-1.56, p_val="<0.001", page=4, location="Results Section 3, Page 4", raw_text="-2.39 kg (0.16) with empagliflozin 25 mg (difference vs placebo: -1.99 kg [95% CI -2.43 to -1.56]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")

    # SBP change at Week 24
    add_out(arm_id="ARM_PLACEBO", domain="cardiovascular", param="Change from baseline in SBP", change_val=-1.4, se=0.7, unit="mmHg", sample_size=225, tp_val=24, page=4, location="Results Section 3, Page 4", raw_text="-1.4 mmHg (0.7) with placebo", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_10MG", domain="cardiovascular", param="Change from baseline in SBP", change_val=-4.1, se=0.7, unit="mmHg", sample_size=225, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-2.7, ci_l=-4.6, ci_u=-0.8, p_val="0.005", page=4, location="Results Section 3, Page 4", raw_text="-4.1 mmHg (0.7) with empagliflozin 10 mg (difference vs placebo: -2.7 mmHg [95% CI -4.6 to -0.8]; P = 0.005)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_25MG", domain="cardiovascular", param="Change from baseline in SBP", change_val=-3.5, se=0.7, unit="mmHg", sample_size=216, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-2.1, ci_l=-4.0, ci_u=-0.2, p_val="0.032", page=4, location="Results Section 3, Page 4", raw_text="-3.5 mmHg (0.7) with empagliflozin 25 mg (difference vs placebo: -2.1 mmHg [-4.0 to -0.2]; P = 0.032)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")

    # MDG change at Week 24 (LOCF)
    add_out(arm_id="ARM_PLACEBO", domain="glycemic", param="Change from baseline in MDG (LOCF)", change_val=0.00, se=0.10, unit="mmol/L", sample_size=225, tp_val=24, page=3, location="Results Section 3, Page 3", raw_text="0.00 mmol/L (0.10) for placebo", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_10MG", domain="glycemic", param="Change from baseline in MDG (LOCF)", change_val=-0.56, se=0.10, unit="mmol/L", sample_size=225, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-0.56, ci_l=-0.83, ci_u=-0.28, p_val="<0.001", page=4, location="Results Section 3, Page 4", raw_text="-0.56 mmol/L (0.10) for empagliflozin 10 mg (diff vs placebo: -0.56 mmol/L [95% CI -0.83 to -0.28]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")
    add_out(arm_id="ARM_EMPA_25MG", domain="glycemic", param="Change from baseline in MDG (LOCF)", change_val=-0.72, se=0.11, unit="mmol/L", sample_size=216, tp_val=24, eff_measure="difference_in_adjusted_means", eff_val=-0.72, ci_l=-1.02, ci_u=-0.43, p_val="<0.001", page=4, location="Results Section 3, Page 4", raw_text="-0.72 mmol/L (0.11) for empagliflozin 25 mg (diff vs placebo: -0.72 mmol/L [-1.02 to -0.43]; P < 0.001)", est_type="ADJUSTED_CHANGE_FROM_BASELINE")

    # --- Safety Adverse Events (Table 2, Page 7) ---
    safety_table = [
        ("One or more AE", 141, 62.7, 152, 67.9, 139, 64.1, 68, 67.3),
        ("One or more drug-related AE", 34, 15.1, 54, 24.1, 43, 19.8, 19, 18.8),
        ("AEs leading to discontinuation", 8, 3.6, 6, 2.7, 7, 3.2, 5, 5.0),
        ("One or more serious AE", 14, 6.2, 11, 4.9, 1, 0.5, 5, 5.0),
        ("Deaths", 0, 0.0, 1, 0.4, 0, 0.0, 0, 0.0),
        ("UTI", 15, 6.7, 21, 9.4, 15, 6.9, 3, 3.0),
        ("Nasopharyngitis", 11, 4.9, 18, 8.0, 13, 6.0, 5, 5.0),
        ("Upper respiratory tract infection", 12, 5.3, 7, 3.1, 11, 5.1, 3, 3.0),
        ("Hypoglycemia", 22, 9.8, 35, 15.6, 28, 12.9, 9, 8.9),
        ("Hyperglycemia", 28, 12.4, 6, 2.7, 5, 2.3, 8, 7.9),
        ("Dizziness", 12, 5.3, 6, 2.7, 9, 4.1, 2, 2.0),
        ("Confirmed hypoglycemia (<=3.9 mmol/L)", 19, 8.4, 36, 16.1, 25, 11.5, 7, 6.9),
        ("Genital infection", 2, 0.9, 6, 2.7, 5, 2.3, 2, 2.0),
    ]

    for label, pbo_ev, pbo_pct, e10_ev, e10_pct, e25_ev, e25_pct, ol_ev, ol_pct in safety_table:
        add_out(arm_id="ARM_PLACEBO", domain="safety", role="SAFETY_OUTCOME", param=label, stat_type="dichotomous", metric="count_percentage", events=pbo_ev, total=225, pct=pbo_pct, unit="participants", tp_val=24, page=7, location="Table 2, Page 7", raw_text=f"{label}: Placebo {pbo_ev} ({pbo_pct}%)")
        add_out(arm_id="ARM_EMPA_10MG", domain="safety", role="SAFETY_OUTCOME", param=label, stat_type="dichotomous", metric="count_percentage", events=e10_ev, total=225, pct=e10_pct, unit="participants", tp_val=24, page=7, location="Table 2, Page 7", raw_text=f"{label}: Empa 10mg {e10_ev} ({e10_pct}%)")
        add_out(arm_id="ARM_EMPA_25MG", domain="safety", role="SAFETY_OUTCOME", param=label, stat_type="dichotomous", metric="count_percentage", events=e25_ev, total=216, pct=e25_pct, unit="participants", tp_val=24, page=7, location="Table 2, Page 7", raw_text=f"{label}: Empa 25mg {e25_ev} ({e25_pct}%)")
        add_out(arm_id="ARM_EMPA_25MG_OL", domain="safety", role="SAFETY_OUTCOME", param=label, stat_type="dichotomous", metric="count_percentage", events=ol_ev, total=101, pct=ol_pct, unit="participants", tp_val=24, page=7, location="Table 2, Page 7", raw_text=f"{label}: Open-label {ol_ev} ({ol_pct}%)")

    ws_outcomes = wb.create_sheet("Outcomes")
    style_sheet(ws_outcomes, outcome_headers, outcomes)

    # 5. Provenance
    prov_headers = ["provenance_id", "study_id", "target_entity", "target_id", "field_name", "source_page", "source_section", "source_evidence"]
    prov_rows = [
        ["PROV_001", "RCT_EMPA_METSU_2013", "Studies", "RCT_EMPA_METSU_2013", "title", 1, "Title", "Empagliflozin as Add-on to Metformin Plus Sulfonylurea in Patients With Type 2 Diabetes"],
        ["PROV_002", "RCT_EMPA_METSU_2013", "Studies", "RCT_EMPA_METSU_2013", "doi", 1, "DOI", "10.2337/dc12-2673"],
        ["PROV_003", "RCT_EMPA_METSU_2013", "Arms", "ARM_PLACEBO", "arm_name", 4, "Table 1", "Placebo: Number of patients 225"],
        ["PROV_004", "RCT_EMPA_METSU_2013", "Arms", "ARM_EMPA_10MG", "arm_name", 4, "Table 1", "Empagliflozin 10 mg: Number of patients 225"],
        ["PROV_005", "RCT_EMPA_METSU_2013", "Arms", "ARM_EMPA_25MG", "arm_name", 4, "Table 1", "Empagliflozin 25 mg: Number of patients 216"],
        ["PROV_006", "RCT_EMPA_METSU_2013", "Outcomes", "PRIMARY_HBA1C", "change_value", 3, "Results Section 3", "adjusted mean (SE) changes of -0.17% (0.05) for placebo, compared with -0.82% (0.05) for empagliflozin 10 mg and -0.77% (0.05) for empagliflozin 25 mg"],
    ]
    ws_prov = wb.create_sheet("Provenance")
    style_sheet(ws_prov, prov_headers, prov_rows)

    # 6. Validation Log
    val_headers = ["issue_id", "study_id", "target_entity", "target_id", "field_name", "issue_type", "message", "status"]
    val_rows = [
        ["VAL_001", "RCT_EMPA_METSU_2013", "Studies", "RCT_EMPA_METSU_2013", "study_id", "INFO", "Extraction workbook initialized and source-grounded against Häring et al. 2013", "RESOLVED"]
    ]
    ws_val = wb.create_sheet("Validation_Log")
    style_sheet(ws_val, val_headers, val_rows)

    wb.save(output_path)
    print("Successfully created Mandros extraction workbook:", output_path)

if __name__ == "__main__":
    out_dir = Path(r"d:\MANDROS-Blind\MANDROS-Blind\data\private\empa plus met")
    out_path = out_dir / "empa vs placebo add on metformin (RCT3)_extracted.xlsx"
    create_workbook(out_path)
