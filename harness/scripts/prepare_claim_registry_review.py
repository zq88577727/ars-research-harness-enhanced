#!/usr/bin/env python3
"""Prepare a human-review worksheet for candidate claim registry updates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def json_block(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_review(candidates_path: Path, output_path: Path) -> dict:
    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])
    needs_review = [candidate for candidate in candidates if candidate.get("status") == "needs-human-review"]
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
        f"Total candidates: `{len(candidates)}`",
        f"Needs human review: `{len(needs_review)}`",
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
    return {
        "ok": True,
        "candidateFile": str(candidates_path),
        "reviewFile": str(output_path),
        "candidateCount": len(candidates),
        "needsHumanReviewCount": len(needs_review),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="harness/claims/nhanes_candidate_claims.json")
    parser.add_argument("--output", default="harness/claims/nhanes_candidate_claim_review.md")
    args = parser.parse_args()
    result = build_review(Path(args.candidates), Path(args.output))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
