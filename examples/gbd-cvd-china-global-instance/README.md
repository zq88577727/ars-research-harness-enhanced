# GBD CVD China-global targeted instance

Data source: `gbd`

Status: source-backed manuscript candidate, not submission-ready

This instance selects the P0 candidate `gbd-cvd-china-global-1990-2023` from
`examples/gbd-burden-minimal-demo/gbd_targeted_query_candidates.csv`. It is the
next real GBD manuscript route after the all-cause minimal demo.

## Research Question

How did the cardiovascular disease burden in China compare with the global
burden from 1990 to 2023 in GBD 2023?

## Target Statement

This is a descriptive disease-burden instance. It compares China and global
cardiovascular disease deaths and DALYs using all-age counts and
age-standardized rates from a verified GBD Results Tool export.
It must not be framed as causal, mechanistic, clinical, or policy-effect
evidence.

## Included Files

- `project_manifest.json`: project-level wiring for the targeted GBD instance.
- `gbd_cvd_query_manifest.csv`: planned query rows for CVD, China/global,
  1990/2023, deaths/DALYs, number/rate.
- `gbd_cvd_query_profile.json`: targeted query profile covering release,
  dimensions, metric separation, age-standardization, uncertainty intervals,
  citation, and reuse boundary.
- `gbd_cvd_analysis_manifest.json`: manifest-driven source export, derived
  summary, provenance, and source-backed claim-upgrade contract.
- `claim_registry.json`: manuscript-specific claim registry. The four numeric
  CVD claims are source-backed manuscript candidates, not submission-ready
  claims.
- `source_exports/gbd_cvd_china_global_1990_2023.csv`: real GBD Results Tool
  export supplied from the user account. This file is local-only and ignored by
  default; it is not part of the public commit scope.
- `source_exports/gbd_cvd_citation.txt`: citation text supplied with the GBD
  export.
- `results/gbd_cvd_china_global_summary.csv`: derived source-backed summary.
- `results/gbd_cvd_provenance.json`: provenance file with source and output
  hashes.
- `gbd_cvd_claim_review_checklist.csv`: P7-7 human review checklist for
  candidate CVD claims.
- `gbd_cvd_claim_review_decisions.json`: P7-8 editable human decision file.
- `gbd_cvd_claim_review_decision_record.json`: P7-8 generated audit record
  summarizing the current claim-review decisions.
- `gbd_cvd_claim_review_helper.csv`: P7-9 tabular review helper combining
  source-backed values, UI, metric/age boundaries, and recommended actions.
- `gbd_cvd_claim_review_helper.md`: P7-9 Markdown review helper for manual
  claim-by-claim review.
- `gbd_cvd_manuscript_review_draft.md`: controlled methods/results fragment
  used to audit claim wording and UI completeness.
- `gbd_cvd_manuscript_fragment.md`: P7-11 formal manuscript-review-ready
  fragment that incorporates the P7-10 reviewed rewrite/downgrade decisions.
- `gbd_cvd_citation_policy_review.md`: P7-12-1 citation policy review tied to
  the export-supplied GBD Results Tool citation.
- `gbd_cvd_reuse_review.md`: P7-12-2 reuse review for source export, derived
  summary, repository, and release-artifact boundaries.
- `gbd_cvd_manuscript_section_draft.md`: P7-12-3 target-journal-oriented
  Methods, Results, Limitations, and Data Availability draft.
- `public_release_audit.md`: P7-13 file-classification audit for open-source
  release safety.
- `release_commit_scope_audit.md`: P7-14 commit-scope audit separating public
  repository files from local-only source exports and generated caches.
- `submission_readiness_gate.md`: pre-submission blocker documenting why this
  source-backed candidate is not submission-ready.

## P7-6 Export Path

The runtime could inspect the public GBD Results Tool metadata, but the targeted
`php/data.php` export path returned a browser challenge when called directly.
Therefore, this instance uses a conservative manual-export ingestion path. The
approved CSV is stored at:

```text
examples/gbd-cvd-china-global-instance/source_exports/gbd_cvd_china_global_1990_2023.csv
```

Expected dimensions must match `gbd_cvd_query_manifest.csv`: GBD 2023
`version_id` 8352, cardiovascular diseases, China and Global, Both sexes, 1990
and 2023, Deaths and DALYs, all-age counts and age-standardized rates, with
`val`, `lower`, and `upper`.

Regenerate the source-backed artifacts:

```bash
python3 scripts/generate_gbd_targeted_results.py --project examples/gbd-cvd-china-global-instance --dry-run
python3 scripts/generate_gbd_targeted_results.py --project examples/gbd-cvd-china-global-instance
python3 harness/validators/validate_gbd_targeted_scaffold.py --require-export
```

The generator writes `results/gbd_cvd_china_global_summary.csv`,
`results/gbd_cvd_china_global_summary.md`,
`results/gbd_cvd_provenance.json`, and
`claim_registry.source_backed.json`. The reviewed source-backed registry has
been promoted to `claim_registry.json`.

## P7-7 Submission-Readiness Gate

Run the manuscript-review package gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py \
  --require-manuscript-review-ready
