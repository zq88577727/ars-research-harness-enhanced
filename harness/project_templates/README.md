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

CHARLS runs should pair `variable_map.charls.template.csv`,
`charls_wave_map.template.csv`, `charls_file_manifest.template.csv`,
`charls_codebook_extract.template.csv`,
`charls_codebook_import_sample.template.csv`,
`charls_variable_mapping_decisions.template.json`, and
`charls_design_gate.template.json`: the variable map records analysis variables
and semantic decisions, the wave map records baseline/follow-up roles and time
anchors, the file manifest records local-only raw files, waves, modules, access
status, and optional checksums, the codebook extract records source-variable
metadata for candidate review, the codebook import sample gives CI a
metadata-only import fixture, the variable-mapping decisions file records human
approval or deferral decisions, and the design gate links S1/S2 decisions to the
research question, estimand, temporal ordering, attrition, weight, and claim
language boundaries. The validators and importer check metadata without reading
restricted data unless strict local-readiness modes are explicitly requested.

`harness/scripts/import_charls_codebook_extract.py` can convert a local
variable-level CHARLS codebook CSV/TSV, or XLS/XLSX when local Excel
dependencies are installed, into the `charls_codebook_extract.csv` schema. Use
`--dry-run` first; source official codebook files should remain in ignored local
directories such as `data/charls/codebooks/`.

`harness/scripts/rehearse_charls_codebook_import.py` sits between local
codebook import and human mapping decisions. It discovers or accepts local
codebook files, builds a temporary extract, generates conservative
source-variable candidates for S1/S2 review, and reports
`awaiting-local-codebook` when no local files are present.

GBD runs should pair `gbd_query_manifest.template.csv` with
`gbd_analysis_manifest.template.json`: the query manifest records exported
dimensions row by row, while the analysis manifest controls source files,
outputs, comparison years, and interpretation boundaries for generation and
validation.

When a GBD endpoint is public or otherwise approved for scripted access,
`scripts/fetch_gbd_export.py` can read the analysis manifest's `download` block
and create a metadata-rich CSV. Existing exports are not overwritten unless the
caller passes `--force`.
