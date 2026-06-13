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
| `results/S8b/figure1_flow.png` and historical `submission_package/figures/figure1_flow.png` copy | 168,271 bytes each before refactor | identical before refactor | P7-17b removed the submission-package copy and retained `results/S8b/figure1_flow.png` as canonical. |
| `results/S8b/figure2_subgroup_prevalence.png` and historical `submission_package/figures/figure2_subgroup_prevalence.png` copy | 293,949 bytes each before refactor | identical before refactor | P7-17b removed the submission-package copy and retained `results/S8b/figure2_subgroup_prevalence.png` as canonical. |

Decision: P7-17b completed the single-source refactor. The results copies are
the canonical files cited by revision traces and checkpoints; the DOCX builder
now embeds those canonical files directly.

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

## P7-17b Single-Source Figure Refactor

P7-17b promotes `examples/nhanes-undiagnosed-diabetes/results/S8b/` to the
canonical location for NHANES generated figures.

Implemented decisions:

- remove duplicate PNG copies from `submission_package/figures/`;
- keep `results/S8b/figure1_flow.png` and
  `results/S8b/figure2_subgroup_prevalence.png` as the only tracked figure
  files;
- update `manuscript_final_generic_sci.md` to cite the canonical result paths;
- update `scripts/build_submission_docx.py` so the submission DOCX embeds the
  canonical result figures directly;
- update `package_manifest.csv` so it no longer lists removed duplicate PNG
  copies;
- update `harness/artifact_policy.json` so future duplicate figure copies are
  blocked by `validate_artifact_policy.py`.

The generated DOCX remains a tracked teaching deliverable, but its embedded
figures now come from a single canonical source.

## Next Cleanup Batch

The next P7-17 batch should choose exactly one remaining artifact class:

1. GBD minimal-demo real default CSV replacement or migration.
2. NHANES large intermediate CSV replacement by checksums or smaller summaries.

Each batch should run full validation and GitHub Actions independently.
