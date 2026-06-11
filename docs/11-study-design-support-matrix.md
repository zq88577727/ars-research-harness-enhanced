# Study Design Support Matrix

This matrix prevents scaffolded support from being mistaken for completed
analysis capability.

| Study family | Example/data source | Current support level | Reporting guideline | Required boundary |
|---|---|---|---|---|
| Cross-sectional public-use survey | NHANES 2017-2018 undiagnosed diabetes | Complete teaching example | STROBE | Associations only; single HbA1c is an epidemiologic definition, not clinical diagnosis |
| Longitudinal aging cohort | CHARLS | Scaffold only | STROBE/RECORD depending on data linkage and reporting frame | Requires approved data, wave linkage, attrition plan, missingness plan, and citation terms |
| Disease burden / comparative burden | GBD | Scaffold only | GATHER-style source transparency plus journal requirements | Requires release version, query dimensions, metric definitions, and uncertainty interval interpretation |
| Systematic review / meta-analysis | Future PRISMA project | Template placeholder only | PRISMA | Requires search strategy, screening log, eligibility decisions, extraction, and risk-of-bias assessment |
| Prediction model | Future TRIPOD project | Template placeholder only | TRIPOD | Requires train/test or validation design, calibration, discrimination, and external validation plan |
| Randomized trial | Future CONSORT project | Template placeholder only | CONSORT | Requires trial registration, randomization, allocation, intervention, adherence, and harms reporting |
| Diagnostic accuracy | Future STARD project | Template placeholder only | STARD | Requires index test, reference standard, threshold rules, and diagnostic accuracy estimates |
| Real-world evidence / record linkage | Future RECORD project | Template placeholder only | RECORD/STROBE | Requires database provenance, code lists, linkage rules, and privacy governance |

## Current Interpretation

Only the NHANES example currently demonstrates the full S0-S9 loop with
analysis outputs, manuscript text, registered references, registered claims,
revision trace, and a submission package.

CHARLS and GBD files are deliberately scaffolded. They are useful for project
initialization, data governance, and workflow planning, but they are not
evidence that CHARLS or GBD manuscript results have been produced.

## Template Governance

Study design templates may be present before a complete example exists. When a
template is placeholder-only, its README and manifest must say so explicitly.
New completed examples should include:

- data/source manifest,
- methods plan,
- executable or documented analysis route,
- S3 results,
- source-backed claim registry,
- reporting checklist mapping,
- S7 integrity audit,
- final package or release artifact.
