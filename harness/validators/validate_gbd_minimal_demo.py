#!/usr/bin/env python3
"""Validate the GBD minimal teaching demo."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


REQUIRED_QUERY_COLUMNS = {"gbd_release", "measure", "metric", "cause", "location", "age", "sex", "year", "export_file"}
ALLOWED_TIERS = {"core", "supporting", "background"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate(root: Path, demo: Path) -> dict:
    path = root / demo
    failures = []
    manifest_path = path / "project_manifest.json"
    query_path = path / "gbd_query_manifest.csv"
    source_path = path / "source_exports/gbd_results_minimal_fixture.csv"
    summary_csv_path = path / "results/gbd_minimal_summary.csv"
    summary_md_path = path / "results/gbd_minimal_summary.md"
    real_source_path = path / "source_exports/gbd_results_real_default_data.csv"
    real_summary_csv_path = path / "results/gbd_real_default_summary.csv"
    real_summary_md_path = path / "results/gbd_real_default_summary.md"
    registry_path = path / "claim_registry.json"

    required_files = [manifest_path, query_path, source_path, summary_csv_path, summary_md_path, registry_path]
    for required in required_files:
        if not required.exists():
            failures.append({"check": "file_exists", "path": str(required.relative_to(root))})
    if failures:
        return {"ok": False, "demo": str(demo), "failures": failures}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("capabilityStatus") not in {"minimal-demo", "minimal-demo-plus-real-default-export"}:
        failures.append({"check": "capability_status", "actual": manifest.get("capabilityStatus")})
    if not manifest.get("teachingFixture"):
        failures.append({"check": "teaching_fixture_declared"})

    query_rows = read_csv(query_path)
    if not query_rows:
        failures.append({"check": "query_rows_present"})
    else:
        missing = sorted(REQUIRED_QUERY_COLUMNS - set(query_rows[0].keys()))
        if missing:
            failures.append({"check": "query_manifest_columns", "missing": missing})
        for row in query_rows:
            for column in REQUIRED_QUERY_COLUMNS:
                if not row.get(column):
                    failures.append({"check": "query_dimension_filled", "column": column, "row": row.get("measure")})

    source_rows = read_csv(source_path)
    measures = {row.get("measure") for row in source_rows}
    if measures != {"Deaths", "DALYs"}:
        failures.append({"check": "source_measures", "expected": ["Deaths", "DALYs"], "actual": sorted(measures)})
    if any(row.get("metric") != "Number" for row in source_rows):
        failures.append({"check": "metric_number_only"})
    if not all(row.get("fixture_note") for row in source_rows):
        failures.append({"check": "fixture_note_present"})

    if {"Deaths", "DALYs"}.issubset(measures):
        deaths = Decimal(next(row["val"] for row in source_rows if row["measure"] == "Deaths"))
        dalys = Decimal(next(row["val"] for row in source_rows if row["measure"] == "DALYs"))
        expected_ratio = (dalys / deaths).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        summary_rows = read_csv(summary_csv_path)
        if not summary_rows:
            failures.append({"check": "summary_rows_present"})
        else:
            summary = summary_rows[0]
            if Decimal(summary["deaths_number"]) != deaths:
                failures.append({"check": "deaths_match_source"})
            if Decimal(summary["dalys_number"]) != dalys:
                failures.append({"check": "dalys_match_source"})
            if Decimal(summary["dalys_per_death"]) != expected_ratio:
                failures.append({"check": "derived_ratio", "expected": str(expected_ratio), "actual": summary["dalys_per_death"]})
            if "not a publishable burden estimate" not in summary.get("interpretation_boundary", ""):
                failures.append({"check": "summary_boundary"})

    if manifest.get("capabilityStatus") == "minimal-demo-plus-real-default-export":
        for required in [real_source_path, real_summary_csv_path, real_summary_md_path]:
            if not required.exists():
                failures.append({"check": "real_default_file_exists", "path": str(required.relative_to(root))})
        if real_source_path.exists() and real_summary_csv_path.exists():
            real_rows = read_csv(real_source_path)
            real_summary = read_csv(real_summary_csv_path)[0]
            for field in ["source_endpoint", "downloaded_on", "source_note"]:
                if not all(row.get(field) for row in real_rows):
                    failures.append({"check": "real_source_metadata", "field": field})
            deaths_2023 = next((row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Number" and row["year"] == "2023"), None)
            dalys_2023 = next((row for row in real_rows if row["measure"] == "DALYs" and row["metric"] == "Number" and row["year"] == "2023"), None)
            rate_1990 = next((row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Rate" and row["year"] == "1990"), None)
            rate_2023 = next((row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Rate" and row["year"] == "2023"), None)
            if not all([deaths_2023, dalys_2023, rate_1990, rate_2023]):
                failures.append({"check": "real_required_rows_present"})
            else:
                if Decimal(real_summary["deaths_number"]) != Decimal(deaths_2023["val"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
                    failures.append({"check": "real_deaths_match_source"})
                if Decimal(real_summary["dalys_number"]) != Decimal(dalys_2023["val"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
                    failures.append({"check": "real_dalys_match_source"})
                if "Real GBD Results Tool default endpoint output" not in real_summary.get("interpretation_boundary", ""):
                    failures.append({"check": "real_summary_boundary"})

    manuscript = summary_md_path.read_text(encoding="utf-8")
    if real_summary_md_path.exists():
        manuscript += "\n" + real_summary_md_path.read_text(encoding="utf-8")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    claim_checks = []
    for claim in registry.get("claims", []):
        source = root / claim["sourceFile"]
        text_ok = claim["expectedText"] in manuscript
        tier_ok = claim.get("tier") in ALLOWED_TIERS
        boundary_ok = bool(claim.get("interpretationBoundary"))
        source_ok = source.exists()
        claim_checks.append({"claim": claim["id"], "text": text_ok, "tier": tier_ok, "boundary": boundary_ok, "source": source_ok})
        if not text_ok:
            failures.append({"check": "claim_text_present", "claim": claim["id"]})
        if not tier_ok:
            failures.append({"check": "claim_tier", "claim": claim["id"]})
        if not boundary_ok:
            failures.append({"check": "claim_boundary", "claim": claim["id"]})
        if not source_ok:
            failures.append({"check": "claim_source", "claim": claim["id"], "source": claim["sourceFile"]})

    return {
        "ok": not failures,
        "demo": str(demo),
        "claimCount": len(registry.get("claims", [])),
        "claimChecks": claim_checks,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--demo", default="examples/gbd-burden-minimal-demo")
    args = parser.parse_args()
    result = validate(Path(args.root), Path(args.demo))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
