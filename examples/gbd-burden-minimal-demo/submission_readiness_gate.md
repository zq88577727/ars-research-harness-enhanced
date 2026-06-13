# GBD Submission Readiness Gate

Status: manuscript-review-ready, not submission-ready

Updated P7-5 status: the all-cause demo has been downgraded to fixture-only.
Real GBD manuscript scaffolding now lives in
`examples/gbd-cvd-china-global-instance/`.

This gate combines the GBD query profile, provenance sidecar, claim registry,
citation policy, and reuse boundary. It is intentionally stricter than the demo
validator: the demo can pass CI while this gate blocks real submission until the
remaining publication risks are closed.

## Manuscript-Specific Research Question

Among global, all-age, both-sex populations in the GBD 2023 Results Tool default
endpoint, what were the estimated all-cause deaths and DALYs in 2023, and how
did the all-cause death rate change from 1990 to 2023?

Target statement: this is a descriptive GBD endpoint analysis that must preserve
release, version, query dimensions, metric type, uncertainty intervals, citation
requirements, and reuse boundaries. It must not be phrased as causal,
mechanistic, clinical, or policy-effect evidence.

## Current Blockers

- Query profile status is `manuscript-review-ready`, not `submission-ready`.
- IHME/GHDx citation policy now has a manuscript citation draft, but final
  journal/IHME wording still requires human confirmation before submission.
- Reuse boundary is `manuscript-review-ready-not-redistributable`; exact
  redistribution and release-artifact permissions still require human
  confirmation.
- Uncertainty intervals are now carried into the candidate manuscript claims,
  but final UI wording still requires journal-specific review.
- Age handling is now explicit: `All ages` is not age-standardized and must not
  be described as age-adjusted.
- Project `capabilityStatus` remains `minimal-demo-plus-real-default-export`,
  not `submission-ready`.

## Claim Disposition

Teaching fixture claims may remain in the repository as internal traceability
checks, but they are not manuscript claims:

| Claim | Current role | Submission action |
|---|---|---|
| `gbd-demo-deaths` | teaching fixture number claim | Retain internally only |
| `gbd-demo-dalys` | teaching fixture number claim | Retain internally only |
| `gbd-demo-derived-ratio` | derived traceability check | Retain internally only |
| `gbd-demo-boundary` | demo boundary statement | Retain internally as a repository boundary |

The following claims are manuscript-specific candidates, but they are not
submission-ready until the strict gate passes:

| Claim | Current role | Submission action |
|---|---|---|
| `gbd-global-2023-deaths` | 2023 death number with UI | Complete citation, reuse, query profile, and journal wording |
| `gbd-global-2023-dalys` | 2023 DALY number with UI | Complete citation, reuse, query profile, and journal wording |
| `gbd-global-death-rate-change-1990-2023` | endpoint-scale rate change | Confirm metric scale and uncertainty treatment |
| `gbd-global-all-cause-scope-boundary` | manuscript boundary statement | Finalize GBD data-use and citation language |

Decision: do not promote the 4 former all-cause candidate claims to
`submission-ready`. After P7-5 they are retained as fixture-only repository
checks. The selected real-topic route is the CVD China/global scaffold.

## Human Review Checklist

The file `gbd_claim_review_checklist.csv` is the P7-1 decision table for the 4
candidate manuscript claims. Each row must record:

- claim id and current disposition;
- allowed decisions: retain, rewrite, downgrade, or delete;
- recommended decision and pending human-review status;
- rationale;
- citation, UI, metric, and age rules;
- manuscript action and submission upgrade requirement.

## Manuscript Review Draft

The file `gbd_manuscript_review_draft.md` is the P7-2 review draft. It contains
only a short Research Question, Data Source, Methods, Results, Limitations, and
Review Decisions section. It is not a full paper and should not be submitted as
one.

## Topic Upgrade Decision

The file `gbd_topic_upgrade_decision.md` is the P7-4 decision record. It keeps
the current global all-cause rows as a review fixture and blocks direct
promotion of those claims to `submission-ready`.

The file `gbd_targeted_query_candidates.csv` lists concrete next-query options
for a real manuscript. Each candidate must specify a cause, location strategy,
age strategy, sex strategy, measures, metrics, years, rationale, known risks,
priority, and pending human-selection status.

The selected candidate is `gbd-cvd-china-global-1990-2023`, instantiated at
`examples/gbd-cvd-china-global-instance/`.

## Gate Commands

Informational mode, suitable for CI:

```bash
python3 harness/validators/validate_gbd_submission_readiness.py
```

Manuscript-review-ready mode, suitable for CI when the review package must be
complete:

```bash
python3 harness/validators/validate_gbd_submission_readiness.py \
  --require-manuscript-review-ready
```

Manuscript-review-ready plus topic-upgrade mode, suitable for CI when the
project must also prove that a real GBD manuscript will be instantiated from a
targeted query rather than from the all-cause demo:

```bash
python3 harness/validators/validate_gbd_submission_readiness.py \
  --require-manuscript-review-ready \
  --require-topic-upgrade-decision
```

Strict submission mode, expected to fail until the blockers above are closed:

```bash
python3 harness/validators/validate_gbd_submission_readiness.py \
  --require-submission-ready
```

## Upgrade Criteria

To pass strict submission mode:

1. Update `gbd_query_profile.json` from `manuscript-review-ready` to
   `submission-ready` only after citation, reuse, uncertainty interval, metric,
   and age-standardization wording decisions are complete.
2. Keep fixture claims internal and promote only manuscript-specific candidate
   claims backed by the approved GBD export and source-aware interpretation
   boundaries.
3. Confirm IHME/GHDx citation and redistribution requirements.
4. Regenerate provenance and summary artifacts.
5. Replace or extend `gbd_targeted_query_candidates.csv` with the selected real
   query and generate a manuscript-specific claim registry for that query.
6. Re-run the strict gate and the full validation suite.
