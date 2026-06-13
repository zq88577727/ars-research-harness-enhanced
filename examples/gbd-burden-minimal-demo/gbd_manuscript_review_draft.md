# GBD Manuscript Review Draft

Status: manuscript-review-ready, not submission-ready

## Research Question

Among global, all-age, both-sex populations in the GBD 2023 Results Tool default
endpoint, what were the estimated all-cause deaths and DALYs in 2023, and how
did the all-cause death rate change from 1990 to 2023?

## Data Source

This review draft uses the Institute for Health Metrics and Evaluation (IHME)
Global Health Data Exchange GBD Results Tool default endpoint for GBD 2023
(version_id 8352), accessed on 2026-06-11. The query is limited to Global,
All causes, All ages, Both sexes, with Deaths and DALYs as Number metrics and
Deaths as a Rate metric. The current citation draft is recorded in
`gbd_query_profile.json` and must be confirmed against IHME/GHDx and target
journal requirements before submission.

## Methods Fragment

The source export was traced through `gbd_query_manifest.csv`,
`gbd_analysis_manifest.json`, and `results/gbd_provenance.json`. Numeric claims
were restricted to source rows with explicit measure, metric, cause, location,
age, sex, year, value, lower, and upper fields. Counts and rates were handled as
separate metrics. `All ages` was treated as a GBD age category and not age-standardized or age-adjusted.

## Results Fragment

In the GBD 2023 default endpoint, the global all-cause, all-age, both-sex 2023
Number rows contained 60,043,088.86 deaths (UI 59,045,447.00-61,239,779.90)
and 2,799,135,266.30 DALYs (UI 2,566,897,218.51-3,084,150,438.57).

The all-cause death Rate row changed from 0.00898401 in 1990 to 0.00744413 in
2023, a -17.14% endpoint-scale relative change. This rate-change sentence should
remain supporting text unless a formal uncertainty treatment for the derived
change is added.

## Limitations Fragment

This draft is descriptive and should not be read as causal, mechanistic,
clinical, or policy-effect evidence. The endpoint uses Global, All causes, All
ages, Both sexes rows and therefore does not support disease-specific,
country-specific, age-standardized, age-adjusted, or subgroup claims. Reuse and
redistribution terms for the exact export and any derived tables require human
confirmation before manuscript submission.

## Review Decisions Required

- Confirm whether the deaths and DALYs Number claims are retained as main
  Results sentences or rewritten for target journal style.
- Decide whether the rate-change sentence remains supporting text, moves to a
  supplement, or is removed until uncertainty propagation is added.
- Confirm final IHME/GHDx citation wording and whether the committed small CSV
  may remain in the repository.
- Confirm that all uses of `UI`, `All ages`, `Number`, and `Rate` match the
  query profile and claim review checklist.
