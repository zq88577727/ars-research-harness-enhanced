# Enhanced Validation Roadmap

This enhanced fork adds two layers above the original checkpoint-first workflow:

1. Evidence validators that check manuscript claims against generated artifacts.
2. Reusable templates for reporting guidelines, study designs, journal profiles,
   and reviewer-response traces.

## First-priority upgrades

- `harness/validators/validate_manuscript_numbers.py` checks high-risk numbers
  in the final manuscript against CSV result files.
- `harness/reference_registry/nhanes_undiagnosed_diabetes.references.json` stores
  verified reference metadata and claim-to-reference mappings.
- `harness/validators/validate_references.py` checks manuscript references
  against that registry. It runs offline by default and supports `--online` for
  DOI/URL reachability checks when network access is available.
- `harness/validators/validate_external_literature.py` adds optional Crossref
  and PubMed verification for DOI-bearing references.
- `harness/claims/nhanes_claim_registry.json` and
  `harness/validators/validate_claims.py` make core manuscript claims explicit,
  source-backed, and bounded by interpretation rules.
- `harness/scripts/extract_candidate_claims.py` and
  `harness/validators/validate_candidate_claims.py` create and validate a
  human-review queue of numeric candidate claims before registry expansion.
- `harness/scripts/prepare_claim_registry_review.py` turns that queue into a
  Markdown review worksheet with draft registry objects. The worksheet still
  requires human source-file, source-field, and interpretation-boundary review.
- `requirements.txt`, `renv.lock`, and `Dockerfile` declare reproducible Python
  and R environments.

## Second-stage upgrades

- `harness/reporting_checklists/strobe.observational.json` upgrades the STROBE
  checklist from a reader-facing Markdown table to a structured audit artifact.
- `harness/study_design_templates/` adds contracts for STROBE, CONSORT, PRISMA,
  TRIPOD, RECORD, and STARD workflows.
- `harness/journal_profiles/generic_sci.json` declares target-journal readiness
  constraints and required manuscript statements.
- `harness/revision_traces/nhanes_s8_major_revision_trace.json` maps reviewer
  requests to revision responses, evidence files, and manuscript anchors.
- `.github/workflows/validate.yml` runs the validation suite in CI.
- `data_sources/` adds NHANES, CHARLS, and GBD adapter manifests with explicit
  access and raw-data policies.
- `harness/scripts/generate_revision_diff_report.py` produces an auditable diff
  report between manuscript stages.

Run the local audit suite with:

```bash
python3 harness/scripts/run_all_validations.py
```

Run live DOI checks only in a network-enabled environment:

```bash
python3 harness/validators/validate_external_literature.py --online
```

Generate the manuscript revision diff report with:

```bash
python3 harness/scripts/generate_revision_diff_report.py
```
