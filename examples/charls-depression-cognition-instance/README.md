# CHARLS depressive symptoms and cognitive function longitudinal manuscript

Data source: `charls`

Status: scaffold only. This folder does not contain raw data, completed analysis outputs, or manuscript-ready results.

Dataset-level policy is inherited from `data_sources/charls.json`; this project manifest records run-specific state.

## Research Question

Among middle-aged and older CHARLS participants with baseline and follow-up linkage, are baseline depressive symptoms associated with follow-up cognitive function or cognitive decline?

## Current Boundary

This instance is a concrete research-question scaffold, not a completed CHARLS
analysis. The S1/S2 design gate is specific to baseline depressive symptoms and
follow-up cognitive function, but all CHARLS source variables remain
`TBD_after_codebook_review` until official local codebook/questionnaire metadata
is reviewed.

The current blocking checks are expected:

- CHARLS portal access is externally blocked: 2008 Pilot, 2011 Wave1, and 2020
  Wave5 were observed as waiting for review on 2026-06-13. See
  `external_blockers.md`.
- no official local CHARLS codebook file has been found under
  `data/charls/codebooks/`;
- `primary_exposure` still needs a codebook-confirmed depressive-symptom source
  variable or derived scale;
- `primary_outcome` still needs codebook-confirmed cognitive-function items,
  score construction, or cognitive-decline derivation;
- `attrition_status`, linkage variables, and weight decisions are still pending.

Run the strict local codebook rehearsal after placing official local codebook
metadata under `data/charls/codebooks/`:

```bash
python3 harness/scripts/rehearse_charls_codebook_import.py \
  --project examples/charls-depression-cognition-instance \
  --require-input
```

Run the current design gate:

```bash
python3 harness/validators/validate_charls_design_gate.py \
  --project examples/charls-depression-cognition-instance
```

Run strict readiness only after source-variable mappings, attrition, and weight
decisions have been reviewed:

```bash
python3 harness/validators/validate_charls_design_gate.py \
  --project examples/charls-depression-cognition-instance \
  --require-ready
```

## Required Next Steps

1. Keep the CHARLS portal review recorded as an external blocker until access is approved.
2. Continue only work that does not require restricted CHARLS files: S0/S1/S2 wording,
   non-causal interpretation boundaries, and placeholder review rules.
3. After approval, place official codebook/questionnaire metadata under
   `data/charls/codebooks/` and re-run the strict codebook rehearsal.
4. After raw data download, place local files in the ignored raw-data directory declared by
   `project_manifest.json` and re-run the strict local dry-run.
5. Complete the CHARLS S1/S2 design gate before any real longitudinal analysis.
6. Record reviewed variable-mapping decisions and generate a review draft variable map.
7. Do not draft final claims until S3 results and S7 validation artifacts exist.
