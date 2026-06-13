#!/usr/bin/env python3
"""Plan an NHANES/CHARLS/GBD manuscript workflow from a broad topic."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "examples/topic-plans"


@dataclass(frozen=True)
class KeywordRule:
    terms: tuple[str, ...]
    weight: int
    reason: str


DATASET_RULES: dict[str, list[KeywordRule]] = {
    "nhanes": [
        KeywordRule(("nutrition", "diet", "dietary", "physical activity", "smoking", "sleep", "bmi", "obesity"), 3, "NHANES contains interview, examination, lifestyle, and anthropometric variables."),
        KeywordRule(("glucose", "hba1c", "diabetes", "prediabetes", "lipid", "cholesterol", "blood pressure", "hypertension"), 3, "NHANES supports cross-sectional cardiometabolic and laboratory-marker analyses."),
        KeywordRule(("us", "u.s.", "american", "population", "survey"), 2, "NHANES is a U.S. population survey with complex survey design."),
    ],
    "charls": [
        KeywordRule(("aging", "older", "elderly", "middle-aged", "cognition", "cognitive", "memory", "depression", "cesd"), 4, "CHARLS is designed for aging, cognition, depression, and social/health trajectories."),
        KeywordRule(("longitudinal", "follow-up", "trajectory", "decline", "incident", "baseline", "attrition"), 4, "CHARLS can support longitudinal designs after wave linkage and attrition planning."),
        KeywordRule(("frailty", "disability", "adl", "chronic disease", "multimorbidity", "retirement", "socioeconomic"), 3, "CHARLS includes aging-related health, function, and socioeconomic domains."),
        KeywordRule(("china", "chinese"), 3, "CHARLS is a China aging cohort."),
    ],
    "gbd": [
        KeywordRule(("burden", "mortality", "death", "dalys", "ylds", "ylls", "prevalence trend", "incidence trend"), 4, "GBD is suitable for descriptive disease-burden, mortality, and DALY analyses."),
        KeywordRule(("trend", "1990", "2023", "age-standardized", "global", "regional", "country", "china"), 3, "GBD supports location/year/age/sex/metric query profiles and uncertainty intervals."),
        KeywordRule(("cardiovascular", "cancer", "stroke", "copd", "liver disease", "kidney disease", "dementia"), 2, "GBD cause hierarchies can frame disease-specific burden questions."),
    ],
}

OMICS_TERMS = (
    "bioinformatics",
    "omics",
    "transcriptomic",
    "transcriptome",
    "genomic",
    "genome",
    "gene",
    "genes",
    "differential expression",
    "wgcna",
    "single-cell",
    "single cell",
    "scrna",
    "tcga",
    "geo",
    "gtex",
    "proteomic",
    "methylation",
    "immune infiltration",
    "pathway",
)

TOPIC_DOMAINS = {
    "cardiometabolic": ("diabetes", "obesity", "bmi", "hba1c", "glucose", "lipid", "hypertension", "cardiovascular", "stroke"),
    "aging_neuropsych": ("aging", "older", "elderly", "cognition", "cognitive", "memory", "depression", "frailty", "dementia"),
    "disease_burden": ("burden", "mortality", "dalys", "ylds", "ylls", "incidence", "prevalence", "trend"),
    "lifestyle_environment": ("diet", "nutrition", "physical activity", "sleep", "smoking", "alcohol", "environment"),
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "topic-plan"


def detect_terms(topic: str, terms: tuple[str, ...]) -> list[str]:
    text = topic.lower()
    return [term for term in terms if term in text]


def score_dataset(topic: str, dataset: str) -> tuple[int, list[str], list[str]]:
    score = 0
    reasons: list[str] = []
    matched: list[str] = []
    for rule in DATASET_RULES[dataset]:
        hits = detect_terms(topic, rule.terms)
        if hits:
            score += rule.weight
            matched.extend(hits)
            reasons.append(rule.reason)
    return score, sorted(set(matched)), sorted(set(reasons))


def detect_domains(topic: str) -> list[str]:
    domains = []
    for domain, terms in TOPIC_DOMAINS.items():
        if detect_terms(topic, terms):
            domains.append(domain)
    return domains or ["general_medical_topic"]


def dataset_role(dataset: str, score: int, omics_requested: bool) -> str:
    if dataset == "nhanes":
        base = "cross-sectional phenotype, exposure, laboratory, lifestyle, and survey-weighted association route"
    elif dataset == "charls":
        base = "aging, depression/cognition/function, chronic disease, and longitudinal trajectory route"
    else:
        base = "disease-burden, mortality/DALY, trend, location, metric, and uncertainty-interval route"
    if score == 0:
        return f"optional only; {base} if the topic is reframed to fit this dataset"
    if omics_requested:
        return f"{base}; cannot provide molecular mechanism or omics evidence without external omics databases"
    return base


def support_level(dataset: str, score: int) -> str:
    if score >= 6:
        return "primary"
    if score >= 3:
        return "secondary"
    if score > 0:
        return "exploratory"
    return "not_recommended"


def design_for_dataset(dataset: str) -> dict:
    if dataset == "nhanes":
        return {
            "studyDesign": "cross-sectional complex survey analysis",
            "reportingGuideline": "STROBE",
            "requiredGate": "S2 survey-weighted analysis plan before S3 execution",
            "claimBoundary": "association and weighted prevalence only; no causal language and no clinical diagnosis from a single measurement",
        }
    if dataset == "charls":
        return {
            "studyDesign": "longitudinal cohort or wave-specific cross-sectional aging analysis",
            "reportingGuideline": "STROBE/RECORD depending on linkage and reporting frame",
            "requiredGate": "S1/S2 design gate with wave linkage, temporal ordering, attrition, missingness, and weight decision",
            "claimBoundary": "temporal association or trajectory language only unless a defensible causal design is added",
        }
    return {
        "studyDesign": "descriptive disease burden or comparative trend analysis",
        "reportingGuideline": "GATHER-style source transparency plus journal requirements",
        "requiredGate": "query profile with release, measure, metric, cause, location, age, sex, year, UI, citation, and reuse review",
        "claimBoundary": "burden/trend description with uncertainty intervals; no patient-level risk-factor or mechanism claims",
    }


def candidate_questions(topic: str, recommended: list[str], omics_requested: bool) -> list[dict]:
    questions: list[dict] = []
    if "charls" in recommended:
        questions.append({
            "id": "charls-longitudinal",
            "dataSource": "CHARLS",
            "question": f"Among middle-aged and older adults, how is {topic} related to longitudinal changes in aging-related outcomes after wave linkage and attrition assessment?",
            "status": "scaffold_until_local_data_ready",
        })
    if "nhanes" in recommended:
        questions.append({
            "id": "nhanes-cross-sectional",
            "dataSource": "NHANES",
            "question": f"In a survey-weighted U.S. adult sample, what cross-sectional associations link {topic} with measurable phenotypes, laboratory markers, or lifestyle factors?",
            "status": "template_supported; requires cycle/variable selection",
        })
    if "gbd" in recommended:
        questions.append({
            "id": "gbd-burden-trend",
            "dataSource": "GBD",
            "question": f"What are the burden and time trends for diseases or outcomes related to {topic} across locations, years, age groups, and sex strata?",
            "status": "query_profile_required_before_claims",
        })
    if omics_requested:
        questions.append({
            "id": "omics-extension",
            "dataSource": "External omics databases",
            "question": f"What molecular signatures or pathways related to {topic} can be evaluated using GEO/TCGA/GTEx or other omics sources?",
            "status": "not_supported_by_nhanes_charls_gbd_only",
        })
    return questions


def manuscript_path(recommended: list[str], omics_requested: bool) -> list[dict]:
    stages = [
        {"stage": "S0", "task": "intake topic, target population, disease/outcome, intended database combination, and data-access status"},
        {"stage": "S1", "task": "convert broad topic into dataset-specific answerable research questions"},
        {"stage": "S2", "task": "write analysis plan and dataset-specific gate: survey weights, wave linkage, or GBD query profile"},
        {"stage": "S3", "task": "execute or import validated results; do not draft numeric claims before this stage"},
        {"stage": "S4", "task": "interpret results with study-design boundaries and uncertainty intervals where applicable"},
        {"stage": "S5", "task": "build paper outline and table/figure shell"},
        {"stage": "S6", "task": "draft manuscript sections with cautious causal and diagnostic language"},
        {"stage": "S7", "task": "claim registry, citation registry, data provenance, and guideline checklist audit"},
        {"stage": "S8", "task": "review/revision simulation and response trace"},
        {"stage": "S9", "task": "final manuscript package and readiness report"},
    ]
    if omics_requested:
        stages.insert(2, {
            "stage": "S1b",
            "task": "decide whether the paper is epidemiology-only or requires a separate omics data module; NHANES/CHARLS/GBD cannot prove molecular mechanism alone",
        })
    return stages


def build_plan(topic: str, title: str | None = None) -> dict:
    omics_hits = detect_terms(topic, OMICS_TERMS)
    omics_requested = bool(omics_hits)
    domains = detect_domains(topic)

    dataset_scores = []
    for dataset in ("nhanes", "charls", "gbd"):
        score, matched, reasons = score_dataset(topic, dataset)
        dataset_scores.append({
            "id": dataset,
            "score": score,
            "supportLevel": support_level(dataset, score),
            "matchedTerms": matched,
            "role": dataset_role(dataset, score, omics_requested),
            "reasons": reasons,
            "design": design_for_dataset(dataset),
        })
    dataset_scores.sort(key=lambda item: item["score"], reverse=True)
    recommended = [item["id"] for item in dataset_scores if item["supportLevel"] in {"primary", "secondary"}]
    if not recommended:
        recommended = [dataset_scores[0]["id"]]

    cautions = [
        "Do not write cross-sectional associations as causal effects.",
        "Do not write single laboratory measurements or survey responses as definitive clinical diagnoses.",
        "Do not write descriptive public-database analyses as mechanistic studies.",
        "Do not draft manuscript-ready numeric claims until S3 outputs and S7 claim/citation audits exist.",
    ]
    if omics_requested:
        cautions.append("NHANES, CHARLS, and GBD are not sufficient for transcriptomic/genomic/single-cell mechanism claims; add GEO/TCGA/GTEx or equivalent omics sources if the paper requires bioinformatics evidence.")

    return {
        "schemaVersion": "topic-research-plan-v1",
        "topic": topic,
        "title": title or f"Topic plan: {topic}",
        "status": "planning-only-not-analysis",
        "domains": domains,
        "omicsRequested": omics_requested,
        "omicsTerms": omics_hits,
        "recommendedDataSources": recommended,
        "datasetScores": dataset_scores,
        "candidateResearchQuestions": candidate_questions(topic, recommended, omics_requested),
        "manuscriptWorkflow": manuscript_path(recommended, omics_requested),
        "requiredHumanDecisions": [
            "Confirm the target population and disease/outcome scope.",
            "Choose one primary dataset route before analysis execution.",
            "Confirm local access status for CHARLS and any restricted data.",
            "Confirm GBD release/query dimensions and citation/reuse boundary before using GBD claims.",
            "Decide whether external omics databases are required for a bioinformatics manuscript.",
        ],
        "cautionLanguage": cautions,
        "nextActions": [
            "Use this plan as S0/S1 input, not as completed analysis.",
            "Instantiate a dataset-specific project only after choosing the primary route.",
            "Run the relevant design gate before S3 analysis and manuscript numeric claims.",
        ],
    }


def render_markdown(plan: dict) -> str:
    lines = [
        f"# {plan['title']}",
        "",
        f"Topic: {plan['topic']}",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Recommendation",
        "",
        "Recommended data sources: " + ", ".join(plan["recommendedDataSources"]),
        "",
        "| Data source | Support | Score | Role |",
        "| --- | --- | ---: | --- |",
    ]
    for item in plan["datasetScores"]:
        lines.append(f"| {item['id']} | {item['supportLevel']} | {item['score']} | {item['role']} |")
    lines.extend(["", "## Candidate Research Questions", ""])
    for question in plan["candidateResearchQuestions"]:
        lines.append(f"- **{question['id']}** ({question['dataSource']}): {question['question']} Status: `{question['status']}`")
    lines.extend(["", "## Manuscript Workflow", ""])
    for stage in plan["manuscriptWorkflow"]:
        lines.append(f"- **{stage['stage']}**: {stage['task']}")
    lines.extend(["", "## Required Human Decisions", ""])
    for item in plan["requiredHumanDecisions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Caution Language", ""])
    for item in plan["cautionLanguage"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Actions", ""])
    for item in plan["nextActions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_plan(plan: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_json = output_dir / "topic_plan.json"
    plan_md = output_dir / "topic_plan.md"
    workflow_seed = output_dir / "workflow-seed.json"
    plan_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_md.write_text(render_markdown(plan), encoding="utf-8")
    seed = {
        "workflow": "academic-research-suite-checkpoint-first",
        "sourcePlan": str(plan_json.relative_to(ROOT)),
        "currentStage": "S0",
        "checkpointFirst": True,
        "status": "topic-plan-only",
        "recommendedDataSources": plan["recommendedDataSources"],
        "nextRequiredStage": "S0 intake confirmation and S1 research question refinement",
    }
    workflow_seed.write_text(json.dumps(seed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "outputDir": str(output_dir.relative_to(ROOT)),
        "planJson": str(plan_json.relative_to(ROOT)),
        "planMarkdown": str(plan_md.relative_to(ROOT)),
        "workflowSeed": str(workflow_seed.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a topic-to-database manuscript workflow plan.")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--title")
    parser.add_argument("--output")
    args = parser.parse_args()
    plan = build_plan(args.topic, title=args.title)
    output = Path(args.output) if args.output else DEFAULT_OUTPUT_ROOT / slugify(args.topic)
    if not output.is_absolute():
        output = ROOT / output
    result = write_plan(plan, output)
    result["recommendedDataSources"] = plan["recommendedDataSources"]
    result["omicsRequested"] = plan["omicsRequested"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
