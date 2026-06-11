#!/usr/bin/env python3
"""Validate CHARLS/GBD project scaffolds."""

from __future__ import annotations

import argparse
import csv
import json
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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
    if data_source == "charls":
        variable_map = path / "variable_map.csv"
        if not variable_map.exists():
            failures.append({"check": "charls_variable_map_exists"})
        else:
            rows = read_csv(variable_map)
            required = [row for row in rows if row.get("required", "").lower() == "true"]
            if not required:
                failures.append({"check": "charls_required_variables_present"})
    elif data_source == "gbd":
        query_manifest = path / "gbd_query_manifest.csv"
        if not query_manifest.exists():
            failures.append({"check": "gbd_query_manifest_exists"})
        else:
            rows = read_csv(query_manifest)
            required_cols = set(manifest.get("requiredQueryDimensions", [])) | {"export_file"}
            missing_cols = sorted(required_cols - set(rows[0].keys())) if rows else sorted(required_cols)
            if missing_cols:
                failures.append({"check": "gbd_query_manifest_columns", "missing": missing_cols})
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
