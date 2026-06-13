# GBD CVD Release Commit Scope Audit

Status: P7-14 release commit scope review.

## Decision

Proceed with a scoped public commit after the validation suite passes.

Do not use `git add .` for this release. Stage only the public-reviewable
workflow, manifest, validator, derived-summary, citation, reuse, and review
artifacts listed below. Keep raw/restricted source data local unless a separate
license/reuse review explicitly allows redistribution.

## Public Commit Scope

These files are suitable for public repository review in this release:

| Scope | Files |
| --- | --- |
| Repository policy and roadmap | `.gitignore`, `DATA_POLICY.md`, `ROADMAP.md` |
| Documentation | `docs/08-enhanced-validation-roadmap.md`, `docs/10-charls-gbd-onboarding.zh-CN.md`, `harness/checkpoint-first-workflow.md` |
| CHARLS blocker tracking | `examples/charls-depression-cognition-instance/README.md`, `examples/charls-depression-cognition-instance/charls_file_manifest.csv`, `examples/charls-depression-cognition-instance/project_manifest.json`, `examples/charls-depression-cognition-instance/external_blockers.md` |
| GBD minimal fixture and topic-selection history | `examples/gbd-burden-minimal-demo/README.md`, `examples/gbd-burden-minimal-demo/claim_registry.json`, `examples/gbd-burden-minimal-demo/gbd_analysis_manifest.json`, `examples/gbd-burden-minimal-demo/gbd_query_profile.json`, `examples/gbd-burden-minimal-demo/gbd_targeted_query_candidates.csv`, `examples/gbd-burden-minimal-demo/gbd_topic_upgrade_decision.md`, `examples/gbd-burden-minimal-demo/gbd_claim_review_checklist.csv`, `examples/gbd-burden-minimal-demo/gbd_manuscript_review_draft.md`, `examples/gbd-burden-minimal-demo/project_manifest.json`, `examples/gbd-burden-minimal-demo/submission_readiness_gate.md`, `examples/gbd-burden-minimal-demo/results/gbd_provenance.json`, `examples/gbd-burden-minimal-demo/results/gbd_real_default_summary.csv`, `examples/gbd-burden-minimal-demo/results/gbd_real_default_summary.md` |
| GBD CVD manuscript-candidate instance | `examples/gbd-cvd-china-global-instance/README.md`, `examples/gbd-cvd-china-global-instance/project_manifest.json`, `examples/gbd-cvd-china-global-instance/gbd_cvd_query_manifest.csv`, `examples/gbd-cvd-china-global-instance/gbd_cvd_query_profile.json`, `examples/gbd-cvd-china-global-instance/gbd_cvd_analysis_manifest.json`, `examples/gbd-cvd-china-global-instance/claim_registry.json`, `examples/gbd-cvd-china-global-instance/claim_registry.source_backed.json`, `examples/gbd-cvd-china-global-instance/gbd_cvd_claim_review_checklist.csv`, `examples/gbd-cvd-china-global-instance/gbd_cvd_claim_review_decisions.json`, `examples/gbd-cvd-china-global-instance/gbd_cvd_claim_review_decision_record.json`, `examples/gbd-cvd-china-global-instance/gbd_cvd_claim_review_helper.csv`, `examples/gbd-cvd-china-global-instance/gbd_cvd_claim_review_helper.md`, `examples/gbd-cvd-china-global-instance/gbd_cvd_manuscript_review_draft.md`, `examples/gbd-cvd-china-global-instance/gbd_cvd_manuscript_fragment.md`, `examples/gbd-cvd-china-global-instance/gbd_cvd_manuscript_section_draft.md`, `examples/gbd-cvd-china-global-instance/gbd_cvd_citation_policy_review.md`, `examples/gbd-cvd-china-global-instance/gbd_cvd_reuse_review.md`, `examples/gbd-cvd-china-global-instance/public_release_audit.md`, `examples/gbd-cvd-china-global-instance/release_commit_scope_audit.md`, `examples/gbd-cvd-china-global-instance/submission_readiness_gate.md` |
| GBD CVD public derived artifacts | `examples/gbd-cvd-china-global-instance/results/README.md`, `examples/gbd-cvd-china-global-instance/results/gbd_cvd_china_global_summary.csv`, `examples/gbd-cvd-china-global-instance/results/gbd_cvd_china_global_summary.md`, `examples/gbd-cvd-china-global-instance/results/gbd_cvd_provenance.json` |
| GBD CVD citation evidence | `examples/gbd-cvd-china-global-instance/source_exports/README.md`, `examples/gbd-cvd-china-global-instance/source_exports/gbd_cvd_citation.txt` |
| Scripts and validators | `harness/scripts/run_all_validations.py`, `harness/scripts/apply_gbd_cvd_claim_review_decisions.py`, `harness/scripts/generate_gbd_cvd_claim_review_helper.py`, `harness/validators/validate_gbd_minimal_demo.py`, `harness/validators/validate_gbd_submission_readiness.py`, `harness/validators/validate_gbd_targeted_scaffold.py`, `harness/validators/validate_gbd_cvd_submission_readiness.py`, `harness/validators/validate_gbd_cvd_manuscript_fragment.py`, `harness/validators/validate_gbd_cvd_submission_package.py`, `harness/validators/validate_gbd_public_release_safety.py`, `scripts/generate_gbd_minimal_results.py`, `scripts/generate_gbd_targeted_results.py` |

## Local-Only Exclusions

These files or directories must not be committed or packaged for a public
release:

| Path | Reason |
| --- | --- |
| `examples/gbd-cvd-china-global-instance/source_exports/gbd_cvd_china_global_1990_2023.csv` | Real GBD Results Tool source export; local-only until redistribution permission is confirmed |
| `data/gbd/raw/` | Reserved for raw GBD downloads; not repository content |
| `data/charls/raw/` | Restricted CHARLS respondent-level data; never repository content |
| `data/charls/codebooks/` | CHARLS local codebook/questionnaire workspace; keep local unless redistribution terms permit publication |
| `harness/scripts/__pycache__/`, `harness/validators/__pycache__/`, `scripts/__pycache__/` | Generated Python bytecode cache |

## Existing Tracked Artifacts To Revisit Separately

The repository already tracks NHANES raw XPT files, NHANES figures/DOCX outputs,
and the older GBD minimal-demo real default endpoint CSV. P7-14 does not remove
or rewrite those historical artifacts. A later repository-size and data-policy
cleanup should decide whether to migrate bulky teaching outputs to releases or
replace real GBD demo exports with smaller synthetic fixtures.

## Pre-Commit Gate

Run the following before committing:

```bash
python3 harness/validators/validate_gbd_public_release_safety.py
python3 harness/validators/validate_gbd_cvd_submission_package.py --allow-missing-source-export
python3 harness/scripts/run_all_validations.py
```

The strict local package gate can also be run when the local GBD source export is
available:

```bash
python3 harness/validators/validate_gbd_cvd_submission_package.py
```

## Commit Recommendation

Commit and push only after the scoped public files above are staged and the
local-only exclusions remain unstaged/ignored. The recommended commit message is:

```text
Add GBD CVD public release readiness gates
```
