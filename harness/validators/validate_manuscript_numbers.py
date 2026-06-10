#!/usr/bin/env python3
"""Validate that manuscript claims match generated result artifacts.

This validator is intentionally conservative: it checks high-value manuscript
numbers that are easy to drift during revision, then emits a JSON audit report.
It does not try to parse every number in the article.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    label: str
    expected: str
    source: str
    ok: bool


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fmt_int(value: str | int | float) -> str:
    return f"{int(float(value)):,}"


def fmt_pct(value: str | float) -> str:
    return f"{float(value):.2f}%"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u2013", "-").replace("\u2014", "-"))


def add_contains(checks: list[Check], manuscript: str, label: str, expected: str, source: str) -> None:
    checks.append(Check(label=label, expected=expected, source=source, ok=expected in manuscript))


def validate(run_root: Path, manuscript_path: Path) -> dict:
    text = normalize_text(manuscript_path.read_text(encoding="utf-8"))
    checks: list[Check] = []

    results_s3 = run_root / "results" / "S3"
    results_s8b = run_root / "results" / "S8b"

    flow = read_csv(results_s3 / "flow_counts.csv")
    flow_map = {row["step"]: row["n"] for row in flow}
    add_contains(
        checks,
        text,
        "final analytic sample",
        f"{fmt_int(flow_map['After excluding pregnant participants'])} remained",
        "results/S3/flow_counts.csv",
    )
    add_contains(
        checks,
        text,
        "interview participants",
        f"{fmt_int(flow_map['NHANES 2017-2018 interview participants'])} NHANES 2017-2018 interview participants",
        "results/S3/flow_counts.csv",
    )
    add_contains(
        checks,
        text,
        "adults aged 20 or older",
        f"{fmt_int(flow_map['Adults aged >=20 years'])} were aged 20 years or older",
        "results/S3/flow_counts.csv",
    )

    prevalence = read_csv(results_s3 / "weighted_prevalence_overall.csv")
    prev_map = {row["outcome"]: row for row in prevalence}
    undx = prev_map["HbA1c-defined undiagnosed diabetes"]
    prediabetes = prev_map["HbA1c-defined prediabetes"]
    add_contains(
        checks,
        text,
        "undiagnosed diabetes prevalence",
        f"{fmt_pct(undx['weighted_percent'])} (95% CI, {fmt_pct(undx['ci_low'])}-{fmt_pct(undx['ci_high'])})",
        "results/S3/weighted_prevalence_overall.csv",
    )
    add_contains(
        checks,
        text,
        "undiagnosed diabetes cases",
        f"{fmt_int(undx['unweighted_cases'])} participants had HbA1c >=6.5%",
        "results/S3/weighted_prevalence_overall.csv",
    )
    add_contains(
        checks,
        text,
        "prediabetes prevalence",
        f"{fmt_pct(prediabetes['weighted_percent'])} (95% CI, {fmt_pct(prediabetes['ci_low'])}-{fmt_pct(prediabetes['ci_high'])})",
        "results/S3/weighted_prevalence_overall.csv",
    )
    add_contains(
        checks,
        text,
        "prediabetes cases",
        f"{fmt_int(prediabetes['unweighted_cases'])} participants had HbA1c 5.7%-6.4%",
        "results/S3/weighted_prevalence_overall.csv",
    )

    fasting = read_csv(results_s8b / "fasting_weighted_sensitivity_prevalence.csv")
    fasting_map = {row["outcome"]: row for row in fasting}
    hba1c_only = fasting_map["HbA1c-defined undiagnosed diabetes in fasting subsample"]
    hba1c_or_fpg = fasting_map["HbA1c or fasting glucose-defined undiagnosed diabetes in fasting subsample"]
    add_contains(
        checks,
        text,
        "fasting subsample combined definition",
        f"{fmt_int(hba1c_or_fpg['unweighted_cases'])} cases of HbA1c- or fasting-glucose-defined undiagnosed diabetes among {fmt_int(hba1c_or_fpg['unweighted_n'])} participants",
        "results/S8b/fasting_weighted_sensitivity_prevalence.csv",
    )
    add_contains(
        checks,
        text,
        "fasting sensitivity increase",
        f"{fmt_pct(hba1c_only['weighted_percent'])} (95% CI, {fmt_pct(hba1c_only['ci_low'])}-{fmt_pct(hba1c_only['ci_high'])}) using HbA1c alone to {fmt_pct(hba1c_or_fpg['weighted_percent'])} (95% CI, {fmt_pct(hba1c_or_fpg['ci_low'])}-{fmt_pct(hba1c_or_fpg['ci_high'])})",
        "results/S8b/fasting_weighted_sensitivity_prevalence.csv",
    )

    table2 = read_csv(results_s8b / "table2_formatted.csv")
    table2_map = {row["Variable"]: row for row in table2}
    for label, variable, manuscript_phrase in [
        ("waist circumference OR", "Waist circumference, per cm", "waist circumference"),
        ("non-HDL OR", "Non-HDL cholesterol, per mg/dL", "non-HDL cholesterol"),
        ("Asian OR", "Non-Hispanic Asian vs Non-Hispanic White", "Non-Hispanic Asian participants"),
        ("Black OR", "Non-Hispanic Black vs Non-Hispanic White", "Non-Hispanic Black participants"),
        ("physical activity OR", "Any reported physical activity vs none", "any physical activity"),
    ]:
        value = table2_map[variable]["OR (95% CI)"]
        or_value, ci = value.split(" ", 1)
        expected = f"{manuscript_phrase} (OR"
        if variable in {"Waist circumference, per cm", "Non-HDL cholesterol, per mg/dL"}:
            expected = f"{manuscript_phrase} (OR per"
        checks.append(
            Check(
                label=label,
                expected=f"{expected} ... {or_value}; 95% CI, {ci.strip('()')}",
                source="results/S8b/table2_formatted.csv",
                ok=or_value in text and ci.strip("()") in text,
            )
        )

    failures = [check.__dict__ for check in checks if not check.ok]
    return {
        "ok": not failures,
        "manuscript": str(manuscript_path),
        "checks": [check.__dict__ for check in checks],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-root",
        default="examples/nhanes-undiagnosed-diabetes",
        help="Run directory containing results/ and submission_package/.",
    )
    parser.add_argument(
        "--manuscript",
        default="examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_generic_sci.md",
        help="Markdown manuscript to audit.",
    )
    args = parser.parse_args()
    result = validate(Path(args.run_root), Path(args.manuscript))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
