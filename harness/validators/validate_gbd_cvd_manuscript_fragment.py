#!/usr/bin/env python3
"""Validate the P7-11 GBD CVD manuscript fragment against reviewed claims."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"
REQUIRED_HEADINGS = [
    "## Research Question",
    "## Methods Fragment",
    "## Results Fragment",
    "## Claim Registry Linkage",
    "## Submission Boundary",
]
REQUIRED_METHOD_TERMS = [
    "GBD 2023",
    "version_id 8352",
    "Cardiovascular diseases",
    "China",
    "Global",
    "Both sexes",
    "1990",
    "2023",
    "All ages",
    "Number metric",
    "Age-standardized",
    "Rate metric",
    "UI",
]
FORBIDDEN_TERMS = [
    "caused by",
    "led to",
    "confidence interval",
    "p value",
    "clinical diagnosis",
    "mechanism",
    "policy effect",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def section(text: str, heading: str) -> str:
    pattern = rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group("body") if match else ""


def contains_forbidden(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in FORBIDDEN_TERMS if term in lowered]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def has_term(text: str, term: str) -> bool:
    return normalize_text(term) in normalize_text(text)


def validate(project: Path) -> dict:
    project_dir = project if project.is_absolute() else ROOT / project
    failures: list[dict] = []
    warnings: list[dict] = []

    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": rel(project_dir), "failures": [{"check": "project_manifest_exists"}]}

    manifest = load_json(manifest_path)
    fragment_path = root_path(manifest.get("manuscriptFragment", ""))
    registry_path = root_path(manifest.get("claimRegistry", ""))
    decisions_path = root_path(manifest.get("claimReviewDecisions", ""))
    record_path = root_path(manifest.get("claimReviewDecisionRecord", ""))
    analysis_manifest_path = root_path(manifest.get("analysisManifest", ""))

    for label, path in [
        ("manuscript_fragment", fragment_path),
        ("claim_registry", registry_path),
        ("claim_review_decisions", decisions_path),
        ("claim_review_decision_record", record_path),
        ("analysis_manifest", analysis_manifest_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})
    if failures:
        return {"ok": False, "project": rel(project_dir), "failures": failures}

    fragment = fragment_path.read_text(encoding="utf-8")
    registry = load_json(registry_path)
    decisions = load_json(decisions_path).get("decisions", [])
    record = load_json(record_path)
    analysis_manifest = load_json(analysis_manifest_path)

    claims = registry.get("claims", [])
    expected_claim_ids = {claim.get("id") for claim in claims if claim.get("submissionDisposition") == "candidate-manuscript-claim"}
    decisions_by_id = {item.get("claimId"): item for item in decisions}
    record_by_id = {item.get("claimId"): item for item in record.get("decisions", [])}

    for heading in REQUIRED_HEADINGS:
        if heading not in fragment:
            failures.append({"check": "fragment_heading", "heading": heading})

    methods = section(fragment, "## Methods Fragment")
    results = section(fragment, "## Results Fragment")
    linkage = section(fragment, "## Claim Registry Linkage")

    for term in REQUIRED_METHOD_TERMS:
        if not has_term(methods, term):
            failures.append({"check": "methods_required_term", "term": term})
    for term in ["not submission-ready", "IHME/GHDx citation wording", "reuse and redistribution terms"]:
        if not has_term(fragment, term):
            failures.append({"check": "submission_boundary_term", "term": term})

    forbidden = contains_forbidden(fragment)
    if forbidden:
        normalized_fragment = normalize_text(fragment).lower()
        allowed_contexts = {
            "confidence interval": "are not interpreted as confidence intervals or p values",
            "p value": "are not interpreted as confidence intervals or p values",
            "policy effect": "does not estimate causal, clinical, mechanistic, intervention, or policy effects",
            "mechanism": "does not estimate causal, clinical, mechanistic, intervention, or policy effects",
        }
        remaining = [
            term
            for term in forbidden
            if allowed_contexts.get(term, "") not in normalized_fragment
        ]
        if remaining:
            failures.append({"check": "fragment_forbidden_wording", "terms": remaining})

    if set(decisions_by_id) != expected_claim_ids:
        failures.append({"check": "decision_claim_coverage", "expected": sorted(expected_claim_ids), "actual": sorted(decisions_by_id)})
    if set(record_by_id) != expected_claim_ids:
        failures.append({"check": "decision_record_claim_coverage", "expected": sorted(expected_claim_ids), "actual": sorted(record_by_id)})
    if record.get("pendingDecisionCount") != 0 or record.get("reviewedDecisionCount") != len(expected_claim_ids):
        failures.append({
            "check": "decision_record_review_counts",
            "pending": record.get("pendingDecisionCount"),
            "reviewed": record.get("reviewedDecisionCount"),
            "expectedReviewed": len(expected_claim_ids),
        })

    for claim_id in sorted(expected_claim_ids):
        if claim_id not in linkage:
            failures.append({"check": "linkage_claim_id", "claim": claim_id})
        decision = decisions_by_id.get(claim_id, {}).get("decision")
        record_decision = record_by_id.get(claim_id, {}).get("decision")
        if decision != record_decision:
            failures.append({"check": "decision_record_match", "claim": claim_id, "decision": decision, "recordDecision": record_decision})
        if decision == "rewrite":
            replacement = decisions_by_id[claim_id].get("replacementText", "")
            if not replacement:
                failures.append({"check": "rewrite_replacement_text", "claim": claim_id})
            elif not has_term(results, replacement):
                failures.append({"check": "rewrite_text_in_results", "claim": claim_id})
        if decision == "approve":
            action = decisions_by_id[claim_id].get("manuscriptAction", "")
            if "boundary" not in action.lower() or "descriptive" not in fragment.lower():
                failures.append({"check": "approved_boundary_placement", "claim": claim_id})
        if decision == "downgrade":
            source_text = next((claim.get("expectedText", "") for claim in claims if claim.get("id") == claim_id), "")
            if source_text and has_term(results, source_text):
                failures.append({"check": "downgraded_claim_not_leading_result", "claim": claim_id})
            if not has_term(results, "supporting or table-only evidence"):
                failures.append({"check": "downgraded_claim_supporting_note", "claim": claim_id})
        if decisions_by_id.get(claim_id, {}).get("submissionReady") is True:
            failures.append({"check": "fragment_claim_not_submission_ready", "claim": claim_id})

    analysis = analysis_manifest.get("analyses", {}).get("cvdChinaGlobal", {})
    boundary = analysis.get("interpretationBoundary", "")
    for term in ["Counts and age-standardized rates must remain separate", "uncertainty intervals must be retained", "no causal"]:
        if term not in boundary:
            failures.append({"check": "analysis_boundary_term", "term": term})

    if "Percent rows" in fragment:
        warnings.append({"check": "percent_rows_in_fragment", "message": "P7-11 fragment should avoid percent-row narrative unless separately validated."})

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "manuscriptFragment": rel(fragment_path),
        "claimRegistry": rel(registry_path),
        "claimReviewDecisions": rel(decisions_path),
        "claimReviewDecisionRecord": rel(record_path),
        "claimCount": len(expected_claim_ids),
        "rewriteClaimCount": sum(1 for item in decisions if item.get("decision") == "rewrite"),
        "downgradedClaimCount": sum(1 for item in decisions if item.get("decision") == "downgrade"),
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    args = parser.parse_args()
    result = validate(Path(args.project))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
