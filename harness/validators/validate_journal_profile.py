#!/usr/bin/env python3
"""Validate manuscript readiness against a journal profile."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def validate(manuscript_path: Path, profile_path: Path) -> dict:
    manuscript = manuscript_path.read_text(encoding="utf-8")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    text_for_count = re.sub(r"^#.*$", "", manuscript, flags=re.MULTILINE)
    word_count = len(re.findall(r"\b[\w'-]+\b", text_for_count))
    references = re.findall(r"^\d+\.\s+", manuscript, flags=re.MULTILINE)
    table_figure_mentions = len(re.findall(r"\b(?:Table|Figure)\s+\d+", manuscript))
    failures = []

    limits = profile["limits"]
    if word_count > limits["wordCount"]["max"]:
        failures.append({"check": "word_count_max", "actual": word_count, "max": limits["wordCount"]["max"]})
    if word_count < limits["wordCount"]["min"]:
        failures.append({"check": "word_count_min", "actual": word_count, "min": limits["wordCount"]["min"]})
    if len(references) > limits["references"]["max"]:
        failures.append({"check": "reference_count_max", "actual": len(references), "max": limits["references"]["max"]})
    if table_figure_mentions > limits["tablesAndFigures"]["max"] * 6:
        failures.append({"check": "table_figure_mentions_review", "actualMentions": table_figure_mentions})

    missing_statements = []
    statement_labels = {
        "funding": "Funding:",
        "conflicts_of_interest": "Conflicts of interest:",
        "data_availability": "# Data Availability",
        "ethics_statement": "# Ethics Statement",
        "author_contributions": "Author contributions:",
        "acknowledgements": "Acknowledgements:"
    }
    for statement in profile.get("requiredStatements", []):
        label = statement_labels.get(statement, statement)
        if label not in manuscript:
            missing_statements.append(statement)
    if missing_statements:
        failures.append({"check": "required_statements", "missing": missing_statements})

    return {
        "ok": not failures,
        "profile": str(profile_path),
        "manuscript": str(manuscript_path),
        "wordCount": word_count,
        "referenceCount": len(references),
        "tableFigureMentionCount": table_figure_mentions,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", default="examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_generic_sci.md")
    parser.add_argument("--profile", default="harness/journal_profiles/generic_sci.json")
    args = parser.parse_args()
    result = validate(Path(args.manuscript), Path(args.profile))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
