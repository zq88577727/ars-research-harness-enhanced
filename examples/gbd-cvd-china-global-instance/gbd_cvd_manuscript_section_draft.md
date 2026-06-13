# GBD CVD Manuscript Section Draft

Status: submission-package-ready draft, not final submission-ready.

## Methods

We conducted a descriptive disease-burden analysis using the IHME/GHDx GBD
Results Tool export for GBD 2023, version_id 8352. The source file was
`source_exports/gbd_cvd_china_global_1990_2023.csv`, with provenance recorded in
`results/gbd_cvd_provenance.json` and citation text recorded in
`source_exports/gbd_cvd_citation.txt`. The query was restricted to
Cardiovascular diseases, China and Global, Both sexes, and the years 1990 and
2023. Measures were Deaths and DALYs. All ages with the Number metric was used
for count-burden estimates; Age-standardized with the Rate metric was used for
rate comparisons. Values were reported with the lower and upper uncertainty
interval fields from the export and are described as UI values.

The manuscript citation draft is: Global Burden of Disease Collaborative
Network. Global Burden of Disease Study 2023 (GBD 2023) Results. Seattle,
United States: Institute for Health Metrics and Evaluation (IHME), 2024.
Available from https://vizhub.healthdata.org/gbd-results/. Accessed
2026-06-11.

This analysis is descriptive. It does not estimate causal, clinical,
mechanistic, intervention, or policy effects.

## Results

In GBD 2023, all-age cardiovascular disease deaths in China were estimated at
3,303,961.86 (UI 2,797,927.14-3,795,995.79) in 1990 and 4,501,842.59 (UI
3,855,077.51-5,013,029.84) in 2023, using the Number metric.

In GBD 2023, all-age cardiovascular disease DALYs in China were estimated at
81,454,987.01 (UI 68,389,231.42-94,748,209.77) in 1990 and 89,327,031.66 (UI
78,881,688.75-97,824,746.45) in 2023, using the Number metric.

For the age-standardized cardiovascular disease death rate in GBD 2023, China
was estimated at 496.65 (UI 420.03-571.17) in 1990 and 208.03 (UI
178.08-233.08) in 2023, compared with global estimates of 375.51 (UI
346.66-401.06) in 1990 and 214.94 (UI 194.23-229.57) in 2023.

The age-standardized cardiovascular disease DALY rate comparison is retained as
supporting or table-only evidence and should not be used as a leading narrative
claim unless the final manuscript elevates DALY rates to a primary outcome.

## Limitations

The analysis is based on modeled GBD estimates from a manually exported Results
Tool CSV rather than individual-level clinical data. All-age Number estimates
and age-standardized Rate estimates answer different descriptive questions and
should not be combined as if they were the same metric. UI values should not be
renamed as confidence intervals or p values. Citation wording, IHME/GHDx reuse
terms, and target-journal formatting require final human confirmation before
submission-ready status.

## Data Availability Draft

The source estimates were obtained from the IHME/GHDx GBD Results Tool. This
repository records the query manifest, source-export provenance, derived
aggregate summary, citation review, and reuse review. Public redistribution of
the source export or derived tables should follow IHME/GHDx terms and the
target journal's data availability requirements.
