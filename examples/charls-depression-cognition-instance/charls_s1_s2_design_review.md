# CHARLS S1/S2 Design Gate Instantiation Worksheet

Project: `examples/charls-depression-cognition-instance`
Design gate: `examples/charls-depression-cognition-instance/charls_design_gate.json`
Variable map: `examples/charls-depression-cognition-instance/variable_map.csv`
Wave map: `examples/charls-depression-cognition-instance/charls_wave_map.csv`
Codebook extract: `examples/charls-depression-cognition-instance/charls_codebook_extract.csv`

Status: scaffold instantiation aid only. This worksheet does not approve analysis and does not replace human codebook review.

## Summary

- Target variables reviewed: 10
- Codebook extract rows: 5
- Usable source-variable rows: 0
- Candidate suggestions: 0
- Variables still requiring human mapping: 10

## S1/S2 Decisions Still Required

- primary_exposure requires human-confirmed source variable mapping
- primary_outcome requires human-confirmed source variable mapping
- attrition_status requires human-confirmed source variable mapping
- sample_weight requires human-confirmed source variable mapping
- participant_id requires human-confirmed source variable mapping
- wave requires human-confirmed source variable mapping
- baseline_wave requires human-confirmed source variable mapping
- followup_wave requires human-confirmed source variable mapping
- age requires human-confirmed source variable mapping
- sex requires human-confirmed source variable mapping
- weight decision remains unresolved
- codebook extract has no usable source-variable rows; fill charls_codebook_extract.csv from official metadata

## Variable Candidate Review

| canonical variable | role | wave role | current source variable | candidate suggestions | required human action |
|---|---|---|---|---|---|
| primary_exposure | exposure | baseline | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| primary_outcome | outcome | followup | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| attrition_status | missingness | followup | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| sample_weight | weight | baseline | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| participant_id | id | cross_wave | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| wave | time | cross_wave | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| baseline_wave | time | baseline | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| followup_wave | time | followup | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| age | covariate | baseline | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |
| sex | covariate | baseline | `TBD_after_codebook_review` | No candidate from current codebook extract | confirm source variable and update semantic_status to mapped/derived |

## Human Review Contract

Before changing `variable_map.csv` or setting `charls_design_gate.json` to `ready-for-analysis`, a human reviewer should:

1. Confirm each selected source variable against the official CHARLS questionnaire or codebook.
2. Record exact coding, missingness, and derivation decisions in `variable_map.csv`.
3. Confirm exposure measurement precedes outcome ascertainment.
4. Document attrition and weight decisions in `charls_design_gate.json`.
5. Keep causal, diagnostic, and clinical-recommendation language blocked unless a separate justified design supports it.
