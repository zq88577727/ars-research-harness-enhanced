# P8 End-to-End Topic-To-Manuscript Demo

Status: `demo-ready-not-submission-ready`
Topic: depression, cognitive decline, cardiovascular disease burden, and bioinformatics mechanisms in older adults

## Workflow Chain

- `P8-1 topic plan`: examples/topic-plans/depression-cognition-cvd-bioinformatics/topic_plan.json
- `P8-2 project scaffolds`: examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/instantiation_manifest.json
- `P8-3 manuscript blueprints`: project-level manuscript_blueprint.json files
- `P8-4 writing adapters`: project-level writing_adapter.json and shell files

## Project Outputs

### charls

Project: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-charls`
Status: `supported-demo-project`

Manuscript type: longitudinal aging cohort manuscript
Blueprint: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-charls/manuscript_blueprint.json`
Writing adapter: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-charls/writing_adapter.json`
Methods shell: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-charls/methods_shell.md`
Results shell: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-charls/results_shell.md`
Readiness: `not-ready-for-results-or-submission`

Blocked until:

- S3 data execution exists
- source/export provenance exists
- claim registry is source-backed
- S7 integrity and citation checks pass

### gbd

Project: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd`
Status: `supported-demo-project`

Manuscript type: GBD descriptive disease-burden manuscript
Blueprint: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/manuscript_blueprint.json`
Writing adapter: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/writing_adapter.json`
Methods shell: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/methods_shell.md`
Results shell: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-gbd/results_shell.md`
Readiness: `not-ready-for-results-or-submission`

Blocked until:

- S3 data execution exists
- source/export provenance exists
- claim registry is source-backed
- S7 integrity and citation checks pass

### external_omics

Project: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-external-omics`
Status: `external-omics-boundary`

Boundary artifact: `examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/depression-cognitive-decline-cardiovascular-disease-burden-and-bioinfo-external-omics/external_omics_required.md`
Next required: P10 external omics module before mechanism claims.

## Overall Boundary

This demo proves topic-to-project startup and writing scaffolding. It does not prove data access, analysis execution, source-backed results, omics support, or submission readiness.
