# ars-research-harness

A checkpoint-first academic research workflow harness. This repository turns an AI-assisted paper workflow into a traceable, reproducible, human-confirmed process.

The included case study uses the NHANES 2017-2018 public-use files to build a manuscript package on HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults. NHANES is the repository's complete closed-loop example. CHARLS now has local-only restricted-data manifests and validators, but remains scaffold-only until user-downloaded files are placed outside git. GBD includes a fixture-only minimal demo and a source-backed CVD China/global manuscript-candidate instance. The CVD instance has query, provenance, derived-summary, citation/reuse, and claim-review gates, but it is not submission-ready and does not redistribute the raw GBD source export.

![Research-to-Paper Harness](assets/diagrams/01-overview-japanese-handdrawn.png)

Figure 1 frames the repository as a complete path from public health data to a submission-ready package. It is useful as the opening slide in a workshop: the point is not to let AI jump straight to a manuscript, but to keep each research decision visible.

## Why This Exists

AI can draft quickly, but research work needs staged decisions: research question, methods, analysis, interpretation, drafting, citation checks, peer-review simulation, revision, and final packaging. This project keeps those stages separate.

Core properties:

- checkpoint-first stage gates
- explicit `workflow-run.json` state
- validator-backed workflow status
- artifact trail for every stage
- complete NHANES example that can be reused as a template
- explicit capability boundaries: NHANES is a complete teaching case; CHARLS is
  scaffolded until approved local data/codebooks are available; GBD has both a
  fixture-only minimal demo and a CVD source-backed manuscript candidate that
  still requires human citation, reuse, journal, and submission review
- enhanced manuscript-number, reference, reporting-checklist, journal-profile,
  environment-lock, and reviewer-response trace validators
- CI validation, optional Crossref/PubMed literature checks, structured claim
  registries, automatic revision diff reports, and source-aware NHANES/CHARLS/GBD
  adapter manifests

## Quick Start

Install Python dependencies and make sure the R packages `haven`, `dplyr`, `readr`, and `survey` are available:

```bash
python3 -m pip install -r requirements.txt
Rscript -e 'install.packages(c("haven", "dplyr", "readr", "survey"), repos="https://cloud.r-project.org")'
```

```bash
python3 scripts/download_nhanes_small_pack.py
Rscript scripts/run_nhanes_analysis.R
python3 scripts/generate_tables.py
Rscript scripts/generate_figures.R
python3 scripts/build_submission_docx.py
python3 harness/scripts/validate_checkpoint_workflow.py examples/nhanes-undiagnosed-diabetes/workflow-run.json
python3 harness/scripts/run_all_validations.py
python3 harness/scripts/generate_readiness_report.py --format markdown
python3 harness/scripts/extract_candidate_claims.py \
  examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_generic_sci.md \
  --registry harness/claims/nhanes_claim_registry.json \
  --prefix nhanes --limit 40 \
  --output harness/claims/nhanes_candidate_claims.json
python3 harness/scripts/prepare_claim_registry_review.py
python3 harness/scripts/apply_claim_review_decisions.py
python3 harness/validators/validate_charls_local_dry_run.py
```

Start a CHARLS or GBD run after data access/export is ready:

```bash
python3 harness/scripts/init_public_database_project.py charls charls-example \
  --title "CHARLS public-database manuscript" \
  --research-question "To be refined in S1"

python3 harness/scripts/init_public_database_project.py gbd gbd-example \
  --title "GBD burden manuscript" \
  --research-question "To be refined in S1"
```

These commands create scaffolded run folders only. They do not download CHARLS
or GBD data and do not create defensible manuscript claims until S3 analysis
outputs and S7 integrity checks are complete.

For CHARLS, the local restricted-data dry run checks manifest structure, local
path boundaries, variable mapping, checksums when supplied, and raw-data git
tracking without opening the restricted data files:

```bash
python3 harness/validators/validate_charls_local_dry_run.py
python3 harness/validators/validate_charls_local_dry_run.py --require-local-data
```

For the included GBD demo, the public default endpoint can be checked without
modifying files:

