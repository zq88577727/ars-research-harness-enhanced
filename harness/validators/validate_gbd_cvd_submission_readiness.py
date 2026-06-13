#!/usr/bin/env python3
"""Submission-readiness gate for the source-backed GBD CVD instance."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"

CLAIM_REVIEW_REQUIRED_COLUMNS = {
    "claim_id",
    "current_disposition",
    "allowed_decisions",
    "recommended_decision",
    "decision_status",
    "rationale",
    "citation_rule",
    "ui_rule",
    "metric_rule",
    "age_rule",
    "wording_rule",
    "manuscript_action",
    "submission_upgrade_requirement",
}
ALLOWED_RECOMMENDATIONS = {"retain", "rewrite", "downgrade", "delete"}
ALLOWED_REVIEW_DECISIONS = {"pending", "approve", "rewrite", "downgrade", "delete"}
REVIEWED_DECISIONS = {"approve", "rewrite", "downgrade", "delete"}
REVIEW_DRAFT_REQUIRED_HEADINGS = [
    "## Research Question",
    "## Data Source",
    "## Methods Fragment",
    "## Results Fragment",
    "## Limitations Fragment",
    "## Review Decisions Required",
]
REVIEW_DRAFT_REQUIRED_TERMS = [
    "GBD 2023",
    "version_id 8352",
    "cardiovascular diseases",
    "China",
    "Global",
    "All-age",
    "age-standardized",
    "Number",
    "Rate",
    "UI",
    "not submission-ready",
]
FORBIDDEN_WORDING = [
    "caused by",
    "led to",
    "due to policy",
    "clinical diagnosis",
    "mechanism",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def contains_any(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def validate_claim_review(path: Path, expected_claim_ids: set[str], require_submission_ready: bool, failures: list[dict]) -> dict:
    if not path.exists():
        failures.append({"check": "claim_review_checklist_exists", "path": rel(path)})
        return {"rowCount": 0, "coveredClaims": [], "pendingHumanReviewCount": 0}
    rows = read_csv(path)
    if not rows:
        failures.append({"check": "claim_review_checklist_rows"})
        return {"rowCount": 0, "coveredClaims": [], "pendingHumanReviewCount": 0}
    missing_columns = sorted(CLAIM_REVIEW_REQUIRED_COLUMNS - set(rows[0]))
    if missing_columns:
        failures.append({"check": "claim_review_checklist_columns", "missing": missing_columns})
    by_claim = {row.get("claim_id"): row for row in rows if row.get("claim_id")}
    missing_claims = sorted(expected_claim_ids - set(by_claim))
    extra_claims = sorted(set(by_claim) - expected_claim_ids)
    if missing_claims:
        failures.append({"check": "claim_review_checklist_coverage", "missing": missing_claims})
    if extra_claims:
        failures.append({"check": "claim_review_checklist_extra_claims", "extra": extra_claims})

    pending = 0
    for claim_id in sorted(expected_claim_ids & set(by_claim)):
        row = by_claim[claim_id]
        for field in CLAIM_REVIEW_REQUIRED_COLUMNS:
            if not row.get(field):
                failures.append({"check": "claim_review_field", "claim": claim_id, "field": field})
        allowed = set(row.get("allowed_decisions", "").split("|"))
        if not ALLOWED_RECOMMENDATIONS <= allowed:
            failures.append({"check": "claim_review_allowed_decisions", "claim": claim_id, "actual": sorted(allowed)})
        if row.get("recommended_decision") not in ALLOWED_RECOMMENDATIONS:
            failures.append({"check": "claim_review_recommendation", "claim": claim_id, "actual": row.get("recommended_decision")})
        if row.get("decision_status") == "pending_human_review":
            pending += 1
        elif row.get("decision_status") not in {"reviewed", "approved_for_submission"}:
            failures.append({"check": "claim_review_decision_status", "claim": claim_id, "actual": row.get("decision_status")})
        if require_submission_ready and row.get("decision_status") != "approved_for_submission":
            failures.append({"check": "claim_review_submission_approval", "claim": claim_id, "actual": row.get("decision_status")})

    return {
        "rowCount": len(rows),
        "coveredClaims": sorted(expected_claim_ids & set(by_claim)),
        "missingClaims": missing_claims,
        "pendingHumanReviewCount": pending,
    }


def validate_decision_record(path: Path, expected_claim_ids: set[str], require_submission_ready: bool, failures: list[dict]) -> dict:
    if not path.exists():
        failures.append({"check": "claim_review_decision_record_exists", "path": rel(path)})
        return {"decisionCount": 0, "pendingDecisionCount": 0, "reviewedDecisionCount": 0}
    record = load_json(path)
    if record.get("schemaVersion") != "gbd-cvd-claim-review-decision-record-v1":
        failures.append({"check": "claim_review_decision_record_schema", "actual": record.get("schemaVersion")})
    decisions = record.get("decisions", [])
    by_claim = {item.get("claimId"): item for item in decisions if item.get("claimId")}
    missing = sorted(expected_claim_ids - set(by_claim))
    extra = sorted(set(by_claim) - expected_claim_ids)
    if missing:
        failures.append({"check": "claim_review_decision_record_coverage", "missing": missing})
    if extra:
        failures.append({"check": "claim_review_decision_record_extra_claims", "extra": extra})
    pending = 0
    reviewed = 0
    for claim_id in sorted(expected_claim_ids & set(by_claim)):
        item = by_claim[claim_id]
        decision = item.get("decision")
        if decision not in ALLOWED_REVIEW_DECISIONS:
            failures.append({"check": "claim_review_decision_record_decision", "claim": claim_id, "actual": decision})
        if decision == "pending":
            pending += 1
        elif decision in REVIEWED_DECISIONS:
            reviewed += 1
        if require_submission_ready and decision != "approve":
            failures.append({"check": "claim_review_decision_record_submission_approval", "claim": claim_id, "actual": decision})
    return {
        "decisionCount": len(decisions),
        "coveredClaims": sorted(expected_claim_ids & set(by_claim)),
        "pendingDecisionCount": pending,
        "reviewedDecisionCount": reviewed,
    }


def validate_review_draft(path: Path, summary_path: Path, failures: list[dict]) -> dict:
    if not path.exists():
        failures.append({"check": "manuscript_review_draft_exists", "path": rel(path)})
        return {"headingCount": 0}
    text = path.read_text(encoding="utf-8")
    for heading in REVIEW_DRAFT_REQUIRED_HEADINGS:
        if heading not in text:
            failures.append({"check": "manuscript_review_draft_heading", "heading": heading})
    for term in REVIEW_DRAFT_REQUIRED_TERMS:
        if term not in text:
            failures.append({"check": "manuscript_review_draft_term", "term": term})
    forbidden = contains_any(text, FORBIDDEN_WORDING)
    if forbidden:
        failures.append({"check": "manuscript_review_draft_forbidden_wording", "terms": forbidden})

    if summary_path.exists():
        summary_rows = read_csv(summary_path)
        summary_text = path.read_text(encoding="utf-8")
        for row in summary_rows:
            for field in [
                "deaths_1990",
                "deaths_2023",
                "dalys_1990",
                "dalys_2023",
                "death_rate_1990",
                "death_rate_2023",
                "daly_rate_1990",
                "daly_rate_2023",
            ]:
                value = row.get(field, "")
                if value:
                    compact = f"{float(value):,.2f}" if float(value) >= 1000 else f"{float(value):.2f}"
                    plain = f"{float(value):.2f}"
                    if compact not in summary_text and plain not in summary_text:
                        failures.append({"check": "manuscript_review_draft_summary_value", "location": row.get("location"), "field": field, "value": compact})

    return {"headingCount": sum(1 for heading in REVIEW_DRAFT_REQUIRED_HEADINGS if heading in text)}


def validate_claim_wording(claims: list[dict], summary_path: Path, failures: list[dict]) -> dict:
    source_backed = [claim for claim in claims if claim.get("claimRole") == "source-backed-candidate-result"]
    if len(source_backed) != 4:
        failures.append({"check": "source_backed_claim_count", "actual": len(source_backed), "expected": 4})
    for claim in source_backed:
        text = claim.get("expectedText", "")
        if "UI" not in text:
            failures.append({"check": "claim_ui_wording", "claim": claim.get("id")})
        if "TBD" in text:
            failures.append({"check": "claim_tbd_removed", "claim": claim.get("id")})
        if claim.get("sourceFile") != rel(summary_path):
            failures.append({"check": "claim_source_file", "claim": claim.get("id"), "actual": claim.get("sourceFile")})
        forbidden = contains_any(text, FORBIDDEN_WORDING)
        if forbidden:
            failures.append({"check": "claim_forbidden_wording", "claim": claim.get("id"), "terms": forbidden})
        if claim.get("submissionDisposition") != "candidate-manuscript-claim":
            failures.append({"check": "claim_submission_disposition", "claim": claim.get("id"), "actual": claim.get("submissionDisposition")})
    return {"sourceBackedClaimCount": len(source_backed)}


def validate(project: Path, require_manuscript_review_ready: bool, require_submission_ready: bool) -> dict:
    failures: list[dict] = []
    blockers: list[str] = []
    warnings: list[dict] = []

    project_dir = project if project.is_absolute() else ROOT / project
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": rel(project_dir), "failures": [{"check": "project_manifest_exists"}]}
    manifest = load_json(manifest_path)

    query_profile_path = root_path(manifest.get("queryProfile", ""))
    analysis_manifest_path = root_path(manifest.get("analysisManifest", ""))
    provenance_path = root_path(manifest.get("provenanceFile", ""))
    claim_registry_path = root_path(manifest.get("claimRegistry", ""))
    claim_review_path = root_path(manifest.get("claimReviewChecklist", ""))
    claim_review_decisions_path = root_path(manifest.get("claimReviewDecisions", ""))
    claim_review_record_path = root_path(manifest.get("claimReviewDecisionRecord", ""))
    review_draft_path = root_path(manifest.get("manuscriptReviewDraft", ""))
    gate_doc_path = root_path(manifest.get("submissionReadinessGate", ""))

    for label, path in [
        ("query_profile", query_profile_path),
        ("analysis_manifest", analysis_manifest_path),
        ("provenance", provenance_path),
        ("claim_registry", claim_registry_path),
        ("submission_readiness_gate", gate_doc_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})
    if failures:
        return {"ok": False, "project": rel(project_dir), "failures": failures}

    query_profile = load_json(query_profile_path)
    analysis_manifest = load_json(analysis_manifest_path)
    provenance = load_json(provenance_path)
    claim_registry = load_json(claim_registry_path)
    analysis = analysis_manifest.get("analyses", {}).get("cvdChinaGlobal", {})
    provenance_analysis = provenance.get("analyses", {}).get("cvdChinaGlobal", {})

    source_path = root_path(analysis.get("sourceFile", ""))
    citation_path = root_path(analysis.get("sourceCitationFile", ""))
    summary_path = root_path(analysis.get("outputCsv", ""))
    summary_md_path = root_path(analysis.get("outputMarkdown", ""))

    for label, path in [
        ("source_export", source_path),
        ("source_citation", citation_path),
        ("summary_csv", summary_path),
        ("summary_markdown", summary_md_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})

    if manifest.get("capabilityStatus") != "source-backed-manuscript-candidate":
        blockers.append(f"project capabilityStatus is {manifest.get('capabilityStatus')}; expected source-backed-manuscript-candidate")
    if query_profile.get("profileStatus") != "source-backed-manuscript-candidate":
        blockers.append(f"query profile status is {query_profile.get('profileStatus')}; expected source-backed-manuscript-candidate")
    if require_submission_ready and manifest.get("capabilityStatus") != "submission-ready":
        blockers.append("project is not marked submission-ready")

    if analysis_manifest.get("queryProfile") != manifest.get("queryProfile"):
        failures.append({"check": "analysis_query_profile_link"})
    if analysis_manifest.get("claimRegistry") != manifest.get("claimRegistry"):
        failures.append({"check": "analysis_claim_registry_link"})
    if provenance.get("analysisManifest") != manifest.get("analysisManifest"):
        failures.append({"check": "provenance_analysis_manifest_link"})
    if provenance_analysis.get("sourceFile") != analysis.get("sourceFile"):
        failures.append({"check": "provenance_source_link"})
    if provenance_analysis.get("sourceCitationFile") != analysis.get("sourceCitationFile"):
        failures.append({"check": "provenance_source_citation_link"})

    citation_policy = query_profile.get("citationPolicy", {})
    if citation_policy.get("citationStatus") != "source-citation-recorded":
        blockers.append(f"citation status is {citation_policy.get('citationStatus')}; expected source-citation-recorded")
    if require_submission_ready and citation_policy.get("citationStatus") != "submission-ready":
        blockers.append("citation policy is not submission-ready")
    for field in ["source", "resultsToolUrl", "accessDate", "manuscriptCitationDraft", "finalSubmissionRequirement"]:
        if not citation_policy.get(field):
            failures.append({"check": "citation_policy_field", "field": field})
    if citation_path.exists():
        citation_text = citation_path.read_text(encoding="utf-8")
        for term in ["Global Burden of Disease Study 2023", "Institute for Health Metrics and Evaluation", "https://vizhub.healthdata.org/gbd-results/"]:
            if term not in citation_text:
                failures.append({"check": "source_citation_text", "term": term})

    reuse = query_profile.get("reuseBoundary", {})
    if reuse.get("status") != "source-export-terms-review-required":
        blockers.append(f"reuse status is {reuse.get('status')}; expected source-export-terms-review-required")
    if require_submission_ready and reuse.get("status") != "submission-ready":
        blockers.append("reuse terms are not confirmed for submission")
    if not reuse.get("submissionBoundary"):
        failures.append({"check": "reuse_submission_boundary"})

    ui_policy = query_profile.get("uncertaintyIntervalPolicy", {})
    if not {"lower", "upper"} <= set(ui_policy.get("sourceFieldsRequired", [])):
        failures.append({"check": "ui_source_fields"})
    if not ui_policy.get("submissionBoundary"):
        failures.append({"check": "ui_submission_boundary"})

    if not query_profile.get("metricPolicy", {}).get("metricSeparationRequired"):
        failures.append({"check": "metric_separation_required"})
    if query_profile.get("ageStandardization", {}).get("status") != "planned-age-standardized-rates-plus-all-age-counts":
        failures.append({"check": "age_standardization_status", "actual": query_profile.get("ageStandardization", {}).get("status")})

    claims = claim_registry.get("claims", [])
    expected_claim_ids = {claim.get("id") for claim in claims if claim.get("submissionDisposition") == "candidate-manuscript-claim"}
    claim_wording_summary = validate_claim_wording(claims, summary_path, failures)
    claim_review_summary = validate_claim_review(claim_review_path, expected_claim_ids, require_submission_ready, failures)
    decision_record_summary = validate_decision_record(claim_review_record_path, expected_claim_ids, require_submission_ready, failures)
    review_draft_summary = validate_review_draft(review_draft_path, summary_path, failures)

    gate_text = gate_doc_path.read_text(encoding="utf-8")
    for term in ["Current Blockers", "Required Submission Upgrade Criteria", "not submission-ready"]:
        if term not in gate_text:
            failures.append({"check": "submission_gate_doc_term", "term": term})

    if claim_review_summary["pendingHumanReviewCount"]:
        blockers.append(f"{claim_review_summary['pendingHumanReviewCount']} claim review decisions remain pending_human_review")
    if decision_record_summary["pendingDecisionCount"]:
        blockers.append(f"{decision_record_summary['pendingDecisionCount']} claim review decision-record entries remain pending")
    blockers.append("IHME/GHDx citation wording requires final human confirmation")
    blockers.append("IHME/GHDx reuse and redistribution terms require final human confirmation")
    blockers.append("Methods/results fragment is not a complete target-journal manuscript")

    if require_submission_ready and blockers:
        failures.append({"check": "submission_readiness_blockers", "blockers": blockers})

    status = "submission-ready" if not failures and not blockers else "source-backed-not-submission-ready"
    if blockers and not require_submission_ready:
        warnings.append({"check": "submission_readiness_blockers", "count": len(blockers)})

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "status": status,
        "requireManuscriptReviewReady": require_manuscript_review_ready,
        "requireSubmissionReady": require_submission_ready,
        "queryProfile": rel(query_profile_path),
        "provenanceFile": rel(provenance_path),
        "summaryCsv": rel(summary_path),
        "claimReviewChecklist": rel(claim_review_path),
        "claimReviewDecisions": rel(claim_review_decisions_path),
        "claimReviewDecisionRecord": rel(claim_review_record_path),
        "manuscriptReviewDraft": rel(review_draft_path),
        "claimWordingSummary": claim_wording_summary,
        "claimReviewSummary": claim_review_summary,
        "decisionRecordSummary": decision_record_summary,
        "manuscriptReviewDraftSummary": review_draft_summary,
        "blockers": blockers,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    parser.add_argument("--require-manuscript-review-ready", action="store_true")
    parser.add_argument("--require-submission-ready", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.project), args.require_manuscript_review_ready, args.require_submission_ready)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
