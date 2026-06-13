# GBD CVD Public Release Audit

Status: P7-13 public-release safety review.

## Summary

The GBD CVD instance is suitable for repository review as a source-backed
manuscript candidate, but the raw GBD Results Tool CSV remains local-only until
IHME/GHDx reuse and redistribution terms are confirmed for public repository
distribution.

## File Classification

| Path | Classification | Recommended action |
| --- | --- | --- |
| `source_exports/gbd_cvd_china_global_1990_2023.csv` | Local-only raw GBD export | Do not commit; keep ignored; use for strict local reproduction only |
| `source_exports/gbd_cvd_citation.txt` | Citation evidence | Commit with citation review |
| `gbd_cvd_query_manifest.csv` | Query metadata | Commit |
| `gbd_cvd_query_profile.json` | Query/citation/reuse profile | Commit |
| `gbd_cvd_analysis_manifest.json` | Analysis metadata | Commit |
| `results/gbd_cvd_provenance.json` | Provenance metadata with source hash | Commit |
| `results/gbd_cvd_china_global_summary.csv` | Derived aggregate summary | Commit only with citation/reuse review notes |
| `results/gbd_cvd_china_global_summary.md` | Derived aggregate summary | Commit only with citation/reuse review notes |
| `gbd_cvd_citation_policy_review.md` | Compliance review | Commit |
| `gbd_cvd_reuse_review.md` | Compliance review | Commit |
| `gbd_cvd_manuscript_section_draft.md` | Manuscript section draft | Commit |
| `release_commit_scope_audit.md` | Release commit scope audit | Commit |

For the full release staging decision, see `release_commit_scope_audit.md`.

## Required Safety Gate

Run:

```bash
python3 harness/validators/validate_gbd_public_release_safety.py
```

The gate fails if the raw GBD source export is tracked or staged. It permits a
local source export to exist for strict reproduction as long as it remains
untracked and ignored.

## Open-Source Validation Mode

Public clones may not have the raw source export. Use the CI-safe submission
package validation mode:

```bash
python3 harness/validators/validate_gbd_cvd_submission_package.py \
  --allow-missing-source-export
```

Strict local reproduction can still run without this flag when the approved
source export is present locally.
