#!/usr/bin/env python3
"""Generate a tabular review helper for GBD CVD claim decisions."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def fmt_interval(row: dict[str, str], value: str, lower: str, upper: str) -> str:
    return f"{row[value]} (UI {row[lower]}-{row[upper]})"


def build_evidence_summary(claim_id: str, summary_rows: list[dict[str, str]]) -> str:
    by_location = {row["location"]: row for row in summary_rows}
    china = by_location.get("China", {})
    global_row = by_location.get("Global", {})
    if claim_id == "gbd-cvd-china-global-rq-boundary":
        return "No numeric estimate; scope boundary anchored to query manifest and claim registry."
    if claim_id == "gbd-cvd-deaths-count-change-china":
        return (
            "China all-age Deaths Number: "
            f"1990 {fmt_interval(china, 'deaths_1990', 'deaths_1990_lower', 'deaths_1990_upper')}; "
            f"2023 {fmt_interval(china, 'deaths_2023', 'deaths_2023_lower', 'deaths_2023_upper')}; "
            f"change {china['deaths_percent_change_1990_2023']}%."
        )
    if claim_id == "gbd-cvd-dalys-count-change-china":
        return (
            "China all-age DALYs Number: "
            f"1990 {fmt_interval(china, 'dalys_1990', 'dalys_1990_lower', 'dalys_1990_upper')}; "
            f"2023 {fmt_interval(china, 'dalys_2023', 'dalys_2023_lower', 'dalys_2023_upper')}; "
            f"change {china['dalys_percent_change_1990_2023']}%."
        )
    if claim_id == "gbd-cvd-death-rate-comparison-china-global":
        return (
            "Age-standardized Deaths Rate: "
            f"China 1990 {fmt_interval(china, 'death_rate_1990', 'death_rate_1990_lower', 'death_rate_1990_upper')}, "
            f"China 2023 {fmt_interval(china, 'death_rate_2023', 'death_rate_2023_lower', 'death_rate_2023_upper')}; "
            f"Global 1990 {fmt_interval(global_row, 'death_rate_1990', 'death_rate_1990_lower', 'death_rate_1990_upper')}, "
            f"Global 2023 {fmt_interval(global_row, 'death_rate_2023', 'death_rate_2023_lower', 'death_rate_2023_upper')}."
        )
    if claim_id == "gbd-cvd-daly-rate-comparison-china-global":
        return (
            "Age-standardized DALYs Rate: "
            f"China 1990 {fmt_interval(china, 'daly_rate_1990', 'daly_rate_1990_lower', 'daly_rate_1990_upper')}, "
            f"China 2023 {fmt_interval(china, 'daly_rate_2023', 'daly_rate_2023_lower', 'daly_rate_2023_upper')}; "
            f"Global 1990 {fmt_interval(global_row, 'daly_rate_1990', 'daly_rate_1990_lower', 'daly_rate_1990_upper')}, "
            f"Global 2023 {fmt_interval(global_row, 'daly_rate_2023', 'daly_rate_2023_lower', 'daly_rate_2023_upper')}."
        )
    return "No evidence summary rule configured."


def decision_prompt(row: dict[str, str]) -> str:
    recommended = row.get("recommended_decision", "")
    if recommended == "retain":
        return "Suggested: approve if boundary wording is retained; otherwise rewrite."
    if recommended == "rewrite":
        return "Suggested: rewrite or approve with final journal wording; downgrade if too dense for main text."
    if recommended == "downgrade":
        return "Suggested: downgrade unless uncertainty and wording are finalized."
    return "Choose approve, rewrite, downgrade, or delete after human review."


def markdown_table(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    header = "| " + " | ".join(fieldnames) + " |"
    sep = "| " + " | ".join(["---"] * len(fieldnames)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(row.get(field, "").replace("\n", " ").replace("|", "/") for field in fieldnames) + " |")
    return "\n".join([header, sep, *body])


def generate(project: Path) -> dict:
    project_dir = project if project.is_absolute() else ROOT / project
    manifest = load_json(project_dir / "project_manifest.json")
    summary_path = root_path(load_json(root_path(manifest["analysisManifest"]))["analyses"]["cvdChinaGlobal"]["outputCsv"])
    registry_path = root_path(manifest["claimRegistry"])
    checklist_path = root_path(manifest["claimReviewChecklist"])
    decisions_path = root_path(manifest["claimReviewDecisions"])
    output_csv = root_path(manifest["claimReviewHelperCsv"])
    output_md = root_path(manifest["claimReviewHelperMarkdown"])

    summary_rows = read_csv(summary_path)
    registry = load_json(registry_path)
    claims_by_id = {claim["id"]: claim for claim in registry.get("claims", [])}
    checklist_rows = read_csv(checklist_path)
    decisions = {item["claimId"]: item for item in load_json(decisions_path).get("decisions", [])}

    helper_rows = []
    for row in checklist_rows:
        claim_id = row["claim_id"]
        claim = claims_by_id.get(claim_id, {})
        decision = decisions.get(claim_id, {})
        helper_rows.append(
            {
                "claim_id": claim_id,
                "tier": claim.get("tier", ""),
                "claim_role": claim.get("claimRole", ""),
                "current_decision": decision.get("decision", "pending"),
                "recommended_decision": row.get("recommended_decision", ""),
                "decision_options": "approve|rewrite|downgrade|delete",
                "source_backed_text": claim.get("expectedText", ""),
                "evidence_values": build_evidence_summary(claim_id, summary_rows),
                "metric_boundary": row.get("metric_rule", ""),
                "age_boundary": row.get("age_rule", ""),
                "ui_boundary": row.get("ui_rule", ""),
                "wording_boundary": row.get("wording_rule", ""),
                "review_prompt": decision_prompt(row),
            }
        )

    fieldnames = [
        "claim_id",
        "tier",
        "claim_role",
        "current_decision",
        "recommended_decision",
        "decision_options",
        "source_backed_text",
        "evidence_values",
        "metric_boundary",
        "age_boundary",
        "ui_boundary",
        "wording_boundary",
        "review_prompt",
    ]
    write_csv(output_csv, helper_rows, fieldnames)
    output_md.write_text(
        "\n".join(
            [
                "# GBD CVD Claim Review Helper",
                "",
                "Status: decision-support table only. This helper does not approve claims.",
                "",
                "Edit `gbd_cvd_claim_review_decisions.json` after reviewing the rows below.",
                "",
                markdown_table(helper_rows, fieldnames),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "project": rel(project_dir),
        "helperCsv": rel(output_csv),
        "helperMarkdown": rel(output_md),
        "claimCount": len(helper_rows),
        "pendingDecisionCount": sum(1 for row in helper_rows if row["current_decision"] == "pending"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    args = parser.parse_args()
    result = generate(Path(args.project))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
