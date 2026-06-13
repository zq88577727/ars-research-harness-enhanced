# GBD CVD Manuscript Fragment

Status: manuscript-review-ready fragment, not submission-ready.

## Research Question

How did the cardiovascular disease burden in China compare with the global
burden from 1990 to 2023 in GBD 2023?

## Methods Fragment

We conducted a descriptive analysis of cardiovascular disease burden estimates
from the IHME/GHDx GBD Results Tool using GBD 2023, version_id 8352. The source
export was `source_exports/gbd_cvd_china_global_1990_2023.csv`, and the bundled
source citation was `source_exports/gbd_cvd_citation.txt`.

The query was restricted to Cardiovascular diseases, China and Global, Both
sexes, and the years 1990 and 2023. Deaths and DALYs were evaluated with two
separate metric strategies. All ages with the Number metric was used only for
count-burden statements. Age-standardized with the Rate metric was used only for
rate comparisons. Uncertainty intervals are reported as UI values from the GBD
export and are not interpreted as confidence intervals or p values.

Source rows were traced through `gbd_cvd_query_manifest.csv`,
`gbd_cvd_analysis_manifest.json`, `results/gbd_cvd_provenance.json`, and
`claim_registry.json`. The analysis is descriptive and does not estimate causal,
clinical, mechanistic, intervention, or policy effects.

## Results Fragment

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

## Claim Registry Linkage

| claim_id | decision | manuscript placement |
| --- | --- | --- |
| gbd-cvd-china-global-rq-boundary | approve | Methods and limitations boundary |
| gbd-cvd-deaths-count-change-china | rewrite | Results text |
| gbd-cvd-dalys-count-change-china | rewrite | Results text |
| gbd-cvd-death-rate-comparison-china-global | rewrite | Results text |
| gbd-cvd-daly-rate-comparison-china-global | downgrade | Supporting or table-only evidence |

## Submission Boundary

This fragment is not submission-ready. Final use requires author confirmation of
IHME/GHDx citation wording, reuse and redistribution terms for the exact source
export and derived tables, target-journal UI style, and consistency with the
complete manuscript.
