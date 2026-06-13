# P7-17 Artifact Cleanup Implementation

Status: first implementation pass.

Date: 2026-06-13.

## Scope

P7-17 starts from the P7-16 cleanup plan and implements artifact policy
enforcement before deleting or migrating scientific evidence files.

This pass deliberately does not move or delete NHANES raw XPT files. They are
public-use teaching inputs for the complete NHANES closed-loop example.

## Artifact Audit

### NHANES DOCX

Tracked DOCX files:

| Path | Size | Decision |
| --- | ---: | --- |
| `examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_generic_sci.docx` | 54,062 bytes | Keep. Listed in `package_manifest.csv` as a generic final DOCX. |
| `examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_with_tables_figures.docx` | 327,431 bytes | Keep. Documented as the primary teaching deliverable with embedded tables and figures. |

Decision: no DOCX deletion in this pass. The files are small and currently
serve different reader-facing roles.

### NHANES PNG Figures

Tracked figure copies:

| Pair | Size | SHA-256 status | Decision |
| --- | ---: | --- | --- |
| `results/S8b/figure1_flow.png` and `submission_package/figures/figure1_flow.png` | 168,271 bytes each | identical | Keep pending a single-source figure refactor. |
| `results/S8b/figure2_subgroup_prevalence.png` and `submission_package/figures/figure2_subgroup_prevalence.png` | 293,949 bytes each | identical | Keep pending a single-source figure refactor. |

Decision: do not delete either copy in this pass. The results copies are cited
by revision traces and checkpoints; the submission-package copies are listed in
the package manifest and consumed by the DOCX builder.

### GBD Minimal Demo CSV

Tracked source export CSV files:

| Path | Size | Decision |
| --- | ---: | --- |
| `examples/gbd-burden-minimal-demo/source_exports/gbd_results_minimal_fixture.csv` | 533 bytes | Keep as the tiny offline teaching fixture. |
| `examples/gbd-burden-minimal-demo/source_exports/gbd_results_real_default_data.csv` | 71,715 bytes | Keep pending replacement. It is still referenced by the query manifest, claim registry, analysis manifest, and provenance. |

Decision: no GBD minimal-demo CSV deletion in this pass. The legacy real default
CSV should be replaced only in a separate scoped commit after the demo is
converted to a smaller fixture or local-only export route.

## Implemented Enforcement

P7-17 adds:

- `harness/artifact_policy.json`
- `harness/validators/validate_artifact_policy.py`
- `harness/scripts/run_all_validations.py` gate integration

The validator blocks:

- tracked CHARLS raw data or official codebooks;
- tracked GBD raw directories;
- tracked GBD CVD raw source-export CSVs;
- source-export CSVs that are not reviewed in the policy;
- large tracked files that are not reviewed in the policy;
- reviewed duplicate figure groups whose files diverge unexpectedly.

The validator warns, but does not fail, for reviewed transitional artifacts such
as the duplicate NHANES figure copies and the legacy GBD real default CSV.

## Next Cleanup Batch

The next P7-17 batch should choose exactly one artifact class:

1. NHANES figure single-source refactor.
2. GBD minimal-demo real default CSV replacement or migration.
3. NHANES large intermediate CSV replacement by checksums or smaller summaries.

Each batch should run full validation and GitHub Actions independently.
