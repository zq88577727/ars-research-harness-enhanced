#!/usr/bin/env python3
"""Submission-readiness gate for GBD demo projects.

This validator combines the GBD query profile, provenance sidecar, claim
registry, citation policy, and reuse boundary. Default mode is informational and
allows a demo to remain not submission-ready. Strict mode blocks until demo-only
claims and boundaries are upgraded.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-burden-minimal-demo"

DEMO_BOUNDARY_MARKERS = [
    "demo",
    "fixture",
    "teaching",
    "workflow demonstration",
    "before manuscript use",
    "before submission",
    "not a publishable",
    "verify query dimensions",
    "reuse-term confirmation",
]

MANUSCRIPT_REVIEW_READY_PROFILE_STATUSES = {"manuscript-review-ready", "submission-ready"}
SUBMISSION_READY_PROFILE_STATUSES = {"submission-ready"}
SUBMISSION_READY_REUSE_STATUSES = {"terms-confirmed", "submission-ready"}
SUBMISSION_READY_CITATION_STATUSES = {"complete", "submission-ready"}
MANUSCRIPT_REVIEW_READY_REUSE_STATUSES = {
    "manuscript-review-ready-not-redistributable",
    "terms-confirmed",
    "submission-ready",
}
MANUSCRIPT_REVIEW_READY_CITATION_STATUSES = {
    "manuscript-review-ready",
    "complete",
    "submission-ready",
}
CLAIM_DISPOSITIONS_ALLOWED = {
    "internal-retain",
    "candidate-manuscript-claim",
    "upgrade-before-submission",
    "submission-ready",
}
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
    "manuscript_action",
    "submission_upgrade_requirement",
}
CLAIM_REVIEW_ALLOWED_RECOMMENDATIONS = {"retain", "rewrite", "downgrade", "delete"}
MANUSCRIPT_REVIEW_DRAFT_REQUIRED_HEADINGS = [
    "## Research Question",
    "## Data Source",
    "## Methods Fragment",
    "## Results Fragment",
    "## Limitations Fragment",
    "## Review Decisions Required",
]
TOPIC_UPGRADE_DECISION_REQUIRED_HEADINGS = [
    "## Current Decision",
    "## Recommended Route",
    "## Required Upgrade Decisions",
    "## Decision Record",
]
TOPIC_UPGRADE_DECISION_REQUIRED_TERMS = [
    "Do not promote the current all-cause candidate claims to `submission-ready`",
    "targeted GBD query",
    "age-standardized",
    "uncertainty intervals",
    "reuse boundary",
]
TARGETED_QUERY_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_id",
    "research_question",
    "cause",
    "location",
    "age_strategy",
    "sex",
    "measures",
    "metrics",
    "years",
    "primary_claim_type",
    "rationale",
    "known_risks",
    "recommended_priority",
    "decision_status",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def project_path(project: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def contains_demo_marker(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in DEMO_BOUNDARY_MARKERS)


def classify_claim(claim: dict) -> dict:
    disposition = claim.get("submissionDisposition")
    text = " ".join(
        str(claim.get(field, ""))
        for field in ["id", "type", "sourceFile", "interpretationBoundary", "expectedText"]
    )
    if disposition == "submission-ready":
        readiness = "candidate-submission-claim"
        required_action = "Confirm journal-specific wording, uncertainty interval handling, and citation placement."
    elif disposition == "candidate-manuscript-claim":
        readiness = "candidate-manuscript-claim"
        required_action = "Retain as a manuscript-specific candidate, but block submission until citation, reuse, query profile, and wording gates pass."
    elif disposition == "internal-retain":
        readiness = "internal-retain-not-manuscript"
        required_action = "Retain only for repository traceability or teaching; exclude from manuscript result claims."
    elif disposition == "upgrade-before-submission" or contains_demo_marker(text):
        readiness = "requires-upgrade-before-submission"
        required_action = "Replace demo/fixture boundary with submission-ready source, citation, query, uncertainty, and reuse evidence."
    else:
        readiness = "requires-disposition-review"
        required_action = "Add submissionDisposition to classify whether this claim is internal, candidate manuscript, or submission-ready."
    return {
        "id": claim.get("id"),
        "tier": claim.get("tier"),
        "type": claim.get("type"),
        "claimRole": claim.get("claimRole"),
        "submissionDisposition": disposition,
        "sourceFile": claim.get("sourceFile"),
        "readiness": readiness,
        "requiredAction": required_action,
    }


def validate_claim_review_checklist(
    path: Path,
    manuscript_candidate_claims: list[dict],
    failures: list[dict],
) -> dict:
    rows = read_csv(path) if path.exists() else []
    if not rows:
        failures.append({"check": "claim_review_checklist_rows"})
        return {"rowCount": 0, "coveredClaims": []}
    missing_columns = sorted(CLAIM_REVIEW_REQUIRED_COLUMNS - set(rows[0]))
    if missing_columns:
        failures.append({"check": "claim_review_checklist_columns", "missing": missing_columns})
    row_by_claim = {row.get("claim_id"): row for row in rows if row.get("claim_id")}
    candidate_ids = {claim["id"] for claim in manuscript_candidate_claims}
    missing_claims = sorted(candidate_ids - set(row_by_claim))
    extra_claims = sorted(set(row_by_claim) - candidate_ids)
    if missing_claims:
        failures.append({"check": "claim_review_checklist_coverage", "missing": missing_claims})
    if extra_claims:
        failures.append({"check": "claim_review_checklist_extra_claims", "extra": extra_claims})
    for claim_id in sorted(candidate_ids & set(row_by_claim)):
        row = row_by_claim[claim_id]
        for field in CLAIM_REVIEW_REQUIRED_COLUMNS:
            if not row.get(field):
                failures.append({"check": "claim_review_checklist_field", "claim": claim_id, "field": field})
        options = set(row.get("allowed_decisions", "").split("|"))
        if not CLAIM_REVIEW_ALLOWED_RECOMMENDATIONS <= options:
            failures.append({"check": "claim_review_allowed_decisions", "claim": claim_id, "actual": sorted(options)})
        if row.get("recommended_decision") not in CLAIM_REVIEW_ALLOWED_RECOMMENDATIONS:
            failures.append({"check": "claim_review_recommended_decision", "claim": claim_id, "actual": row.get("recommended_decision")})
        if row.get("decision_status") != "pending_human_review":
            failures.append({"check": "claim_review_decision_status", "claim": claim_id, "actual": row.get("decision_status")})
    return {
        "rowCount": len(rows),
        "coveredClaims": sorted(candidate_ids & set(row_by_claim)),
        "missingClaims": missing_claims,
    }


def validate_manuscript_review_draft(path: Path, failures: list[dict]) -> dict:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    for heading in MANUSCRIPT_REVIEW_DRAFT_REQUIRED_HEADINGS:
        if heading not in text:
            failures.append({"check": "manuscript_review_draft_heading", "heading": heading})
    required_terms = ["GBD 2023", "version_id 8352", "UI", "All ages", "not age-standardized", "not submission-ready"]
    for term in required_terms:
        if term not in text:
            failures.append({"check": "manuscript_review_draft_term", "term": term})
    return {"headingCount": sum(1 for heading in MANUSCRIPT_REVIEW_DRAFT_REQUIRED_HEADINGS if heading in text)}


def validate_topic_upgrade_decision(decision_path: Path, candidates_path: Path, failures: list[dict]) -> dict:
    decision_text = decision_path.read_text(encoding="utf-8") if decision_path.exists() else ""
    normalized_decision_text = " ".join(decision_text.split()).lower()
    for heading in TOPIC_UPGRADE_DECISION_REQUIRED_HEADINGS:
        if heading not in decision_text:
            failures.append({"check": "topic_upgrade_decision_heading", "heading": heading})
    for term in TOPIC_UPGRADE_DECISION_REQUIRED_TERMS:
        if term.lower() not in normalized_decision_text:
            failures.append({"check": "topic_upgrade_decision_term", "term": term})

    rows = read_csv(candidates_path) if candidates_path.exists() else []
    if not rows:
        failures.append({"check": "targeted_query_candidates_rows"})
        return {"candidateCount": 0, "p0Candidates": []}

    missing_columns = sorted(TARGETED_QUERY_CANDIDATE_REQUIRED_COLUMNS - set(rows[0]))
    if missing_columns:
        failures.append({"check": "targeted_query_candidates_columns", "missing": missing_columns})

    p0_candidates = []
    selected_candidates = []
    for row in rows:
        candidate_id = row.get("candidate_id")
        for field in TARGETED_QUERY_CANDIDATE_REQUIRED_COLUMNS:
            if not row.get(field):
                failures.append({"check": "targeted_query_candidate_field", "candidate": candidate_id, "field": field})
        if row.get("recommended_priority") == "P0":
            p0_candidates.append(candidate_id)
        if row.get("decision_status") == "selected_for_scaffold":
            selected_candidates.append(candidate_id)
        elif row.get("decision_status") != "pending_human_selection":
            failures.append(
                {
                    "check": "targeted_query_candidate_decision_status",
                    "candidate": candidate_id,
                    "actual": row.get("decision_status"),
                }
            )
        metric_text = row.get("metrics", "")
        age_text = row.get("age_strategy", "")
        if "Rate" not in metric_text or "Number" not in metric_text:
            failures.append({"check": "targeted_query_metric_separation", "candidate": candidate_id})
        if "Age-standardized" not in age_text and "age-standardized" not in age_text:
            failures.append({"check": "targeted_query_age_standardization_plan", "candidate": candidate_id})

    if len(rows) < 3:
        failures.append({"check": "targeted_query_candidates_minimum", "actual": len(rows)})
    if not p0_candidates:
        failures.append({"check": "targeted_query_candidates_p0_present"})

    if len(selected_candidates) != 1:
        failures.append({"check": "targeted_query_candidate_selected_count", "actual": len(selected_candidates)})

    return {"candidateCount": len(rows), "p0Candidates": p0_candidates, "selectedCandidates": selected_candidates}


def validate(
    project: Path,
    require_manuscript_review_ready: bool,
    require_submission_ready: bool,
    require_topic_upgrade_decision: bool,
) -> dict:
    failures: list[dict] = []
    blockers: list[str] = []
    warnings: list[dict] = []
    require_manuscript_review_ready = require_manuscript_review_ready or require_submission_ready

    project_dir = project if project.is_absolute() else ROOT / project
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": str(project), "failures": [{"check": "project_manifest_exists"}]}
    manifest = load_json(manifest_path)
    fixture_only_project = str(manifest.get("capabilityStatus", "")).startswith("fixture-only")

    analysis_manifest_path = project_path(project_dir, manifest.get("analysisManifest", ""))
    claim_registry_path = project_path(project_dir, manifest.get("claimRegistry", ""))
    query_profile_path = project_path(project_dir, manifest.get("queryProfile", ""))
    provenance_path = project_path(project_dir, manifest.get("provenanceFile", ""))
    claim_review_path = project_path(project_dir, manifest.get("claimReviewChecklist", ""))
    manuscript_review_draft_path = project_path(project_dir, manifest.get("manuscriptReviewDraft", ""))
    topic_upgrade_decision_path = project_path(project_dir, manifest.get("topicUpgradeDecision", ""))
    targeted_query_candidates_path = project_path(project_dir, manifest.get("targetedQueryCandidates", ""))

    for label, path in [
        ("analysis_manifest", analysis_manifest_path),
        ("claim_registry", claim_registry_path),
        ("query_profile", query_profile_path),
        ("provenance", provenance_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})
    if failures:
        return {"ok": False, "project": str(project), "failures": failures}

    analysis_manifest = load_json(analysis_manifest_path)
    claim_registry = load_json(claim_registry_path)
    query_profile = load_json(query_profile_path)
    provenance = load_json(provenance_path)

    for field in ["researchQuestion", "targetStatement", "scopeBoundary"]:
        if not claim_registry.get(field):
            failures.append({"check": "claim_registry_manuscript_context", "field": field})

    if analysis_manifest.get("queryProfile") != manifest.get("queryProfile"):
        failures.append({"check": "analysis_manifest_query_profile_link"})
    if analysis_manifest.get("provenanceFile") != manifest.get("provenanceFile"):
        failures.append({"check": "analysis_manifest_provenance_link"})
    if query_profile.get("provenanceFile") != manifest.get("provenanceFile"):
        failures.append({"check": "query_profile_provenance_link"})
    if provenance.get("analysisManifest") != manifest.get("analysisManifest"):
        failures.append({"check": "provenance_analysis_manifest_link"})
    if provenance.get("queryManifest") != manifest.get("queryManifest"):
        failures.append({"check": "provenance_query_manifest_link"})

    profile_status = query_profile.get("profileStatus")
    if profile_status not in MANUSCRIPT_REVIEW_READY_PROFILE_STATUSES:
        blockers.append(f"query profile status is {profile_status}; expected manuscript-review-ready or submission-ready")
    if require_submission_ready and profile_status not in SUBMISSION_READY_PROFILE_STATUSES:
        blockers.append(f"query profile status is {profile_status}; expected submission-ready")

    citation = query_profile.get("citationPolicy", {})
    if citation.get("citationStatus") not in MANUSCRIPT_REVIEW_READY_CITATION_STATUSES:
        blockers.append("GBD citation policy is not ready for manuscript review")
    if require_submission_ready and citation.get("citationStatus") not in SUBMISSION_READY_CITATION_STATUSES:
        blockers.append("GBD citation policy is not complete for submission")
    for field in ["source", "resultsToolUrl", "accessDate", "manuscriptCitationDraft", "finalSubmissionRequirement"]:
        if not citation.get(field):
            failures.append({"check": "citation_policy_field", "field": field})

    reuse = query_profile.get("reuseBoundary", {})
    if reuse.get("status") not in MANUSCRIPT_REVIEW_READY_REUSE_STATUSES:
        blockers.append(f"reuse boundary status is {reuse.get('status')}; expected manuscript-review-ready or terms-confirmed")
    if require_submission_ready and reuse.get("status") not in SUBMISSION_READY_REUSE_STATUSES:
        blockers.append(f"reuse boundary status is {reuse.get('status')}; IHME/GHDx reuse terms must be confirmed")
    if contains_demo_marker(reuse.get("rule", "")):
        blockers.append("reuse boundary still contains demo-only wording")
    if not reuse.get("submissionBoundary"):
        failures.append({"check": "reuse_submission_boundary"})

    ui_policy = query_profile.get("uncertaintyIntervalPolicy", {})
    if contains_demo_marker(ui_policy.get("narrativePolicy", "")):
        blockers.append("uncertainty interval policy is still demo-only")
    if not {"lower", "upper"} <= set(ui_policy.get("sourceFieldsRequired", [])):
        failures.append({"check": "uncertainty_interval_fields"})
    if not ui_policy.get("reviewReadyRule"):
        failures.append({"check": "uncertainty_interval_review_ready_rule"})

    metric_policy = query_profile.get("metricPolicy", {})
    if not metric_policy.get("metricSeparationRequired"):
        failures.append({"check": "metric_separation_required"})

    age_standardization = query_profile.get("ageStandardization", {})
    if not age_standardization.get("status"):
        failures.append({"check": "age_standardization_status"})
    if contains_demo_marker(age_standardization.get("evidence", "")):
        blockers.append("age-standardization statement is still demo-specific")
    if age_standardization.get("status") == "not-age-standardized" and not age_standardization.get("allAgesInterpretationRule"):
        failures.append({"check": "all_ages_interpretation_rule"})

    claim_readiness = [classify_claim(claim) for claim in claim_registry.get("claims", [])]
    upgrade_claims = [claim for claim in claim_readiness if claim["readiness"] == "requires-upgrade-before-submission"]
    disposition_review_claims = [claim for claim in claim_readiness if claim["readiness"] == "requires-disposition-review"]
    manuscript_candidate_claims = [claim for claim in claim_readiness if claim["readiness"] == "candidate-manuscript-claim"]
    internal_retain_claims = [claim for claim in claim_readiness if claim["readiness"] == "internal-retain-not-manuscript"]
    submission_ready_claims = [claim for claim in claim_readiness if claim["readiness"] == "candidate-submission-claim"]
    unknown_dispositions = [
        claim
        for claim in claim_registry.get("claims", [])
        if claim.get("submissionDisposition") not in CLAIM_DISPOSITIONS_ALLOWED
    ]
    if unknown_dispositions:
        failures.append(
            {
                "check": "claim_submission_disposition",
                "claims": [claim.get("id") for claim in unknown_dispositions],
            }
        )
    if upgrade_claims:
        blockers.append(f"{len(upgrade_claims)} GBD claims require upgrade before submission")
    if disposition_review_claims:
        blockers.append(f"{len(disposition_review_claims)} GBD claims require explicit submission disposition review")
    if not manuscript_candidate_claims and not submission_ready_claims and not fixture_only_project:
        failures.append({"check": "manuscript_specific_claims_present"})
    if manuscript_candidate_claims and require_submission_ready:
        blockers.append(f"{len(manuscript_candidate_claims)} manuscript-specific GBD candidate claims are not submission-ready")

    claim_review_summary = {"rowCount": 0, "coveredClaims": []}
    manuscript_review_draft_summary = {"headingCount": 0}
    topic_upgrade_summary = {"candidateCount": 0, "p0Candidates": []}
    if require_manuscript_review_ready and fixture_only_project:
        failures.append({"check": "fixture_only_project_cannot_require_manuscript_review"})

    if require_manuscript_review_ready and not fixture_only_project:
        for label, path in [
            ("claim_review_checklist", claim_review_path),
            ("manuscript_review_draft", manuscript_review_draft_path),
        ]:
            if not str(path) or not path.exists():
                failures.append({"check": f"{label}_exists", "path": str(path)})
        if str(claim_review_path) and claim_review_path.exists():
            claim_review_summary = validate_claim_review_checklist(claim_review_path, manuscript_candidate_claims, failures)
        if str(manuscript_review_draft_path) and manuscript_review_draft_path.exists():
            manuscript_review_draft_summary = validate_manuscript_review_draft(manuscript_review_draft_path, failures)

    if require_topic_upgrade_decision:
        for label, path in [
            ("topic_upgrade_decision", topic_upgrade_decision_path),
            ("targeted_query_candidates", targeted_query_candidates_path),
        ]:
            if not str(path) or not path.exists():
                failures.append({"check": f"{label}_exists", "path": str(path)})
        if (
            str(topic_upgrade_decision_path)
            and topic_upgrade_decision_path.exists()
            and str(targeted_query_candidates_path)
            and targeted_query_candidates_path.exists()
        ):
            topic_upgrade_summary = validate_topic_upgrade_decision(
                topic_upgrade_decision_path,
                targeted_query_candidates_path,
                failures,
            )

    if require_submission_ready and manifest.get("capabilityStatus") != "submission-ready":
        blockers.append(f"project capabilityStatus is {manifest.get('capabilityStatus')}; expected submission-ready")

    if not failures and not blockers and fixture_only_project:
        status = "fixture-only"
    elif not failures and not blockers and profile_status == "manuscript-review-ready":
        status = "manuscript-review-ready"
    elif not blockers and not failures:
        status = "submission-ready"
    else:
        status = "demo-not-submission-ready"
    if blockers and not require_submission_ready:
        warnings.append({"check": "submission_readiness_blockers", "count": len(blockers)})
    if require_submission_ready and blockers:
        failures.append({"check": "submission_readiness_blockers", "blockers": blockers})

    return {
        "ok": not failures,
        "project": str(project_dir.relative_to(ROOT) if project_dir.is_relative_to(ROOT) else project_dir),
        "status": status,
        "requireSubmissionReady": require_submission_ready,
        "queryProfile": str(query_profile_path.relative_to(ROOT) if query_profile_path.is_relative_to(ROOT) else query_profile_path),
        "provenanceFile": str(provenance_path.relative_to(ROOT) if provenance_path.is_relative_to(ROOT) else provenance_path),
        "claimCount": len(claim_readiness),
        "researchQuestion": claim_registry.get("researchQuestion"),
        "targetStatement": claim_registry.get("targetStatement"),
        "claimReviewChecklist": str(claim_review_path.relative_to(ROOT) if str(claim_review_path) and claim_review_path.is_relative_to(ROOT) else claim_review_path),
        "claimReviewSummary": claim_review_summary,
        "manuscriptReviewDraft": str(manuscript_review_draft_path.relative_to(ROOT) if str(manuscript_review_draft_path) and manuscript_review_draft_path.is_relative_to(ROOT) else manuscript_review_draft_path),
        "manuscriptReviewDraftSummary": manuscript_review_draft_summary,
        "topicUpgradeDecision": str(topic_upgrade_decision_path.relative_to(ROOT) if str(topic_upgrade_decision_path) and topic_upgrade_decision_path.is_relative_to(ROOT) else topic_upgrade_decision_path),
        "targetedQueryCandidates": str(targeted_query_candidates_path.relative_to(ROOT) if str(targeted_query_candidates_path) and targeted_query_candidates_path.is_relative_to(ROOT) else targeted_query_candidates_path),
        "topicUpgradeSummary": topic_upgrade_summary,
        "claimsInternalRetain": internal_retain_claims,
        "claimsRequiringUpgrade": upgrade_claims + disposition_review_claims,
        "claimsCandidateForManuscript": manuscript_candidate_claims,
        "claimsSubmissionReady": submission_ready_claims,
        "blockers": blockers,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(DEFAULT_PROJECT.relative_to(ROOT)))
    parser.add_argument("--require-manuscript-review-ready", action="store_true")
    parser.add_argument("--require-submission-ready", action="store_true")
    parser.add_argument("--require-topic-upgrade-decision", action="store_true")
    args = parser.parse_args()
    result = validate(
        Path(args.project),
        args.require_manuscript_review_ready,
        args.require_submission_ready,
        args.require_topic_upgrade_decision,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
