#!/usr/bin/env python3
"""Validate dataset-specific writing adapters."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GLOB = "examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/*/writing_adapter.json"
DATASET_REQUIREMENTS = {
    "nhanes": ["weighted cross-sectional estimate", "survey design", "association"],
    "charls": ["longitudinal association", "wave linkage", "attrition"],
    "gbd": ["GBD release", "uncertainty interval", "age-standardized", "all-age count"],
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_adapter(path: Path) -> list[dict]:
    failures: list[dict] = []
    adapter = load_json(path)
    if adapter.get("schemaVersion") != "dataset-writing-adapter-v1":
        failures.append({"check": "schemaVersion", "file": rel(path), "actual": adapter.get("schemaVersion")})
    if adapter.get("status") != "adapter-shell-not-final-manuscript":
        failures.append({"check": "status", "file": rel(path), "actual": adapter.get("status")})
    dataset = adapter.get("dataSource")
    if dataset not in DATASET_REQUIREMENTS:
        failures.append({"check": "supportedDataSource", "file": rel(path), "actual": dataset})
        return failures
    source_blueprint = ROOT / adapter.get("sourceBlueprint", "")
    if not source_blueprint.exists():
        failures.append({"check": "sourceBlueprintExists", "file": rel(path), "path": adapter.get("sourceBlueprint")})
    for key in ["methodsShell", "resultsShell"]:
        shell = ROOT / adapter.get(key, "")
        if not shell.exists():
            failures.append({"check": f"{key}Exists", "file": rel(path), "path": adapter.get(key)})
            continue
        text = shell.read_text(encoding="utf-8")
        if "adapter-shell-not-final-manuscript" not in text:
            failures.append({"check": "shellStatus", "file": rel(shell)})
        if "TODO:" not in text:
            failures.append({"check": "shellTodoBoundary", "file": rel(shell)})
    required = adapter.get("requiredLanguage", [])
    for term in DATASET_REQUIREMENTS[dataset]:
        if term not in required:
            failures.append({"check": "requiredLanguage", "file": rel(path), "term": term})
    if not adapter.get("prohibitedLanguage"):
        failures.append({"check": "prohibitedLanguage", "file": rel(path)})
    if len(adapter.get("methodsSections", [])) < 5:
        failures.append({"check": "methodsSections", "file": rel(path)})
    if len(adapter.get("resultsSections", [])) < 3:
        failures.append({"check": "resultsSections", "file": rel(path)})
    serialized = json.dumps(adapter, ensure_ascii=False).lower()
    if "final-manuscript" in serialized and adapter.get("status") != "adapter-shell-not-final-manuscript":
        failures.append({"check": "finalManuscriptLeak", "file": rel(path)})
    if "source-backed" in serialized and "claim registry is source-backed" not in serialized:
        failures.append({"check": "sourceBackedLeak", "file": rel(path)})
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("adapters", nargs="*")
    args = parser.parse_args()
    if args.adapters:
        paths = [Path(item) if Path(item).is_absolute() else ROOT / item for item in args.adapters]
    else:
        paths = sorted(ROOT.glob(DEFAULT_GLOB))
    failures: list[dict] = []
    for path in paths:
        failures.extend(validate_adapter(path))
    result = {
        "ok": not failures,
        "adapterCount": len(paths),
        "adapters": [rel(path) for path in paths],
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
