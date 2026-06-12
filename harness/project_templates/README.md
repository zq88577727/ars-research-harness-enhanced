# Project Templates

These templates are used by `harness/scripts/init_public_database_project.py` to
create a new research run without committing restricted raw data.

Supported project types:

- `charls`
- `gbd`

Generated runs are intentionally incomplete until a human fills the research
question, variable mapping, data access status, and query dimensions.

Each project manifest references a source-of-truth adapter through
`dataSourceManifest`. Dataset-level access rules, raw-data policy, and required
harness stages live in `data_sources/*.json`; project manifests should keep only
run-specific state such as access progress, local paths, variable maps, and query
manifests.

GBD runs should pair `gbd_query_manifest.template.csv` with
`gbd_analysis_manifest.template.json`: the query manifest records exported
dimensions row by row, while the analysis manifest controls source files,
outputs, comparison years, and interpretation boundaries for generation and
validation.

When a GBD endpoint is public or otherwise approved for scripted access,
`scripts/fetch_gbd_export.py` can read the analysis manifest's `download` block
and create a metadata-rich CSV. Existing exports are not overwritten unless the
caller passes `--force`.
