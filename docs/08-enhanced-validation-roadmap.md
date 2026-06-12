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
- `harness/claims/nhanes_candidate_claim_decisions.json` records machine-readable
  review decisions for every candidate that needs human review. Pending decisions
  are allowed, but approved `register` decisions must include complete,
  source-backed registry drafts.
- `harness/scripts/apply_claim_review_decisions.py` converts only approved
  `register` decisions into a draft registry-additions file; it does not mutate
  the authoritative claim registry.
- `scripts/fetch_gbd_export.py` reads the GBD analysis manifest's `download`
  block, performs a non-overwriting dry run in CI, and can fetch approved public
  GBD endpoint data into metadata-rich CSV exports when run intentionally.
- `harness/validators/validate_charls_local_dry_run.py` checks local CHARLS
  restricted-data readiness without opening raw data files. Default mode supports
  metadata-only scaffolds; `--require-local-data` blocks analysis until required
  local files are present, required variables are mapped to source variables or
  documented derivations, semantic variable fields are complete, wave roles are
  auditable, and optional checksums match.
- `harness/validators/validate_charls_design_gate.py` checks the CHARLS S1/S2
  research-design gate. It links `charls_design_gate.json` to the variable map
  and wave map, then validates the research question, estimand, exposure/outcome
  temporal ordering, attrition plan, weight decision, and no-causal-language
  boundary. Default mode allows scaffold projects to remain pending;
  `--require-ready` blocks real analysis until placeholders are resolved.
- `harness/scripts/prepare_charls_design_gate_instance.py` turns the CHARLS S1/S2
  gate into an instantiation worksheet. It reads `charls_codebook_extract.csv`
  when available, suggests candidate source variables for human review, and
  records unresolved mapping, attrition, weight, and research-question decisions
  without mutating the variable map or design gate.
- `harness/scripts/import_charls_codebook_extract.py` imports local
  variable-level CHARLS codebook metadata into the codebook extract schema. It
  supports CSV/TSV by default, optional XLS/XLSX through local Excel
  dependencies, dry-run previews, append/dedupe writes, and rejection of likely
  respondent-level wide data.
- `harness/scripts/apply_charls_variable_mapping_decisions.py` closes the
  human-review loop from CHARLS codebook extract to variable-map draft. It
  validates `charls_variable_mapping_decisions.json`, permits pending scaffold
  decisions by default, blocks strict reviewed mode until required targets are
  resolved, and only updates `variable_map.csv` when explicitly requested.
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

Run the CHARLS S1/S2 design gate:

```bash
python3 harness/validators/validate_charls_design_gate.py
python3 harness/validators/validate_charls_design_gate.py --require-ready
python3 harness/scripts/prepare_charls_design_gate_instance.py --dry-run
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --dry-run
```

Generate the manuscript revision diff report with:

```bash
python3 harness/scripts/generate_revision_diff_report.py
```
