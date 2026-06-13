#!/usr/bin/env python3
"""Generate manuscript blueprints from instantiated topic scaffolds."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


DATASET_BLUEPRINTS = {
    "nhanes": {
        "manuscriptType": "cross-sectional complex survey manuscript",
        "reportingGuideline": "STROBE observational checklist plus NHANES survey-method documentation",
        "methods": [
            "Data source and study population",
            "Survey design, weights, strata, and primary sampling units",
            "Exposure and outcome definitions",
            "Covariates and missing-data handling",
            "Weighted descriptive analysis",
            "Weighted regression or prevalence-ratio analysis",
            "Sensitivity analyses",
            "Ethics, public-use data, and reproducibility",
        ],
        "tables": [
            {"id": "table1", "label": "Weighted baseline characteristics by exposure or outcome group"},
            {"id": "table2", "label": "Weighted prevalence or association estimates"},
            {"id": "table3", "label": "Sensitivity and subgroup analyses"},
            {"id": "figure1", "label": "Analytic-sample flow diagram"},
        ],
        "claimBoundary": "Use weighted cross-sectional association language only; do not infer causality or clinical diagnosis from one measurement.",
    },
    "charls": {
        "manuscriptType": "longitudinal aging cohort manuscript",
        "reportingGuideline": "STROBE/RECORD depending on linkage and reporting frame",
        "methods": [
            "Data source, waves, and access status",
            "Study population and eligibility criteria",
            "Wave linkage and temporal ordering",
            "Exposure, outcome, and covariate definitions",
            "Attrition, missingness, and follow-up assessment",
            "Weight and target-population decision",
            "Longitudinal statistical model",
            "Sensitivity analyses",
            "Ethics, data-use boundary, and reproducibility",
        ],
        "tables": [
            {"id": "table1", "label": "Baseline characteristics by exposure group"},
            {"id": "table2", "label": "Wave linkage, attrition, and missingness summary"},
            {"id": "table3", "label": "Longitudinal association estimates"},
            {"id": "figure1", "label": "Cohort construction and follow-up flow"},
            {"id": "figure2", "label": "Outcome trajectory or predicted-risk plot"},
        ],
        "claimBoundary": "Use temporal association or trajectory language only unless a defensible causal design is added.",
    },
    "gbd": {
        "manuscriptType": "GBD descriptive disease-burden manuscript",
        "reportingGuideline": "GATHER-style source transparency plus journal requirements",
        "methods": [
            "GBD release, source, and reuse boundary",
            "Query profile: measure, metric, cause, location, age, sex, and year",
            "Count, rate, percent, and age-standardization decisions",
            "Uncertainty interval interpretation",
            "Derived summaries and trend calculations",
            "Citation and IHME/GHDx reuse policy",
            "Sensitivity or stratified comparisons where defined",
            "Reproducibility and source-export provenance",
        ],
        "tables": [
            {"id": "table1", "label": "GBD query dimensions and export provenance"},
            {"id": "table2", "label": "Burden estimates with uncertainty intervals"},
            {"id": "table3", "label": "Temporal changes by location, sex, or age group"},
            {"id": "figure1", "label": "Burden trend plot with uncertainty intervals"},
        ],
        "claimBoundary": "Use descriptive burden and trend language only; do not infer patient-level risk factors, mechanisms, or intervention effects.",
    },
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slug_from_project(project_dir: Path) -> str:
    return project_dir.name[:80]


def title_candidates(project: dict, profile: dict) -> list[str]:
    base = project.get("title", "Manuscript project").replace(" [CHARLS scaffold]", "").replace(" [GBD scaffold]", "").replace(" [NHANES scaffold]", "")
    return [
        f"{base}: a {profile['manuscriptType']}",
        f"{base}: protocol-ready analysis blueprint",
    ]


def initial_claims(project: dict, project_dir: Path, profile: dict) -> list[dict]:
    dataset = project.get("dataSource")
    slug = slug_from_project(project_dir)
    return [
        {
            "id": f"{slug}-scope-boundary",
            "tier": "core",
            "type": "scope-boundary",
            "claimRole": "methods-boundary",
            "submissionDisposition": "draft-only-not-source-backed",
            "expectedText": project.get("researchQuestion", "Research question to be refined."),
            "sourceFile": rel(project_dir / "project_manifest.json"),
            "sourceFields": ["researchQuestion", "dataSource", "topicPlanDesign"],
            "evidenceStatus": "scaffold-only",
            "interpretationBoundary": profile["claimBoundary"],
        },
        {
            "id": f"{slug}-methods-readiness",
            "tier": "core",
            "type": "methods-readiness",
            "claimRole": "gate-blocker",
            "submissionDisposition": "draft-only-not-source-backed",
            "expectedText": f"{dataset.upper()} analysis claims are blocked until S3 outputs and S7 integrity checks exist.",
            "sourceFile": rel(project_dir / "workflow-run.json"),
            "sourceFields": ["stages", "risks"],
            "evidenceStatus": "not-source-backed",
            "interpretationBoundary": "Planning claim only; must not appear as a numeric result.",
        },
    ]


def build_blueprint(project_manifest: Path) -> dict:
    project = load_json(project_manifest)
    dataset = project.get("dataSource")
    if dataset not in DATASET_BLUEPRINTS:
        raise ValueError(f"unsupported dataset for manuscript blueprint: {dataset}")
    project_dir = project_manifest.parent
    profile = DATASET_BLUEPRINTS[dataset]
    claim_registry_path = project_dir / "claim_registry.draft.json"
    blueprint_path = project_dir / "manuscript_blueprint.json"
    markdown_path = project_dir / "manuscript_blueprint.md"
    claim_registry = {
        "schemaVersion": "draft-claim-registry-v1",
        "status": "draft-not-source-backed",
        "project": rel(project_dir),
        "sourceProjectManifest": rel(project_manifest),
        "claims": initial_claims(project, project_dir, profile),
    }
    write_json(claim_registry_path, claim_registry)
    blueprint = {
        "schemaVersion": "manuscript-blueprint-v1",
        "status": "blueprint-draft-not-manuscript",
        "project": rel(project_dir),
        "sourceProjectManifest": rel(project_manifest),
        "dataSource": dataset,
        "titleCandidates": title_candidates(project, profile),
        "researchQuestion": project.get("researchQuestion", ""),
        "manuscriptType": profile["manuscriptType"],
        "reportingGuidelinePath": profile["reportingGuideline"],
        "methodsFramework": profile["methods"],
        "tableFigureShell": profile["tables"],
        "claimRegistryDraft": rel(claim_registry_path),
        "readinessGate": {
            "minimumNextStage": "S3 data execution and S7 integrity check before numeric manuscript claims",
            "blockedUntil": [
                "dataset-specific design gate is reviewed",
                "source data/export provenance exists",
                "claim registry entries are source-backed",
                "methods/results consistency gate passes",
            ],
        },
        "boundary": profile["claimBoundary"],
        "nextStage": "P8-4 dataset-specific writing adapters",
    }
    write_json(blueprint_path, blueprint)
    markdown_path.write_text(render_markdown(blueprint), encoding="utf-8")
    return {
        "project": rel(project_dir),
        "blueprint": rel(blueprint_path),
        "markdown": rel(markdown_path),
        "claimRegistryDraft": rel(claim_registry_path),
    }


def render_markdown(blueprint: dict) -> str:
    lines = [
        "# Manuscript Blueprint",
        "",
        f"Status: `{blueprint['status']}`",
        f"Data source: `{blueprint['dataSource']}`",
        f"Manuscript type: {blueprint['manuscriptType']}",
        "",
        "## Candidate Titles",
        "",
    ]
    lines.extend(f"- {title}" for title in blueprint["titleCandidates"])
    lines.extend([
        "",
        "## Research Question",
        "",
        blueprint["researchQuestion"],
        "",
        "## Methods Framework",
        "",
    ])
    lines.extend(f"- {item}" for item in blueprint["methodsFramework"])
    lines.extend([
        "",
        "## Table And Figure Shell",
        "",
    ])
    lines.extend(f"- `{item['id']}`: {item['label']}" for item in blueprint["tableFigureShell"])
    lines.extend([
        "",
        "## Claim Registry Draft",
        "",
        f"`{blueprint['claimRegistryDraft']}`",
        "",
        "## Boundary",
        "",
        blueprint["boundary"],
        "",
        "## Readiness Gate",
        "",
    ])
    lines.extend(f"- {item}" for item in blueprint["readinessGate"]["blockedUntil"])
    lines.append("")
    return "\n".join(lines)


def project_manifests_from_instantiation(path: Path) -> list[Path]:
    manifest = load_json(path)
    project_manifests = []
    for item in manifest.get("createdProjects", []):
        if item.get("dataSource") == "external_omics":
            continue
        project_manifests.append(ROOT / item["projectManifest"])
    return project_manifests


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manuscript blueprint artifacts from topic scaffolds.")
    parser.add_argument("--project", help="Project directory or project_manifest.json path.")
    parser.add_argument("--manifest", help="Topic instantiation manifest; generates blueprints for supported projects.")
    args = parser.parse_args()
    if bool(args.project) == bool(args.manifest):
        print(json.dumps({"ok": False, "error": "Provide exactly one of --project or --manifest."}, indent=2))
        return 1

    if args.project:
        path = Path(args.project)
        if not path.is_absolute():
            path = ROOT / path
        project_manifests = [path if path.name == "project_manifest.json" else path / "project_manifest.json"]
    else:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = ROOT / manifest_path
        project_manifests = project_manifests_from_instantiation(manifest_path)

    outputs = []
    try:
        for project_manifest in project_manifests:
            outputs.append(build_blueprint(project_manifest))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "generated": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
