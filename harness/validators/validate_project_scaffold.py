#!/usr/bin/env python3
"""Validate CHARLS/GBD project scaffolds."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


REQUIRED_STAGE_KEYS = [
    "S0_intake",
    "S1_research_question",
    "S2_method_analysis_plan",
    "S3_evidence_data_execution",
    "S4_interpretation",
    "S5_outline",
    "S6_draft",
    "S7_integrity_citation_check",
    "S8_review_revision",
    "S9_finalize_closeout",
]

CHARLS_REQUIRED_VARIABLES = {
    "participant_id",
    "wave",
    "baseline_wave",
    "followup_wave",
    "age",
    "sex",
    "primary_exposure",
    "attrition_status",
    "primary_outcome",
}

CHARLS_FILE_MANIFEST_COLUMNS = {
    "wave",
    "year",
    "file_label",
    "expected_local_path",
    "module",
    "required_for_minimal_longitudinal",
    "access_status",
    "checksum_sha256",
    "notes",
}

CHARLS_CODEBOOK_EXTRACT_COLUMNS = {
    "source_wave",
    "file_label",
    "module",
    "source_variable",
    "variable_label",
    "construct_keywords",
    "measurement_domain",
    "measurement_type",
    "wave_role",
    "eligible_roles",
    "notes",
}

CHARLS_DESIGN_GATE_REQUIRED_FIELDS = {
    "researchQuestion",
    "estimand",
    "temporalOrdering",
    "attritionPlan",
    "weightDecision",
    "claimBoundaries",
}

CHARLS_VARIABLE_MAPPING_DECISION_VALUES = {"pending", "map_source", "derive", "defer", "reject_candidate"}

RAW_FILE_EXTENSIONS = {".dta", ".sav", ".sas7bdat", ".xpt", ".csv", ".zip", ".rar", ".7z"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def git_tracked_files_under(path: str) -> list[str]:
    try:
        completed = subprocess.run(["git", "ls-files", path], check=True, capture_output=True, text=True)
    except Exception:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def validate_charls_project(path: Path, manifest: dict, failures: list[dict]) -> None:
    if manifest.get("studyDesign") != "longitudinal cohort scaffold":
        failures.append({"check": "charls_study_design", "actual": manifest.get("studyDesign")})
    if "must not be committed" not in manifest.get("localRawDataPolicy", ""):
        failures.append({"check": "charls_local_raw_policy"})
    if not manifest.get("interpretationBoundary"):
        failures.append({"check": "charls_interpretation_boundary"})

    variable_map = path / "variable_map.csv"
    if not variable_map.exists():
        failures.append({"check": "charls_variable_map_exists"})
    else:
        rows = read_csv(variable_map)
        required_names = {row.get("canonical_name") for row in rows if row.get("required", "").lower() == "true"}
        missing = sorted(CHARLS_REQUIRED_VARIABLES - required_names)
        if missing:
            failures.append({"check": "charls_required_variables_present", "missing": missing})

    design_gate_value = manifest.get("designGate")
    if not design_gate_value:
        failures.append({"check": "charls_design_gate_declared"})
    else:
        design_gate = path / "charls_design_gate.json"
        if not design_gate.exists():
            failures.append({"check": "charls_design_gate_exists"})
        else:
            gate = json.loads(design_gate.read_text(encoding="utf-8"))
            missing_gate_fields = sorted(CHARLS_DESIGN_GATE_REQUIRED_FIELDS - set(gate))
            if missing_gate_fields:
                failures.append({"check": "charls_design_gate_fields", "missing": missing_gate_fields})

    codebook_extract_value = manifest.get("codebookExtract")
    if not codebook_extract_value:
        failures.append({"check": "charls_codebook_extract_declared"})
    else:
        codebook_extract = path / "charls_codebook_extract.csv"
        if not codebook_extract.exists():
            failures.append({"check": "charls_codebook_extract_exists"})
        else:
            rows = read_csv(codebook_extract)
            if not rows:
                failures.append({"check": "charls_codebook_extract_rows"})
            else:
                missing_cols = sorted(CHARLS_CODEBOOK_EXTRACT_COLUMNS - set(rows[0].keys()))
                if missing_cols:
                    failures.append({"check": "charls_codebook_extract_columns", "missing": missing_cols})

    decisions_value = manifest.get("variableMappingDecisions")
    if not decisions_value:
        failures.append({"check": "charls_variable_mapping_decisions_declared"})
    else:
        decisions_path = path / "charls_variable_mapping_decisions.json"
        if not decisions_path.exists():
            failures.append({"check": "charls_variable_mapping_decisions_exists"})
        else:
            decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            if decisions.get("schemaVersion") != "charls-variable-mapping-decisions-v1":
                failures.append({"check": "charls_variable_mapping_decisions_schema"})
            decision_items = decisions.get("decisions", [])
            if not decision_items:
                failures.append({"check": "charls_variable_mapping_decisions_rows"})
            invalid_decisions = [
                item.get("canonicalName")
                for item in decision_items
                if item.get("decision") not in CHARLS_VARIABLE_MAPPING_DECISION_VALUES
            ]
            if invalid_decisions:
                failures.append({"check": "charls_variable_mapping_decision_values", "variables": invalid_decisions})

    codebook_import_sample_value = manifest.get("codebookImportSample")
    if not codebook_import_sample_value:
        failures.append({"check": "charls_codebook_import_sample_declared"})
    elif not (path / "charls_codebook_import_sample.csv").exists():
        failures.append({"check": "charls_codebook_import_sample_exists"})

    file_manifest_value = manifest.get("fileManifest")
    if not file_manifest_value:
        failures.append({"check": "charls_file_manifest_declared"})
        return
    file_manifest = path / "charls_file_manifest.csv"
    if not file_manifest.exists():
        failures.append({"check": "charls_file_manifest_exists"})
        return

    rows = read_csv(file_manifest)
    if not rows:
        failures.append({"check": "charls_file_manifest_rows"})
        return
    missing_cols = sorted(CHARLS_FILE_MANIFEST_COLUMNS - set(rows[0].keys()))
    if missing_cols:
        failures.append({"check": "charls_file_manifest_columns", "missing": missing_cols})

    raw_dir = manifest.get("rawDataDirectory", "")
    required_rows = [row for row in rows if row.get("required_for_minimal_longitudinal", "").lower() == "true"]
    if len(required_rows) < 2:
        failures.append({"check": "charls_minimum_longitudinal_files"})
    for row in rows:
        expected = row.get("expected_local_path", "")
        if raw_dir and expected and not expected.startswith(raw_dir.rstrip("/") + "/"):
            failures.append({"check": "charls_expected_path_under_raw_dir", "path": expected})
        if row.get("access_status") not in {"not_downloaded", "downloaded_local", "not_required", "pending"}:
            failures.append({"check": "charls_access_status", "status": row.get("access_status")})
        if manifest.get("accessStatus", {}).get("rawFilesDownloaded") and row.get("required_for_minimal_longitudinal", "").lower() == "true":
            local_path = Path(expected)
            if "<" in expected or ">" in expected or not local_path.exists():
                failures.append({"check": "charls_required_local_file_exists", "path": expected})

    tracked = [
        file
        for file in git_tracked_files_under(raw_dir)
        if Path(file).suffix.lower() in RAW_FILE_EXTENSIONS
    ]
    if tracked:
        failures.append({"check": "charls_raw_files_not_tracked", "tracked": tracked})


def validate_project(path: Path) -> dict:
    failures = []
    manifest_path = path / "project_manifest.json"
    workflow_path = path / "workflow-run.json"
    if not manifest_path.exists():
        failures.append({"check": "project_manifest_exists", "path": str(manifest_path)})
        manifest = {}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not workflow_path.exists():
        failures.append({"check": "workflow_exists", "path": str(workflow_path)})
        workflow = {}
    else:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))

    missing_stages = [key for key in REQUIRED_STAGE_KEYS if key not in workflow.get("stages", {})]
    if missing_stages:
        failures.append({"check": "workflow_stages", "missing": missing_stages})

    data_source = manifest.get("dataSource")
    data_source_manifest = manifest.get("dataSourceManifest")
    if not data_source_manifest:
        failures.append({"check": "data_source_manifest_declared"})
    else:
        source_manifest_path = Path(data_source_manifest)
        if not source_manifest_path.exists():
            failures.append({"check": "data_source_manifest_exists", "path": data_source_manifest})
        else:
            source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
            if source_manifest.get("id") != data_source:
                failures.append(
                    {
                        "check": "data_source_manifest_matches",
                        "dataSource": data_source,
                        "manifestId": source_manifest.get("id"),
                    }
                )

    if data_source == "charls":
        validate_charls_project(path, manifest, failures)
    elif data_source == "gbd":
        query_manifest = path / "gbd_query_manifest.csv"
        analysis_manifest = path / "gbd_analysis_manifest.json"
        if not query_manifest.exists():
            failures.append({"check": "gbd_query_manifest_exists"})
        else:
            rows = read_csv(query_manifest)
            required_cols = set(manifest.get("requiredQueryDimensions", [])) | {"export_file"}
            missing_cols = sorted(required_cols - set(rows[0].keys())) if rows else sorted(required_cols)
            if missing_cols:
                failures.append({"check": "gbd_query_manifest_columns", "missing": missing_cols})
        if not manifest.get("analysisManifest"):
            failures.append({"check": "gbd_analysis_manifest_declared"})
        if not analysis_manifest.exists():
            failures.append({"check": "gbd_analysis_manifest_exists"})
        else:
            analysis = json.loads(analysis_manifest.read_text(encoding="utf-8"))
            if not analysis.get("analyses"):
                failures.append({"check": "gbd_analysis_manifest_analyses"})
    else:
        failures.append({"check": "supported_data_source", "dataSource": data_source})

    return {"ok": not failures, "project": str(path), "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    args = parser.parse_args()
    result = validate_project(Path(args.project))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
