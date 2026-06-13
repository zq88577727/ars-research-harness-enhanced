# External Blockers

This file records blockers that depend on external data-provider actions or
user-controlled local files. These blockers should pause the affected CHARLS
steps without being treated as project failures.

## CHARLS Portal Review

Status date: 2026-06-13

Observed portal status:

- 2008 CHARLS Pilot: application waiting for review [2026-06-13]
- 2011 CHARLS Wave1: application waiting for review [2026-06-13]
- 2020 CHARLS Wave5: application waiting for review [2026-06-13]
- 2013 CHARLS Wave2, 2015 Wave3, 2018 Wave4, and Harmonized CHARLS: still need
  application or status confirmation before they can support this instance.

Impact:

- P6-8 real local codebook import rehearsal remains blocked until official
  CHARLS codebook/questionnaire files are approved and placed under
  `data/charls/codebooks/`.
- P6-9 local restricted-data dry-run remains blocked until approved raw data
  files are downloaded into ignored local paths under `data/charls/raw/`.
- The CHARLS depression-cognition instance must remain `scaffold-only`; it must
  not be described as a completed CHARLS analysis.

Allowed work while blocked:

- Refine S0/S1/S2 study design text and non-causal interpretation boundaries.
- Improve the variable-mapping decision worksheet using placeholders and
  documented review rules.
- Continue NHANES, GBD, claim-review, CI, documentation, and artifact-governance
  work that does not require restricted CHARLS files.

Resume criteria:

1. CHARLS portal status changes from waiting for review to approved/downloadable
   for the waves selected by the S1/S2 estimand.
2. Official codebook/questionnaire files are downloaded locally and placed in
   `data/charls/codebooks/`.
3. Required raw data files are downloaded locally and referenced in
   `charls_file_manifest.csv` without committing restricted files.
4. Re-run:

```bash
python3 harness/scripts/rehearse_charls_codebook_import.py \
  --project examples/charls-depression-cognition-instance \
  --require-input

python3 harness/validators/validate_charls_local_dry_run.py \
  --project examples/charls-depression-cognition-instance \
  --require-local-data
```
