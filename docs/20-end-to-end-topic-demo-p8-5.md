# P8-5 End-To-End Topic Demo

Status: first implementation pass.

Date: 2026-06-13.

## Objective

P8-5 closes the P8 phase by proving that a user can start with one broad topic
and reach usable paper-planning artifacts without manually stitching together
the intermediate files.

The demonstrated chain is:

```text
topic -> topic plan -> project scaffolds -> manuscript blueprint -> writing shells -> readiness gate summary
```

## Entry Point

```bash
python3 harness/scripts/run_topic_to_manuscript_demo.py \
  examples/topic-plans/depression-cognition-cvd-bioinformatics/topic_plan.json
```

Generated files:

- `examples/topic-plans/depression-cognition-cvd-bioinformatics/end_to_end_demo_report.json`
- `examples/topic-plans/depression-cognition-cvd-bioinformatics/end_to_end_demo_report.md`

## What The Demo Proves

The report confirms that:

- P8-1 produced a topic plan;
- P8-2 instantiated CHARLS, GBD, and external-omics boundary projects;
- P8-3 produced manuscript blueprints for supported projects;
- P8-4 produced dataset-specific Methods and Results writing shells;
- CHARLS and GBD remain blocked until source data/export provenance, S3
  execution, source-backed claim registry, and S7 integrity checks exist;
- external omics remains a P10-level future module, not a current capability.

## Boundary

P8-5 is a workflow demo, not a real manuscript production run. It does not
prove:

- CHARLS data access;
- GBD export availability for a new query;
- source-backed results;
- valid omics analysis;
- submission readiness.

## Validation

```bash
python3 harness/validators/validate_topic_to_manuscript_demo.py
```

The validator checks that:

- the demo report uses the expected schema;
- the report status is `demo-ready-not-submission-ready`;
- P8-1 through P8-4 are represented in the workflow chain;
- CHARLS, GBD, and external-omics boundary outputs are present;
- CHARLS and GBD are marked not ready for results or submission;
- the external-omics item points to P10 before mechanism claims;
- the overall boundary states that data access, source-backed results, and
  submission readiness are not proven.

The validator is part of `harness/scripts/run_all_validations.py`.

## P8 Completion

After P8-5, the project can start a manuscript project from a topic. It still
does not automatically complete a real paper. That is the purpose of P9:

- P9-1: select a real main manuscript topic;
- P9-2: instantiate CHARLS + GBD dual-database project;
- P9-3: generate manuscript draft v0 with replaceable result sections;
- P9-4: run pre-submission gates for claims, citation, methods/results
  consistency, data boundaries, ethics, and reproducibility.
