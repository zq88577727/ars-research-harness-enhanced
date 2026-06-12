#!/usr/bin/env python3
"""Initialize a CHARLS or GBD research project scaffold."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "harness" / "project_templates"


def slug_ok(slug: str) -> bool:
    return slug.replace("-", "").replace("_", "").isalnum() and ".." not in slug and "/" not in slug


def load_template(kind: str) -> dict:
    path = TEMPLATE_DIR / f"{kind}_project_manifest.template.json"
    return json.loads(path.read_text(encoding="utf-8"))


def init_project(kind: str, slug: str, title: str, research_question: str) -> dict:
    if not slug_ok(slug):
        raise ValueError("slug must contain only letters, numbers, hyphens, or underscores")
    run_root = ROOT / "examples" / slug
    if run_root.exists():
        raise FileExistsError(f"project already exists: {run_root}")

    run_root.mkdir(parents=True)
    (run_root / "checkpoints").mkdir()
    (run_root / "derived").mkdir()
    (run_root / "results").mkdir()
    (run_root / "submission_package").mkdir()

    manifest = load_template(kind)
    manifest["title"] = title
    manifest["researchQuestion"] = research_question
    for key, value in list(manifest.items()):
        if isinstance(value, str):
            manifest[key] = value.replace("<project-slug>", slug)
    manifest_path = run_root / "project_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if kind == "charls":
        shutil.copyfile(TEMPLATE_DIR / "variable_map.charls.template.csv", run_root / "variable_map.csv")
        shutil.copyfile(TEMPLATE_DIR / "charls_file_manifest.template.csv", run_root / "charls_file_manifest.csv")
        shutil.copyfile(TEMPLATE_DIR / "charls_wave_map.template.csv", run_root / "charls_wave_map.csv")
        shutil.copyfile(TEMPLATE_DIR / "charls_codebook_extract.template.csv", run_root / "charls_codebook_extract.csv")
        design_gate = (TEMPLATE_DIR / "charls_design_gate.template.json").read_text(encoding="utf-8")
        (run_root / "charls_design_gate.json").write_text(
            design_gate.replace("<project-slug>", slug),
            encoding="utf-8",
        )
    elif kind == "gbd":
        shutil.copyfile(TEMPLATE_DIR / "gbd_query_manifest.template.csv", run_root / "gbd_query_manifest.csv")
        shutil.copyfile(TEMPLATE_DIR / "gbd_analysis_manifest.template.json", run_root / "gbd_analysis_manifest.json")

    workflow = {
        "workflow": "academic-research-suite-checkpoint-first",
        "topic": title,
        "currentStage": "S0",
        "checkpointFirst": True,
        "autoContinueAllowed": False,
        "dataSource": kind,
        "stages": {
            "S0_intake": {"status": "pending", "artifact": "checkpoints/stage-S0-intake.md", "userConfirmed": False},
            "S1_research_question": {"status": "pending", "artifact": "checkpoints/stage-S1-research-question.md", "userConfirmed": False},
            "S2_method_analysis_plan": {"status": "pending", "artifact": "checkpoints/stage-S2-method-plan.md", "userConfirmed": False},
            "S3_evidence_data_execution": {"status": "pending", "artifact": "checkpoints/stage-S3-evidence-results.md", "userConfirmed": False},
            "S4_interpretation": {"status": "pending", "artifact": "checkpoints/stage-S4-interpretation.md", "userConfirmed": False},
            "S5_outline": {"status": "pending", "artifact": "checkpoints/stage-S5-outline.md", "userConfirmed": False},
            "S6_draft": {"status": "pending", "artifact": "checkpoints/stage-S6-draft.md", "userConfirmed": False},
            "S7_integrity_citation_check": {"status": "pending", "artifact": "checkpoints/stage-S7-integrity-citation-check.md", "userConfirmed": False},
            "S8_review_revision": {"status": "pending", "artifact": "checkpoints/stage-S8-review-revision.md", "userConfirmed": False},
            "S9_finalize_closeout": {"status": "pending", "artifact": "checkpoints/stage-S9-finalize-closeout.md", "userConfirmed": False}
        },
        "artifacts": {"runDirectory": f"examples/{slug}", "projectManifest": "project_manifest.json"},
        "decisions": [],
        "risks": [
            "Raw data must remain outside git unless the data license explicitly allows redistribution.",
            "Manuscript claims must not be drafted as final conclusions until S3 outputs and S7 audits exist."
        ],
        "failures": []
    }
    (run_root / "workflow-run.json").write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    next_steps = [
        "1. Complete S0 intake and confirm data access status.",
        "2. Fill the variable map or query manifest.",
        "3. Place raw data in the ignored local raw-data directory declared by `project_manifest.json`.",
    ]
    if kind == "charls":
        next_steps.append("4. Complete the CHARLS S1/S2 design gate before any real longitudinal analysis.")
        next_steps.append("5. Fill the CHARLS codebook extract and generate the S1/S2 instantiation worksheet.")
        next_steps.append("6. Do not draft final claims until S3 results and S7 validation artifacts exist.")
    else:
        next_steps.append("4. Do not draft final claims until S3 results and S7 validation artifacts exist.")

    readme = [
        f"# {title}",
        "",
        f"Data source: `{kind}`",
        "",
        "Status: scaffold only. This folder does not contain raw data, completed analysis outputs, or manuscript-ready results.",
        "",
        f"Dataset-level policy is inherited from `data_sources/{kind}.json`; this project manifest records run-specific state.",
        "",
        "## Research Question",
        "",
        research_question or "To be completed in S1.",
        "",
        "## Required Next Steps",
        "",
        *next_steps,
        "",
    ]
    (run_root / "README.md").write_text("\n".join(readme), encoding="utf-8")
    return {"ok": True, "project": str(run_root), "manifest": str(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["charls", "gbd"])
    parser.add_argument("slug")
    parser.add_argument("--title", required=True)
    parser.add_argument("--research-question", default="")
    args = parser.parse_args()
    try:
        result = init_project(args.kind, args.slug, args.title, args.research_question)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
