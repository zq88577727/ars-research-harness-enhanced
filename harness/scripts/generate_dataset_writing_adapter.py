#!/usr/bin/env python3
"""Generate dataset-specific manuscript writing adapters from blueprints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


ADAPTERS = {
    "nhanes": {
        "adapterType": "nhanes-cross-sectional-survey-writing-adapter",
        "methodsSections": [
            "Study design and data source",
            "Participants and analytic sample",
            "Exposure, outcome, and covariate definitions",
            "NHANES survey weights and design variables",
            "Statistical analysis",
            "Sensitivity analyses",
            "Ethics and public-use data statement",
        ],
        "resultsSections": [
            "Analytic sample and weighted characteristics",
            "Weighted prevalence or association estimates",
            "Sensitivity and subgroup findings",
        ],
        "requiredLanguage": [
            "weighted cross-sectional estimate",
            "survey design",
            "association",
        ],
        "prohibitedLanguage": [
            "caused",
            "diagnosed",
            "incidence",
            "longitudinal change",
        ],
    },
    "charls": {
        "adapterType": "charls-longitudinal-cohort-writing-adapter",
        "methodsSections": [
            "Study design and CHARLS waves",
            "Participants, eligibility, and wave linkage",
            "Exposure, outcome, and covariate definitions",
            "Temporal ordering and follow-up",
            "Attrition, missingness, and weight decision",
            "Longitudinal statistical analysis",
            "Sensitivity analyses",
            "Ethics and restricted-data use statement",
        ],
        "resultsSections": [
            "Cohort construction and follow-up",
            "Baseline characteristics",
            "Longitudinal association estimates",
            "Attrition and sensitivity analyses",
        ],
        "requiredLanguage": [
            "longitudinal association",
            "wave linkage",
            "attrition",
        ],
        "prohibitedLanguage": [
            "caused",
            "prevented",
            "mechanism",
            "clinical diagnosis",
        ],
    },
    "gbd": {
        "adapterType": "gbd-disease-burden-writing-adapter",
        "methodsSections": [
            "GBD release, data source, and citation policy",
            "Query dimensions and source-export provenance",
            "Measures, metrics, age groups, sex strata, and locations",
            "Age-standardization and all-age count rules",
            "Uncertainty interval interpretation",
            "Derived summaries and trend calculations",
            "Reuse boundary and reproducibility",
        ],
        "resultsSections": [
            "Query profile and included estimates",
            "All-age counts with uncertainty intervals",
            "Age-standardized rates with uncertainty intervals",
            "Temporal changes and location comparisons",
        ],
        "requiredLanguage": [
            "GBD release",
            "uncertainty interval",
            "age-standardized",
            "all-age count",
        ],
        "prohibitedLanguage": [
            "patient-level",
            "risk factor effect",
            "mechanism",
            "intervention effect",
        ],
    },
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_methods(blueprint: dict, adapter: dict) -> str:
    lines = [
        "# Methods Writing Shell",
        "",
        f"Status: `adapter-shell-not-final-manuscript`",
        f"Dataset: `{blueprint['dataSource']}`",
        f"Adapter: `{adapter['adapterType']}`",
        "",
    ]
    for section in adapter["methodsSections"]:
        lines.extend([f"## {section}", "", "TODO: Complete after design gate, source provenance, and analysis outputs are available.", ""])
    lines.extend([
        "## Required Language",
        "",
    ])
    lines.extend(f"- {item}" for item in adapter["requiredLanguage"])
    lines.extend(["", "## Prohibited Language", ""])
    lines.extend(f"- {item}" for item in adapter["prohibitedLanguage"])
    lines.append("")
    return "\n".join(lines)


def render_results(blueprint: dict, adapter: dict) -> str:
    lines = [
        "# Results Writing Shell",
        "",
        f"Status: `adapter-shell-not-final-manuscript`",
        f"Dataset: `{blueprint['dataSource']}`",
        "",
        "Results text is blocked until S3 data execution, provenance, and S7 claim checks exist.",
        "",
    ]
    for section in adapter["resultsSections"]:
        lines.extend([f"## {section}", "", "TODO: Insert source-backed outputs only after validation.", ""])
    return "\n".join(lines)


def generate_for_blueprint(blueprint_path: Path) -> dict:
    blueprint = load_json(blueprint_path)
    dataset = blueprint.get("dataSource")
    if dataset not in ADAPTERS:
        raise ValueError(f"unsupported dataset for writing adapter: {dataset}")
    adapter = ADAPTERS[dataset]
    project_dir = blueprint_path.parent
    adapter_path = project_dir / "writing_adapter.json"
    methods_path = project_dir / "methods_shell.md"
    results_path = project_dir / "results_shell.md"
    payload = {
        "schemaVersion": "dataset-writing-adapter-v1",
        "status": "adapter-shell-not-final-manuscript",
        "project": rel(project_dir),
        "sourceBlueprint": rel(blueprint_path),
        "dataSource": dataset,
        "adapterType": adapter["adapterType"],
        "methodsShell": rel(methods_path),
        "resultsShell": rel(results_path),
        "methodsSections": adapter["methodsSections"],
        "resultsSections": adapter["resultsSections"],
        "requiredLanguage": adapter["requiredLanguage"],
        "prohibitedLanguage": adapter["prohibitedLanguage"],
        "boundary": blueprint.get("boundary", ""),
        "blockedUntil": [
            "S3 data execution exists",
            "source/export provenance exists",
            "claim registry is source-backed",
            "S7 integrity and citation checks pass",
        ],
        "nextStage": "P8-5 end-to-end user demo",
    }
    write_json(adapter_path, payload)
    methods_path.write_text(render_methods(blueprint, adapter), encoding="utf-8")
    results_path.write_text(render_results(blueprint, adapter), encoding="utf-8")
    return {
        "project": rel(project_dir),
        "adapter": rel(adapter_path),
        "methodsShell": rel(methods_path),
        "resultsShell": rel(results_path),
    }


def blueprints_from_manifest(path: Path) -> list[Path]:
    manifest = load_json(path)
    paths = []
    for item in manifest.get("createdProjects", []):
        if item.get("dataSource") == "external_omics":
            continue
        project_dir = ROOT / item["projectDir"]
        paths.append(project_dir / "manuscript_blueprint.json")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dataset-specific writing adapters from manuscript blueprints.")
    parser.add_argument("--blueprint", help="Path to a manuscript_blueprint.json file.")
    parser.add_argument("--manifest", help="Topic instantiation manifest; generates adapters for supported blueprints.")
    args = parser.parse_args()
    if bool(args.blueprint) == bool(args.manifest):
        print(json.dumps({"ok": False, "error": "Provide exactly one of --blueprint or --manifest."}, indent=2))
        return 1
    if args.blueprint:
        path = Path(args.blueprint)
        if not path.is_absolute():
            path = ROOT / path
        blueprints = [path]
    else:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = ROOT / manifest_path
        blueprints = blueprints_from_manifest(manifest_path)
    outputs = []
    try:
        for blueprint_path in blueprints:
            outputs.append(generate_for_blueprint(blueprint_path))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "generated": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
