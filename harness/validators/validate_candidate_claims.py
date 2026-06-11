#!/usr/bin/env python3
"""Validate candidate-claim extraction output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {"already-registered", "needs-human-review"}
ALLOWED_TIERS = {"core", "supporting", "background"}
ALLOWED_TYPES = {
    "model-estimate",
    "prevalence-or-percentage",
    "burden-estimate",
    "sample-size",
    "definition-or-threshold",
    "numeric-claim",
}


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    candidates = data.get("candidates", [])
    if not candidates:
        failures.append({"check": "candidates_present"})
    for candidate in candidates:
        if candidate.get("status") not in ALLOWED_STATUSES:
            failures.append({"check": "status", "id": candidate.get("id"), "status": candidate.get("status")})
        if candidate.get("suggestedTier") not in ALLOWED_TIERS:
            failures.append({"check": "suggested_tier", "id": candidate.get("id"), "tier": candidate.get("suggestedTier")})
        if candidate.get("type") not in ALLOWED_TYPES:
            failures.append({"check": "type", "id": candidate.get("id"), "type": candidate.get("type")})
        if not candidate.get("sentence"):
            failures.append({"check": "sentence", "id": candidate.get("id")})
        if "interpretationBoundaryNeeded" not in candidate:
            failures.append({"check": "interpretation_boundary_flag", "id": candidate.get("id")})
    needs_review = [candidate for candidate in candidates if candidate.get("status") == "needs-human-review"]
    tiers = {tier: 0 for tier in sorted(ALLOWED_TIERS)}
    for candidate in candidates:
        tier = candidate.get("suggestedTier")
        if tier in tiers:
            tiers[tier] += 1
    return {
        "ok": not failures,
        "candidateFile": str(path),
        "candidateCount": len(candidates),
        "needsHumanReviewCount": len(needs_review),
        "suggestedTiers": tiers,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="harness/claims/nhanes_candidate_claims.json")
    args = parser.parse_args()
    result = validate(Path(args.candidates))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
