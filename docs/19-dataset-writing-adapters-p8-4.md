# P8-4 Dataset-Specific Writing Adapters

Status: first implementation pass.

Date: 2026-06-13.

## Objective

P8-4 turns manuscript blueprints into dataset-specific writing shells. The goal
is to prevent one generic medical-paper template from blurring study designs:
NHANES, CHARLS, and GBD need different Methods and Results language.

## Entry Point

Generate writing adapters for all supported blueprints in an instantiation
manifest:

```bash
python3 harness/scripts/generate_dataset_writing_adapter.py \
  --manifest examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/instantiation_manifest.json
```

Generate one adapter from one blueprint:

```bash
python3 harness/scripts/generate_dataset_writing_adapter.py \
  --blueprint examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/manuscript_blueprint.json
```

## Generated Artifacts

Each supported project receives:

- `writing_adapter.json`
- `methods_shell.md`
- `results_shell.md`

## Dataset Boundaries

NHANES adapter:

- manuscript type: cross-sectional complex survey;
- required language: weighted cross-sectional estimate, survey design,
  association;
- blocked language: caused, diagnosed, incidence, longitudinal change.

CHARLS adapter:

- manuscript type: longitudinal aging cohort;
- required language: longitudinal association, wave linkage, attrition;
- blocked language: caused, prevented, mechanism, clinical diagnosis.

GBD adapter:

- manuscript type: disease-burden analysis;
- required language: GBD release, uncertainty interval, age-standardized,
  all-age count;
- blocked language: patient-level, risk factor effect, mechanism,
  intervention effect.

External omics:

- no adapter is generated;
- the current repository only records that real GEO/TCGA/GTEx/HPA/STRING/KEGG/GO
  support would require a separate module.

## Boundary

P8-4 does not generate final manuscript text. The Methods and Results shells are
structured TODO files that are blocked until:

- S3 data execution exists;
- source/export provenance exists;
- claim registry is source-backed;
- S7 integrity and citation checks pass.

## Validation

```bash
python3 harness/validators/validate_dataset_writing_adapters.py
```

The validator checks that:

- adapters use the expected schema and shell-only status;
- source blueprint and shell files exist;
- required dataset-specific language is present;
- prohibited-language lists are present;
- shells still contain TODO boundaries;
- adapters remain non-final manuscript shells.

The validator is part of `harness/scripts/run_all_validations.py`.

## Next Step

P8-5 should run an end-to-end user demo:

```text
topic -> topic plan -> project scaffolds -> manuscript blueprint -> writing shells -> readiness gate summary
```

The demo should prove the user can start from one topic and reach usable paper
planning artifacts without hand-selecting every intermediate file.
