#!/usr/bin/env python3
"""Validate the P8 end-to-end topic-to-manuscript demo report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path: Path) -> dict:
    failures: list[dict] = []
    report = load_json(path)
    if report.get("schemaVersion") != "topic-to-manuscript-demo-report-v1":
        failures.append({"check": "schemaVersion", "actual": report.get("schemaVersion")})
    if report.get("status") != "demo-ready-not-submission-ready":
        failures.append({"check": "status", "actual": report.get("status")})
    stages = [item.get("stage") for item in report.get("workflowChain", [])]
    for required in ["P8-1 topic plan", "P8-2 project scaffolds", "P8-3 manuscript blueprints", "P8-4 writing adapters"]:
        if required not in stages:
            failures.append({"check": "workflowStage", "stage": required})
    projects = report.get("projects", [])
    data_sources = {item.get("dataSource") for item in projects}
    for required in ["charls", "gbd", "external_omics"]:
        if required not in data_sources:
            failures.append({"check": "projectDataSource", "dataSource": required})
    for check in report.get("checks", []):
        if not check.get("ok"):
            failures.append({"check": "artifactExists", "artifact": check.get("check"), "path": check.get("path")})
    for project in projects:
        if project.get("dataSource") == "external_omics":
            if "P10" not in project.get("nextRequired", ""):
                failures.append({"check": "externalOmicsP10Boundary", "project": project.get("projectDir")})
            continue
        if project.get("readiness") != "not-ready-for-results-or-submission":
            failures.append({"check": "projectReadiness", "project": project.get("projectDir"), "actual": project.get("readiness")})
        if not project.get("blockedUntil"):
            failures.append({"check": "blockedUntil", "project": project.get("projectDir")})
    boundary = report.get("boundary", "")
    for phrase in ["does not prove data access", "source-backed results", "submission readiness"]:
        if phrase not in boundary:
            failures.append({"check": "boundaryPhrase", "phrase": phrase})
    markdown = path.with_suffix(".md")
    if not markdown.exists():
        failures.append({"check": "markdownReportExists", "path": rel(markdown)})
    return {
        "ok": not failures,
        "report": rel(path),
        "projectCount": len(projects),
        "dataSources": sorted(data_sources),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", nargs="?", default="examples/topic-plans/depression-cognition-cvd-bioinformatics/end_to_end_demo_report.json")
    args = parser.parse_args()
    path = Path(args.report)
    if not path.is_absolute():
        path = ROOT / path
    result = validate(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
