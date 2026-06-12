#!/usr/bin/env python3
"""Validate the CHARLS S1/S2 research-design gate.

This validator links the CHARLS variable map and wave map to the research
question, estimand, temporal ordering, attrition plan, weight decision, and
claim-language boundaries. It does not read restricted CHARLS data.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TOP_LEVEL = {
    "stage",
    "status",
    "linkedInputs",
    "researchQuestion",
    "estimand",
    "temporalOrdering",
    "attritionPlan",
    "weightDecision",
    "claimBoundaries",
    "manuscriptLanguage",
}
ALLOWED_STATUSES = {"s1-s2-pending", "ready-for-analysis"}
ALLOWED_ESTIMAND_TYPES = {
    "associational-longitudinal",
    "descriptive-longitudinal",
    "cross-sectional",
}
PLACEHOLDER_VALUES = {
    "",
    "TBD",
    "TBD_after_codebook_review",
    "TBD_after_S1_confirmation",
    "pending",
    "pending_weight_decision",
}
CAUSAL_BOUNDARY_TERMS = {"causal effect", "impact", "leads to", "prevents", "causes"}


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


def is_placeholder(value: str | None) -> bool:
    return (value or "").strip() in PLACEHOLDER_VALUES or (value or "").startswith("To be refined")


def find_row(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str] | None:
    for row in rows:
        if row.get(field) == value:
            return row
    return None


def add_failure(failures: list[dict], check: str, **kwargs: object) -> None:
    failures.append({"check": check, **kwargs})


def validate(project: Path, require_ready: bool) -> dict:
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
        add_failure(failures, "data_source_is_charls", dataSource=manifest.get("dataSource"))

    gate_value = manifest.get("designGate")
    gate_path = project_path(gate_value, project_dir) if gate_value else project_dir / "charls_design_gate.json"
    if not gate_path.exists():
        add_failure(failures, "design_gate_exists", path=gate_value or str(gate_path))
        gate = {}
    else:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))

    missing_top = sorted(REQUIRED_TOP_LEVEL - set(gate))
    if missing_top:
        add_failure(failures, "design_gate_top_level_fields", missing=missing_top)

    if gate.get("stage") != "S1_S2":
        add_failure(failures, "design_gate_stage", stage=gate.get("stage"))
    if gate.get("status") not in ALLOWED_STATUSES:
        add_failure(failures, "design_gate_status", status=gate.get("status"))

    variable_map_value = gate.get("linkedInputs", {}).get("variableMap") or manifest.get("variableMap")
    wave_map_value = gate.get("linkedInputs", {}).get("waveMap") or manifest.get("waveMap")
    variable_map = project_path(variable_map_value, project_dir) if variable_map_value else None
    wave_map = project_path(wave_map_value, project_dir) if wave_map_value else None

    if not variable_map or not variable_map.exists():
        add_failure(failures, "variable_map_exists", path=variable_map_value)
        variable_rows: list[dict[str, str]] = []
    else:
        variable_rows = read_csv(variable_map)

    if not wave_map or not wave_map.exists():
        add_failure(failures, "wave_map_exists", path=wave_map_value)
        wave_rows: list[dict[str, str]] = []
    else:
        wave_rows = read_csv(wave_map)

    variable_names = {row.get("canonical_name") for row in variable_rows}
    wave_ids = {row.get("wave") for row in wave_rows}

    rq = gate.get("researchQuestion", {})
    estimand = gate.get("estimand", {})
    temporal = gate.get("temporalOrdering", {})
    attrition = gate.get("attritionPlan", {})
    weight = gate.get("weightDecision", {})

    if rq.get("exposure") not in variable_names:
        add_failure(failures, "research_question_exposure_variable_known", variable=rq.get("exposure"))
    if rq.get("outcome") not in variable_names:
        add_failure(failures, "research_question_outcome_variable_known", variable=rq.get("outcome"))
    if estimand.get("type") not in ALLOWED_ESTIMAND_TYPES:
        add_failure(failures, "estimand_type_allowed", estimandType=estimand.get("type"))
    if estimand.get("timeOrigin") not in variable_names:
        add_failure(failures, "estimand_time_origin_variable_known", variable=estimand.get("timeOrigin"))
    if estimand.get("followUp") not in variable_names:
        add_failure(failures, "estimand_followup_variable_known", variable=estimand.get("followUp"))

    baseline_wave = temporal.get("baselineWave")
    followup_wave = temporal.get("followupWave")
    if baseline_wave not in wave_ids:
        add_failure(failures, "temporal_baseline_wave_known", wave=baseline_wave)
    if followup_wave not in wave_ids:
        add_failure(failures, "temporal_followup_wave_known", wave=followup_wave)
    baseline_row = find_row(wave_rows, "wave", baseline_wave)
    followup_row = find_row(wave_rows, "wave", followup_wave)
    if baseline_row and baseline_row.get("wave_role") != "baseline":
        add_failure(failures, "temporal_baseline_wave_role", wave=baseline_wave, waveRole=baseline_row.get("wave_role"))
    if followup_row and followup_row.get("wave_role") != "followup":
        add_failure(failures, "temporal_followup_wave_role", wave=followup_wave, waveRole=followup_row.get("wave_role"))
    if baseline_wave == followup_wave and baseline_wave:
        add_failure(failures, "temporal_baseline_precedes_followup", baselineWave=baseline_wave, followupWave=followup_wave)

    exposure_name = temporal.get("exposureVariable")
    outcome_name = temporal.get("outcomeVariable")
    exposure_row = find_row(variable_rows, "canonical_name", exposure_name)
    outcome_row = find_row(variable_rows, "canonical_name", outcome_name)
    if not exposure_row:
        add_failure(failures, "temporal_exposure_variable_known", variable=exposure_name)
    elif exposure_row.get("role") != "exposure":
        add_failure(failures, "temporal_exposure_role", variable=exposure_name, role=exposure_row.get("role"))
    elif exposure_row.get("wave_role") != "baseline":
        add_failure(failures, "temporal_exposure_wave_role", variable=exposure_name, waveRole=exposure_row.get("wave_role"))
    if not outcome_row:
        add_failure(failures, "temporal_outcome_variable_known", variable=outcome_name)
    elif outcome_row.get("role") != "outcome":
        add_failure(failures, "temporal_outcome_role", variable=outcome_name, role=outcome_row.get("role"))
    elif outcome_row.get("wave_role") != "followup":
        add_failure(failures, "temporal_outcome_wave_role", variable=outcome_name, waveRole=outcome_row.get("wave_role"))

    attrition_row = find_row(variable_rows, "canonical_name", attrition.get("variable", ""))
    if attrition.get("required") is not True:
        add_failure(failures, "attrition_required_true")
    if not attrition_row:
        add_failure(failures, "attrition_variable_known", variable=attrition.get("variable"))
    elif attrition_row.get("role") != "missingness":
        add_failure(failures, "attrition_variable_role", variable=attrition.get("variable"), role=attrition_row.get("role"))

    weight_row = find_row(variable_rows, "canonical_name", weight.get("variable", ""))
    if weight.get("requiredBeforeAnalysis") is not True:
        add_failure(failures, "weight_required_before_analysis_true")
    if not weight_row:
        add_failure(failures, "weight_variable_known", variable=weight.get("variable"))
    elif weight_row.get("role") != "weight":
        add_failure(failures, "weight_variable_role", variable=weight.get("variable"), role=weight_row.get("role"))

    claim_boundaries = gate.get("claimBoundaries", [])
    boundary_ids = {item.get("id") for item in claim_boundaries if isinstance(item, dict)}
    if "no-causal-language" not in boundary_ids:
        add_failure(failures, "claim_boundary_no_causal_language_present")
    prohibited = {item.lower() for item in estimand.get("prohibitedLanguage", [])}
    if not CAUSAL_BOUNDARY_TERMS.intersection(prohibited):
        add_failure(failures, "estimand_prohibited_causal_terms_present")
    allowed = {item.lower() for item in estimand.get("allowedLanguage", [])}
    if "association" not in allowed and "longitudinal association" not in allowed:
        add_failure(failures, "estimand_allows_association_language")

    boundary_statement = gate.get("manuscriptLanguage", {}).get("boundaryStatement", "")
    if "does not authorize causal" not in boundary_statement:
        add_failure(failures, "manuscript_language_causal_boundary_statement")

    if is_placeholder(rq.get("text")):
        warnings.append({"check": "research_question_pending", "message": "S1 research question still contains placeholder text."})
    if is_placeholder(estimand.get("contrast")):
        warnings.append({"check": "estimand_contrast_pending", "message": "S2 estimand contrast is not yet analysis-ready."})
    if is_placeholder(weight.get("status")):
        warnings.append({"check": "weight_decision_pending", "message": "Weight decision remains pending; target-population claims are blocked."})

    readiness_blockers = []
    if gate.get("status") != "ready-for-analysis":
        readiness_blockers.append("design gate status is not ready-for-analysis")
    if is_placeholder(rq.get("text")):
        readiness_blockers.append("research question is unresolved")
    if is_placeholder(estimand.get("contrast")):
        readiness_blockers.append("estimand contrast is unresolved")
    if is_placeholder(weight.get("status")):
        readiness_blockers.append("weight decision is unresolved")
    for row in [exposure_row, outcome_row, attrition_row]:
        if row and (row.get("semantic_status") not in {"mapped", "derived"} or is_placeholder(row.get("source_variable"))):
            readiness_blockers.append(f"{row.get('canonical_name')} is not mapped to a real CHARLS source variable")
    if require_ready and readiness_blockers:
        add_failure(failures, "ready_for_analysis_requirements", blockers=readiness_blockers)

    checks.extend(
        [
            {"check": "designGateDeclared", "ok": bool(gate_value or gate_path.exists())},
            {"check": "variableMapRows", "count": len(variable_rows), "ok": bool(variable_rows)},
            {"check": "waveMapRows", "count": len(wave_rows), "ok": bool(wave_rows)},
            {"check": "temporalOrderingLinked", "ok": bool(exposure_row and outcome_row and baseline_row and followup_row)},
            {"check": "attritionPlanLinked", "ok": bool(attrition_row)},
            {"check": "weightDecisionLinked", "ok": bool(weight_row)},
            {"check": "claimLanguageBoundaryPresent", "ok": "no-causal-language" in boundary_ids},
            {"check": "readinessBlockers", "count": len(readiness_blockers), "ok": not readiness_blockers},
        ]
    )

    if failures:
        status = "blocked"
    elif readiness_blockers:
        status = "s1-s2-design-pending"
    else:
        status = "ready-for-analysis"

    return {
        "ok": not failures,
        "project": str(project),
        "status": status,
        "requireReady": require_ready,
        "checks": checks,
        "warnings": warnings,
        "readinessBlockers": readiness_blockers,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.project), args.require_ready)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
