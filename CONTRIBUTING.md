# Contributing

Contributions should strengthen the harness as an auditable research workflow.
Do not add unsupported scientific claims, restricted raw data, or generated
artifacts that cannot be reproduced.

## Before Opening a Pull Request

1. Keep scope narrow and explain which workflow stage or validator is affected.
2. Run local validation:

   ```bash
   python3 harness/scripts/run_all_validations.py
   ```

3. If you add a data source, update `data_sources/`, the relevant project
   template, and the study-design support matrix.
4. If you add manuscript claims, register source-backed core claims in
   `harness/claims/`.
5. If you add generated artifacts, explain whether they are committed teaching
   artifacts, release artifacts, or locally regenerated files.

## Scientific Standards

- Do not write cross-sectional associations as causal effects.
- Do not write a single laboratory measurement as a clinical diagnosis.
- Do not write descriptive public-database work as mechanistic evidence.
- Use the reporting guideline that matches the study design.
- Keep source citation and data access requirements visible.

## Data Rules

Follow `DATA_POLICY.md`. Restricted raw data, credentials, portal tokens, direct
identifiers, and private account screenshots must not be committed.

## Documentation Rules

When adding or changing capabilities, update the README and relevant docs so
external users can distinguish complete examples from scaffolds.
