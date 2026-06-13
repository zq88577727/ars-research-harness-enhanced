# P8-1 Topic-to-Manuscript Planning

Status: first implementation pass.

Date: 2026-06-13.

## Objective

P8 shifts the project back from repository maintenance to the user-facing
medical manuscript workflow.

The target interaction is:

1. User gives a broad medical research topic.
2. The harness recommends which of NHANES, CHARLS, and GBD can support the
   topic.
3. The harness states the research-design boundary and manuscript route.
4. The harness flags whether the topic requires external omics databases for
   bioinformatics or mechanism claims.
5. The resulting plan becomes S0/S1 input for a dataset-specific project.

## Entry Point

```bash
python3 harness/scripts/plan_research_from_topic.py \
  --topic "depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults" \
  --output examples/topic-plans/depression-cognition-cvd-bioinformatics
```

Generated files:

- `topic_plan.json`
- `topic_plan.md`
- `workflow-seed.json`

## Current Scope

The planner supports a deterministic, auditable first pass:

- NHANES: cross-sectional U.S. survey, laboratory/anthropometric/lifestyle
  phenotype and association route.
- CHARLS: aging, depression, cognition, chronic disease, function, and
  longitudinal route after local data/codebook access.
- GBD: disease burden, mortality, DALYs, trends, locations, metrics, and
  uncertainty interval route.

If a topic includes bioinformatics language, such as genes, transcriptomics,
single-cell, GEO, TCGA, GTEx, WGCNA, or immune infiltration, the plan explicitly
states that NHANES/CHARLS/GBD alone cannot support molecular mechanism claims.
Those manuscripts require an external omics module.

## Boundary

This stage does not download data, run analysis, or create manuscript-ready
numeric claims. It produces a planning artifact that must be confirmed in S0/S1
before project instantiation.

## Validation

`harness/validators/validate_topic_plan.py` checks that a plan:

- declares planning-only status;
- scores all three core public database routes;
- includes dataset-specific study design, guideline, required gate, and claim
  boundary;
- contains S0-S9 manuscript workflow stages;
- includes caution language against causal, diagnostic, and mechanism
  overclaiming;
- includes an omics-extension warning when the topic requests bioinformatics
  evidence.

The validator is part of `harness/scripts/run_all_validations.py`.

## Next Step

P8-2 should convert an approved topic plan into one or more dataset-specific
project scaffolds:

- CHARLS design-gate scaffold when longitudinal aging data are primary.
- GBD query-profile scaffold when disease burden is primary.
- NHANES cross-sectional scaffold when U.S. survey phenotyping is primary.
- External omics placeholder only when bioinformatics evidence is required.
