# Roadmap

This roadmap separates proven workflow capability from planned production
hardening.

## Current Stable Scope

- Complete NHANES teaching case from question framing to DOCX submission package.
- S0-S9 checkpoint-first workflow with human confirmation gates.
- Local validators for workflow state, manuscript numbers, references, claims,
  reporting checklist status, journal profile, environment lock, revision trace,
  revision diff report, data source manifests, and scaffolded public-database projects.
- CHARLS and GBD scaffold generation with data-access boundaries.

## Near-Term Priorities

1. Expand structured claim registry coverage for the NHANES manuscript.
2. Keep STROBE mapping fully explicit, including bias handling and
   author-completed funding statements.
3. Maintain clear documentation that CHARLS and GBD are scaffolds until real
   approved data, variable/query maps, S3 outputs, and S7 audits exist.
4. Reduce drift between data source manifests, project templates, and example
   manifests by treating `data_sources/*.json` as the source-of-truth layer.
5. Treat CHARLS portal approval as an external blocker: continue NHANES, GBD,
   claim-review, CI, and documentation hardening while waiting for approved
   CHARLS files, then resume P6-8/P6-9 after local codebook and raw data are
   available.

## Production-Hardening Targets

1. Add optional online literature checks for Crossref, PubMed, and journal
   instructions while keeping offline CI deterministic.
2. Add a stronger claim extraction workflow that classifies candidate numeric
   sentences as `core`, `supporting`, `background`, or `non-claim`.
3. Add one real CHARLS analysis walkthrough after data-use requirements are
   confirmed by the user and the current portal review blocker is closed.
4. Add one real GBD query-to-table-to-figure walkthrough using a documented
   Results Tool export or approved API route.
5. Improve artifact governance by moving large generated packages to releases
   when they are not needed for everyday validation.

## Out of Scope Unless Added Later

- Automatic journal acceptance prediction.
- Clinical diagnostic decision support.
- Causal inference claims from cross-sectional examples.
- Redistribution of restricted CHARLS raw files.
- Guaranteed programmatic access to GBD beyond the user's approved export/API route.
