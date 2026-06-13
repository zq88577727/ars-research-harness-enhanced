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
- `scripts/generate_gbd_minimal_results.py` now emits a GBD provenance sidecar
  that links the analysis manifest, query manifest, source exports, output
  hashes, endpoint metadata, and interpretation boundaries. The GBD validator
  checks query-row-to-source-row coverage plus provenance hash consistency.
- `examples/gbd-burden-minimal-demo/gbd_query_profile.json` adds a GATHER-style
  query profile audit for GBD release/version, metric separation, uncertainty
  intervals, age-standardization status, citation readiness, and reuse boundary.
  `validate_gbd_minimal_demo.py` blocks the demo if this profile drifts from the
  query manifest, analysis manifest, or source exports.
- `harness/validators/validate_gbd_submission_readiness.py` adds a strict GBD
  submission gate that combines query profile, provenance, claim registry,
  citation policy, and reuse boundary. Default mode is CI-safe; strict
  `--require-submission-ready` mode blocks until demo claims are upgraded.
- `examples/gbd-burden-minimal-demo/gbd_query_profile.json` is now
  `manuscript-review-ready`: it has a manuscript citation draft, reuse boundary,
  uncertainty-interval wording rule, and explicit `All ages`/not-age-standardized
  interpretation rule. This is still below `submission-ready`; strict submission
  mode continues to block until human citation, reuse, and journal wording checks
  are complete.
- `examples/gbd-burden-minimal-demo/gbd_claim_review_checklist.csv` and
  `gbd_manuscript_review_draft.md` close the manuscript-review package for the 4
  candidate GBD claims. `validate_gbd_submission_readiness.py
  --require-manuscript-review-ready` now checks that the human decision table and
  review draft are present and cover the candidate claims.
- `examples/gbd-burden-minimal-demo/gbd_topic_upgrade_decision.md` and
  `gbd_targeted_query_candidates.csv` add the P7-4 topic-upgrade layer. The
  validator's `--require-topic-upgrade-decision` mode requires an explicit
  decision not to promote the global all-cause demo directly to
  `submission-ready` and requires a targeted GBD query candidate matrix with P0
  options.
- `examples/gbd-cvd-china-global-instance/` is the P7-5 selected targeted GBD
  scaffold for `gbd-cvd-china-global-1990-2023`. It adds a CVD China/global
  query manifest, targeted query profile, and manuscript-specific claim
  skeleton. `validate_gbd_targeted_scaffold.py` requires the scaffold to remain
  `targeted-scaffold-awaiting-export` and blocks numeric result claims until a
  matching CVD export is present and provenance-backed.
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
- `harness/scripts/rehearse_charls_codebook_import.py` runs the project-level
  local codebook rehearsal. It discovers or accepts ignored local codebook
  files, transforms them into a temporary extract, generates conservative
  candidate source-variable suggestions, and reports `awaiting-local-codebook`
  rather than fabricating results when no local files are present.
- `examples/charls-depression-cognition-instance/external_blockers.md` records
  the current CHARLS portal review state as an external dependency. While the
  provider review is pending, P6-8/P6-9 should remain paused and non-CHARLS or
  metadata-only work should continue.
- `harness/scripts/apply_charls_variable_mapping_decisions.py` closes the
  human-review loop from CHARLS codebook extract to variable-map draft. It
  validates `charls_variable_mapping_decisions.json`, permits pending scaffold
  decisions by default, blocks strict reviewed mode until required targets are
  resolved, and only updates `variable_map.csv` when explicitly requested.
- `examples/gbd-cvd-china-global-instance/gbd_cvd_analysis_manifest.json`
  defines the P7-6 targeted CVD GBD export-to-claim pathway. It links the CVD
  query manifest, query profile, source export, derived summary, provenance,
  and source-backed claim registry output without generating numeric claims
  before a matching GBD Results Tool CSV is present.
- `scripts/generate_gbd_targeted_results.py` validates a real targeted GBD CSV
  against the CVD query manifest, generates derived summary CSV/Markdown,
  writes provenance with file hashes, and emits
  `claim_registry.source_backed.json`. In CI/dry-run mode it reports
  `awaiting-source-export` rather than fabricating GBD values.
- `harness/validators/validate_gbd_targeted_scaffold.py --require-export` is
  the strict P7-6 gate. Default validation allows the scaffold to remain
  blocked on external export; strict mode requires the source CSV and generated
  provenance/result artifacts.
- `harness/validators/validate_gbd_cvd_submission_readiness.py` adds the P7-7
  CVD submission-readiness gate. It validates the source-backed CVD query
  profile, source export, provenance, derived summary, claim registry, human
  claim-review checklist, manuscript review draft, UI completeness, metric/age
  separation, citation policy, and reuse boundary. Manuscript-review mode passes
  with explicit blockers; strict submission mode fails until human citation,
  reuse, claim-review, and target-journal manuscript checks are complete.
