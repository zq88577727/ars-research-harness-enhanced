#!/usr/bin/env python3
"""Dry-run validation for local CHARLS restricted-data placement.

The validator checks metadata, paths, variable maps, git tracking status, and
optional checksums. It does not open or parse restricted CHARLS data files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ACCESS_STATUSES = {"not_downloaded", "downloaded_local", "not_required", "pending"}
RAW_FILE_EXTENSIONS = {".dta", ".sav", ".sas7bdat", ".xpt", ".csv", ".zip", ".rar", ".7z"}
REQUIRED_FILE_COLUMNS = {
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
REQUIRED_VARIABLE_COLUMNS = {
    "canonical_name",
    "source_wave",
    "source_file",
    "source_variable",
    "role",
    "required",
    "notes",
}
REQUIRED_VARIABLES = {
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def project_path(value: str, project_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.exists() or value.startswith(("data/", "examples/", "harness/", "data_sources/")):
        return root_relative
    return project_dir / path


def git_tracked_files_under(path: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", path],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(project: Path, require_local_data: bool) -> dict:
    project_dir = project.resolve()
    failures: list[dict] = []
    warnings: list[dict] = []
    checks: list[dict] = []

    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {
            "ok": False,
            "project": str(project),
            "status": "invalid-project",
            "checks": [],
            "warnings": [],
            "failures": [{"check": "project_manifest_exists", "path": str(manifest_path)}],
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataSource") != "charls":
        failures.append({"check": "data_source_is_charls", "dataSource": manifest.get("dataSource")})

    raw_dir_value = manifest.get("rawDataDirectory", "")
    raw_dir = project_path(raw_dir_value, project_dir) if raw_dir_value else None
    if not raw_dir_value:
        failures.append({"check": "raw_data_directory_declared"})
    elif raw_dir and not str(raw_dir.relative_to(ROOT) if raw_dir.is_relative_to(ROOT) else raw_dir).startswith(raw_dir_value):
        warnings.append({"check": "raw_data_directory_resolved", "path": str(raw_dir)})

    if "must not be committed" not in manifest.get("localRawDataPolicy", ""):
        failures.append({"check": "local_raw_data_policy"})

    file_manifest_value = manifest.get("fileManifest")
    variable_map_value = manifest.get("variableMap")
    file_manifest = project_path(file_manifest_value, project_dir) if file_manifest_value else None
    variable_map = project_path(variable_map_value, project_dir) if variable_map_value else None
    if not file_manifest or not file_manifest.exists():
        failures.append({"check": "file_manifest_exists", "path": file_manifest_value})
        file_rows: list[dict[str, str]] = []
    else:
        file_rows = read_csv(file_manifest)
        if not file_rows:
            failures.append({"check": "file_manifest_has_rows"})
        else:
            missing = sorted(REQUIRED_FILE_COLUMNS - set(file_rows[0]))
            if missing:
                failures.append({"check": "file_manifest_columns", "missing": missing})

    if not variable_map or not variable_map.exists():
        failures.append({"check": "variable_map_exists", "path": variable_map_value})
        variable_rows: list[dict[str, str]] = []
    else:
        variable_rows = read_csv(variable_map)
        if not variable_rows:
            failures.append({"check": "variable_map_has_rows"})
        else:
            missing = sorted(REQUIRED_VARIABLE_COLUMNS - set(variable_rows[0]))
            if missing:
                failures.append({"check": "variable_map_columns", "missing": missing})
            required_names = {row.get("canonical_name") for row in variable_rows if row.get("required", "").lower() == "true"}
            missing_required = sorted(REQUIRED_VARIABLES - required_names)
            if missing_required:
                failures.append({"check": "required_variable_contract", "missing": missing_required})

    required_rows = [
        row
        for row in file_rows
        if row.get("required_for_minimal_longitudinal", "").lower() == "true"
    ]
    local_ready_count = 0
    placeholder_count = 0
    missing_required_count = 0
    checksum_checked_count = 0
    for row in file_rows:
        expected = row.get("expected_local_path", "")
        access_status = row.get("access_status", "")
        is_required = row.get("required_for_minimal_longitudinal", "").lower() == "true"
        if access_status not in ALLOWED_ACCESS_STATUSES:
            failures.append({"check": "access_status_allowed", "row": row.get("file_label"), "status": access_status})
        if not expected:
            failures.append({"check": "expected_local_path_present", "row": row.get("file_label")})
            continue
        if raw_dir_value and not expected.startswith(raw_dir_value.rstrip("/") + "/"):
            failures.append({"check": "expected_path_under_raw_dir", "path": expected})
        has_placeholder = "<" in expected or ">" in expected
        if has_placeholder:
            placeholder_count += 1
            if access_status == "downloaded_local":
                failures.append({"check": "downloaded_path_not_placeholder", "path": expected})
        local_path = project_path(expected, project_dir)
        exists = local_path.exists()
        if access_status == "downloaded_local":
            if not exists:
                failures.append({"check": "downloaded_local_file_exists", "path": expected})
            elif not local_path.is_file():
                failures.append({"check": "downloaded_local_is_file", "path": expected})
            else:
                local_ready_count += 1
                checksum = row.get("checksum_sha256", "").strip()
                if checksum:
                    checksum_checked_count += 1
                    actual = sha256_file(local_path)
                    if actual.lower() != checksum.lower():
                        failures.append({"check": "checksum_sha256_matches", "path": expected})
                else:
                    warnings.append({"check": "checksum_recommended", "path": expected})
        elif is_required:
            missing_required_count += 1
            if require_local_data:
                failures.append({"check": "required_local_file_ready", "path": expected, "status": access_status})

    if len(required_rows) < 2:
        failures.append({"check": "minimum_two_required_waves", "requiredRows": len(required_rows)})

    if raw_dir_value:
        tracked_raw = [
            file
            for file in git_tracked_files_under(raw_dir_value)
            if Path(file).suffix.lower() in RAW_FILE_EXTENSIONS
        ]
        if tracked_raw:
            failures.append({"check": "restricted_raw_files_not_tracked", "tracked": tracked_raw})
        checks.append({"check": "restricted_raw_files_not_tracked", "trackedCount": len(tracked_raw), "ok": not tracked_raw})

    checks.extend(
        [
            {"check": "fileManifestRows", "count": len(file_rows), "ok": bool(file_rows)},
            {"check": "requiredRows", "count": len(required_rows), "ok": len(required_rows) >= 2},
            {"check": "localReadyRows", "count": local_ready_count, "ok": local_ready_count > 0},
            {"check": "placeholderRows", "count": placeholder_count, "ok": placeholder_count == 0},
            {"check": "missingRequiredRows", "count": missing_required_count, "ok": missing_required_count == 0},
            {"check": "checksumCheckedRows", "count": checksum_checked_count, "ok": checksum_checked_count > 0},
        ]
    )

    if failures:
        status = "blocked"
    elif local_ready_count == 0 and not require_local_data:
        status = "awaiting-local-data"
        warnings.append(
            {
                "check": "local_data_not_present",
                "message": "No CHARLS files marked downloaded_local; metadata-only dry run passed.",
            }
        )
    else:
        status = "local-data-ready"

    return {
        "ok": not failures,
        "project": str(project),
        "status": status,
        "requireLocalData": require_local_data,
        "checks": checks,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--require-local-data", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.project), args.require_local_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