```

Run the strict submission gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py \
  --require-submission-ready
```

The strict gate is expected to fail until human claim-review decisions, final
IHME/GHDx citation wording, reuse-term confirmation, and complete target-journal
manuscript context are available.

## P7-8 Claim Review Decision Loop

Edit `gbd_cvd_claim_review_decisions.json` one claim at a time. Allowed
decisions are:

- `approve`: retain as a manuscript candidate; not submission-ready by itself.
- `rewrite`: retain only with `replacementText`.
- `downgrade`: keep as supporting, table-only, supplement-only, or boundary
  text.
- `delete`: remove from manuscript use.

Generate an audit record without changing the checklist:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py
```

Require all five decisions to be reviewed:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py \
  --require-reviewed
```

After human review is complete, update the checklist from the decision file:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py \
  --require-reviewed \
  --update-checklist
```

## P7-9 Claim Review Helper

Generate the table used by human reviewers before editing the decision file:

```bash
python3 harness/scripts/generate_gbd_cvd_claim_review_helper.py
```

The helper reads the source-backed summary, claim registry, review checklist,
and current decision file, then writes `gbd_cvd_claim_review_helper.csv` and
`gbd_cvd_claim_review_helper.md`. It centralizes the five candidate claims with
their source-backed values, uncertainty intervals, metric boundary, age boundary,
wording boundary, current decision, recommended decision, and allowed action
set. It is decision support only; the auditable human action remains editing
`gbd_cvd_claim_review_decisions.json` followed by the P7-8 decision-record
command.

## P7-10 Reviewed Claim Decisions

The five CVD candidate claims have been reviewed through the decision loop:

- Scope boundary: `approve`.
- China all-age CVD deaths Number claim: `rewrite`.
- China all-age CVD DALYs Number claim: `rewrite`.
- China-global age-standardized CVD death-rate claim: `rewrite`.
- China-global age-standardized CVD DALY-rate claim: `downgrade`.

The reviewed decision record is generated with:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py \
  --require-reviewed \
  --update-checklist
python3 harness/scripts/generate_gbd_cvd_claim_review_helper.py
```

This closes the project-level claim-review loop, but it does not make the claims
submission-ready. Final submission still requires target-journal wording,
IHME/GHDx citation wording, reuse-term confirmation, and full manuscript context.

## P7-11 Manuscript Fragment Consistency Gate

The P7-10 reviewed decisions are incorporated into
`gbd_cvd_manuscript_fragment.md`. This fragment is separate from the earlier
review draft: it is the controlled Methods/Results text used to test whether
reviewed claim wording, claim registry coverage, and decision-record status are
internally consistent.

Run the consistency gate:

```bash
python3 harness/validators/validate_gbd_cvd_manuscript_fragment.py
```

The gate verifies that all five candidate claim IDs are linked, all three
`rewrite` replacement texts appear in Results, the downgraded DALY-rate claim is
kept as supporting/table-only evidence, Methods preserve GBD release and query
dimensions, and no causal, clinical, mechanistic, or policy-effect wording is
introduced.

## P7-12 Submission Package Evidence Layer

P7-12 adds the citation, reuse, and manuscript-section evidence layer needed
before any final submission decision:

- `gbd_cvd_citation_policy_review.md` records the export-supplied citation,
  source citation hash, recommended manuscript citation draft, and remaining
  journal/IHME wording confirmations.
- `gbd_cvd_reuse_review.md` records source-export and derived-summary hashes,
  size checks, repository retention boundaries, and release-artifact boundaries.
- `gbd_cvd_manuscript_section_draft.md` converts the P7-11 fragment into
  Methods, Results, Limitations, and Data Availability draft sections.

Run the P7-12 package gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_package.py
```

This gate can pass while the strict submission gate still fails. That is the
intended state: P7-12 makes the package reviewable, but final submission still
requires human confirmation of citation style, reuse terms, and target-journal
context.

## P7-13 Public Release Safety

The raw GBD Results Tool CSV is local-only by default and is ignored by
`.gitignore`. The source citation, query metadata, provenance metadata, derived
aggregate summaries, and compliance reviews can be committed as the reviewable
open-source package.

Run the public-release safety gate:

```bash
python3 harness/validators/validate_gbd_public_release_safety.py
```

The gate fails if `source_exports/gbd_cvd_china_global_1990_2023.csv` or other
restricted/raw data files are tracked or staged. See `public_release_audit.md`
for the file-by-file release classification.

## P7-14 Release Commit Scope

`release_commit_scope_audit.md` records the intended public commit scope for
this release. It explicitly excludes the raw GBD source export, CHARLS raw data,
CHARLS local codebooks, reserved GBD raw-data directories, and generated Python
caches. It recommends a scoped commit only after the public-release safety gate,
the CI-safe submission package gate, and the full validation runner pass.

## Boundary

This folder now contains a small real CVD GBD export and provenance-backed
derived results. It may support manuscript candidate wording, but not final
submission. Submission-ready status still requires human confirmation of
IHME/GHDx reuse terms, journal-specific citation wording, uncertainty interval
presentation, and final manuscript context.
