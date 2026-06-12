#!/usr/bin/env python3
"""Prepare a CHARLS S1/S2 design-gate instantiation worksheet.

The script reads scaffold metadata and an optional codebook extract CSV, then
creates a human-review worksheet. It never reads restricted CHARLS raw data and
does not mutate the variable map or design gate.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_CODEBOOK_COLUMNS = {
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
PLACEHOLDER_VALUES = {"", "TBD", "TBD_after_codebook_review", "pending", "pending_weight_decision"}


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
    stripped = (value or "").strip()
    return stripped in PLACEHOLDER_VALUES or stripped.startswith("To be refined")


def tokens(*values: str) -> set[str]:
    text = " ".join(value or "" for value in values).lower()
    return {token for token in re.split(r"[^a-z0-9_]+", text) if len(token) >= 3}


def split_values(value: str) -> set[str]:
    return {item.strip().lower() for item in re.split(r"[;,|]", value or "") if item.strip()}


def score_candidate(variable: dict[str, str], candidate: dict[str, str]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    role = variable.get("role", "").lower()
    source_wave = variable.get("source_wave", "").lower()
    source_file = variable.get("source_file", "").lower()
    domain = variable.get("measurement_domain", "").lower()
    measurement_type = variable.get("measurement_type", "").lower()
    wave_role = variable.get("wave_role", "").lower()

    eligible_roles = split_values(candidate.get("eligible_roles", ""))
    if role and role in eligible_roles:
        score += 4
        reasons.append("role")
    if domain and domain == candidate.get("measurement_domain", "").lower():
        score += 3
        reasons.append("domain")
    if measurement_type and measurement_type == candidate.get("measurement_type", "").lower():
        score += 2
        reasons.append("measurement_type")
    if wave_role and wave_role == candidate.get("wave_role", "").lower():
        score += 2
        reasons.append("wave_role")
    if source_wave in {"", "all"} or source_wave == candidate.get("source_wave", "").lower():
        score += 1
        reasons.append("wave")
    if source_file in {"", "derived", "not_applicable"} or source_file == candidate.get("file_label", "").lower():
        score += 1
        reasons.append("file_label")

    variable_terms = tokens(
        variable.get("canonical_name", ""),
        variable.get("construct", ""),
        variable.get("measurement_domain", ""),
        variable.get("notes", ""),
    )
    candidate_terms = tokens(
        candidate.get("source_variable", ""),
        candidate.get("variable_label", ""),
        candidate.get("construct_keywords", ""),
        candidate.get("notes", ""),
    )
    overlap = sorted(variable_terms & candidate_terms)
    if overlap:
        score += min(4, len(overlap))
        reasons.append("terms:" + ",".join(overlap[:4]))

    if is_placeholder(candidate.get("source_variable")):
        score -= 2
        reasons.append("placeholder_source_variable")
    return score, reasons


def candidate_rows(variable: dict[str, str], codebook_rows: list[dict[str, str]], limit: int) -> list[dict]:
    ranked = []
    for candidate in codebook_rows:
        if is_placeholder(candidate.get("source_variable")):
            continue
        score, reasons = score_candidate(variable, candidate)
        if score > 0:
            ranked.append({"score": score, "reasons": reasons, "candidate": candidate})
    ranked.sort(key=lambda item: (-item["score"], item["candidate"].get("source_variable", "")))
    return ranked[:limit]


def design_targets(variable_rows: list[dict[str, str]], gate: dict) -> list[dict[str, str]]:
    names = []
    for value in [
        gate.get("researchQuestion", {}).get("exposure"),
        gate.get("researchQuestion", {}).get("outcome"),
        gate.get("temporalOrdering", {}).get("exposureVariable"),
        gate.get("temporalOrdering", {}).get("outcomeVariable"),
        gate.get("attritionPlan", {}).get("variable"),
        gate.get("weightDecision", {}).get("variable"),
    ]:
        if value and value not in names:
            names.append(value)
    for row in variable_rows:
        if row.get("required", "").lower() == "true" and row.get("canonical_name") not in names:
            names.append(row.get("canonical_name"))
    rows_by_name = {row.get("canonical_name"): row for row in variable_rows}
    return [rows_by_name[name] for name in names if name in rows_by_name]


def render_markdown(result: dict) -> str:
    lines = [
        "# CHARLS S1/S2 Design Gate Instantiation Worksheet",
        "",
        f"Project: `{result['project']}`",
        f"Design gate: `{result['designGate']}`",
        f"Variable map: `{result['variableMap']}`",
        f"Wave map: `{result['waveMap']}`",
        f"Codebook extract: `{result['codebookExtract']}`",
        "",
        "Status: scaffold instantiation aid only. This worksheet does not approve analysis and does not replace human codebook review.",
        "",
        "## Summary",
        "",
        f"- Target variables reviewed: {result['targetVariableCount']}",
        f"- Codebook extract rows: {result['codebookRowCount']}",
        f"- Usable source-variable rows: {result['usableCodebookRowCount']}",
        f"- Candidate suggestions: {result['candidateSuggestionCount']}",
        f"- Variables still requiring human mapping: {result['needsHumanMappingCount']}",
        "",
        "## S1/S2 Decisions Still Required",
        "",
    ]
    for item in result["readinessBlockers"]:
        lines.append(f"- {item}")
    if not result["readinessBlockers"]:
        lines.append("- None detected by this worksheet generator.")
    lines.extend(
        [
            "",
            "## Variable Candidate Review",
            "",
            "| canonical variable | role | wave role | current source variable | candidate suggestions | required human action |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in result["targets"]:
        suggestions = []
        for candidate in item["candidates"]:
            row = candidate["candidate"]
            suggestions.append(
                f"`{row.get('source_variable')}` ({row.get('source_wave')}/{row.get('file_label')}, score {candidate['score']})"
            )
        if not suggestions:
            suggestions = ["No candidate from current codebook extract"]
        lines.append(
            "| {canonical} | {role} | {wave_role} | `{source_variable}` | {suggestions} | {action} |".format(
                canonical=item["canonicalName"],
                role=item["role"],
                wave_role=item["waveRole"],
                source_variable=item["currentSourceVariable"],
                suggestions="<br>".join(suggestions),
                action=item["requiredHumanAction"],
            )
        )
    lines.extend(
        [
            "",
            "## Human Review Contract",
            "",
            "Before changing `variable_map.csv` or setting `charls_design_gate.json` to `ready-for-analysis`, a human reviewer should:",
            "",
            "1. Confirm each selected source variable against the official CHARLS questionnaire or codebook.",
            "2. Record exact coding, missingness, and derivation decisions in `variable_map.csv`.",
            "3. Confirm exposure measurement precedes outcome ascertainment.",
            "4. Document attrition and weight decisions in `charls_design_gate.json`.",
            "5. Keep causal, diagnostic, and clinical-recommendation language blocked unless a separate justified design supports it.",
            "",
        ]
    )
    return "\n".join(lines)


def build(project: Path, codebook_arg: str | None, candidate_limit: int) -> dict:
    project_dir = project.resolve()
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing project manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataSource") != "charls":
        raise ValueError("project manifest must declare dataSource=charls")

    gate_path = project_path(manifest.get("designGate", "charls_design_gate.json"), project_dir)
    variable_map = project_path(manifest.get("variableMap", "variable_map.csv"), project_dir)
    wave_map = project_path(manifest.get("waveMap", "charls_wave_map.csv"), project_dir)
    codebook_path = project_path(codebook_arg, project_dir) if codebook_arg else project_dir / "charls_codebook_extract.csv"

    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    variable_rows = read_csv(variable_map)
    codebook_rows = read_csv(codebook_path) if codebook_path.exists() else []
    codebook_missing = []
    if codebook_rows:
        codebook_missing = sorted(REQUIRED_CODEBOOK_COLUMNS - set(codebook_rows[0]))
        if codebook_missing:
            codebook_rows = []
    usable_codebook_rows = [row for row in codebook_rows if not is_placeholder(row.get("source_variable"))]

    targets = []
    readiness_blockers = []
    for row in design_targets(variable_rows, gate):
        candidates = candidate_rows(row, usable_codebook_rows, candidate_limit)
        current_source = row.get("source_variable", "")
        needs_mapping = row.get("semantic_status") not in {"mapped", "derived"} or is_placeholder(current_source)
        if needs_mapping:
            readiness_blockers.append(f"{row.get('canonical_name')} requires human-confirmed source variable mapping")
        action = "confirm source variable and update semantic_status to mapped/derived" if needs_mapping else "verify existing mapping remains valid"
        targets.append(
            {
                "canonicalName": row.get("canonical_name"),
                "role": row.get("role"),
                "waveRole": row.get("wave_role"),
                "currentSourceVariable": current_source,
                "semanticStatus": row.get("semantic_status"),
                "requiredHumanAction": action,
                "candidates": candidates,
            }
        )

    if is_placeholder(gate.get("researchQuestion", {}).get("text")):
        readiness_blockers.append("research question remains placeholder text")
    if is_placeholder(gate.get("estimand", {}).get("contrast")):
        readiness_blockers.append("estimand contrast remains unresolved")
    if is_placeholder(gate.get("weightDecision", {}).get("status")):
        readiness_blockers.append("weight decision remains unresolved")
    if codebook_missing:
        readiness_blockers.append("codebook extract is missing required columns: " + ", ".join(codebook_missing))
    if not usable_codebook_rows:
        readiness_blockers.append("codebook extract has no usable source-variable rows; fill charls_codebook_extract.csv from official metadata")

    candidate_count = sum(len(item["candidates"]) for item in targets)
    result = {
        "ok": not codebook_missing,
        "project": str(project),
        "designGate": str(gate_path.relative_to(ROOT) if gate_path.is_relative_to(ROOT) else gate_path),
        "variableMap": str(variable_map.relative_to(ROOT) if variable_map.is_relative_to(ROOT) else variable_map),
        "waveMap": str(wave_map.relative_to(ROOT) if wave_map.is_relative_to(ROOT) else wave_map),
        "codebookExtract": str(codebook_path.relative_to(ROOT) if codebook_path.is_relative_to(ROOT) else codebook_path),
        "targetVariableCount": len(targets),
        "codebookRowCount": len(codebook_rows),
        "usableCodebookRowCount": len(usable_codebook_rows),
        "candidateSuggestionCount": candidate_count,
        "needsHumanMappingCount": sum(1 for item in targets if item["requiredHumanAction"].startswith("confirm")),
        "readinessBlockers": readiness_blockers,
        "targets": targets,
    }
    result["markdown"] = render_markdown(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--codebook-extract", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        result = build(Path(args.project), args.codebook_extract, args.candidate_limit)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    output_path = Path(args.output) if args.output else Path(args.project) / "charls_s1_s2_design_review.md"
    if args.dry_run:
        payload = {key: value for key, value in result.items() if key != "markdown"}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1

    output = project_path(str(output_path), ROOT)
    output.write_text(result["markdown"], encoding="utf-8")
    payload = {key: value for key, value in result.items() if key != "markdown"}
    payload["output"] = str(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
