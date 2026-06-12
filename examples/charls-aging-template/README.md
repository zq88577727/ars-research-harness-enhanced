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
5. Fill `charls_design_gate.json` with the S1/S2 research question, estimand,
   temporal-ordering, attrition, weight, and claim-language decisions.
6. Fill `charls_codebook_extract.csv` with codebook-level metadata for candidate
   source variables. Do not copy raw participant data into this file.
7. Generate and review `charls_s1_s2_design_review.md`.
8. Place raw data in the ignored local raw-data directory declared by
   `project_manifest.json`; do not commit raw `.dta`, `.sav`, `.sas7bdat`, CSV,
   or archive files.
9. Do not draft final claims until S3 results and S7 validation artifacts exist.

## S1/S2 Design Gate

`charls_design_gate.json` connects the variable and wave maps to the research
question and method-analysis plan. It is intentionally scaffold-only until the
research question, exposure, outcome, attrition plan, and weight decision are
confirmed.

Run the design gate during S1/S2:

```bash
python3 harness/validators/validate_charls_design_gate.py
```

The default gate checks that:

- the research question points to variables in `variable_map.csv`;
- baseline and follow-up waves are declared in `charls_wave_map.csv`;
- exposure is baseline-positioned and outcome is follow-up-positioned;
- attrition and weight variables are connected to explicit S2 decisions;
- manuscript language includes a no-causal-overclaim boundary.

Run the strict gate before real CHARLS analysis:

```bash
python3 harness/validators/validate_charls_design_gate.py --require-ready
```

Strict mode blocks analysis until the design gate is marked
`ready-for-analysis`, the research question and estimand are no longer
placeholders, exposure/outcome/attrition variables are mapped or derived from
real CHARLS variables, and the weight decision is no longer pending.

## S1/S2 Instantiation Assistant

`charls_codebook_extract.csv` is a codebook-level extract used to propose
candidate source variables for human review. It should contain official CHARLS
metadata such as source variable names, labels, modules, waves, measurement
domains, and eligible analysis roles. It must not contain respondent-level data.

Generate the worksheet:

```bash
python3 harness/scripts/prepare_charls_design_gate_instance.py
```

The command writes `charls_s1_s2_design_review.md`. The worksheet lists each
target variable from the design gate and variable map, any candidate source
variables found in the codebook extract, and the human action required before
`variable_map.csv` or `charls_design_gate.json` can be marked analysis-ready.

CI uses dry-run mode so validation remains read-only:

```bash
python3 harness/scripts/prepare_charls_design_gate_instance.py --dry-run
```

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
