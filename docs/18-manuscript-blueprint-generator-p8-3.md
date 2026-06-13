# P8-3 Manuscript Blueprint Generator

Status: first implementation pass.

Date: 2026-06-13.

## Objective

P8-3 converts instantiated topic scaffolds into manuscript blueprints. This
moves the workflow from "a project folder exists" to "the manuscript structure
is explicit enough to guide writing and analysis."

## Entry Point

Generate blueprints for all supported projects in an instantiation manifest:

```bash
python3 harness/scripts/generate_manuscript_blueprint.py \
  --manifest examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/instantiation_manifest.json
```

Generate a blueprint for one project:

```bash
python3 harness/scripts/generate_manuscript_blueprint.py \
  --project examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd
```

## Generated Artifacts

Each supported project receives:

- `manuscript_blueprint.json`
- `manuscript_blueprint.md`
- `claim_registry.draft.json`

The JSON blueprint records:

- candidate titles;
- research question;
- manuscript type;
- reporting-guideline path;
- Methods framework;
- table and figure shell;
- draft claim registry path;
- readiness gate;
- interpretation boundary.

## Dataset Behavior

Current P8-3 behavior is dataset-specific but still conservative:

- NHANES: cross-sectional complex survey manuscript blueprint.
- CHARLS: longitudinal aging cohort manuscript blueprint.
- GBD: descriptive disease-burden manuscript blueprint.
- External omics: skipped. The repository only records that an external omics
  module is required; it does not generate a fake omics manuscript blueprint.

## Boundary

P8-3 is not a manuscript generator. It does not:

- write final Introduction, Methods, Results, or Discussion sections;
- create source-backed numeric claims;
- run analysis;
- make a project submission-ready;
- claim support for real GEO/TCGA/GTEx/HPA/STRING/KEGG/GO workflows.

The draft claim registry is explicitly marked `draft-not-source-backed`.

## Validation

```bash
python3 harness/validators/validate_manuscript_blueprints.py
```

The validator checks that:

- blueprints use the expected schema and draft status;
- source project manifests and draft claim registries exist;
- Methods and table/figure shells are populated;
- claim registry entries remain draft-only and not source-backed;
- readiness gates explicitly require S3 data execution and S7 integrity checks;
- no blueprint is marked submission-ready.

The validator is part of `harness/scripts/run_all_validations.py`.

## Next Step

P8-4 should turn these blueprints into dataset-specific writing adapters:

- NHANES: survey-weighted cross-sectional Methods and Results shell.
- CHARLS: longitudinal cohort Methods and Results shell.
- GBD: disease-burden Methods and Results shell with GBD citation, UI, metric,
  and age-standardization language.
- Omics: explicit unsupported placeholder until a real external module exists.
