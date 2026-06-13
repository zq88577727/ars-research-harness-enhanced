# GBD CVD Reuse Review

Status: reviewed for submission package, human confirmation required before final public release or final submission.

## Evidence Reviewed

- Source export: `source_exports/gbd_cvd_china_global_1990_2023.csv`
- Source export size: 4,953 bytes
- Source export SHA-256:
  `04fe316583e715d970af720be23087e62011aefbf74f8ff7b2a1de66da96b763`
- Source citation file: `source_exports/gbd_cvd_citation.txt`
- Derived summary: `results/gbd_cvd_china_global_summary.csv`
- Derived summary size: 1,763 bytes
- Derived summary SHA-256:
  `88b4431517e4794731c05eec5e00377eadfa9ec1d6c74c8d8fdc7196fd7a45cc`
- Official policy URLs recorded for human confirmation:
  `https://www.healthdata.org/Data-tools-practices/data-practices/ihme-free-charge-non-commercial-user-agreement`
  and `https://www.healthdata.org/data-tools-practices/data-practices/terms-and-conditions`

## Repository Decision

This project may keep the small source export and derived summary as a local
review fixture while the repository remains in manuscript-review status. The
source export should not be treated as a general redistribution dataset, and it
should not be packaged into public release artifacts until IHME/GHDx reuse and
redistribution terms are confirmed by a human reviewer.

## Derived Output Decision

The derived summary is an aggregate, non-participant-level table generated from
the exact query manifest and source export. It may be used for manuscript review
and validation. Public release of derived tables still requires the same citation
and reuse review note because the values originate from the GBD Results Tool.

## Required Before Submission-Ready

1. Confirm IHME/GHDx terms for the exact source export and derived summary.
2. Confirm whether public repository storage of the small source export is
   permitted or whether it should move to a local-only artifact path.
3. Confirm whether release artifacts may include derived CSV/Markdown summaries.
4. Confirm that the manuscript data availability statement does not imply
   unrestricted redistribution of IHME/GHDx data.
