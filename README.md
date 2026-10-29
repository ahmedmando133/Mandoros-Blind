# Mandroos Blind (MANDOROS BLIND™)

<p align="center">
  <img src="logo.svg" width="130" alt="Mandroos Blind Logo — Letter M wearing sleek black sunglasses" />
  <br>
  <strong>100% Clinical Trial Analysis & Side-by-Side Verification Engine</strong>
  <br>
  <a href="https://ahmedmando133.github.io/Mandoros-Blind/"><strong>🌐 Live Website: https://ahmedmando133.github.io/Mandoros-Blind/</strong></a>
</p>

Mandroos Blind (MANDOROS BLIND™) is a source-grounded audit, extraction, and automated repair platform for RCT workbooks and trial publications. It features a side-by-side interactive interface: **Module 1 (The Analysis)** alongside **Module 2 (100% Compliance Assessment)** with row-by-row condition checking, atomic range splitting, and live export to verified multi-sheet Excel (.xlsx), CSV, and full printable reports.

## What is implemented

- Local Arabic/English web interface; uploaded studies stay on the device.
- Deterministic workbook checks for arm references, sample-scope conflation, atomic values, p-value splitting, missingness markers, provenance and duplicate/integrity problems.
- Atomic comparison operators: Excel exports use separate `<`, `=` and `>` columns containing the literal symbols before the related numeric value and unit. Bounded ranges use minimum/maximum fields, with inclusivity exported as text rather than checkboxes.
- Outcome-defining threshold and subgroup columns appear immediately after `outcome` in Excel exports.
- Sample-derived proportions use the explicit measure label `sample_proportion`.
- P-values are stored once in `Statistical Tests`. Between-arm tests link both arm-specific outcome rows with one `comparison_id`; within-arm subgroup tests retain their arm and factor scope.
- Scientific regression fixture for the supplied metformin DPP/DPPOS paper.
- Scientific regression fixture for the supplied 2024 orlistat trial, including complete Table 1 baseline extraction, all Table 2 secondary efficacy endpoints, primary gout-flare and SUA results, and main-article safety outcomes.
- Scientific regression fixture for the supplied Ferrannini et al. 2010 dapagliflozin trial. It rejects the mismatched DAPA-HF Mandros content and preserves all printed Table 1 baseline, Table 2 efficacy/laboratory and Table 3 safety observations from the supplied main article.
- Scientific regression fixture for the supplied SELECT semaglutide trial. It preserves Tables 1-4, Figure 1 directly printed number-at-risk labels, quantified Results text, all 16 Table 3 SE fields, all 10 arm-level log-analysis percentage changes, ODDS_RATIO and HAZARD_RATIO semantics, and hierarchical-testing restrictions.
- Scientific regression fixture for the supplied Simvastatin pneumonia trial. It separates median/IQR from confidence intervals, consolidates printed n (%) into one observation with atomic count/denominator/percentage fields, preserves randomized/baseline/timepoint-specific analyzed N, and inventories 58 source-reported statistical comparisons.
- Independent source-inventory completeness validation with per-finding statuses (`VERIFIED`, missing, incomplete, statistical-type mismatch, numerical mismatch, source conflict, not reported, or manual review). Each run writes `source_completeness_report.json` beside the corrected workbook when a source-adjudicated inventory is available.
- Additive project skill `skills/mandros-source-completeness/SKILL.md`, which applies the new checks to future studies without replacing the existing main prompts or workflow.
- Additive project skill `skills/mandoros-blind-phase1-statistical-integrity/SKILL.md`, which applies the Simvastatin-derived Phase 1 statistical-integrity rules to future studies without changing Phase 2, the UI, model selection, or existing extraction prompts.
- Automatic optimal-extraction prompt `standards/optimal_extraction_prompt_v1.md` and machine-readable statistical definitions `standards/clinical_trial_statistics_v1.json`. `run.py` loads and hashes them with the project skill on every trial and writes `extraction_policy_report.json`; users do not need to request the skill for each study.
- Runtime source-identity and primary-endpoint gates require the complete study/outcome/arm/timepoint/population/N/statistic/value/unit/locator tuple. A page-level numeric match alone no longer counts as verification. Generic normalization can still produce a draft, but it cannot be labeled scientifically validated until an independent PDF-first inventory is reconciled.
- Complete Table 1 adherence extraction: four adherence levels across both arms in the 2-year DPP phase, metformin across the 9-year DPP+DPPOS period, all reported overall/race/sex strata, adherence-stratified >5% weight-loss outcomes, and explicit placebo non-applicability after discontinuation.
- Versioned backend rules derived from the supplied Phase 1 JSON and Word prompt.
- Separate standards layers: CONSORT 2025 and ICH E9/E9(R1) for trial reporting/statistics, Cochrane RoB 2 for bias appraisal, and PRISMA 2020 for the later systematic-review workflow.
- A corrected Excel model with study details, arms/doses/frequency, inclusion, exclusion, baseline status, efficacy, safety, provenance and validation log.
- Generic future-study conversion that requires only the original trial PDF and the Mandros Excel. It does not use or require a manual Excel benchmark.

## Safety boundary

Passing spreadsheet structure is **not** proof of scientific correctness. For a new trial, the system normalizes Mandros records, checks their cited evidence against the PDF, and creates the corrected workbook. Exact page-level matches can be source-checked; uncertain records remain `REQUIRES_REVIEW` and are excluded from automatic meta-analysis readiness. The system never invents a missing outcome or unavailable supplementary result.

