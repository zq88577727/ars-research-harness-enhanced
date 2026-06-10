# Production Feasibility Matrix

This project can be hardened into a serious medical manuscript workflow, but the
production boundary must be stated honestly.

## What is implemented now

| Capability | Status | Notes |
|---|---|---|
| CI validation | Implemented | `.github/workflows/validate.yml` runs local validators on push and pull request. |
| External literature API path | Implemented as optional | `validate_external_literature.py --online` checks DOI references through Crossref and PubMed when network access allows. Offline CI verifies eligibility and registry coverage. |
| Structured claim extraction and registry | Implemented as first pass | `harness/claims/nhanes_claim_registry.json` registers core claims; validator samples remaining numeric sentences for expansion. |
| Real journal profile | Implemented as profile scaffold | `bmc_public_health.json` records source-checked facts and conservative soft limits. Target-journal final checks still require current author instructions. |
| Automatic diff report | Implemented | `generate_revision_diff_report.py` produces a Markdown report from S7b to S8b. |
| Stricter environment reproducibility | Implemented as layered controls | Pinned Python packages, `renv.lock`, Dockerfile, and dated Posit Package Manager snapshot are included. |
| NHANES adapter | Implemented with data example | Full NHANES teaching case remains reproducible. |
| CHARLS adapter | Implemented as access-aware manifest | Raw CHARLS data are not committed; user must download through official registered portal. |
| GBD adapter | Implemented as query/export-aware manifest | Raw GBD exports are not assumed; use approved Results Tool/API/export route. |

## What still requires external action

| Dependency | Why it cannot be fully automated here |
|---|---|
| CHARLS raw files | CHARLS data access uses a data portal with sign in/sign up. Users must comply with CHARLS terms and place files locally. |
| GBD bulk/API access | GBD exports depend on IHME/GHDx tools, release versions, query dimensions, and access conditions. |
| Live Crossref/PubMed checks | Network and SSL/API availability vary by environment; CI should keep offline checks deterministic. |
| Target-journal final formatting | Public journal pages change and many submission requirements are only visible in current author instructions or submission systems. |
| Human scientific accountability | Statistical, clinical, ethical, and authorship decisions still require qualified human review. |

## Objective conclusion

It is feasible to move this project into a serious production workflow for
public-database medical manuscripts if the team accepts an access-aware adapter
model: NHANES can be packaged as a reproducible example, while CHARLS and GBD
should be represented by manifests, query plans, local raw-data contracts, and
derived-output audits rather than committed raw data.

