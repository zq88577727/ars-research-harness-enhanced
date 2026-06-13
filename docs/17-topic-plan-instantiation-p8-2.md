# P8-2 Topic Plan Instantiation

Status: first implementation pass.

Date: 2026-06-13.

## Objective

P8-2 converts an approved topic plan into dataset-specific project scaffolds.
The goal is to move from "the harness can recommend databases" to "the harness
can start a concrete manuscript project from a topic."

## Entry Point

```bash
python3 harness/scripts/instantiate_from_topic_plan.py \
  examples/topic-plans/depression-cognition-cvd-bioinformatics/topic_plan.json
```

Default output:

```text
examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/
```

## Generated Artifacts

For each recommended supported data source, the script creates:

- `project_manifest.json`
- `workflow-run.json`
- `README.md`
- `checkpoints/stage-S0-intake.md`
- `checkpoints/stage-S1-research-question.md`
- `checkpoints/stage-S2-method-plan.md`
- placeholder S3-S9 checkpoint files

Dataset-specific files are added where applicable:

- CHARLS: file manifest, wave map, variable map, codebook import sample,
  variable-mapping decision file, and S1/S2 design gate.
- GBD: query manifest and analysis manifest.
- NHANES: variable-target seed file when NHANES is selected.

If the topic requests bioinformatics or molecular-mechanism evidence, the
script creates an `external_omics` placeholder project with
`external_omics_required.md`. This is a boundary artifact, not a supported
omics analysis module.

## Example

The current demonstration topic is:

```text
depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults
```

The instantiated example creates:

- a CHARLS longitudinal-cohort scaffold;
- a GBD disease-burden scaffold;
- an external-omics boundary placeholder.

## Boundary

P8-2 is scaffold-only. It does not:

- download NHANES, CHARLS, GBD, GEO, TCGA, GTEx, HPA, STRING, KEGG, or GO data;
- run statistical or bioinformatics analysis;
- create source-backed numeric claims;
- generate a manuscript draft;
- make a scaffold submission-ready.

The generated projects are S0-S2 starting points. They must be reviewed before
S3 data execution, claim registry creation, or manuscript drafting.

## Validation

```bash
python3 harness/validators/validate_topic_scaffolds.py
```

The validator checks that:

- the instantiation manifest uses the expected schema and scaffold-only status;
- source topic plan and project manifests exist;
- CHARLS, GBD, and NHANES required scaffold files are present where relevant;
- external omics is explicitly marked unsupported by the current harness;
- generated files do not retain `<project-slug>` placeholders or
  `examples/examples` path duplication;
- manifest path references point to files that exist.

The validator is part of `harness/scripts/run_all_validations.py`.

## Next Step

P8-3 should generate a manuscript blueprint from one instantiated project:

- candidate title;
- refined research question;
- Methods framework;
- table and figure shell;
- initial claim registry draft;
- reporting checklist path such as STROBE or GATHER.
