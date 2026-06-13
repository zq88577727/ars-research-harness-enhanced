# P7-16 Repository Artifact Cleanup Plan

Status: planning audit only. No files are deleted or migrated in P7-16 planning.

Date: 2026-06-13.

## Objective

Reduce repository weight and clarify artifact policy without weakening the
research-workflow proof. The repository should remain useful as an inspectable
teaching harness, but it should not become a storage bucket for raw inputs,
large generated packages, or user-specific exports.

## Current Tracked Artifact Inventory

Measured from tracked files in the repository:

| Category | Count | Size | Current role | Recommended action |
| --- | ---: | ---: | --- | --- |
| NHANES raw XPT files under `data/nhanes_2017_2018/raw/` | 12 | 14,878,240 bytes | Public-use teaching input for the complete NHANES closed loop | Keep for now as canonical teaching data; revisit if repository size becomes a barrier |
| Diagram PNG files under `assets/diagrams/` | 4 | 9,833,708 bytes | README/workshop visual explanation | Keep for now; optionally compress in a later visual-asset pass |
| NHANES result CSV files under `examples/nhanes-undiagnosed-diabetes/results/` | 22 | 2,708,573 bytes | Validator-backed result evidence | Keep validator-required tables; identify large intermediate tables for regeneration-only status |
| NHANES DOCX submission packages | 2 | 381,493 bytes | Curated end-to-end manuscript package evidence | Keep one curated final DOCX; consider moving duplicate/alternate DOCX to release artifacts |
| NHANES generated figures | 4 | 924,440 bytes | Submission package and result evidence | Keep one canonical set; avoid adding repeated regenerated copies |
| GBD minimal-demo source export CSVs | 2 | 72,248 bytes | Fixture plus older real default endpoint demo | Keep tiny fixture; consider downgrading/removing real default endpoint CSV after CVD route becomes canonical |

## File-Level Priorities

### P7-16-A Keep

Keep these unless a later release-size target requires stronger action:

- `data/nhanes_2017_2018/raw/*.xpt`
- canonical NHANES S3/S8b result tables used by validators
- canonical NHANES final manuscript Markdown
- P7 GBD CVD query/profile/provenance/derived summaries/review records
- public-release and release-commit audit files

Rationale: these are the evidence trail proving the checkpoint-first research
workflow.

### P7-16-B Move To Release Artifacts Later

Candidate files for GitHub Release artifacts:

- duplicate or alternate NHANES DOCX outputs
- frozen workshop bundles
- high-resolution diagram source/export variants if added later
- repeated generated figures not referenced by validators or README

Rationale: useful for readers, but not always required for source-control
review.

### P7-16-C Regenerate Locally

Candidate files for regeneration-only status:

- large intermediate analytic tables when their validator coverage can be
  replaced by smaller checksums or summary tables
- exploratory tables not referenced by manuscript-number, claim, or readiness
  validators
- future CHARLS or GBD outputs generated from local-only or user-specific
  source exports

Rationale: these should remain reproducible but not necessarily committed.

### P7-16-D Remove Or Replace After Separate Review

Do not remove these automatically, but review them first:

- `examples/gbd-burden-minimal-demo/source_exports/gbd_results_real_default_data.csv`
- duplicate NHANES figure copies under both `results/S8b/` and
  `submission_package/figures/`
- duplicate DOCX variants if one final manuscript package is enough

Rationale: removal changes the public teaching surface and should be done in a
separate scoped commit with updated validators/docs.

## Required Gates Before Any Cleanup Commit

Before deleting, migrating, or replacing any artifact:

```bash
python3 harness/scripts/run_all_validations.py
python3 harness/validators/validate_gbd_public_release_safety.py
git diff --check
```

If an artifact is moved to GitHub Releases, add a committed pointer file or
documentation entry that says how to regenerate or retrieve it.

## Recommended Next Commit Scope

P7-16 should be split into small commits:

1. Add artifact inventory and cleanup policy only.
2. Add validator coverage for artifact expectations, if needed.
3. Move or remove one class of artifacts at a time.
4. Re-run full validation and GitHub Actions after each class.

The first implementation candidate is to audit duplicate NHANES generated
figures and DOCX files, because those are generated outputs with lower
scientific risk than raw teaching data.
