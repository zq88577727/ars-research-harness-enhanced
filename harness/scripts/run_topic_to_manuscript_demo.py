#!/usr/bin/env python3
"""Build an end-to-end demo report for the topic-to-manuscript P8 workflow."""

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


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_exists(path: Path, label: str, checks: list[dict]) -> bool:
    ok = path.exists()
    checks.append({"check": label, "path": rel(path), "ok": ok})
    return ok


def project_summary(item: dict, checks: list[dict]) -> dict:
    dataset = item.get("dataSource")
    project_dir = ROOT / item.get("projectDir", "")
    summary = {
        "dataSource": dataset,
        "projectDir": rel(project_dir),
        "status": "external-omics-boundary" if dataset == "external_omics" else "supported-demo-project",
    }
    if dataset == "external_omics":
        boundary = project_dir / "external_omics_required.md"
        check_exists(boundary, f"{dataset}.boundary", checks)
        summary["boundaryArtifact"] = rel(boundary)
        summary["nextRequired"] = "P10 external omics module before mechanism claims."
        return summary

    required = {
        "projectManifest": project_dir / "project_manifest.json",
        "workflowRun": project_dir / "workflow-run.json",
        "manuscriptBlueprint": project_dir / "manuscript_blueprint.json",
        "claimRegistryDraft": project_dir / "claim_registry.draft.json",
        "writingAdapter": project_dir / "writing_adapter.json",
        "methodsShell": project_dir / "methods_shell.md",
        "resultsShell": project_dir / "results_shell.md",
    }
    for label, path in required.items():
        check_exists(path, f"{dataset}.{label}", checks)
    blueprint = load_json(required["manuscriptBlueprint"]) if required["manuscriptBlueprint"].exists() else {}
    adapter = load_json(required["writingAdapter"]) if required["writingAdapter"].exists() else {}
    summary.update({
        "manuscriptType": blueprint.get("manuscriptType"),
        "blueprint": rel(required["manuscriptBlueprint"]),
        "writingAdapter": rel(required["writingAdapter"]),
        "methodsShell": rel(required["methodsShell"]),
        "resultsShell": rel(required["resultsShell"]),
        "readiness": "not-ready-for-results-or-submission",
        "blockedUntil": adapter.get("blockedUntil", []),
    })
    return summary


def render_markdown(report: dict) -> str:
    lines = [
        "# P8 End-to-End Topic-To-Manuscript Demo",
        "",
        f"Status: `{report['status']}`",
        f"Topic: {report['topic']}",
        "",
        "## Workflow Chain",
        "",
    ]
    for step in report["workflowChain"]:
        lines.append(f"- `{step['stage']}`: {step['artifact']}")
    lines.extend(["", "## Project Outputs", ""])
    for project in report["projects"]:
        lines.extend([
            f"### {project['dataSource']}",
            "",
            f"Project: `{project['projectDir']}`",
            f"Status: `{project['status']}`",
            "",
        ])
        if project["dataSource"] == "external_omics":
            lines.extend([
                f"Boundary artifact: `{project['boundaryArtifact']}`",
                f"Next required: {project['nextRequired']}",
                "",
            ])
        else:
            lines.extend([
                f"Manuscript type: {project.get('manuscriptType')}",
                f"Blueprint: `{project['blueprint']}`",
                f"Writing adapter: `{project['writingAdapter']}`",
                f"Methods shell: `{project['methodsShell']}`",
                f"Results shell: `{project['resultsShell']}`",
                f"Readiness: `{project['readiness']}`",
                "",
                "Blocked until:",
                "",
            ])
            lines.extend(f"- {item}" for item in project.get("blockedUntil", []))
            lines.append("")
    lines.extend([
        "## Overall Boundary",
        "",
        report["boundary"],
        "",
    ])
    return "\n".join(lines)


def build_report(topic_plan_path: Path) -> dict:
    checks: list[dict] = []
    plan = load_json(topic_plan_path)
    topic_dir = topic_plan_path.parent
    instantiation_manifest = topic_dir / "scaffolds" / "instantiation_manifest.json"
    check_exists(topic_plan_path, "topicPlan", checks)
    check_exists(topic_dir / "topic_plan.md", "topicPlanMarkdown", checks)
    check_exists(topic_dir / "workflow-seed.json", "workflowSeed", checks)
    check_exists(instantiation_manifest, "instantiationManifest", checks)
    instantiation = load_json(instantiation_manifest)
    projects = [project_summary(item, checks) for item in instantiation.get("createdProjects", [])]
    report = {
        "schemaVersion": "topic-to-manuscript-demo-report-v1",
        "status": "demo-ready-not-submission-ready",
        "topic": plan.get("topic", ""),
        "sourceTopicPlan": rel(topic_plan_path),
        "workflowChain": [
            {"stage": "P8-1 topic plan", "artifact": rel(topic_plan_path)},
            {"stage": "P8-2 project scaffolds", "artifact": rel(instantiation_manifest)},
            {"stage": "P8-3 manuscript blueprints", "artifact": "project-level manuscript_blueprint.json files"},
            {"stage": "P8-4 writing adapters", "artifact": "project-level writing_adapter.json and shell files"},
        ],
        "projects": projects,
        "checks": checks,
        "boundary": "This demo proves topic-to-project startup and writing scaffolding. It does not prove data access, analysis execution, source-backed results, omics support, or submission readiness.",
    }
    report["ok"] = all(item["ok"] for item in checks)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a P8 end-to-end demo report.")
    parser.add_argument("topic_plan", nargs="?", default="examples/topic-plans/depression-cognition-cvd-bioinformatics/topic_plan.json")
    args = parser.parse_args()
    topic_plan_path = Path(args.topic_plan)
    if not topic_plan_path.is_absolute():
        topic_plan_path = ROOT / topic_plan_path
    try:
        report = build_report(topic_plan_path)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    topic_dir = topic_plan_path.parent
    json_path = topic_dir / "end_to_end_demo_report.json"
    md_path = topic_dir / "end_to_end_demo_report.md"
    write_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "report": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
