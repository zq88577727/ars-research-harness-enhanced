# GBD CVD Submission Readiness Gate

Status: source-backed manuscript candidate, not submission-ready

This gate combines the CVD query profile, source export, provenance sidecar,
derived summary, claim registry, citation policy, reuse boundary, human review
checklist, and manuscript review draft. It is a pre-submission blocker, not a
submission approval.

## Current Evidence Package

- Query profile: `gbd_cvd_query_profile.json`
- Query manifest: `gbd_cvd_query_manifest.csv`
- Analysis manifest: `gbd_cvd_analysis_manifest.json`
- Source export: `source_exports/gbd_cvd_china_global_1990_2023.csv`
- Source citation: `source_exports/gbd_cvd_citation.txt`
- Derived summary: `results/gbd_cvd_china_global_summary.csv`
- Provenance: `results/gbd_cvd_provenance.json`
- Claim registry: `claim_registry.json`
- Human review checklist: `gbd_cvd_claim_review_checklist.csv`
- Human review decisions: `gbd_cvd_claim_review_decisions.json`
- Human review decision record: `gbd_cvd_claim_review_decision_record.json`
- Claim review helper CSV: `gbd_cvd_claim_review_helper.csv`
- Claim review helper Markdown: `gbd_cvd_claim_review_helper.md`
- Manuscript review draft: `gbd_cvd_manuscript_review_draft.md`
- Manuscript fragment: `gbd_cvd_manuscript_fragment.md`
- Citation policy review: `gbd_cvd_citation_policy_review.md`
- Reuse review: `gbd_cvd_reuse_review.md`
- Manuscript section draft: `gbd_cvd_manuscript_section_draft.md`

## Current Blockers

- Query profile status is `source-backed-manuscript-candidate`, not
  `submission-ready`.
- Citation status is `source-citation-recorded`; P7-12 citation review is
  complete for submission-package review, but not final journal-ready.
- Reuse boundary is `source-export-terms-review-required`; IHME/GHDx reuse and
  redistribution terms have been reviewed for package boundaries but still
  require human confirmation before public release or final submission.
- Claim review decisions are complete at the project-review level, but no claim
  is approved for final submission until citation wording, reuse terms, and
  target-journal manuscript context are confirmed.
- The P7-11 manuscript fragment is internally consistent with reviewed claims,
  but it is still a controlled fragment rather than a complete target-journal
  manuscript.
- The P7-12 manuscript section draft is suitable for package review, but not a
  complete target-journal manuscript.

## Required Submission Upgrade Criteria

1. Confirm IHME/GHDx citation wording against the exact target journal style.
2. Confirm reuse and redistribution terms for the exact CSV and derived summary.
3. Confirm the P7-10 claim decisions against the final author-approved
   manuscript wording.
4. Confirm all numeric claims carry UI values and do not call UI confidence
   intervals or p values.
5. Confirm all-age Number claims and age-standardized Rate claims remain
   separate.
6. Confirm methods and results fragments use the same query dimensions,
   source files, release, version_id, measures, metrics, age categories, sex,
   years, and interpretation boundary.
7. Update `project_manifest.json`, `gbd_cvd_query_profile.json`, and
   `claim_registry.json` to `submission-ready` only after the prior criteria
   pass.

## Gate Commands

Informational gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py
```

Manuscript-review package gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py \
  --require-manuscript-review-ready
```

Strict submission gate, expected to fail until the blockers above are closed:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py \
  --require-submission-ready
```

Claim decision loop:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py --require-reviewed
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py --require-reviewed --update-checklist
```

Claim review helper:

```bash
python3 harness/scripts/generate_gbd_cvd_claim_review_helper.py
```

Manuscript fragment consistency gate:

```bash
python3 harness/validators/validate_gbd_cvd_manuscript_fragment.py
```

Submission package evidence gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_package.py
```

P7-10 reviewed decision loop:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py --require-reviewed --update-checklist
python3 harness/scripts/generate_gbd_cvd_claim_review_helper.py
```
