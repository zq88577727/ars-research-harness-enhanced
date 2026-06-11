# GBD burden minimal demo

Data source: `gbd`

Status: minimal teaching demo. This folder demonstrates how a GBD-style query
manifest, tiny export fixture, derived result table, narrative summary, and
claim registry can move through the harness to S7 integrity checking.

This is not a publishable burden study. Replace the fixture with an approved
GBD Results Tool export or approved API route before writing real manuscript
claims.

## Research Question

Can a minimal GBD Results-style export be traced from query dimensions to a
derived burden summary and source-backed claims?

## What Is Included

- `gbd_query_manifest.csv`: exact query dimensions for the teaching fixture.
- `source_exports/gbd_results_minimal_fixture.csv`: small committed fixture in a
  GBD Results-style table shape.
- `results/gbd_minimal_summary.csv`: derived summary produced by
  `scripts/generate_gbd_minimal_results.py`.
- `results/gbd_minimal_summary.md`: manuscript-style result paragraph with
  explicit interpretation boundaries.
- `claim_registry.json`: source-backed claim registry for S7 checking.
- `workflow-run.json`: checkpoint state through S7.

## Regenerate Results

```bash
python3 scripts/generate_gbd_minimal_results.py
python3 harness/validators/validate_gbd_minimal_demo.py
```

## Boundary

Counts, rates, percentages, age-standardized estimates, and uncertainty
intervals must not be mixed. This demo uses two global all-cause number rows as
a traceability fixture only. A real GBD manuscript must record release version,
measure, metric, cause, location, age, sex, year, export date, citation, and
permitted redistribution route.
