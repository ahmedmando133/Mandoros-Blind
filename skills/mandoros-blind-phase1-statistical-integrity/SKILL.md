---
name: mandoros-blind-phase1-statistical-integrity
description: Apply the source-grounded, backward-compatible MANDROS Blind Phase 1 extraction and statistical-integrity workflow to every RCT PDF plus Mandros Excel pair. Use for future-study extraction, verification, correction, source completeness, statistical classification, provenance, or workbook export. Do not redesign MANDROS, replace existing workflow components, invent data, or modify Phase 2.
---

# MANDROS Blind Phase 1 Statistical Integrity

Use this skill as an additive verification layer. Preserve the current Phase 1
architecture, user workflow, prompts, extraction components, worksheet names,
correctly extracted records, and identifiers. Do not modify Phase 2, the user
interface, authentication, API-key handling, Gemini integration, or model
selection.

## Automatic project use

The project runner loads this skill's system prompt and statistical reference
through the versioned standards bundle on every run. Users do not need to name
the skill for an ordinary future trial. Keep this skill implicit and automatic.

Before extracting or validating a study:

1. Apply `standards/optimal_extraction_prompt_v1.md` as the controlling Phase 1
   extraction prompt.
2. Use `standards/clinical_trial_statistics_v1.json` to classify explicitly
   reported statistics without inferring an unreported method.
3. Apply the existing `mandros-source-completeness` inventory/status rules.
4. Preserve any unresolved source or project-rule contradiction and request
   human adjudication before changing scientific content.

For the rationale and routing of authorities, read
[scientific-authorities.md](references/scientific-authorities.md). When
maintaining or evaluating extraction methods, read
[external-methods.md](references/external-methods.md). External repositories
are design references only; do not add their models, dependencies, prompts or
datasets without a separate compatibility, license and regression review.

## Statistical representation

- Read table and figure footnotes before classifying an estimate.
- For `median (Q1, Q3)`, store median, Q1 and Q3 as distinct fields. Never copy
  Q1/Q3 into `ci_lower`, `ci_upper`, or `ci_level`.
- Preserve a genuine confidence interval when the paper reports it separately
  from the IQR. Do not infer confidence intervals.
- Keep mean, SD, SE, median, IQR, confidence intervals and effect estimates in
  their correct statistical fields.
- Classify the outcome data type before interpreting its numbers: continuous,
  binary, count/rate, ordinal, time-to-event, repeated-measures or other as
  explicitly supported.
- Preserve trial-specific terms, endpoint definitions, instruments, analysis
  metrics, aggregation methods and timepoints. Never normalize away the exact
  source meaning.

## Counts and percentages

- A patient/event count uses `count` or `participants`, never `%`.
- A printed percentage uses `%` and remains distinct from its count.
- When the source prints `n (%)`, keep one observation row and store event
  count, event denominator and percentage in separate cells. Do not create a
  second independent outcome for the same finding.
- For sex-specific safety rows, never use total arm N as the male/female
  denominator. Use the source-reported sex subgroup N; if it is absent, retain
  the printed count and percentage and leave the denominator blank with an
  explicit not-reported status.
- Do not calculate an unprinted percentage unless an existing documented rule
  authorizes it. Mark any transparent derivation explicitly.

## Sample-size scope

- Preserve `n_randomized`, `n_baseline`, `n_analyzed`, analyzed timepoint,
  analysis population, event count and event denominator independently.
- Never replace an unreported outcome-specific N with randomized or baseline N.
- Do not put changing sample sizes inside outcome names.
- Keep Day 4, Day 7 and other timepoint-specific populations separate.

## Statistical tests

- Inventory explicitly reported comparisons from baseline tables, efficacy,
  safety, Results text, figure annotations and footnotes.
- Preserve outcome, arms, timepoint, population, between/within-group scope,
  test type, p-value operator, p-value, nominal/adjusted status and source
  locator.
- Preserve `p < 0.001` as `<` plus `0.001`; never convert it to equality.
- Preserve Mann-Whitney U, Wilcoxon signed-rank, Fisher's exact and other tests
  only when the source supports the assignment.
- Do not calculate or invent a missing p-value or test type.

## Provenance and observation identity

- Store the PDF page and, when known, table, figure, Results section or footnote.
- If a locator cannot be established, use `REQUIRES_MANUAL_REVIEW`; never invent
  a page.
- Treat study, arm, outcome, timepoint, subgroup, analysis population and
  statistical measure as the observation key.
- Keep baseline, follow-up and change-from-baseline observations separate.
- When the same result occurs in several source locations, keep one canonical
  observation and multiple provenance occurrences rather than duplicate data.
- Preserve genuine source conflicts and require adjudication instead of
  silently choosing one printed value.

## Validation and acceptance

Before export, check for:

1. IQR boundaries duplicated into CI fields.
2. Event counts labeled with percent units.
3. Randomized N substituted for analyzed N.
4. Missing explicit statistical comparisons.
5. Missing or fabricated source locators.
6. Duplicate observation keys.
7. Unsupported supplementary values.
8. Isolated numbers lacking arm/outcome/timepoint/population relations.
9. Outcome-type, effect-measure or analysis-population misclassification.
10. Missing multiplicity, hierarchy, transformation or covariate semantics
    that the source explicitly reports.
11. A number that appears on the cited page but does not match the complete
    source identity tuple: study, outcome, arm, timepoint, population,
    analyzed N/denominator, statistic, unit and locator.
12. Primary-endpoint records that do not match the source-defined scheduled
    timepoint, metric, population and uncertainty type for every arm.
13. Eligibility records whose evidence comes from rescue therapy, visit
    scheduling, follow-up, discontinuation or analysis-population text rather
    than the eligibility section.

For an unseen study, loading this skill or hashing its prompt is not proof that
the rules ran. Require a runtime source inventory, tuple-level reconciliation
and primary-endpoint gate in the exported validation report. If the local
runtime has no semantic extraction model or source-adjudicated truth bundle,
export only an explicit draft and retain blocking review status.

Leave unreported values blank. Never fabricate numerical or statistical
information. Do not claim 100% completeness unless an independent source-based
inventory demonstrates it. Keep Study Information, Treatment Arms, Baseline,
Efficacy, Safety, Statistical Tests and Validation Log separately organized.

