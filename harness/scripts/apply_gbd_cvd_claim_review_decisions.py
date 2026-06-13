#!/usr/bin/env python3
"""Apply or audit human review decisions for GBD CVD manuscript candidate claims."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"
ALLOWED_DECISIONS = {"pending", "approve", "rewrite", "downgrade", "delete"}
REVIEWED_DECISIONS = {"approve", "rewrite", "downgrade", "delete"}
CHECKLIST_STATUS_BY_DECISION = {
    "pending": "pending_human_review",
    "approve": "reviewed",
    "rewrite": "reviewed",
    "downgrade": "reviewed",
    "delete": "reviewed",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def validate_decision_item(item: dict, claim_ids: set[str], require_reviewed: bool) -> list[dict]:
    failures = []
    claim_id = item.get("claimId")
    decision = item.get("decision")
    if claim_id not in claim_ids:
        failures.append({"check": "decision_claim_exists", "claim": claim_id})
    if decision not in ALLOWED_DECISIONS:
        failures.append({"check": "decision_allowed", "claim": claim_id, "actual": decision})
        return failures
    if require_reviewed and decision not in REVIEWED_DECISIONS:
        failures.append({"check": "decision_reviewed_required", "claim": claim_id, "actual": decision})
    if decision in REVIEWED_DECISIONS:
        for field in ["reviewer", "reviewedAt", "rationale", "manuscriptAction"]:
            if not item.get(field) or str(item.get(field)).strip() == "TBD":
                failures.append({"check": "review_decision_field", "claim": claim_id, "field": field})
    if decision == "rewrite" and not item.get("replacementText"):
        failures.append({"check": "rewrite_replacement_text", "claim": claim_id})
    if decision == "delete" and item.get("submissionReady") is True:
        failures.append({"check": "deleted_claim_not_submission_ready", "claim": claim_id})
    if item.get("submissionReady") is True and decision not in {"approve", "rewrite"}:
        failures.append({"check": "submission_ready_decision", "claim": claim_id, "decision": decision})
    return failures


def apply_decisions(project: Path, require_reviewed: bool, update_checklist: bool, output_override: Path | None) -> dict:
    project_dir = project if project.is_absolute() else ROOT / project
    manifest = load_json(project_dir / "project_manifest.json")
    checklist_path = root_path(manifest["claimReviewChecklist"])
    decisions_path = root_path(manifest["claimReviewDecisions"])
    record_path = output_override or root_path(manifest["claimReviewDecisionRecord"])

    checklist_rows = read_csv(checklist_path)
    fieldnames = list(checklist_rows[0]) if checklist_rows else []
    decisions_data = load_json(decisions_path)
    claim_ids = {row["claim_id"] for row in checklist_rows}
    decision_items = decisions_data.get("decisions", [])
    decisions_by_claim = {item.get("claimId"): item for item in decision_items}

    failures: list[dict] = []
    missing = sorted(claim_ids - set(decisions_by_claim))
    extra = sorted(set(decisions_by_claim) - claim_ids)
    if missing:
        failures.append({"check": "decision_coverage_missing", "missing": missing})
    if extra:
        failures.append({"check": "decision_coverage_extra", "extra": extra})
    for item in decision_items:
        failures.extend(validate_decision_item(item, claim_ids, require_reviewed))

    decision_counts: dict[str, int] = {}
    applied_rows = []
    for row in checklist_rows:
        item = decisions_by_claim.get(row["claim_id"], {"decision": "pending"})
        decision = item.get("decision", "pending")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        updated = dict(row)
        if decision in ALLOWED_DECISIONS:
            updated["recommended_decision"] = "retain" if decision == "approve" else decision
            updated["decision_status"] = CHECKLIST_STATUS_BY_DECISION[decision]
            if item.get("rationale") and item.get("rationale") != "TBD by human reviewer.":
                updated["rationale"] = item["rationale"]
            if item.get("manuscriptAction") and item.get("manuscriptAction") != "TBD":
                updated["manuscript_action"] = item["manuscriptAction"]
            if decision == "rewrite" and item.get("replacementText"):
                updated["wording_rule"] = f"Use reviewed replacement wording: {item['replacementText']}"
            if decision == "delete":
                updated["manuscript_action"] = "Remove from manuscript use."
        applied_rows.append(updated)

    record = {
        "schemaVersion": "gbd-cvd-claim-review-decision-record-v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "project": rel(project_dir),
        "sourceChecklist": rel(checklist_path),
        "sourceDecisions": rel(decisions_path),
        "updatedChecklist": rel(checklist_path) if update_checklist else None,
        "requireReviewed": require_reviewed,
        "updateChecklist": update_checklist,
        "decisionCounts": decision_counts,
        "claimCount": len(claim_ids),
        "reviewedDecisionCount": sum(decision_counts.get(decision, 0) for decision in REVIEWED_DECISIONS),
        "pendingDecisionCount": decision_counts.get("pending", 0),
        "decisions": [
            {
                "claimId": item.get("claimId"),
                "decision": item.get("decision"),
                "reviewer": item.get("reviewer"),
                "reviewedAt": item.get("reviewedAt"),
                "rationale": item.get("rationale"),
                "replacementText": item.get("replacementText", ""),
                "manuscriptAction": item.get("manuscriptAction"),
                "submissionReady": item.get("submissionReady", False),
            }
            for item in decision_items
        ],
        "failures": failures,
    }
    record["ok"] = not failures
    write_json(record_path, record)
    if update_checklist and not failures:
        write_csv(checklist_path, applied_rows, fieldnames)

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "decisionsFile": rel(decisions_path),
        "decisionRecord": rel(record_path),
        "updateChecklist": update_checklist,
        "requireReviewed": require_reviewed,
        "decisionCounts": decision_counts,
        "pendingDecisionCount": record["pendingDecisionCount"],
        "reviewedDecisionCount": record["reviewedDecisionCount"],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    parser.add_argument("--require-reviewed", action="store_true")
    parser.add_argument("--update-checklist", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    result = apply_decisions(
        Path(args.project),
        require_reviewed=args.require_reviewed,
        update_checklist=args.update_checklist,
        output_override=Path(args.output) if args.output else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
