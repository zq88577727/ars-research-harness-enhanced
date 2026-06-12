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
8. Record reviewed decisions in `charls_variable_mapping_decisions.json` and
   generate a draft variable map for review.
9. Place raw data in the ignored local raw-data directory declared by
   `project_manifest.json`; do not commit raw `.dta`, `.sav`, `.sas7bdat`, CSV,
   or archive files.
10. Do not draft final claims until S3 results and S7 validation artifacts exist.

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

## Local Codebook Importer

The local codebook importer helps turn a narrow CHARLS codebook table into the
`charls_codebook_extract.csv` schema. Place official local codebook or
questionnaire exports under an ignored directory such as
`data/charls/codebooks/`; do not commit those source files unless their license
explicitly allows redistribution.

Preview a local codebook import without writing output:

```bash
python3 harness/scripts/import_charls_codebook_extract.py \
  --input data/charls/codebooks/<local-codebook>.csv \
  --dry-run
```

Write or append only after the preview confirms that the input is
variable-level metadata:

```bash
python3 harness/scripts/import_charls_codebook_extract.py \
  --input data/charls/codebooks/<local-codebook>.csv \
  --append
```

The importer supports CSV/TSV by default and XLS/XLSX when the local Python
environment has a compatible Excel engine. It rejects likely respondent-level
wide data and requires a source-variable column before importing. The included
`charls_codebook_import_sample.csv` is a metadata-only sample for CI and
training; replace it with official local CHARLS metadata for a real project.

Run a full local rehearsal that discovers files under `data/charls/codebooks/`,
imports codebook metadata into a temporary extract, and generates candidate
source-variable suggestions without mutating the project:

```bash
python3 harness/scripts/rehearse_charls_codebook_import.py
```

Run the same rehearsal against a specific local codebook:

```bash
python3 harness/scripts/rehearse_charls_codebook_import.py \
  --input data/charls/codebooks/<local-codebook>.csv
```

Use strict mode when a real local codebook is expected:

```bash
python3 harness/scripts/rehearse_charls_codebook_import.py --require-input
```

The rehearsal returns `awaiting-local-codebook` when no local codebook is found.
It returns candidate suggestions only above a conservative score threshold
(`--min-candidate-score`, default `12`). Reports generated with
`--write-report` should remain local unless the underlying official codebook
metadata is redistributable.

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

## Variable Mapping Decision Loop

`charls_variable_mapping_decisions.json` records human review decisions that
convert codebook candidates into a draft `variable_map.csv` update. The default
state is `pending`; pending decisions are valid for a scaffold but block real
analysis.

Validate the decision file without writing output:

```bash
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --dry-run
```

After a human reviewer has approved source-variable mappings or derivations,
generate a review draft:

```bash
python3 harness/scripts/apply_charls_variable_mapping_decisions.py
```

This writes `variable_map.review_draft.csv` and leaves `variable_map.csv`
unchanged. Updating the authoritative variable map requires an explicit reviewed
gate:

```bash
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --require-reviewed --update-variable-map
```

Do not use `--update-variable-map` until the selected source variables,
derivation rules, coding decisions, missingness decisions, and interpretation
boundaries have all been checked against official CHARLS documentation.

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
