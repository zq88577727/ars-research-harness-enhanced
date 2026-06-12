#!/usr/bin/env python3
"""Validate CHARLS variable-mapping decisions and create a draft variable map.

The default mode is conservative: it validates the human decision file and
writes a review draft CSV, leaving the authoritative `variable_map.csv`
unchanged. Use `--update-variable-map` only after manual review.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_DECISIONS = {"pending", "map_source", "derive", "defer", "reject_candidate"}
PLACEHOLDER_VALUES = {"", "TBD", "TBD_after_codebook_review", "pending", "pending_weight_decision"}
REQUIRED_TARGETS = {
    "primary_exposure",
    "primary_outcome",
    "attrition_status",
    "sample_weight",
    "participant_id",
    "wave",
    "baseline_wave",
    "followup_wave",
    "age",
    "sex",
}
REVIEWED_DECISIONS = {"map_source", "derive", "defer", "reject_candidate"}
APPLIED_DECISIONS = {"map_source", "derive"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def project_path(value: str, project_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.exists() or value.startswith(("data/", "examples/", "harness/", "data_sources/")):
        return root_relative
    return project_dir / path


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def is_placeholder(value: str | None) -> bool:
    return (value or "").strip() in PLACEHOLDER_VALUES


def load_context(project: Path, decisions_arg: str | None) -> dict:
    project_dir = project.resolve()
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing project manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataSource") != "charls":
        raise ValueError("project manifest must declare dataSource=charls")
    variable_map = project_path(manifest.get("variableMap", "variable_map.csv"), project_dir)
    codebook_extract = project_path(manifest.get("codebookExtract", "charls_codebook_extract.csv"), project_dir)
    decisions_path = project_path(
        decisions_arg or manifest.get("variableMappingDecisions", "charls_variable_mapping_decisions.json"),
        project_dir,
    )
    return {
        "projectDir": project_dir,
        "manifest": manifest,
        "variableMap": variable_map,
        "codebookExtract": codebook_extract,
        "decisionsPath": decisions_path,
    }


def usable_codebook_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    usable = {}
    for row in rows:
        source_variable = row.get("source_variable", "")
        if is_placeholder(source_variable):
            continue
        key = (source_variable, row.get("source_wave", ""), row.get("file_label", ""))
        usable[key] = row
    return usable


def validate_decisions(variable_rows: list[dict[str, str]], codebook_rows: list[dict[str, str]], decisions_data: dict, require_reviewed: bool) -> dict:
    failures: list[dict] = []
    warnings: list[dict] = []
    variable_names = {row.get("canonical_name") for row in variable_rows}
    codebook_by_key = usable_codebook_rows(codebook_rows)
    decisions = decisions_data.get("decisions", [])
    seen: set[str] = set()
    reviewed_count = 0
    applied_count = 0
    pending_count = 0

    if decisions_data.get("schemaVersion") != "charls-variable-mapping-decisions-v1":
        failures.append({"check": "schema_version", "schemaVersion": decisions_data.get("schemaVersion")})

    for item in decisions:
        canonical = item.get("canonicalName", "")
        decision = item.get("decision", "")
        seen.add(canonical)
        if canonical not in variable_names:
            failures.append({"check": "canonical_variable_exists", "canonicalName": canonical})
        if decision not in ALLOWED_DECISIONS:
            failures.append({"check": "decision_allowed", "canonicalName": canonical, "decision": decision})
            continue
        if decision == "pending":
            pending_count += 1
            if not item.get("rationale"):
                failures.append({"check": "pending_rationale", "canonicalName": canonical})
            continue

        reviewed_count += 1
        if not item.get("reviewer") or not item.get("reviewedAt") or not item.get("rationale"):
            failures.append({"check": "review_metadata_required", "canonicalName": canonical, "decision": decision})
        if decision in APPLIED_DECISIONS:
            applied_count += 1
            if item.get("semanticStatusAfter") not in {"mapped", "derived"}:
                failures.append({"check": "semantic_status_after", "canonicalName": canonical, "semanticStatusAfter": item.get("semanticStatusAfter")})
            if not item.get("codingDecision") or not item.get("missingnessDecision") or not item.get("interpretationBoundary"):
                failures.append({"check": "analysis_decisions_required", "canonicalName": canonical})

        if decision == "map_source":
            key = (item.get("selectedSourceVariable", ""), item.get("sourceWave", ""), item.get("sourceFile", ""))
            if key not in codebook_by_key:
                failures.append(
                    {
                        "check": "selected_source_variable_in_codebook_extract",
                        "canonicalName": canonical,
                        "selectedSourceVariable": item.get("selectedSourceVariable"),
                        "sourceWave": item.get("sourceWave"),
                        "sourceFile": item.get("sourceFile"),
                    }
                )
        elif decision == "derive":
            if not item.get("selectedSourceVariable") and not item.get("derivationRule"):
                failures.append({"check": "derive_source_or_rule", "canonicalName": canonical})
        elif decision in {"defer", "reject_candidate"}:
            if not item.get("rationale"):
                failures.append({"check": "defer_or_reject_rationale", "canonicalName": canonical, "decision": decision})

    missing_targets = sorted(REQUIRED_TARGETS - seen)
    if missing_targets:
        failures.append({"check": "required_targets_have_decisions", "missing": missing_targets})
    if require_reviewed:
        unreviewed = sorted(
            item.get("canonicalName")
            for item in decisions
            if item.get("canonicalName") in REQUIRED_TARGETS and item.get("decision") == "pending"
        )
        if unreviewed:
            failures.append({"check": "required_targets_reviewed", "pending": unreviewed})
    if pending_count:
        warnings.append({"check": "pending_decisions", "count": pending_count})
    if not codebook_by_key:
        warnings.append({"check": "no_usable_codebook_rows", "message": "Only pending/derive/defer decisions can be validated until real codebook rows are added."})

    return {
        "ok": not failures,
        "decisionCounts": {
            "pending": pending_count,
            "reviewed": reviewed_count,
            "applied": applied_count,
        },
        "failures": failures,
        "warnings": warnings,
    }


def apply_to_rows(variable_rows: list[dict[str, str]], decisions_data: dict) -> tuple[list[dict[str, str]], list[dict]]:
    decisions_by_name = {item.get("canonicalName"): item for item in decisions_data.get("decisions", [])}
    updated_rows = []
    applied = []
    for row in variable_rows:
        updated = dict(row)
        decision = decisions_by_name.get(row.get("canonical_name"))
        if decision and decision.get("decision") in APPLIED_DECISIONS:
            updated["source_wave"] = decision.get("sourceWave") or updated.get("source_wave", "")
            updated["source_file"] = decision.get("sourceFile") or updated.get("source_file", "")
            updated["source_variable"] = decision.get("selectedSourceVariable") or updated.get("source_variable", "")
            updated["semantic_status"] = decision.get("semanticStatusAfter") or updated.get("semantic_status", "")
            updated["coding_decision"] = decision.get("codingDecision") or updated.get("coding_decision", "")
            updated["missingness_decision"] = decision.get("missingnessDecision") or updated.get("missingness_decision", "")
            updated["interpretation_boundary"] = decision.get("interpretationBoundary") or updated.get("interpretation_boundary", "")
            if decision.get("decision") == "derive" and decision.get("derivationRule"):
                updated["notes"] = (updated.get("notes", "") + f" Derived rule: {decision['derivationRule']}").strip()
            applied.append({"canonicalName": row.get("canonical_name"), "decision": decision.get("decision")})
        updated_rows.append(updated)
    return updated_rows, applied


def apply_decisions(project: Path, decisions_arg: str | None, output_arg: str | None, dry_run: bool, update_variable_map: bool, require_reviewed: bool) -> dict:
    context = load_context(project, decisions_arg)
    variable_rows = read_csv(context["variableMap"])
    codebook_rows = read_csv(context["codebookExtract"]) if context["codebookExtract"].exists() else []
    decisions_data = json.loads(context["decisionsPath"].read_text(encoding="utf-8"))
    validation = validate_decisions(variable_rows, codebook_rows, decisions_data, require_reviewed)
    updated_rows, applied = apply_to_rows(variable_rows, decisions_data)

    output_path = project_path(
        output_arg or decisions_data.get("outputDraftVariableMap", "variable_map.review_draft.csv"),
        context["projectDir"],
    )
    target_path = context["variableMap"] if update_variable_map else output_path
    if update_variable_map and not require_reviewed:
        validation["failures"].append({"check": "update_requires_reviewed_gate", "message": "Use --require-reviewed when updating the authoritative variable map."})
        validation["ok"] = False

    if validation["ok"] and not dry_run:
        fieldnames = list(variable_rows[0].keys()) if variable_rows else []
        write_csv(target_path, updated_rows, fieldnames)

    return {
        "ok": validation["ok"],
        "project": str(project),
        "variableMap": rel(context["variableMap"]),
        "codebookExtract": rel(context["codebookExtract"]),
        "decisionsFile": rel(context["decisionsPath"]),
        "outputFile": rel(target_path),
        "dryRun": dry_run,
        "updateVariableMap": update_variable_map,
        "requireReviewed": require_reviewed,
        "appliedDecisionCount": len(applied),
        "appliedDecisions": applied,
        "decisionCounts": validation["decisionCounts"],
        "warnings": validation["warnings"],
        "failures": validation["failures"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--decisions", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update-variable-map", action="store_true")
    parser.add_argument("--require-reviewed", action="store_true")
    args = parser.parse_args()
    try:
        result = apply_decisions(
            project=Path(args.project),
            decisions_arg=args.decisions,
            output_arg=args.output,
            dry_run=args.dry_run,
            update_variable_map=args.update_variable_map,
            require_reviewed=args.require_reviewed,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
