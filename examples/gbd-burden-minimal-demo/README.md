# GBD burden minimal demo

Data source: `gbd`

Status: fixture-only teaching demo plus a real GBD Results Tool default
endpoint export. This folder demonstrates how a GBD-style query manifest, tiny
export fixture, real default endpoint output, derived result tables, narrative
summaries, and claim registry can move through the harness to S7 integrity
checking.

This is not a publishable burden study and is no longer the manuscript route.
Real GBD manuscript scaffolding has moved to
`examples/gbd-cvd-china-global-instance/`.

## Research Question

Can a minimal GBD Results-style export be traced from query dimensions to a
derived burden summary and source-backed claims?

The earlier all-cause manuscript rehearsal question is retained only as project
history. Current real-topic work uses the selected CVD China/global scaffold.

## What Is Included

- `gbd_query_manifest.csv`: exact query dimensions for the teaching fixture and
  real default endpoint rows.
- `gbd_query_profile.json`: GATHER-style GBD query profile audit covering
  release/version, metric separation, age-standardization status, uncertainty
  interval policy, citation requirements, and reuse boundaries.
- `gbd_analysis_manifest.json`: manifest-driven analysis control file that
  declares source exports, output artifacts, dimension filters, years, and
  interpretation boundaries used by the generator and validator.
- `source_exports/gbd_results_minimal_fixture.csv`: small committed fixture in a
  GBD Results-style table shape.
- `source_exports/gbd_results_real_default_data.csv`: real GBD Results Tool
  public default endpoint output downloaded on 2026-06-11.
- `results/gbd_minimal_summary.csv`: derived summary produced by
  `scripts/generate_gbd_minimal_results.py`.
- `results/gbd_real_default_summary.csv`: derived summary from the real default
  endpoint output.
- `results/gbd_minimal_summary.md`: manuscript-style result paragraph with
  explicit interpretation boundaries.
- `results/gbd_provenance.json`: machine-readable provenance sidecar linking
  the analysis manifest, query manifest, source exports, output hashes, endpoint
  metadata, and interpretation boundaries.
- `submission_readiness_gate.md`: reader-facing summary of the strict GBD
  submission blockers and claim-upgrade requirements.
- `claim_registry.json`: source-backed claim registry for S7 checking.
- `gbd_claim_review_checklist.csv`: human review checklist for the 4
  manuscript-specific candidate claims, including retain/rewrite/downgrade/delete
  options and citation, UI, metric, and age rules.
- `gbd_manuscript_review_draft.md`: short review draft with data source,
  methods, results, limitations, and required review decisions.
- `gbd_topic_upgrade_decision.md`: P7-4 decision record explaining why the
  current global all-cause demo remains a fixture and must not be promoted
  directly to submission-ready.
- `gbd_targeted_query_candidates.csv`: candidate matrix for selecting a real
  disease-specific or location-specific GBD query before generating new
  manuscript claims.
- `workflow-run.json`: checkpoint state through S7.

## Regenerate Results

```bash
python3 scripts/fetch_gbd_export.py --dry-run
# To intentionally refresh the committed demo export:
# python3 scripts/fetch_gbd_export.py --force
python3 scripts/generate_gbd_minimal_results.py
python3 harness/validators/validate_gbd_minimal_demo.py
```

`scripts/fetch_gbd_export.py` reads the `download` block in
`gbd_analysis_manifest.json`. It refuses to overwrite an existing export unless
`--force` is supplied, writes endpoint/date/source-note metadata into the CSV,
and is intended only for public or otherwise approved GBD export routes.
`scripts/generate_gbd_minimal_results.py` regenerates summary outputs and
`results/gbd_provenance.json`; the validator checks that each query-manifest row
matches source rows and that the provenance hashes match the current source and
output files.
`harness/validators/validate_gbd_minimal_demo.py` also checks
`gbd_query_profile.json` so that release/version, metric type, uncertainty
interval fields, age-standardization wording, citation readiness, and reuse
boundaries are explicit before GBD claims are promoted beyond demo status.
`harness/validators/validate_gbd_submission_readiness.py` combines the query
profile, provenance sidecar, claim registry, citation policy, and reuse boundary
into a submission gate. Default mode now recognizes the query profile as
`manuscript-review-ready`; strict mode with `--require-submission-ready` still
fails until manuscript-specific candidate claims are promoted, final citation and
reuse wording are confirmed, and teaching-fixture claims remain internal-only.
Use `--require-manuscript-review-ready` when CI should require the review
checklist and manuscript review draft, without pretending the project is ready
for journal submission. Use `--require-topic-upgrade-decision` when CI should
also require the P7-4 topic-upgrade decision and targeted query candidate
matrix, so the all-cause demo cannot be treated as a final manuscript topic by
default.

## Boundary

Counts, rates, percentages, age-standardized estimates, and uncertainty
intervals must not be mixed. This demo uses two global all-cause number rows as
a traceability fixture only. A real GBD manuscript must record release version,
measure, metric, cause, location, age, sex, year, export date, citation, and
permitted redistribution route.

Before real GBD manuscript drafting, choose a row from
`gbd_targeted_query_candidates.csv` or add a better targeted query candidate.
The selected row is now `gbd-cvd-china-global-1990-2023`; the instantiated
scaffold is `examples/gbd-cvd-china-global-instance/`. The current global
all-cause claims are fixture-only and should not be upgraded directly to
`submission-ready`.
