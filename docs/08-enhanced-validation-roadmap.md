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

Run the local audit suite with:

```bash
python3 harness/scripts/run_all_validations.py
```

