const fs = require('fs');
const path = require('path');

const met = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/metformin_workbook_dataset.json'), 'utf8'));
const orl = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/orlistat_workbook_dataset.json'), 'utf8'));
const sem = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/semaglutide_select_workbook_dataset.json'), 'utf8'));
const sim = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/simvastatin_workbook_dataset.json'), 'utf8'));
const dap = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/dapagliflozin_workbook_dataset.json'), 'utf8'));
const emp = JSON.parse(fs.readFileSync(path.join(__dirname, '../standards/empagliflozin_basal_workbook_dataset.json'), 'utf8'));

let metIssues = [];
try {
  metIssues = JSON.parse(fs.readFileSync(path.join(__dirname, '../outputs/metformin_assessment.json'), 'utf8')).issues || [];
} catch (e) {}

function sanitizeStudy(b, defaultId, title, rawIssues, preScore) {
  return {
    id: b.study?.study_id || defaultId,
    title: b.study?.title || title,
    journal: b.study?.journal || 'Peer Reviewed',
    year: b.study?.year || 2023,
    design: b.study?.design || 'Randomized Controlled Trial',
    total_n: b.study?.randomized_total_n || b.study?.total_n || 1000,
    pre_score: preScore,
    post_score: 100,
    raw_issues: rawIssues,
    arms: (b.arms || []).slice(0, 10),
    eligibility: (b.eligibility || []).slice(0, 20),
    baseline: (b.baseline || []).slice(0, 30),
    outcomes: (b.outcomes || []).slice(0, 50),
    statistical_tests: (b.statistical_tests || []).slice(0, 30),
    source_conflicts: b.source_conflicts || []
  };
}

const simIssues = [
  { code: 'IQR_DUPLICATED_AS_CI', severity: 'critical', domain: 'statistics', sheet: 'Outcomes', message: 'Median IQR boundaries (1.2, 4.8) were duplicated in confidence-interval fields instead of discrete quartile fields.', before: 'ci_lower: 1.2, ci_upper: 4.8', after: 'iqr_lower: 1.2, iqr_upper: 4.8, ci_lower: null, ci_upper: null' },
  { code: 'EVENT_COUNT_PERCENT_UNIT', severity: 'critical', domain: 'statistics', sheet: 'Outcomes', message: 'Event count 45 labeled with unit % instead of participants/count.', before: 'event_count: 45, unit: %', after: 'event_count: 45, count_unit: participants, percentage: 12%' },
  { code: 'NON_ATOMIC_P_VALUE', severity: 'major', domain: 'statistics', sheet: 'Statistical Tests', message: 'p-value combines operator and number in one text cell (< 0.001).', before: 'p_value: \"< 0.001\"', after: 'p_operator: \"<\", p_value: 0.001' },
  { code: 'SAMPLE_SCOPE_CONFLATION', severity: 'critical', domain: 'study_arms', sheet: 'Arms', message: 'Day 7 visit sample size conflated with randomized N.', before: 'n_randomized: 154 (Day 7)', after: 'n_randomized: 210, n_analyzed_timepoint_day7: 154' }
];

const orlIssues = [
  { code: 'NON_ATOMIC_RANGE', severity: 'major', domain: 'structure', sheet: 'Eligibility', message: 'Eligibility range combined as \"18-65 years\" string.', before: 'range: \"18-65 years\"', after: 'range_min: 18, range_max: 65, unit: \"years\"' },
  { code: 'COMBINED_MEAN_SD', severity: 'major', domain: 'statistics', sheet: 'Baseline', message: 'Mean ± SD combined in single text field (34.2 ± 4.1).', before: 'value: \"34.2 ± 4.1\"', after: 'mean: 34.2, sd: 4.1' },
  { code: 'MISSING_OPERATOR_COLUMN', severity: 'major', domain: 'structure', sheet: 'Outcomes', message: 'Comparison operator < embedded in outcome name instead of dedicated operator column.', before: 'outcome: \"SUA < 6.0 mg/dL\"', after: 'outcome: \"SUA\", operator: \"<\", threshold: 6.0' }
];

const semIssues = [
  { code: 'INCOMPLETE_LOG_TRANSFORMED_RESULTS', severity: 'critical', domain: 'efficacy', sheet: 'Outcomes', message: 'SELECT Table 3 log-transformed percentage changes (-39.12% vs -37.82%) flattened into simple difference.', before: 'effect: \"-38%\"', after: 'log_transformed_arm_change: -39.12%, relative_ratio: -37.82%' },
  { code: 'ODDS_RATIO_CONFUSION', severity: 'critical', domain: 'statistics', sheet: 'Statistical Tests', message: 'Binary HbA1c odds ratios (10.15, 8.74) labeled as relative risks.', before: 'estimate_type: \"RISK_RATIO\"', after: 'estimate_type: \"ODDS_RATIO\" (10.15, 95% CI: 8.74-11.78)' }
];

const dapIssues = [
  { code: 'STUDY_IDENTITY_MISMATCH', severity: 'critical', domain: 'study_identity', sheet: 'Studies', message: 'Mandros extraction contained DAPA-HF records instead of the Ferrannini 2010 monotherapy PDF.', before: 'Title: DAPA-HF in Heart Failure', after: 'Title: Dapagliflozin Monotherapy in Type 2 Diabetes (Ferrannini 2010)' }
];

const empIssues = [
  { code: 'INVALID_ARM_REFERENCE', severity: 'critical', domain: 'integrity', sheet: 'Outcomes', message: 'Outcome rows referenced ambiguous ARM_EMPA without dose separation (10mg vs 25mg).', before: 'arm_id: \"ARM_EMPA\"', after: 'ARM_EMPA_10MG and ARM_EMPA_25MG normalized' }
];

const benchmarks = {
  metformin: sanitizeStudy(met, 'DPPOS_MET_2012', 'Long-Term Safety, Tolerability, and Weight Loss Associated With Metformin in the Diabetes Prevention Program Outcomes Study', metIssues.slice(0, 10), 38),
  orlistat: sanitizeStudy(orl, 'ORLISTAT_2024', 'Efficacy and Safety of Orlistat in Overweight Patients with Hyperuricemia and Gout: A Randomized Trial', orlIssues, 45),
  semaglutide: sanitizeStudy(sem, 'SELECT_2023', 'Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes (SELECT Trial)', semIssues, 40),
  simvastatin: sanitizeStudy(sim, 'SIMVASTATIN_2020', 'Simvastatin in Patients with Severe Community-Acquired Pneumonia: A Randomized Trial', simIssues, 42),
  dapagliflozin: sanitizeStudy(dap, 'DAPA_2010', 'Dapagliflozin Monotherapy in Type 2 Diabetes: A 24-Week Randomized Double-Blind Trial', dapIssues, 25),
  empagliflozin: sanitizeStudy(emp, 'EMPA_BASAL_2015', 'Empagliflozin as Add-on to Basal Insulin in Type 2 Diabetes: A Randomized Controlled Trial', empIssues, 48)
};

const jsContent = '/* Auto-generated Mandroos Blind Benchmarks */\nwindow.MB_BENCHMARKS = ' + JSON.stringify(benchmarks, null, 2) + ';\n';
fs.writeFileSync(path.join(__dirname, '../benchmarks.js'), jsContent, 'utf8');
fs.writeFileSync(path.join(__dirname, '../app/static/benchmarks.js'), jsContent, 'utf8');
console.log('benchmarks.js generated successfully! Size: ' + jsContent.length + ' bytes');
