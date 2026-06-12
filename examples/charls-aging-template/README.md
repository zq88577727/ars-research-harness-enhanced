# CHARLS aging public-database manuscript template

Data source: `charls`

Status: scaffold only. This folder does not contain raw CHARLS files, linked
waves, analysis outputs, or manuscript-ready results. Dataset-level policy is
in `data_sources/charls.json`; this manifest records only project-specific
state.

## Research Question

To be refined after CHARLS wave access and variable mapping.

## Required Next Steps

1. Complete S0 intake and confirm data access status.
2. Fill `charls_file_manifest.csv` with the exact local filenames, waves, modules,
   and access status after CHARLS portal download.
3. Fill `charls_wave_map.csv` with baseline/follow-up roles, time anchors,
   linkage-key status, weight decisions, and attrition roles.
4. Fill the variable mapping file, including respondent ID, wave, baseline wave,
   follow-up wave, exposure, outcome, attrition status, and weight decision.
   Required variables must carry construct, domain, measurement type, wave role,
   time anchor, coding decision, missingness decision, and interpretation boundary.
5. Place raw data in the ignored local raw-data directory declared by
   `project_manifest.json`; do not commit raw `.dta`, `.sav`, `.sas7bdat`, CSV,
   or archive files.
6. Do not draft final claims until S3 results and S7 validation artifacts exist.

## Local Data Boundary

This scaffold validates metadata only while `rawFilesDownloaded` is `false`.
After local CHARLS files are downloaded and `rawFilesDownloaded` is set to
`true`, required rows in `charls_file_manifest.csv` must point to real local
files under `data/charls/raw/`.

Run the metadata-only dry run while files are not yet downloaded:

```bash
python3 harness/validators/validate_charls_local_dry_run.py
```

In metadata-only mode, source variables may remain `TBD_after_codebook_review`,
but required variables must already describe their semantic construct, wave role,
time anchor, coding decision, missingness decision, and interpretation boundary.

Run the strict local-data gate before any real CHARLS analysis:

```bash
python3 harness/validators/validate_charls_local_dry_run.py --require-local-data
```

Strict mode requires local files and requires required variables to be resolved
to real CHARLS source variables or documented derived variables.

Longitudinal CHARLS claims must not be written as causal conclusions unless the
analysis plan explicitly addresses temporality, attrition, missingness, weights,
and wave linkage.
