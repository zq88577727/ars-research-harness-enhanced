# Manuscript Blueprint

Status: `blueprint-draft-not-manuscript`
Data source: `gbd`
Manuscript type: GBD descriptive disease-burden manuscript

## Candidate Titles

- Depression, cognition, cardiovascular burden, and bioinformatics boundary plan: a GBD descriptive disease-burden manuscript
- Depression, cognition, cardiovascular burden, and bioinformatics boundary plan: protocol-ready analysis blueprint

## Research Question

What are the burden and time trends for diseases or outcomes related to depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults across locations, years, age groups, and sex strata?

## Methods Framework

- GBD release, source, and reuse boundary
- Query profile: measure, metric, cause, location, age, sex, and year
- Count, rate, percent, and age-standardization decisions
- Uncertainty interval interpretation
- Derived summaries and trend calculations
- Citation and IHME/GHDx reuse policy
- Sensitivity or stratified comparisons where defined
- Reproducibility and source-export provenance

## Table And Figure Shell

- `table1`: GBD query dimensions and export provenance
- `table2`: Burden estimates with uncertainty intervals
- `table3`: Temporal changes by location, sex, or age group
- `figure1`: Burden trend plot with uncertainty intervals

## Claim Registry Draft

`examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/claim_registry.draft.json`

## Boundary

Use descriptive burden and trend language only; do not infer patient-level risk factors, mechanisms, or intervention effects.

## Readiness Gate

- dataset-specific design gate is reviewed
- source data/export provenance exists
- claim registry entries are source-backed
- methods/results consistency gate passes
