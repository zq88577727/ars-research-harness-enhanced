#!/usr/bin/env python3
"""Validate the P7-12 GBD CVD submission-package evidence layer."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def has(text: str, term: str) -> bool:
    return norm(term) in norm(text)


def validate(project: Path, allow_missing_source_export: bool = False) -> dict:
    project_dir = project if project.is_absolute() else ROOT / project
    failures: list[dict] = []
    warnings: list[dict] = []

    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": rel(project_dir), "failures": [{"check": "project_manifest_exists"}]}
    manifest = load_json(manifest_path)

    query_profile_path = root_path(manifest.get("queryProfile", ""))
    provenance_path = root_path(manifest.get("provenanceFile", ""))
    citation_review_path = root_path(manifest.get("citationPolicyReview", ""))
    reuse_review_path = root_path(manifest.get("reuseReview", ""))
    section_draft_path = root_path(manifest.get("manuscriptSectionDraft", ""))
    decisions_path = root_path(manifest.get("claimReviewDecisions", ""))

    for label, path in [
        ("query_profile", query_profile_path),
        ("provenance", provenance_path),
        ("citation_policy_review", citation_review_path),
        ("reuse_review", reuse_review_path),
        ("manuscript_section_draft", section_draft_path),
        ("claim_review_decisions", decisions_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})
    if failures:
        return {"ok": False, "project": rel(project_dir), "failures": failures}

    profile = load_json(query_profile_path)
    provenance = load_json(provenance_path)
    decisions = load_json(decisions_path).get("decisions", [])
    citation_review = citation_review_path.read_text(encoding="utf-8")
    reuse_review = reuse_review_path.read_text(encoding="utf-8")
    section_draft = section_draft_path.read_text(encoding="utf-8")

    analysis = provenance.get("analyses", {}).get("cvdChinaGlobal", {})
    citation_policy = profile.get("citationPolicy", {})
    reuse_boundary = profile.get("reuseBoundary", {})

    source_path = root_path(analysis.get("sourceFile", ""))
    source_citation_path = root_path(analysis.get("sourceCitationFile", ""))
    summary_path = root_path(analysis.get("outputCsv", ""))

    for label, path in [
        ("source_citation", source_citation_path),
        ("derived_summary", summary_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": str(path)})
    if not str(source_path) or not source_path.exists():
        if allow_missing_source_export:
            warnings.append({
                "check": "source_export_missing_public_release_mode",
                "path": rel(source_path) if str(source_path) else "",
            })
        else:
            failures.append({"check": "source_export_exists", "path": str(source_path)})

    if source_path.exists() and sha256(source_path) != analysis.get("sourceSha256"):
        failures.append({"check": "source_export_sha256"})
    if source_citation_path.exists() and sha256(source_citation_path) != analysis.get("sourceCitationSha256"):
        failures.append({"check": "source_citation_sha256"})
    if summary_path.exists() and sha256(summary_path) != analysis.get("outputCsvSha256"):
        failures.append({"check": "derived_summary_sha256"})

    if citation_policy.get("citationReviewStatus") != "reviewed-from-export-citation-human-confirmation-required":
        failures.append({"check": "citation_review_status", "actual": citation_policy.get("citationReviewStatus")})
    if citation_policy.get("exportCitationTextSha256") != analysis.get("sourceCitationSha256"):
        failures.append({"check": "citation_review_sha_link"})
    for term in [
        "Global Burden of Disease Collaborative Network",
        "Global Burden of Disease Study 2023 (GBD 2023) Results",
        "Institute for Health Metrics and Evaluation (IHME), 2024",
        "https://vizhub.healthdata.org/gbd-results/",
        "Accessed 2026-06-11",
        "human confirmation required",
    ]:
        if not has(citation_review, term):
            failures.append({"check": "citation_review_term", "term": term})

    if reuse_boundary.get("reviewStatus") != "reviewed-human-confirmation-required":
        failures.append({"check": "reuse_review_status", "actual": reuse_boundary.get("reviewStatus")})
    if source_path.exists() and reuse_boundary.get("sourceExportSizeBytes") != source_path.stat().st_size:
        failures.append({"check": "reuse_source_size", "expected": source_path.stat().st_size, "actual": reuse_boundary.get("sourceExportSizeBytes")})
    if summary_path.exists() and reuse_boundary.get("derivedSummarySizeBytes") != summary_path.stat().st_size:
        failures.append({"check": "reuse_summary_size", "expected": summary_path.stat().st_size, "actual": reuse_boundary.get("derivedSummarySizeBytes")})
    for term in [
        "source export should not be treated as a general redistribution dataset",
        "should not be packaged into public release artifacts",
        "derived summary is an aggregate",
        "human confirmation required",
    ]:
        if not has(reuse_review, term):
            failures.append({"check": "reuse_review_term", "term": term})

    for item in decisions:
        if item.get("decision") == "rewrite" and item.get("replacementText") and not has(section_draft, item["replacementText"]):
            failures.append({"check": "section_rewrite_text", "claim": item.get("claimId")})
        if item.get("decision") == "downgrade" and not has(section_draft, "supporting or table-only evidence"):
            failures.append({"check": "section_downgrade_boundary", "claim": item.get("claimId")})
        if item.get("submissionReady") is True:
            failures.append({"check": "section_claim_not_submission_ready", "claim": item.get("claimId")})

    for term in [
        "## Methods",
        "## Results",
        "## Limitations",
        "## Data Availability Draft",
        "GBD 2023, version_id 8352",
        "Cardiovascular diseases, China and Global, Both sexes",
        "All ages with the Number metric",
        "Age-standardized with the Rate metric",
        "Accessed 2026-06-11",
        "not final submission-ready",
    ]:
        if not has(section_draft, term):
            failures.append({"check": "section_draft_term", "term": term})

    forbidden_positive = ["caused by", "led to", "p <"]
    lowered = section_draft.lower()
    found = [term for term in forbidden_positive if term in lowered]
    if found:
        failures.append({"check": "section_forbidden_positive_wording", "terms": found})

    warnings.append({
        "check": "submission_ready_boundary",
        "message": "P7-12 validates a submission-package evidence layer, not final submission-ready status.",
    })

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "citationPolicyReview": rel(citation_review_path),
        "reuseReview": rel(reuse_review_path),
        "manuscriptSectionDraft": rel(section_draft_path),
        "citationReviewStatus": citation_policy.get("citationReviewStatus"),
        "reuseReviewStatus": reuse_boundary.get("reviewStatus"),
        "sourceExportSizeBytes": source_path.stat().st_size if source_path.exists() else None,
        "derivedSummarySizeBytes": summary_path.stat().st_size if summary_path.exists() else None,
        "allowMissingSourceExport": allow_missing_source_export,
        "rewriteClaimCount": sum(1 for item in decisions if item.get("decision") == "rewrite"),
        "downgradedClaimCount": sum(1 for item in decisions if item.get("decision") == "downgrade"),
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    parser.add_argument("--allow-missing-source-export", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.project), allow_missing_source_export=args.allow_missing_source_export)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
