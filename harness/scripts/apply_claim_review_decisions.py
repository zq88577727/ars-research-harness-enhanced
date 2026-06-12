#!/usr/bin/env python3
"""Create claim-registry additions from approved candidate-claim review decisions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_DECISIONS = {"pending", "register", "reject", "defer", "merge"}
ALLOWED_TIERS = {"core", "supporting", "background"}
REQUIRED_DRAFT_FIELDS = {"id", "tier", "type", "expectedText", "sourceFile", "sourceFields", "interpretationBoundary"}


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


def validate_register_draft(candidate_id: str, draft: object) -> list[dict]:
    failures = []
    if not isinstance(draft, dict):
        return [{"check": "registry_draft_object", "candidateId": candidate_id}]
    missing = sorted(REQUIRED_DRAFT_FIELDS - set(draft))
    if missing:
        failures.append({"check": "registry_draft_required_fields", "candidateId": candidate_id, "missing": missing})
    if draft.get("tier") not in ALLOWED_TIERS:
        failures.append({"check": "registry_draft_tier", "candidateId": candidate_id, "tier": draft.get("tier")})
    for field in REQUIRED_DRAFT_FIELDS:
        if field in draft and has_todo(draft[field]):
            failures.append({"check": "registry_draft_no_todo", "candidateId": candidate_id, "field": field})
    return failures


def apply_decisions(candidates_path: Path, decisions_path: Path, output_path: Path | None) -> dict:
    candidates_data = json.loads(candidates_path.read_text(encoding="utf-8"))
    decisions_data = json.loads(decisions_path.read_text(encoding="utf-8"))
    candidate_ids = {candidate.get("id") for candidate in candidates_data.get("candidates", [])}
    needs_review_ids = {
        candidate.get("id")
        for candidate in candidates_data.get("candidates", [])
        if candidate.get("status") == "needs-human-review"
    }
    failures = []
    additions = []
    seen = set()

    for item in decisions_data.get("decisions", []):
        candidate_id = item.get("candidateId")
        decision = item.get("decision")
        seen.add(candidate_id)
        if candidate_id not in candidate_ids:
            failures.append({"check": "candidate_exists", "candidateId": candidate_id})
        if decision not in ALLOWED_DECISIONS:
            failures.append({"check": "decision_allowed", "candidateId": candidate_id, "decision": decision})
            continue
        if decision == "register":
            failures.extend(validate_register_draft(candidate_id, item.get("registryDraft")))
            if not any(failure.get("candidateId") == candidate_id for failure in failures):
                additions.append(item["registryDraft"])
        elif decision in {"reject", "defer"} and not item.get("rationale"):
            failures.append({"check": "decision_rationale", "candidateId": candidate_id, "decision": decision})
        elif decision == "merge" and not item.get("mergeWith"):
            failures.append({"check": "merge_target", "candidateId": candidate_id})

    missing_decisions = sorted(needs_review_ids - seen)
    if missing_decisions:
        failures.append({"check": "all_needs_review_candidates_have_decisions", "missing": missing_decisions})

    result = {
        "ok": not failures,
        "candidateFile": str(candidates_path),
        "decisionsFile": str(decisions_path),
        "outputFile": str(output_path) if output_path else None,
        "decisionCounts": {},
        "approvedRegisterCount": len(additions),
        "draftAdditions": additions,
        "failures": failures,
    }
    for item in decisions_data.get("decisions", []):
        decision = item.get("decision", "missing")
        result["decisionCounts"][decision] = result["decisionCounts"].get(decision, 0) + 1

    if output_path:
        output = {
            "sourceCandidateFile": str(candidates_path),
            "sourceDecisionsFile": str(decisions_path),
            "claims": additions,
        }
        output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="harness/claims/nhanes_candidate_claims.json")
    parser.add_argument("--decisions", default="harness/claims/nhanes_candidate_claim_decisions.json")
    parser.add_argument("--output", default="harness/claims/nhanes_claim_registry_additions.draft.json")
    args = parser.parse_args()
    result = apply_decisions(Path(args.candidates), Path(args.decisions), Path(args.output) if args.output else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