```bash
python3 scripts/fetch_gbd_export.py --dry-run
```

Key outputs:

- `examples/nhanes-undiagnosed-diabetes/workflow-run.json`
- `examples/nhanes-undiagnosed-diabetes/checkpoints/`
- `examples/nhanes-undiagnosed-diabetes/results/`
- `examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_with_tables_figures.docx`
- `examples/gbd-burden-minimal-demo/`
- `examples/gbd-cvd-china-global-instance/`

Enhanced validation details are documented in
[docs/08-enhanced-validation-roadmap.md](docs/08-enhanced-validation-roadmap.md).
Production feasibility and public-database access boundaries are documented in
[docs/09-production-feasibility-matrix.md](docs/09-production-feasibility-matrix.md).
CHARLS and GBD onboarding steps are documented in
[docs/10-charls-gbd-onboarding.zh-CN.md](docs/10-charls-gbd-onboarding.zh-CN.md).
Study-design support boundaries are documented in
[docs/11-study-design-support-matrix.md](docs/11-study-design-support-matrix.md).
Artifact retention rules are documented in
[docs/12-artifact-governance.md](docs/12-artifact-governance.md).
Post-release public-repository audits are documented in
[docs/13-post-release-audit-p7-15.md](docs/13-post-release-audit-p7-15.md).
Repository artifact cleanup planning is documented in
[docs/14-artifact-cleanup-plan-p7-16.md](docs/14-artifact-cleanup-plan-p7-16.md).
Repository data-use rules are documented in [DATA_POLICY.md](DATA_POLICY.md).

## Workflow

![Checkpoint Loop](assets/diagrams/02-checkpoint-loop-japanese-handdrawn.png)

Figure 2 shows the central control loop: plan, produce an artifact, validate it, wait for human confirmation, then move to the next stage. The "no auto-continue" rule is the main difference between this harness and ordinary one-shot AI writing.

S0-S9 covers intake, research-question framing, methods planning, data execution, interpretation, outline, draft, integrity checks, reviewer-style revision, and final package generation.

## Engineering View

![Harness Architecture](assets/diagrams/03-harness-architecture-japanese-handdrawn.png)

Figure 3 explains the engineering structure: router, workflow, stage contract, state JSON, validator, artifacts, and human confirmation. This makes the project a workflow harness rather than a long prompt.

This is a workflow harness, not just a prompt library. The repository includes stage contracts, state artifacts, validation scripts, example outputs, and human confirmation gates.

## Case Study

![NHANES Case Path](assets/diagrams/04-nhanes-case-path-japanese-handdrawn.png)

Figure 4 maps the case study: NHANES small-pack files become survey-weighted results, tables, figures, and a DOCX package.

## Teaching Use

This repository can be used as a teaching module for a 90-120 minute AI medical research workshop:

1. Use Figure 1 to introduce the full research-to-paper chain.
2. Use Figure 2 to explain checkpoint-first execution.
3. Use Figure 3 to explain the harness engineering layer.
4. Use Figure 4 to walk through the NHANES example.
5. Open `workflow-run.json`, `checkpoints/`, `results/`, and the final DOCX package as live artifacts.

Chinese teaching notes are available in [docs/07-teaching-courseware.zh-CN.md](docs/07-teaching-courseware.zh-CN.md).

The NHANES example demonstrates how a public health dataset becomes survey-weighted results, tables, figures, a manuscript draft, a simulated review trail, and a Word submission package.

The GBD minimal demo demonstrates the same governance pattern on a small
GBD Results-style teaching fixture through S7 integrity checking. It proves
query-to-claim traceability, not a publishable burden analysis.

## Disclaimer

This project is a research workflow and teaching template. It does not guarantee journal acceptance and does not replace statistical, ethical, clinical, or editorial review. Cross-sectional findings must not be written as causal effects, single laboratory measurements must not be written as clinical diagnoses, and descriptive public-database analyses must not be written as mechanism studies. NHANES data are from CDC/NCHS public-use files; CHARLS and GBD users are responsible for following source access, citation, and redistribution rules.

中文文档: [README.zh-CN.md](README.zh-CN.md)
