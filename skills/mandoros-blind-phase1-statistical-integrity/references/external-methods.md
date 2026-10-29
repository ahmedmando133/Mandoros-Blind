# External extraction methods reviewed

Use these as design patterns, not as scientific authorities and not as bundled
dependencies. No external model, dataset, or code is copied into MANDROS Blind.

- **RobotReviewer** — retain the useful principle that PICO/RoB or result
  annotations must point back to evidence in the trial report. MANDROS Blind
  implements this through page/location provenance and verification status.
- **RCT-ART** — retain joint entity-and-relation thinking: intervention,
  comparator, outcome and outcome measure must be linked. Its documented lack
  of comparative-relation extraction is specifically guarded against here by
  stable arm IDs and comparison IDs.
- **Automatically Extracting Numerical Results from RCTs with LLMs** — retain
  the staged pattern of classifying outcome type before extracting binary or
  continuous components, plus separate evaluation of exact/partial field
  correctness. Do not copy prompts or model outputs as truth.
- **GLASS Data Extraction Benchmark** — retain separate evaluation blocks for
  structured values and evidence localization, immutable hashes for reference
  assets, and explicit version/prompt disclosure. Do not import its mixed-
  license benchmark data.
- **Jev Reviewer** — retain evidence quotation/page checking and long-format
  arm-outcome rows as useful usability principles. Do not use `n/a` as a numeric
  missingness marker in this project; retain the project's null/status rules.

Repository links reviewed:

- https://github.com/ijmarshall/robotreviewer
- https://github.com/jetsunwhitton/RCT-ART
- https://github.com/hyesunyun/llm-meta-analysis
- https://github.com/InvestmentMDideas/GLASS-Data-Extraction-Benchmark
- https://github.com/choxos/jev-reviewer

