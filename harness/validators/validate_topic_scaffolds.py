#!/usr/bin/env python3
"""Validate scaffolds instantiated from a topic plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_CHECKPOINTS = [
    "stage-S0-intake.md",
    "stage-S1-research-question.md",
    "stage-S2-method-plan.md",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_no_template_residue(path: Path, failures: list[dict]) -> None:
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        if "<project-slug>" in text:
            failures.append({"check": "templatePlaceholderRemoved", "file": rel(file_path)})
        if "examples/examples/" in text:
            failures.append({"check": "duplicateExamplesPath", "file": rel(file_path)})


def check_manifest_paths(project_manifest: Path, project_data: dict, failures: list[dict]) -> None:
    path_keys = [
        "fileManifest",
        "waveMap",
        "variableMap",
        "designGate",
        "codebookExtract",
        "codebookImportSample",
        "variableMappingDecisions",
        "queryManifest",
        "analysisManifest",
    ]
    for key in path_keys:
        value = project_data.get(key)
        if value and not (ROOT / value).exists():
            failures.append({"check": "projectManifestPathExists", "manifest": rel(project_manifest), "key": key, "path": value})


def validate(manifest_path: Path) -> dict:
    failures: list[dict] = []
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != "topic-plan-instantiation-v1":
        failures.append({"check": "schemaVersion", "actual": manifest.get("schemaVersion")})
    if manifest.get("status") != "scaffold-only-not-analysis":
        failures.append({"check": "status", "actual": manifest.get("status")})
    source_plan = ROOT / manifest.get("sourceTopicPlan", "")
    if not source_plan.exists():
        failures.append({"check": "sourceTopicPlanExists", "path": manifest.get("sourceTopicPlan")})

    projects = manifest.get("createdProjects", [])
    if not projects:
        failures.append({"check": "createdProjects"})
    data_sources = {item.get("dataSource") for item in projects}
    if "external_omics" in data_sources:
        omics_projects = [item for item in projects if item.get("dataSource") == "external_omics"]
        for item in omics_projects:
            project_dir = ROOT / item.get("projectDir", "")
            boundary = project_dir / "external_omics_required.md"
            if not boundary.exists():
                failures.append({"check": "externalOmicsBoundaryExists", "project": item.get("projectDir")})
            elif "does not yet implement" not in boundary.read_text(encoding="utf-8"):
                failures.append({"check": "externalOmicsBoundaryLanguage", "project": item.get("projectDir")})

    for item in projects:
        dataset = item.get("dataSource")
        project_dir = ROOT / item.get("projectDir", "")
        project_manifest = ROOT / item.get("projectManifest", "")
        if not project_dir.exists():
            failures.append({"check": "projectDirExists", "project": item.get("projectDir")})
            continue
        if not project_manifest.exists():
            failures.append({"check": "projectManifestExists", "project": item.get("projectDir")})
            continue
        check_no_template_residue(project_dir, failures)
        project_data = load_json(project_manifest)
        check_manifest_paths(project_manifest, project_data, failures)
        if dataset != "external_omics" and project_data.get("capabilityStatus") != "scaffold-only":
            failures.append({"check": "capabilityStatus", "project": item.get("projectDir"), "actual": project_data.get("capabilityStatus")})
        if dataset == "external_omics":
            if project_data.get("supportedByCurrentHarness") is not False:
                failures.append({"check": "externalOmicsUnsupportedFlag", "project": item.get("projectDir")})
            continue
        workflow = project_dir / "workflow-run.json"
        if not workflow.exists():
            failures.append({"check": "workflowExists", "project": item.get("projectDir")})
        for checkpoint in REQUIRED_CHECKPOINTS:
            path = project_dir / "checkpoints" / checkpoint
            if not path.exists():
                failures.append({"check": "checkpointExists", "project": item.get("projectDir"), "checkpoint": checkpoint})
        if dataset == "charls":
            for required in ["charls_design_gate.json", "variable_map.csv", "charls_file_manifest.csv", "charls_wave_map.csv"]:
                if not (project_dir / required).exists():
                    failures.append({"check": "charlsRequiredFile", "project": item.get("projectDir"), "file": required})
        elif dataset == "gbd":
            for required in ["gbd_query_manifest.csv", "gbd_analysis_manifest.json"]:
                if not (project_dir / required).exists():
                    failures.append({"check": "gbdRequiredFile", "project": item.get("projectDir"), "file": required})
        elif dataset == "nhanes":
            if not (project_dir / "nhanes_variable_targets.csv").exists():
                failures.append({"check": "nhanesVariableTargets", "project": item.get("projectDir")})

    return {
        "ok": not failures,
        "manifest": rel(manifest_path),
        "projectCount": len(projects),
        "dataSources": sorted(data_sources),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default="examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/instantiation_manifest.json")
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    result = validate(manifest_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
