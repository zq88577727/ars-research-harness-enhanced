# Depression, cognition, cardiovascular burden, and bioinformatics boundary plan

Topic: depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults

Status: `planning-only-not-analysis`

## Recommendation

Recommended data sources: charls, gbd

| Data source | Support | Score | Role |
| --- | --- | ---: | --- |
| charls | primary | 8 | aging, depression/cognition/function, chronic disease, and longitudinal trajectory route; cannot provide molecular mechanism or omics evidence without external omics databases |
| gbd | primary | 6 | disease-burden, mortality/DALY, trend, location, metric, and uncertainty-interval route; cannot provide molecular mechanism or omics evidence without external omics databases |
| nhanes | not_recommended | 0 | optional only; cross-sectional phenotype, exposure, laboratory, lifestyle, and survey-weighted association route if the topic is reframed to fit this dataset |

## Candidate Research Questions

- **charls-longitudinal** (CHARLS): Among middle-aged and older adults, how is depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults related to longitudinal changes in aging-related outcomes after wave linkage and attrition assessment? Status: `scaffold_until_local_data_ready`
- **gbd-burden-trend** (GBD): What are the burden and time trends for diseases or outcomes related to depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults across locations, years, age groups, and sex strata? Status: `query_profile_required_before_claims`
- **omics-extension** (External omics databases): What molecular signatures or pathways related to depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults can be evaluated using GEO/TCGA/GTEx or other omics sources? Status: `not_supported_by_nhanes_charls_gbd_only`

## Manuscript Workflow

- **S0**: intake topic, target population, disease/outcome, intended database combination, and data-access status
- **S1**: convert broad topic into dataset-specific answerable research questions
- **S1b**: decide whether the paper is epidemiology-only or requires a separate omics data module; NHANES/CHARLS/GBD cannot prove molecular mechanism alone
- **S2**: write analysis plan and dataset-specific gate: survey weights, wave linkage, or GBD query profile
- **S3**: execute or import validated results; do not draft numeric claims before this stage
- **S4**: interpret results with study-design boundaries and uncertainty intervals where applicable
- **S5**: build paper outline and table/figure shell
- **S6**: draft manuscript sections with cautious causal and diagnostic language
- **S7**: claim registry, citation registry, data provenance, and guideline checklist audit
- **S8**: review/revision simulation and response trace
- **S9**: final manuscript package and readiness report

## Required Human Decisions

- Confirm the target population and disease/outcome scope.
- Choose one primary dataset route before analysis execution.
- Confirm local access status for CHARLS and any restricted data.
- Confirm GBD release/query dimensions and citation/reuse boundary before using GBD claims.
- Decide whether external omics databases are required for a bioinformatics manuscript.

## Caution Language

- Do not write cross-sectional associations as causal effects.
- Do not write single laboratory measurements or survey responses as definitive clinical diagnoses.
- Do not write descriptive public-database analyses as mechanistic studies.
- Do not draft manuscript-ready numeric claims until S3 outputs and S7 claim/citation audits exist.
- NHANES, CHARLS, and GBD are not sufficient for transcriptomic/genomic/single-cell mechanism claims; add GEO/TCGA/GTEx or equivalent omics sources if the paper requires bioinformatics evidence.

## Next Actions

- Use this plan as S0/S1 input, not as completed analysis.
- Instantiate a dataset-specific project only after choosing the primary route.
- Run the relevant design gate before S3 analysis and manuscript numeric claims.
