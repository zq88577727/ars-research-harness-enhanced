# GBD CVD Manuscript Review Draft

Status: source-backed manuscript candidate, not submission-ready

## Research Question

How did the cardiovascular disease burden in China compare with the global
burden from 1990 to 2023 in GBD 2023?

## Data Source

This review draft uses a user-exported CSV from the IHME/GHDx GBD Results Tool
for GBD 2023, version_id 8352. The export is recorded in
`source_exports/gbd_cvd_china_global_1990_2023.csv`, and the bundled citation
text is recorded in `source_exports/gbd_cvd_citation.txt`.

The query is limited to cardiovascular diseases, China and Global, Both sexes,
1990 and 2023, with Deaths and DALYs as measures. All-age Number rows support
count-burden statements. Age-standardized Rate rows support rate comparison
statements. Percent rows present in the export are retained in the raw source
file but excluded from this manuscript candidate analysis.

## Methods Fragment

The source export was traced through `gbd_cvd_query_manifest.csv`,
`gbd_cvd_analysis_manifest.json`, and `results/gbd_cvd_provenance.json`.
Source-backed claims were restricted to rows with explicit GBD release,
version_id, measure, metric, cause, location, age category, sex, year, value,
lower, and upper fields. Counts and rates were handled as separate metrics.
All-age rows were treated as count-burden rows and not as age-standardized
estimates. Age-standardized rows were used only for rate comparisons.

## Results Fragment

In China, all-age CVD deaths changed from 3,303,961.86 (UI
2,797,927.14-3,795,995.79) in 1990 to 4,501,842.59 (UI
3,855,077.51-5,013,029.84) in 2023. All-age CVD DALYs changed from
81,454,987.01 (UI 68,389,231.42-94,748,209.77) in 1990 to 89,327,031.66 (UI
78,881,688.75-97,824,746.45) in 2023.

Globally, all-age CVD deaths changed from 13,137,958.83 (UI
12,200,604.88-14,040,764.43) in 1990 to 19,139,018.09 (UI
17,355,526.66-20,403,359.76) in 2023. Global all-age CVD DALYs changed from
320,141,562.84 (UI 291,872,743.51-344,484,846.93) in 1990 to 436,235,457.79
(UI 401,278,571.34-464,841,017.42) in 2023.

The age-standardized CVD death rate changed from 496.65 (UI 420.03-571.17) to
208.03 (UI 178.08-233.08) in China and from 375.51 (UI 346.66-401.06) to
214.94 (UI 194.23-229.57) globally. The age-standardized CVD DALY rate changed
from 10065.67 (UI 8607.08-11541.62) to 4059.34 (UI 3593.00-4444.04) in China
and from 8061.62 (UI 7403.37-8632.63) to 4863.82 (UI 4460.87-5192.31)
globally.

## Limitations Fragment

This draft is descriptive and should not be read as causal, mechanistic,
clinical, or policy-effect evidence. It does not explain why CVD burden changed,
does not identify individual-level risk factors, and does not estimate an
intervention effect. Final manuscript use requires journal-specific UI wording,
confirmed IHME/GHDx citation wording, and reuse-term review for the exact source
export and derived tables.

## Review Decisions Required

- Confirm whether the four numeric claims remain Results text, move partly to a
  table, or are shortened for journal style.
- Confirm final IHME/GHDx citation wording and whether the small source export
  may remain in the repository.
- Confirm whether UI should be written as parentheses in text, a table column,
  or both.
- Confirm that `All ages`, `Age-standardized`, `Number`, and `Rate` are never
  mixed or mislabeled in the final manuscript.
- Confirm that no causal, clinical, mechanistic, or policy-effect wording is
  introduced during manuscript expansion.