- `harness/scripts/apply_gbd_cvd_claim_review_decisions.py` adds the P7-8 human
  claim-review decision loop. It reads
  `gbd_cvd_claim_review_decisions.json`, validates per-claim decisions
  (`approve`, `rewrite`, `downgrade`, `delete`), writes an auditable
  `gbd_cvd_claim_review_decision_record.json`, and updates the claim review
  checklist only when `--update-checklist` is explicitly requested.
- `harness/scripts/generate_gbd_cvd_claim_review_helper.py` adds the P7-9
  interactive/table-style review helper. It reads the source-backed CVD summary,
  claim registry, review checklist, and current decision file, then generates
  CSV and Markdown tables that place each candidate claim beside its source
  values, uncertainty intervals, metric/age/UI boundaries, current decision,
  recommended decision, and allowed actions.
- P7-10 closes the CVD project-level claim review loop by applying reviewed
  decisions for all five candidate claims: one approved boundary claim, three
  rewritten numeric claims, and one downgraded supporting DALY-rate claim. The
  strict submission gate still blocks final submission until citation wording,
  reuse terms, submission-level claim approval, and complete manuscript context
  are resolved.
- `examples/gbd-cvd-china-global-instance/gbd_cvd_manuscript_fragment.md` and
  `harness/validators/validate_gbd_cvd_manuscript_fragment.py` add the P7-11
  Methods/Results/claim-registry consistency gate. The validator requires the
  three reviewed rewrite texts to appear in Results, the downgraded DALY-rate
  claim to remain supporting/table-only, all five claim IDs to be linked, and
  Methods to preserve GBD release, version, location, sex, age, metric, UI, and
  non-causal interpretation boundaries.
- P7-12 adds a submission-package evidence layer without declaring final
  submission readiness. `gbd_cvd_citation_policy_review.md` records the
  export-supplied citation and recommended manuscript citation draft;
  `gbd_cvd_reuse_review.md` records source-export and derived-summary reuse
  boundaries; `gbd_cvd_manuscript_section_draft.md` converts the reviewed
  fragment into Methods, Results, Limitations, and Data Availability sections.
  `validate_gbd_cvd_submission_package.py` validates hashes, citation/reuse
  review status, section wording, reviewed rewrite claims, downgraded claims,
  and the remaining human-confirmation boundary.
- P7-13 adds public-release safety controls for the GBD CVD instance.
  `public_release_audit.md` classifies files into commit, local-only, and
  release-artifact categories. `.gitignore` excludes the raw CVD GBD source CSV,
  and `validate_gbd_public_release_safety.py` fails if raw/restricted GBD or
  CHARLS files are tracked or staged. The submission-package validator supports
  `--allow-missing-source-export` so open-source clones can validate the
  reviewable package without redistributing the raw GBD export.
- P7-14 adds `release_commit_scope_audit.md`, which converts the release-safety
  decision into an explicit staging boundary: public workflow, manifest,
  derived-result, review, citation, and validator files can be committed, while
  raw GBD source exports, restricted CHARLS data/codebooks, reserved raw-data
  directories, and generated caches remain local-only.
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

Regenerate the P7-9 GBD CVD claim review helper:

```bash
python3 harness/scripts/generate_gbd_cvd_claim_review_helper.py
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

Run the targeted GBD CVD gate:

```bash
python3 harness/validators/validate_gbd_targeted_scaffold.py
python3 scripts/generate_gbd_targeted_results.py --project examples/gbd-cvd-china-global-instance --dry-run
python3 harness/validators/validate_gbd_targeted_scaffold.py --require-export
```

Run the GBD CVD submission-readiness gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_readiness.py --require-manuscript-review-ready
python3 harness/validators/validate_gbd_cvd_submission_readiness.py --require-submission-ready
```

Run the GBD CVD claim-review decision loop:

```bash
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py --require-reviewed
python3 harness/scripts/apply_gbd_cvd_claim_review_decisions.py --require-reviewed --update-checklist
```

Run the P7-11 GBD CVD manuscript fragment consistency gate:

```bash
python3 harness/validators/validate_gbd_cvd_manuscript_fragment.py
```

Run the P7-12 GBD CVD submission package evidence gate:

```bash
python3 harness/validators/validate_gbd_cvd_submission_package.py
python3 harness/validators/validate_gbd_cvd_submission_package.py --allow-missing-source-export
```

Run the P7-13 GBD public-release safety gate:

```bash
python3 harness/validators/validate_gbd_public_release_safety.py
```

Generate the manuscript revision diff report with:

```bash
python3 harness/scripts/generate_revision_diff_report.py
```
