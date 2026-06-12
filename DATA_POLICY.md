# Data Policy

This repository is a research workflow harness, not a data redistribution
service. Every dataset used with the harness must keep its original access,
license, citation, privacy, and ethics requirements visible.

## Data Classes

| Class | Examples | Repository policy |
|---|---|---|
| Public-use teaching data | Small NHANES public-use files used by the included example | May be committed when size is reasonable, source is cited, and the data remain public-use |
| Restricted or registered-access data | CHARLS downloads, harmonized CHARLS files, licensed extracts, local official codebooks or questionnaires with redistribution limits | Do not commit raw files; store locally under ignored raw-data or codebook directories |
| Tool exports with access conditions | GBD Results Tool CSV exports or API downloads | Commit only query manifests and small derived tables when redistribution is allowed |
| Derived non-identifiable outputs | Aggregated tables, model summaries, figures | May be committed as teaching artifacts when they contain no participant-level restricted data |
| Generated manuscript artifacts | DOCX drafts, response letters, readiness checks | Keep one curated teaching package in the example; large or repeated generated artifacts should move to release artifacts |

## NHANES

The NHANES example uses CDC/NCHS public-use files for teaching and
reproducibility. Users must cite the original NHANES source, use the correct
survey weights, strata, and PSU variables, and avoid presenting single-cycle
cross-sectional findings as causal effects.

## CHARLS

CHARLS requires registered access through the CHARLS data portal. This
repository may contain CHARLS manifests, variable maps, workflow states,
variable-level codebook extracts, and derived non-identifiable summaries, but it
must not contain raw CHARLS data.
Users are responsible for confirming the permitted use, citation, and
redistribution terms for every downloaded wave or harmonized file.

Each CHARLS project should maintain a committed `charls_file_manifest.csv` that
describes local-only raw files by wave/module/path/access status without
committing the files themselves. Validators may check local existence after a
project declares that raw files have been downloaded, but they must not require
or expose raw CHARLS contents.

Official CHARLS codebooks, questionnaires, and portal exports should remain
local under ignored directories such as `data/charls/codebooks/` unless their
license explicitly permits redistribution. A committed
`charls_codebook_extract.csv` is acceptable only when it is a narrow
variable-level metadata table: source variable names, labels, modules, waves,
construct keywords, measurement domains, measurement types, eligible analysis
roles, and notes. It must not contain respondent-level rows, direct identifiers,
free-text participant responses, or copied raw records.

## GBD

GBD work should be represented by query manifests that record release version,
measure, metric, cause, location, age, sex, and year. Raw or bulk GBD exports
should not be committed unless the export terms, size, and citation requirements
make redistribution appropriate. Manuscript text must distinguish counts,
rates, percentages, age-standardized estimates, and uncertainty intervals.

## Local Raw-Data Convention

Use ignored local directories for raw inputs:

- `data/charls/raw/`
- `data/charls/codebooks/`
- `data/gbd/raw/`
- project-specific raw directories declared in `project_manifest.json`

Do not include credentials, portal screenshots with private account details,
download tokens, direct personal identifiers, or restricted participant-level
files in commits, issues, pull requests, or release artifacts.

## Claim and Citation Requirements

Any manuscript claim based on a dataset must be traceable to one of:

- a committed public-use source file,
- a committed derived aggregate,
- a local restricted source described by a manifest,
- a query/export manifest with versioned source metadata.

Claims that cannot be traced to a source artifact should remain draft text until
S3 analysis output and S7 integrity checks are complete.
