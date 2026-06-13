#!/usr/bin/env python3
"""Validate a targeted GBD manuscript scaffold before source export exists."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"
REQUIRED_QUERY_COLUMNS = {
    "gbd_release",
    "measure",
    "metric",
    "cause",
    "location",
    "age",
    "sex",
    "year",
    "export_file",
}
ALLOWED_PENDING_DISPOSITIONS = {"pending-export", "candidate-manuscript-claim"}
REQUIRED_ANALYSIS_KEYS = {
    "sourceFile",
    "sourceCitationFile",
    "outputCsv",
    "outputMarkdown",
    "claimRegistryOutput",
    "dimensionFilter",
    "locations",
    "years",
    "countAge",
    "rateAge",
    "requiredColumns",
    "interpretationBoundary",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def validate(project: Path, require_export: bool = False) -> dict:
    failures: list[dict] = []
    warnings: list[dict] = []
    project_dir = project if project.is_absolute() else ROOT / project

    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": rel(project_dir), "failures": [{"check": "project_manifest_exists"}]}
    manifest = load_json(manifest_path)

    query_path = ROOT / manifest.get("queryManifest", "")
    profile_path = ROOT / manifest.get("queryProfile", "")
    analysis_path = ROOT / manifest.get("analysisManifest", "")
    registry_path = ROOT / manifest.get("claimRegistry", "")
    candidates_path = ROOT / manifest.get("sourceCandidateMatrix", "")
    provenance_path = ROOT / manifest.get("provenanceFile", "")
    for label, path in [
        ("query_manifest", query_path),
        ("query_profile", profile_path),
        ("analysis_manifest", analysis_path),
        ("claim_registry", registry_path),
        ("source_candidate_matrix", candidates_path),
    ]:
        if not str(path) or not path.exists():
            failures.append({"check": f"{label}_exists", "path": rel(path)})
    if failures:
        return {"ok": False, "project": rel(project_dir), "failures": failures}

    query_rows = read_csv(query_path)
    profile = load_json(profile_path)
    analysis = load_json(analysis_path)
    registry = load_json(registry_path)
    candidate_rows = read_csv(candidates_path)

    selected_id = manifest.get("selectedCandidateId")
    selected_rows = [row for row in candidate_rows if row.get("candidate_id") == selected_id]
    if len(selected_rows) != 1:
        failures.append({"check": "selected_candidate_present", "selectedCandidateId": selected_id})
    elif selected_rows[0].get("decision_status") != "selected_for_scaffold":
        failures.append({"check": "selected_candidate_status", "actual": selected_rows[0].get("decision_status")})

    capability_status = manifest.get("capabilityStatus")
    if capability_status not in {"targeted-scaffold-awaiting-export", "source-backed-manuscript-candidate"}:
        failures.append({"check": "capability_status", "actual": capability_status})
    if manifest.get("teachingFixture") is not False:
        failures.append({"check": "not_teaching_fixture"})
    if not manifest.get("manuscriptBoundary"):
        failures.append({"check": "manuscript_boundary"})

    if not query_rows:
        failures.append({"check": "query_rows_present"})
    else:
        missing_columns = sorted(REQUIRED_QUERY_COLUMNS - set(query_rows[0]))
        if missing_columns:
            failures.append({"check": "query_manifest_columns", "missing": missing_columns})
        expected_causes = {"Cardiovascular diseases"}
        expected_locations = {"China", "Global"}
        expected_measures = {"Deaths", "DALYs"}
        expected_metrics = {"Number", "Rate"}
        expected_years = {"1990", "2023"}
        expected_ages = {"All ages", "Age-standardized"}
        observed_causes = {row.get("cause") for row in query_rows}
        observed_locations = {row.get("location") for row in query_rows}
        observed_measures = {row.get("measure") for row in query_rows}
        observed_metrics = {row.get("metric") for row in query_rows}
        observed_years = {row.get("year") for row in query_rows}
        observed_ages = {row.get("age") for row in query_rows}
        for label, observed, expected in [
            ("cause", observed_causes, expected_causes),
            ("location", observed_locations, expected_locations),
            ("measure", observed_measures, expected_measures),
            ("metric", observed_metrics, expected_metrics),
            ("year", observed_years, expected_years),
            ("age", observed_ages, expected_ages),
        ]:
            if observed != expected:
                failures.append({"check": f"query_{label}_coverage", "actual": sorted(observed), "expected": sorted(expected)})
        if len(query_rows) != 16:
            failures.append({"check": "query_row_count", "actual": len(query_rows), "expected": 16})
        missing_exports = set()
        present_exports = set()
        for row in query_rows:
            for column in REQUIRED_QUERY_COLUMNS:
                if not row.get(column):
                    failures.append({"check": "query_dimension_filled", "column": column})
            export_path = ROOT / row.get("export_file", "")
            if export_path.exists():
                present_exports.add(rel(export_path))
            elif require_export:
                missing_exports.add(rel(export_path))
        for export_path in sorted(present_exports):
            warnings.append({"check": "source_export_present", "path": export_path})
        for export_path in sorted(missing_exports):
            failures.append({"check": "source_export_exists", "path": export_path})

    if profile.get("schemaVersion") != "gbd-query-profile-v1":
        failures.append({"check": "profile_schema", "actual": profile.get("schemaVersion")})
    if profile.get("profileStatus") != capability_status:
        failures.append({"check": "profile_status", "actual": profile.get("profileStatus")})
    if profile.get("selectedCandidateId") != selected_id:
        failures.append({"check": "profile_selected_candidate"})
    dimensions = profile.get("dimensions", {})
    if dimensions.get("cause") != "Cardiovascular diseases":
        failures.append({"check": "profile_cause", "actual": dimensions.get("cause")})
    if set(dimensions.get("locations", [])) != {"China", "Global"}:
        failures.append({"check": "profile_locations", "actual": dimensions.get("locations")})
    if not profile.get("metricPolicy", {}).get("metricSeparationRequired"):
        failures.append({"check": "metric_separation_required"})
    age_status = profile.get("ageStandardization", {}).get("status")
    if age_status != "planned-age-standardized-rates-plus-all-age-counts":
        failures.append({"check": "age_standardization_status", "actual": age_status})
    ui_fields = set(profile.get("uncertaintyIntervalPolicy", {}).get("sourceFieldsRequired", []))
    if not {"lower", "upper"} <= ui_fields:
        failures.append({"check": "ui_fields"})
    if profile.get("citationPolicy", {}).get("citationStatus") not in {"draft-awaiting-export", "source-citation-recorded"}:
        failures.append({"check": "citation_status", "actual": profile.get("citationPolicy", {}).get("citationStatus")})
    if profile.get("reuseBoundary", {}).get("status") not in {"awaiting-export-terms-review", "source-export-terms-review-required"}:
        failures.append({"check": "reuse_status", "actual": profile.get("reuseBoundary", {}).get("status")})

    if analysis.get("queryProfile") != manifest.get("queryProfile"):
        failures.append({"check": "analysis_query_profile_link"})
    if analysis.get("queryManifest") != manifest.get("queryManifest"):
        failures.append({"check": "analysis_query_manifest_link"})
    if analysis.get("claimRegistry") != manifest.get("claimRegistry"):
        failures.append({"check": "analysis_claim_registry_link"})
    if analysis.get("provenanceFile") != manifest.get("provenanceFile"):
        failures.append({"check": "analysis_provenance_link"})
    analysis_config = analysis.get("analyses", {}).get("cvdChinaGlobal", {})
    missing_analysis_keys = sorted(REQUIRED_ANALYSIS_KEYS - set(analysis_config))
    if missing_analysis_keys:
        failures.append({"check": "analysis_required_keys", "missing": missing_analysis_keys})
    else:
        source_path = ROOT / analysis_config["sourceFile"]
        output_csv = ROOT / analysis_config["outputCsv"]
        output_md = ROOT / analysis_config["outputMarkdown"]
        claim_registry_output = ROOT / analysis_config["claimRegistryOutput"]
        if analysis_config["sourceFile"] not in {row.get("export_file") for row in query_rows}:
            failures.append({"check": "analysis_source_matches_query_manifest", "sourceFile": analysis_config["sourceFile"]})
        if set(analysis_config.get("locations", [])) != {"China", "Global"}:
            failures.append({"check": "analysis_locations", "actual": analysis_config.get("locations")})
        if set(analysis_config.get("years", [])) != {"1990", "2023"}:
            failures.append({"check": "analysis_years", "actual": analysis_config.get("years")})
        if analysis_config.get("countAge") != "All ages":
            failures.append({"check": "analysis_count_age", "actual": analysis_config.get("countAge")})
        if analysis_config.get("rateAge") != "Age-standardized":
            failures.append({"check": "analysis_rate_age", "actual": analysis_config.get("rateAge")})
        if not source_path.exists():
            if require_export:
                failures.append({"check": "analysis_source_export_exists", "path": rel(source_path)})
        else:
            warnings.append({"check": "analysis_source_export_present", "path": rel(source_path)})
            for label, output_path in [
                ("analysis_output_csv", output_csv),
                ("analysis_output_markdown", output_md),
                ("analysis_claim_registry_output", claim_registry_output),
                ("analysis_provenance", provenance_path),
            ]:
                if not output_path.exists():
                    failures.append({"check": f"{label}_exists_after_source_export", "path": rel(output_path)})

    if registry.get("selectedCandidateId") != selected_id:
        failures.append({"check": "registry_selected_candidate"})
    for field in ["researchQuestion", "targetStatement", "scopeBoundary"]:
        if not registry.get(field):
            failures.append({"check": "registry_context", "field": field})
    claims = registry.get("claims", [])
    if len(claims) < 4:
        failures.append({"check": "claim_skeleton_count", "actual": len(claims)})
    pending_claims = [claim for claim in claims if claim.get("submissionDisposition") == "pending-export"]
    source_backed_claims = [claim for claim in claims if claim.get("claimRole") == "source-backed-candidate-result"]
    if capability_status == "targeted-scaffold-awaiting-export" and len(pending_claims) < 3:
        failures.append({"check": "pending_export_claims_present", "actual": len(pending_claims)})
    if capability_status == "source-backed-manuscript-candidate":
        if pending_claims:
            failures.append({"check": "no_pending_claims_after_source_backing", "actual": len(pending_claims)})
        if len(source_backed_claims) < 4:
            failures.append({"check": "source_backed_claims_present", "actual": len(source_backed_claims)})
    for claim in claims:
        if claim.get("submissionDisposition") not in ALLOWED_PENDING_DISPOSITIONS:
            failures.append({"check": "claim_disposition", "claim": claim.get("id"), "actual": claim.get("submissionDisposition")})
        if not claim.get("interpretationBoundary"):
            failures.append({"check": "claim_boundary", "claim": claim.get("id")})
        if claim.get("submissionDisposition") == "pending-export" and "TBD after approved export" not in claim.get("expectedText", ""):
            failures.append({"check": "pending_claim_expected_text", "claim": claim.get("id")})
        if claim.get("claimRole") == "source-backed-candidate-result" and "TBD after approved export" in claim.get("expectedText", ""):
            failures.append({"check": "source_backed_claim_text_resolved", "claim": claim.get("id")})

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "status": manifest.get("capabilityStatus"),
        "selectedCandidateId": selected_id,
        "queryRowCount": len(query_rows),
        "claimCount": len(claims),
        "pendingExportClaimCount": len(pending_claims),
        "sourceBackedClaimCount": len(source_backed_claims),
        "requireExport": require_export,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    parser.add_argument("--require-export", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.project), args.require_export)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