Study identity is a blocking safety gate. If both the Mandros title and DOI are absent from the supplied PDF, generic correction is withheld instead of copying a different trial into a plausible-looking workbook. A source-adjudicated local truth bundle can then be added for that PDF, as was done for the supplied dapagliflozin article.

## Run locally

From the project directory, using Python 3.11+:

### Windows: double-click launcher

Double-click `RUN_MANDROS_BLIND.vbs`. It opens a graphical status window without a Command Prompt, starts the pipeline automatically, displays live progress, and enables **فتح مجلد النتائج** when processing finishes.

The launcher first uses `.venv\\Scripts\\pythonw.exe` when a project virtual environment exists, then falls back to the bundled local Codex Python runtime on this computer.

### Command line

Run the complete unattended pipeline:

```powershell
python run.py
```

The runner recursively discovers source-PDF/extraction-XLSX pairs under `data/`, loads and fingerprints the versioned standards in `standards/`, and processes only new or changed input pairs. `outputs/processing_registry.json` remembers the PDF and workbook hashes. Unchanged historical projects are skipped instead of being run again.

Every run also activates the project-level Phase 1 extraction skill automatically. It preserves trial-specific terminology, separates statistical meanings, checks atomic operators/counts/denominators, links values to arms/outcomes/timepoints/populations and records policy hashes. Conflicting scientific statements or project rules are preserved for human adjudication instead of being silently resolved.

For each future study, create one subfolder under `data/` and place exactly the original RCT PDF and the Excel exported by Mandros in that folder. A manual Excel is not required. The PDF and Mandros Excel are paired automatically when they share the same folder.

Each project has a stable directory under `outputs/studies/`. If the same input path is later changed, its assessment and corrected workbook are updated in that same directory and with the same filenames. New projects receive new stable directories. Session logs are stored under `outputs/logs/`, while `outputs/last_run.json` summarizes the most recent invocation. Source inputs are never modified.

For source-adjudicated studies, the project directory also contains `source_completeness_report.json`. A `100% verified` claim is emitted only when the inventory was built independently of the Excel output and every in-scope main-article finding is verified. Unavailable supplementary files are recorded as not supplied and never populated with invented values.

Files registered as policy sources, PRISMA references, historical manual benchmarks, layouts, or templates remain reference material and are not treated as Mandros extraction inputs. For an unseen trial, the system produces a structurally corrected workbook from the supplied PDF and Mandros Excel only; unsupported scientific assertions are retained with explicit review flags instead of being silently changed.

The current repository does not contain a trained ML checkpoint. `run.py` checks for model artifacts and reuses them if present, but it does not invent or retrain a model. The currently implemented pipeline is deterministic and configuration-driven.

Optional paths can be supplied without changing the one-command default:

```powershell
python run.py --data data --output outputs
```

Intentional full reprocessing is available for maintenance only:

```powershell
python run.py --force
```

Start the local web interface:

```powershell
python -m app.cli serve --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`.

Run the metformin regression audit:

```powershell
python -m app.cli audit --pdf data/private/metformin/source.pdf --xlsx data/private/metformin/mandros_input.xlsx --out outputs
```

Run tests:

```powershell
python -m unittest discover -s tests -v
```

## Repository and privacy

The source studies and private reference files are copied to `data/private/` for local persistence and are excluded by `.gitignore`. Every web upload is persisted under `data/private/studies/<run-id>/` with a local manifest and SHA-256 hashes. `data/manifest.json` records the initial immutable inputs so the evaluation can be reproduced without committing copyrighted or confidential files.

## Current metformin decision

The original Mandros workbook is **REJECT, 38/100** under the provided six-domain comparison rubric. Its major failures include 18 broken outcome-to-arm references, year-9 visit counts used as arm analysis sizes, fabricated 100% Caucasian baseline records, a year-1 placebo value labeled as year 2, overall results mislabeled as Caucasian, and missing safety extraction.

The manual workbook is a useful numerical benchmark but is not a gold standard: it repeats study-level data, stores several adherence categories across columns, uses `NA`, and omits important efficacy and safety results.

## Current orlistat decision

The supplied Mandros workbook is **REJECT, 29/100**. It uses invalid outcome arm IDs, changes the BMI eligibility threshold from 25 to 28 kg/m2, omits most exclusion criteria and nearly all efficacy outcomes, fabricates arm-level 100% Asian baseline rows, misclassifies gout flares as safety, reports incorrect gout-flare counts, and omits the adverse events described in the article. The corrected fixture is stored in `standards/orlistat_workbook_dataset.json`; the private source PDF and Mandros workbook are registered under `data/private/orlistat/`.

## Current Simvastatin decision

The original Mandros workbook is rejected for Phase 1 statistical-integrity failures, including IQR limits copied into CI fields, event counts carrying percent units, incomplete sample-size scope, missing explicit statistical comparisons, and incomplete provenance. The corrected workbook preserves the main article's 36 median/IQR records without fabricated confidence intervals, 26 printed n (%) findings as atomic observations, and 58 statistical-test records. The main article contains a genuine SOFA p-value conflict (`0.026` in Results/Figure 6 versus `0.040` in Table 4); both are retained and the record remains subject to manual adjudication. No unavailable supplementary value is created.

## Next production milestone

Add a blinded dual-review workflow for new studies: independent extractor A, independent verifier B, disagreement adjudication, signed rule/version hashes, and locked export only after all blockers are resolved. Prediction should remain outside the extraction/verification gate until a validated multi-study dataset exists.

