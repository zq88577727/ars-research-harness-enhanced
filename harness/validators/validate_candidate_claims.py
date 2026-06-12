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
ALLOWED_DECISIONS = {"pending", "register", "reject", "defer", "merge"}
REQUIRED_REGISTER_FIELDS = {"id", "tier", "type", "expectedText", "sourceFile", "sourceFields", "interpretationBoundary"}


def has_todo(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or "TODO" in value
    if isinstance(value, list):
        return not value or any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def validate_decisions(decisions_path: Path, candidates: list[dict], failures: list[dict]) -> dict:
    decision_counts = {decision: 0 for decision in sorted(ALLOWED_DECISIONS)}
    if not decisions_path.exists():
        failures.append({"check": "decisions_file_exists", "path": str(decisions_path)})
        return decision_counts

    data = json.loads(decisions_path.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    candidate_ids = {candidate.get("id") for candidate in candidates}
    needs_review_ids = {
        candidate.get("id")
        for candidate in candidates
        if candidate.get("status") == "needs-human-review"
    }
    seen = set()
    for item in decisions:
        candidate_id = item.get("candidateId")
        decision = item.get("decision")
        seen.add(candidate_id)
        if candidate_id not in candidate_ids:
            failures.append({"check": "decision_candidate_exists", "candidateId": candidate_id})
        if decision not in ALLOWED_DECISIONS:
            failures.append({"check": "decision_allowed", "candidateId": candidate_id, "decision": decision})
            continue
        decision_counts[decision] += 1
        if decision == "register":
            draft = item.get("registryDraft")
            if not isinstance(draft, dict):
                failures.append({"check": "registry_draft_object", "candidateId": candidate_id})
                continue
            missing = sorted(REQUIRED_REGISTER_FIELDS - set(draft))
            if missing:
                failures.append({"check": "registry_draft_required_fields", "candidateId": candidate_id, "missing": missing})
            if draft.get("tier") not in ALLOWED_TIERS:
                failures.append({"check": "registry_draft_tier", "candidateId": candidate_id, "tier": draft.get("tier")})
            for field in REQUIRED_REGISTER_FIELDS:
                if field in draft and has_todo(draft[field]):
                    failures.append({"check": "registry_draft_no_todo", "candidateId": candidate_id, "field": field})
        elif decision in {"reject", "defer"} and not item.get("rationale"):
            failures.append({"check": "decision_rationale", "candidateId": candidate_id, "decision": decision})
        elif decision == "merge" and not item.get("mergeWith"):
            failures.append({"check": "merge_target", "candidateId": candidate_id})

    missing_decisions = sorted(needs_review_ids - seen)
    if missing_decisions:
        failures.append({"check": "all_needs_review_candidates_have_decisions", "missing": missing_decisions})
    return decision_counts


def validate(path: Path, review_path: Path | None, decisions_path: Path | None) -> dict:
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
    if review_path:
        if not review_path.exists():
            failures.append({"check": "review_file_exists", "path": str(review_path)})
        else:
            review = review_path.read_text(encoding="utf-8")
            if "human review queue" not in review:
                failures.append({"check": "review_file_boundary"})
            for candidate in needs_review:
                if candidate["id"] not in review:
                    failures.append({"check": "review_candidate_present", "id": candidate["id"]})
    decision_counts = None
    if decisions_path:
        decision_counts = validate_decisions(decisions_path, candidates, failures)
    tiers = {tier: 0 for tier in sorted(ALLOWED_TIERS)}
    for candidate in candidates:
        tier = candidate.get("suggestedTier")
        if tier in tiers:
            tiers[tier] += 1
    return {
        "ok": not failures,
        "candidateFile": str(path),
        "reviewFile": str(review_path) if review_path else None,
        "decisionsFile": str(decisions_path) if decisions_path else None,
        "candidateCount": len(candidates),
        "needsHumanReviewCount": len(needs_review),
        "suggestedTiers": tiers,
        "decisionCounts": decision_counts,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="harness/claims/nhanes_candidate_claims.json")
    parser.add_argument("--review", default="harness/claims/nhanes_candidate_claim_review.md")
    parser.add_argument("--decisions", default="harness/claims/nhanes_candidate_claim_decisions.json")
    args = parser.parse_args()
    result = validate(
        Path(args.candidates),
        Path(args.review) if args.review else None,
        Path(args.decisions) if args.decisions else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
