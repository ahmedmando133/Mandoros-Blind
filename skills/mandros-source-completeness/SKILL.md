---
name: mandros-source-completeness
description: Validate and correct Mandros RCT extraction workbooks against the supplied main-article PDF without redesigning Mandros. Use for every future PDF plus Mandros-XLSX study pair to build an independent numerical source inventory, preserve statistical meaning, and export a source-grounded corrected workbook.
---

# Mandros Source Completeness

Apply this skill as an additive Phase 1 validation layer. Preserve the existing
MANDROS Blind workflow, sheet model, main prompts, identifiers, and runner.

## Evidence boundary

- Treat the supplied main-article PDF as the source of truth.
- Inventory tables, figures, captions, footnotes, Results paragraphs, arms,
  subgroups, timepoints, populations, denominators, and statistical measures
  independently of the Mandros Excel.
- Record supplementary material as unavailable when it was not supplied. Do
  not create or infer supplementary results.
- Preserve directly printed figure labels. Do not turn an unlabelled curve into
  exact values; mark it `REQUIRES_MANUAL_REVIEW` or as requiring digitization.

## Atomic normalized structure

- One row represents one arm-outcome-subgroup-timepoint observation.
- Keep `n_randomized`, `n_baseline`, and outcome-specific `n_analyzed` separate.
- Keep count, denominator, printed percentage, number, unit, dispersion, and
  confidence-limit components in separate cells.
- When the source prints `n (%)`, keep count and percentage on the same row in
  their separate fields. Never derive an unprinted percentage.
- Store baseline `sex` in `characteristic` and `male` or `female` in
  `subgroup_value`. Store `race` and its reported category the same way.
- Store an outcome name without an embedded threshold. Immediately after the
  outcome column, use separate literal `<`, `=`, `>` cells, then threshold
  number and unit. A range uses explicit minimum and maximum fields.
- Store a between-arm p-value once per comparison, not once per arm.

## Statistical semantics

- Inspect footnotes before classifying dispersion. Never substitute SD for SE.
- Classify published odds ratios as `ODDS_RATIO`, hazard ratios as
  `HAZARD_RATIO`, and log-model percentage effects as
  `LOG_TRANSFORMED_RELATIVE_PERCENTAGE_CHANGE`.
- Preserve published arm estimates and published adjusted/model-based effects
  independently. Do not replace a published effect by arithmetic subtraction.
- Preserve the reported test or model only when the source states it.
- Preserve p-value operator/value, CI, comparison, analysis population,
  adjustment, multiplicity, and hierarchical-testing restrictions.
- If a hierarchical test was not performed after a gate failed, leave the
  p-value blank and record the restriction; do not infer significance from CI.

## Completeness validation

For every expected finding, compare the independent source inventory with the
normalized extraction and assign exactly one status:

- `VERIFIED`
- `MISSING_FROM_EXTRACTION`
- `PRESENT_BUT_INCOMPLETE`
- `STATISTICAL_TYPE_MISMATCH`
- `NUMERICAL_MISMATCH`
- `SOURCE_CONFLICT`
- `NOT_REPORTED_IN_SOURCE`
- `REQUIRES_MANUAL_REVIEW`

Retry only missing or ambiguous accessible findings, then revalidate. A 100%
verified claim is allowed only when the independent inventory is complete and
every in-scope finding is verified. Never generate a value to improve a score.

