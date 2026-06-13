#!/usr/bin/env python3
"""Validate topic-to-database manuscript workflow plans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_DATASETS = {"nhanes", "charls", "gbd"}
REQUIRED_STAGE_PREFIXES = {"S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"}
REQUIRED_CAUTIONS = [
    "causal",
    "clinical diagnoses",
    "mechanistic",
    "S3 outputs",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def validate(plan_path: Path) -> dict:
    failures: list[dict] = []
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    if plan.get("schemaVersion") != "topic-research-plan-v1":
        failures.append({"check": "schemaVersion", "actual": plan.get("schemaVersion")})
    if plan.get("status") != "planning-only-not-analysis":
        failures.append({"check": "planningOnlyStatus", "actual": plan.get("status")})

    scores = plan.get("datasetScores", [])
    score_ids = {item.get("id") for item in scores}
    missing_datasets = sorted(REQUIRED_DATASETS - score_ids)
    if missing_datasets:
        failures.append({"check": "datasetScoresCoverCoreSources", "missing": missing_datasets})
    for item in scores:
        if item.get("supportLevel") not in {"primary", "secondary", "exploratory", "not_recommended"}:
            failures.append({"check": "supportLevel", "dataset": item.get("id"), "actual": item.get("supportLevel")})
        design = item.get("design", {})
        for field in ("studyDesign", "reportingGuideline", "requiredGate", "claimBoundary"):
            if not design.get(field):
                failures.append({"check": "datasetDesignField", "dataset": item.get("id"), "field": field})

    recommended = plan.get("recommendedDataSources", [])
    if not recommended:
        failures.append({"check": "recommendedDataSources"})
    invalid_recommended = sorted(set(recommended) - REQUIRED_DATASETS)
    if invalid_recommended:
        failures.append({"check": "recommendedDataSourcesKnown", "invalid": invalid_recommended})

    stages = plan.get("manuscriptWorkflow", [])
    stage_ids = {item.get("stage") for item in stages}
    missing_stages = sorted(REQUIRED_STAGE_PREFIXES - stage_ids)
    if missing_stages:
        failures.append({"check": "manuscriptWorkflowStages", "missing": missing_stages})

    cautions = " ".join(plan.get("cautionLanguage", [])).lower()
    for token in REQUIRED_CAUTIONS:
        if token.lower() not in cautions:
            failures.append({"check": "cautionLanguage", "missingToken": token})
    if plan.get("omicsRequested") and "geo/tcga/gtex" not in cautions:
        failures.append({"check": "omicsBoundary"})

    questions = plan.get("candidateResearchQuestions", [])
    if not questions:
        failures.append({"check": "candidateResearchQuestions"})
    if plan.get("omicsRequested") and not any(q.get("id") == "omics-extension" for q in questions):
        failures.append({"check": "omicsExtensionQuestion"})

    return {
        "ok": not failures,
        "plan": rel(plan_path),
        "recommendedDataSources": recommended,
        "omicsRequested": bool(plan.get("omicsRequested")),
        "datasetScoreCount": len(scores),
        "workflowStageCount": len(stages),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", nargs="?", default="examples/topic-plans/depression-cognition-cvd-bioinformatics/topic_plan.json")
    args = parser.parse_args()
    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path
    result = validate(plan_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
