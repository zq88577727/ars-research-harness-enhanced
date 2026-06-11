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
