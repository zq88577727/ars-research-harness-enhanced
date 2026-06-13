#!/usr/bin/env python3
"""Validate manuscript blueprints generated from topic scaffolds."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GLOB = "examples/topic-plans/depression-cognition-cvd-bioinformatics/scaffolds/*/manuscript_blueprint.json"
SUPPORTED_DATASETS = {"nhanes", "charls", "gbd"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_blueprint(path: Path) -> list[dict]:
    failures: list[dict] = []
    blueprint = load_json(path)
    project_dir = path.parent
    if blueprint.get("schemaVersion") != "manuscript-blueprint-v1":
        failures.append({"check": "schemaVersion", "file": rel(path), "actual": blueprint.get("schemaVersion")})
    if blueprint.get("status") != "blueprint-draft-not-manuscript":
        failures.append({"check": "status", "file": rel(path), "actual": blueprint.get("status")})
    dataset = blueprint.get("dataSource")
    if dataset not in SUPPORTED_DATASETS:
        failures.append({"check": "supportedDataSource", "file": rel(path), "actual": dataset})
    if not blueprint.get("titleCandidates"):
        failures.append({"check": "titleCandidates", "file": rel(path)})
    if not blueprint.get("researchQuestion"):
        failures.append({"check": "researchQuestion", "file": rel(path)})
    if len(blueprint.get("methodsFramework", [])) < 5:
        failures.append({"check": "methodsFramework", "file": rel(path)})
    if len(blueprint.get("tableFigureShell", [])) < 3:
        failures.append({"check": "tableFigureShell", "file": rel(path)})
    project_manifest = ROOT / blueprint.get("sourceProjectManifest", "")
    if not project_manifest.exists():
        failures.append({"check": "sourceProjectManifestExists", "file": rel(path), "path": blueprint.get("sourceProjectManifest")})
    claim_registry = ROOT / blueprint.get("claimRegistryDraft", "")
    if not claim_registry.exists():
        failures.append({"check": "claimRegistryDraftExists", "file": rel(path), "path": blueprint.get("claimRegistryDraft")})
    else:
        failures.extend(validate_claim_registry(claim_registry, dataset))
    markdown = project_dir / "manuscript_blueprint.md"
    if not markdown.exists():
        failures.append({"check": "markdownBlueprintExists", "file": rel(path)})
    else:
        text = markdown.read_text(encoding="utf-8")
        for required in ["Methods Framework", "Table And Figure Shell", "Readiness Gate", "Boundary"]:
            if required not in text:
                failures.append({"check": "markdownSection", "file": rel(markdown), "section": required})
    gate = blueprint.get("readinessGate", {})
    if "S3" not in gate.get("minimumNextStage", "") or "S7" not in gate.get("minimumNextStage", ""):
        failures.append({"check": "readinessGateS3S7", "file": rel(path)})
    if "submission-ready" in json.dumps(blueprint, ensure_ascii=False).lower():
        failures.append({"check": "noSubmissionReadyLanguage", "file": rel(path)})
    return failures


def validate_claim_registry(path: Path, dataset: str | None) -> list[dict]:
    failures: list[dict] = []
    registry = load_json(path)
    if registry.get("schemaVersion") != "draft-claim-registry-v1":
        failures.append({"check": "claimRegistrySchemaVersion", "file": rel(path), "actual": registry.get("schemaVersion")})
    if registry.get("status") != "draft-not-source-backed":
        failures.append({"check": "claimRegistryStatus", "file": rel(path), "actual": registry.get("status")})
    claims = registry.get("claims", [])
    if len(claims) < 2:
        failures.append({"check": "claimCount", "file": rel(path), "actual": len(claims)})
    for claim in claims:
        disposition = claim.get("submissionDisposition", "")
        if disposition != "draft-only-not-source-backed":
            failures.append({"check": "claimDisposition", "file": rel(path), "claim": claim.get("id"), "actual": disposition})
        if claim.get("evidenceStatus") not in {"scaffold-only", "not-source-backed"}:
            failures.append({"check": "claimEvidenceStatus", "file": rel(path), "claim": claim.get("id"), "actual": claim.get("evidenceStatus")})
        if not claim.get("interpretationBoundary"):
            failures.append({"check": "claimBoundary", "file": rel(path), "claim": claim.get("id")})
        if dataset == "gbd" and "mechanism" in claim.get("interpretationBoundary", "").lower() and "do not infer" not in claim.get("interpretationBoundary", "").lower():
            failures.append({"check": "gbdMechanismBoundary", "file": rel(path), "claim": claim.get("id")})
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprints", nargs="*")
    args = parser.parse_args()
    if args.blueprints:
        paths = [Path(item) if Path(item).is_absolute() else ROOT / item for item in args.blueprints]
    else:
        paths = sorted(ROOT.glob(DEFAULT_GLOB))
    failures: list[dict] = []
    for path in paths:
        failures.extend(validate_blueprint(path))
    result = {
        "ok": not failures,
        "blueprintCount": len(paths),
        "blueprints": [rel(path) for path in paths],
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
