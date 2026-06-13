#!/usr/bin/env python3
"""Instantiate dataset-specific scaffolds from a topic research plan."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "harness/project_templates"
STAGE_KEYS = [
    ("S0_intake", "stage-S0-intake.md", "S0 Intake"),
    ("S1_research_question", "stage-S1-research-question.md", "S1 Research Question"),
    ("S2_method_analysis_plan", "stage-S2-method-plan.md", "S2 Method And Analysis Plan"),
    ("S3_evidence_data_execution", "stage-S3-evidence-results.md", "S3 Evidence And Data Execution"),
    ("S4_interpretation", "stage-S4-interpretation.md", "S4 Interpretation"),
    ("S5_outline", "stage-S5-outline.md", "S5 Outline"),
    ("S6_draft", "stage-S6-draft.md", "S6 Draft"),
    ("S7_integrity_citation_check", "stage-S7-integrity-citation-check.md", "S7 Integrity And Citation Check"),
    ("S8_review_revision", "stage-S8-review-revision.md", "S8 Review And Revision"),
    ("S9_finalize_closeout", "stage-S9-finalize-closeout.md", "S9 Finalize And Closeout"),
]


def slugify(value: str) -> str:
    chars = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return "".join(chars).strip("-")[:70] or "topic"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def question_for(plan: dict, dataset: str) -> str:
    dataset_upper = dataset.upper()
    for item in plan.get("candidateResearchQuestions", []):
        if item.get("dataSource", "").upper() == dataset_upper:
            return item.get("question", "")
    return f"To be refined from topic: {plan.get('topic', '')}"


def design_for(plan: dict, dataset: str) -> dict:
    for item in plan.get("datasetScores", []):
        if item.get("id") == dataset:
            return item.get("design", {})
    return {}


def make_workflow(title: str, data_source: str, source_plan: str, project_dir: Path) -> dict:
    stages = {}
    for key, artifact, _title in STAGE_KEYS:
        stages[key] = {
            "status": "pending",
            "artifact": f"checkpoints/{artifact}",
            "userConfirmed": False,
        }
    return {
        "workflow": "academic-research-suite-checkpoint-first",
        "topic": title,
        "currentStage": "S0",
        "checkpointFirst": True,
        "autoContinueAllowed": False,
        "dataSource": data_source,
        "sourceTopicPlan": source_plan,
        "stages": stages,
        "artifacts": {
            "runDirectory": str(project_dir.relative_to(ROOT)),
            "projectManifest": "project_manifest.json",
        },
        "decisions": [],
        "risks": [
            "This scaffold is created from a topic plan and is not completed analysis.",
            "Manuscript claims must not be drafted as final conclusions until S3 outputs and S7 audits exist.",
        ],
        "failures": [],
    }


def write_checkpoint_files(project_dir: Path, plan: dict, dataset: str) -> None:
    checkpoints = project_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    design = design_for(plan, dataset)
    rq = question_for(plan, dataset)
    stage_bodies = {
        "stage-S0-intake.md": [
            "# S0 Intake",
            "",
            f"Topic: {plan.get('topic', '')}",
            f"Dataset route: `{dataset}`",
            "",
            "Status: scaffolded from topic plan; human confirmation required before S1/S2.",
            "",
            "Required confirmations:",
            "- target population",
            "- disease/outcome scope",
            "- data access status",
            "- whether external omics evidence is required",
        ],
        "stage-S1-research-question.md": [
            "# S1 Research Question",
            "",
            rq,
            "",
            "Boundary:",
            design.get("claimBoundary", "To be completed."),
        ],
        "stage-S2-method-plan.md": [
            "# S2 Method And Analysis Plan",
            "",
            f"Study design: {design.get('studyDesign', 'To be completed.')}",
            f"Reporting guideline: {design.get('reportingGuideline', 'To be completed.')}",
            f"Required gate: {design.get('requiredGate', 'To be completed.')}",
            "",
            "Do not proceed to S3 until this gate is reviewed.",
        ],
    }
    for _, filename, title in STAGE_KEYS:
        path = checkpoints / filename
        if filename in stage_bodies:
            path.write_text("\n".join(stage_bodies[filename]) + "\n", encoding="utf-8")
        else:
            path.write_text(f"# {title}\n\nStatus: pending. This stage is not yet instantiated beyond the S0-S2 scaffold.\n", encoding="utf-8")


def copy_template_with_project_slug(source: Path, target: Path, template_slug: str) -> None:
    text = source.read_text(encoding="utf-8").replace("<project-slug>", template_slug)
    target.write_text(text, encoding="utf-8")


def copy_charls_templates(project_dir: Path, template_slug: str) -> None:
    shutil.copyfile(TEMPLATE_DIR / "variable_map.charls.template.csv", project_dir / "variable_map.csv")
    shutil.copyfile(TEMPLATE_DIR / "charls_file_manifest.template.csv", project_dir / "charls_file_manifest.csv")
    shutil.copyfile(TEMPLATE_DIR / "charls_wave_map.template.csv", project_dir / "charls_wave_map.csv")
    shutil.copyfile(TEMPLATE_DIR / "charls_codebook_extract.template.csv", project_dir / "charls_codebook_extract.csv")
    shutil.copyfile(TEMPLATE_DIR / "charls_codebook_import_sample.template.csv", project_dir / "charls_codebook_import_sample.csv")
    copy_template_with_project_slug(
        TEMPLATE_DIR / "charls_variable_mapping_decisions.template.json",
        project_dir / "charls_variable_mapping_decisions.json",
        template_slug,
    )
    copy_template_with_project_slug(
        TEMPLATE_DIR / "charls_design_gate.template.json",
        project_dir / "charls_design_gate.json",
        template_slug,
    )


def copy_gbd_templates(project_dir: Path) -> None:
    shutil.copyfile(TEMPLATE_DIR / "gbd_query_manifest.template.csv", project_dir / "gbd_query_manifest.csv")
    shutil.copyfile(TEMPLATE_DIR / "gbd_analysis_manifest.template.json", project_dir / "gbd_analysis_manifest.json")


def write_nhanes_seed_files(project_dir: Path) -> None:
    variable_map = project_dir / "nhanes_variable_targets.csv"
    with variable_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "candidate_variable", "status", "notes"])
        writer.writeheader()
        writer.writerows([
            {"role": "primary_exposure", "candidate_variable": "TBD", "status": "planned", "notes": "Select from NHANES questionnaire/exam/laboratory files."},
            {"role": "primary_outcome", "candidate_variable": "TBD", "status": "planned", "notes": "Use epidemiologic definitions only; avoid clinical diagnosis overclaiming."},
            {"role": "survey_weight", "candidate_variable": "WTMEC2YR or WTSAF2YR", "status": "planned", "notes": "Choose based on component and fasting subsample design."},
        ])


def create_dataset_project(plan: dict, dataset: str, parent: Path, source_plan: str) -> dict:
    base_slug = slugify(plan.get("topic", "topic"))
    project_dir = parent / f"{base_slug}-{dataset}"
    if project_dir.exists():
        raise FileExistsError(f"project already exists: {project_dir}")
    for subdir in ("checkpoints", "derived", "results", "submission_package"):
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    title = f"{plan.get('title', plan.get('topic', 'Topic plan'))} [{dataset.upper()} scaffold]"
    rq = question_for(plan, dataset)
    design = design_for(plan, dataset)
    project_rel = str(project_dir.relative_to(ROOT))
    template_slug = project_rel.removeprefix("examples/")
    if dataset in {"charls", "gbd"}:
        template = load_json(TEMPLATE_DIR / f"{dataset}_project_manifest.template.json")
        manifest = json.loads(json.dumps(template).replace("<project-slug>", template_slug))
        manifest["title"] = title
        manifest["researchQuestion"] = rq
        manifest["sourceTopicPlan"] = source_plan
        manifest["topicPlanDesign"] = design
    else:
        manifest = {
            "projectType": "nhanes-cross-sectional-project",
            "dataSource": "nhanes",
            "dataSourceManifest": "data_sources/nhanes.json",
            "capabilityStatus": "scaffold-only",
            "title": title,
            "researchQuestion": rq,
            "studyDesign": "cross-sectional complex survey scaffold",
            "sourceTopicPlan": source_plan,
            "topicPlanDesign": design,
            "rawDataDirectory": "data/nhanes_2017_2018/raw",
            "derivedDataDirectory": str((project_dir / "derived").relative_to(ROOT)),
            "localRawDataPolicy": "Use public-use NHANES files with CDC/NCHS citation and correct survey weights.",
            "interpretationBoundary": "Associations and weighted prevalence only; no causal language and no clinical diagnosis from one measurement.",
            "analysisRequirements": [
                "cycle and component selected",
                "survey weights and design variables specified",
                "variable file sources recorded",
                "claim registry and reference registry completed before final draft",
            ],
        }
    write_json(project_dir / "project_manifest.json", manifest)
    write_json(project_dir / "workflow-run.json", make_workflow(title, dataset, source_plan, project_dir))
    write_checkpoint_files(project_dir, plan, dataset)
    if dataset == "charls":
        copy_charls_templates(project_dir, template_slug)
    elif dataset == "gbd":
        copy_gbd_templates(project_dir)
    elif dataset == "nhanes":
        write_nhanes_seed_files(project_dir)

    readme = [
        f"# {title}",
        "",
        f"Data source: `{dataset}`",
        "",
        "Status: scaffolded from topic plan. This is not completed analysis and contains no manuscript-ready claims.",
        "",
        f"Source topic plan: `{source_plan}`",
        "",
        "## Research Question",
        "",
        rq,
        "",
        "## S0-S2 Gate",
        "",
        f"- Study design: {design.get('studyDesign', 'To be completed.')}",
        f"- Reporting guideline: {design.get('reportingGuideline', 'To be completed.')}",
        f"- Required gate: {design.get('requiredGate', 'To be completed.')}",
        f"- Claim boundary: {design.get('claimBoundary', 'To be completed.')}",
        "",
    ]
    (project_dir / "README.md").write_text("\n".join(readme), encoding="utf-8")
    return {"dataSource": dataset, "projectDir": str(project_dir.relative_to(ROOT)), "projectManifest": str((project_dir / "project_manifest.json").relative_to(ROOT))}


def create_omics_boundary(plan: dict, parent: Path, source_plan: str) -> dict | None:
    if not plan.get("omicsRequested"):
        return None
    omics_dir = parent / f"{slugify(plan.get('topic', 'topic'))}-external-omics"
    if omics_dir.exists():
        raise FileExistsError(f"project already exists: {omics_dir}")
    omics_dir.mkdir(parents=True)
    boundary = [
        "# External Omics Required",
        "",
        "Status: boundary placeholder only. This repository does not yet implement a real GEO/TCGA/GTEx/STRING/KEGG/GO analysis module.",
        "",
        f"Source topic plan: `{source_plan}`",
        "",
        "Reason:",
        "",
        "The topic asks for bioinformatics or molecular-mechanism evidence. NHANES, CHARLS, and GBD can support epidemiologic, cohort, and disease-burden components, but they cannot by themselves prove transcriptomic, genomic, single-cell, pathway, or immune-infiltration mechanisms.",
        "",
        "Required future module:",
        "",
        "- external omics data source manifest",
        "- accession/query manifest",
        "- preprocessing and differential-analysis plan",
        "- pathway/enrichment plan",
        "- external database citation and reuse policy",
        "- omics claim registry and figure/table provenance",
        "",
    ]
    (omics_dir / "external_omics_required.md").write_text("\n".join(boundary), encoding="utf-8")
    write_json(omics_dir / "project_manifest.json", {
        "projectType": "external-omics-placeholder",
        "dataSource": "external_omics",
        "capabilityStatus": "placeholder-only-not-supported",
        "sourceTopicPlan": source_plan,
        "omicsTerms": plan.get("omicsTerms", []),
        "supportedByCurrentHarness": False,
        "requiredExternalDatabases": ["GEO", "TCGA", "GTEx", "HPA", "STRING", "KEGG", "GO"],
    })
    return {"dataSource": "external_omics", "projectDir": str(omics_dir.relative_to(ROOT)), "projectManifest": str((omics_dir / "project_manifest.json").relative_to(ROOT))}


def instantiate(plan_path: Path, output_dir: Path, datasets: list[str]) -> dict:
    plan = load_json(plan_path)
    source_plan = str(plan_path.relative_to(ROOT) if plan_path.is_relative_to(ROOT) else plan_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []
    for dataset in datasets:
        created.append(create_dataset_project(plan, dataset, output_dir, source_plan))
    omics = create_omics_boundary(plan, output_dir, source_plan)
    if omics:
        created.append(omics)
    manifest = {
        "schemaVersion": "topic-plan-instantiation-v1",
        "sourceTopicPlan": source_plan,
        "outputDir": str(output_dir.relative_to(ROOT)),
        "status": "scaffold-only-not-analysis",
        "createdProjects": created,
        "nextStage": "P8-3 manuscript blueprint generator",
        "boundary": "These scaffolds initialize S0-S2 gates only; they do not contain completed analyses or manuscript-ready claims.",
    }
    manifest_path = output_dir / "instantiation_manifest.json"
    write_json(manifest_path, manifest)
    return {"ok": True, "manifest": str(manifest_path.relative_to(ROOT)), "createdProjects": created}


def main() -> int:
    parser = argparse.ArgumentParser(description="Instantiate project scaffolds from a topic plan.")
    parser.add_argument("topic_plan")
    parser.add_argument("--output-dir")
    parser.add_argument("--datasets", nargs="*", choices=["nhanes", "charls", "gbd"])
    args = parser.parse_args()
    plan_path = Path(args.topic_plan)
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path
    plan = load_json(plan_path)
    datasets = args.datasets or list(plan.get("recommendedDataSources", []))
    if not datasets:
        print(json.dumps({"ok": False, "error": "No datasets requested or recommended."}, indent=2))
        return 1
    output_dir = Path(args.output_dir) if args.output_dir else plan_path.parent / "scaffolds"
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    try:
        result = instantiate(plan_path, output_dir, datasets)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
