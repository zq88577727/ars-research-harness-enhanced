#!/usr/bin/env python3
"""Prepare a human-review worksheet for candidate claim registry updates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def json_block(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_decisions(
    candidates: list[dict],
    candidates_path: Path,
    registry_path: Path | None,
    existing_decisions_path: Path | None,
) -> dict:
    needs_review = [candidate for candidate in candidates if candidate.get("status") == "needs-human-review"]
    existing_by_id = {}
    if existing_decisions_path and existing_decisions_path.exists():
        existing = json.loads(existing_decisions_path.read_text(encoding="utf-8"))
        existing_by_id = {
            decision.get("candidateId"): decision
            for decision in existing.get("decisions", [])
            if decision.get("candidateId")
        }
    return {
        "candidateFile": str(candidates_path),
        "registry": str(registry_path) if registry_path else None,
        "reviewState": "pending-human-review",
        "allowedDecisions": ["pending", "register", "reject", "defer", "merge"],
        "decisionRules": [
            "Use pending until a human reviewer confirms source artifact, source fields, tier, and interpretation boundary.",
            "Use register only when registryDraft is complete and contains no TODO placeholders.",
            "Use reject for non-claims, duplicated claims, unsupported statements, or sentences that should be rewritten instead of registered.",
            "Use defer when the source artifact or interpretation boundary is not yet available.",
            "Use merge when the sentence is already covered by an existing or broader claim; set mergeWith to that claim id.",
        ],
        "decisions": [existing_by_id.get(candidate["id"], pending_decision(candidate["id"])) for candidate in needs_review],
    }


def pending_decision(candidate_id: str) -> dict:
    return {
        "candidateId": candidate_id,
        "decision": "pending",
        "reviewer": "human-required",
        "rationale": "Pending human review; do not register automatically.",
        "mergeWith": None,
        "registryDraft": None,
    }


def build_review(candidates_path: Path, output_path: Path, decisions_output: Path | None, registry_path: Path | None) -> dict:
    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])
    needs_review = [candidate for candidate in candidates if candidate.get("status") == "needs-human-review"]
    decisions = build_decisions(candidates, candidates_path, registry_path, decisions_output)
    decision_counts: dict[str, int] = {}
    for decision in decisions["decisions"]:
        key = decision.get("decision", "missing")
        decision_counts[key] = decision_counts.get(key, 0) + 1
    lines = [
        "# Candidate Claim Registry Review",
        "",
        "This worksheet is a human review queue, not an automatically approved claim registry.",
        "For each candidate, confirm the exact source file, source fields, expected rendered text,",
        "tier, interpretation boundary, and whether the sentence should be registered at all.",
        "",
        "## Review Rules",
        "",
        "- Core: primary outcome, main model estimate, key denominator, or mandatory interpretation boundary.",
        "- Supporting: sensitivity analysis, secondary estimate, or derived traceability check.",
        "- Background: numeric literature, guideline, or context statement that needs citation but is not a study result.",
        "- Do not register a claim until the exact source artifact and interpretation boundary are known.",
        "",
        f"Candidate file: `{candidates_path}`",
        f"Machine-readable decisions: `{decisions_output}`" if decisions_output else "Machine-readable decisions: not generated",
        f"Total candidates: `{len(candidates)}`",
        f"Needs human review: `{len(needs_review)}`",
        "",
        "## Decision Workflow",
        "",
        "1. Keep a candidate as `pending` until a human reviewer confirms source artifact, source fields, tier, and interpretation boundary.",
        "2. Change the decision to `register`, `reject`, `defer`, or `merge` in the machine-readable decisions file.",
        "3. Run `python3 harness/scripts/apply_claim_review_decisions.py` to produce registry additions for approved `register` decisions.",
        "4. Copy approved additions into the claim registry only after a second review of source traceability.",
        "",
        "## Current Decision Summary",
        "",
        *[f"- `{key}`: `{decision_counts[key]}`" for key in sorted(decision_counts)],
        "",
        "## Registry Drafts",
        "",
    ]
    for candidate in needs_review:
        draft = {
            "id": candidate["id"].replace("-candidate-", "-reviewed-"),
            "tier": candidate["suggestedTier"],
            "type": candidate["type"],
            "expectedText": candidate["sentence"],
            "sourceFile": "TODO",
            "sourceFields": ["TODO"],
            "interpretationBoundary": "TODO",
        }
        lines.extend(
            [
                f"### {candidate['id']}",
                "",
                f"- Suggested tier: `{candidate['suggestedTier']}`",
                f"- Type: `{candidate['type']}`",
                f"- Interpretation boundary needed: `{candidate['interpretationBoundaryNeeded']}`",
                "",
                "Sentence:",
                "",
                f"> {candidate['sentence']}",
                "",
                "Draft registry object:",
                "",
                "```json",
                json_block(draft),
                "```",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    if decisions_output:
        decisions_output.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "candidateFile": str(candidates_path),
        "reviewFile": str(output_path),
        "decisionsFile": str(decisions_output) if decisions_output else None,
        "candidateCount": len(candidates),
        "needsHumanReviewCount": len(needs_review),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="harness/claims/nhanes_candidate_claims.json")
    parser.add_argument("--output", default="harness/claims/nhanes_candidate_claim_review.md")
    parser.add_argument("--decisions-output", default="harness/claims/nhanes_candidate_claim_decisions.json")
    parser.add_argument("--registry", default="harness/claims/nhanes_claim_registry.json")
    args = parser.parse_args()
    result = build_review(
        candidates_path=Path(args.candidates),
        output_path=Path(args.output),
        decisions_output=Path(args.decisions_output) if args.decisions_output else None,
        registry_path=Path(args.registry) if args.registry else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
