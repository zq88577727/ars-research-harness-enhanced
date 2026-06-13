# GBD Topic Upgrade Decision

Status: topic-upgrade-required before any submission-ready claim promotion

## Current Decision

The current GBD minimal demo uses a global, all-cause, all-age, both-sex GBD
2023 default endpoint export. It is suitable for workflow traceability,
manuscript-review rehearsal, and claim-governance testing.

It is not a sufficiently specific publishable GBD research topic. Do not
promote the current all-cause candidate claims to `submission-ready`.

## Recommended Route

Keep the current all-cause rows as a repository review fixture and instantiate a
targeted GBD query before drafting a real GBD manuscript. The targeted query
must select a disease or risk factor, a location strategy, an age strategy, a
sex strategy, measures, metrics, and comparison years before new manuscript
claims are generated.

Selected first upgrade: `gbd-cvd-china-global-1990-2023`, a disease-specific
GBD burden scaffold comparing cardiovascular disease burden in China and
globally using age-standardized rates plus all-age counts, with uncertainty
intervals preserved and metric types separated in the claim registry.

## Why The Current Demo Should Not Be Upgraded Directly

- `All causes` is too broad for a focused biomedical manuscript unless the
  paper is explicitly a methods or surveillance overview.
- `All ages` is not an age-standardized estimate and should not be used as a
  substitute for age-adjusted rates.
- Global all-cause deaths and DALYs are useful for validating data flow, but
  they do not define a disease-specific epidemiologic question.
- Submission-ready claims require final IHME/GHDx citation wording, reuse
  confirmation, journal wording review, and exact query dimensions.

## Required Upgrade Decisions

Before a GBD manuscript can move beyond manuscript review, record all of the
following:

1. Disease or risk-factor focus.
2. Location scope, such as China, global, region, or comparator locations.
3. Age strategy, explicitly distinguishing all-age counts from
   age-standardized rates.
4. Sex strategy.
5. Measures, such as deaths, DALYs, prevalence, incidence, or YLDs.
6. Metrics, with numbers, rates, percentages, and age-standardized rates kept
   in separate claims.
7. Years and comparison frame.
8. Uncertainty-interval wording rule.
9. GBD release, version, export route, access date, and citation policy.
10. Reuse boundary for repository artifacts and manuscript outputs.

## Decision Record

- Keep existing all-cause candidate claims as `candidate-manuscript-claim` for
  historical review rehearsal only.
- Downgrade existing all-cause claims to fixture-only repository checks.
- Do not promote current all-cause claims to `submission-ready`.
- Use `examples/gbd-cvd-china-global-instance/` as the selected targeted GBD
  manuscript scaffold.
- After a targeted query is selected and exported, create a new or upgraded
  claim registry that is manuscript-specific to that query.
