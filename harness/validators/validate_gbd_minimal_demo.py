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


def matches(row: dict[str, str], dimensions: dict[str, str]) -> bool:
    return all(row.get(key) == value for key, value in dimensions.items() if value)


def find_row(rows: list[dict[str, str]], dimensions: dict[str, str], measure: dict[str, str], year: str | None = None) -> dict[str, str] | None:
    filters = dict(dimensions)
    filters.update(measure)
    if year:
        filters["year"] = year
    return next((row for row in rows if matches(row, filters)), None)


def validate_analysis_config(root: Path, config: dict, failures: list[dict], label: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    source = root / config["sourceFile"]
    output_csv = root / config["outputCsv"]
    output_md = root / config["outputMarkdown"]
    for required in [source, output_csv, output_md]:
        if not required.exists():
            failures.append({"check": "analysis_file_exists", "analysis": label, "path": str(required.relative_to(root))})
    source_rows = read_csv(source) if source.exists() else []
    summary_rows = read_csv(output_csv) if output_csv.exists() else []
    if source.exists() and not source_rows:
        failures.append({"check": "analysis_source_rows_present", "analysis": label})
    if output_csv.exists() and not summary_rows:
        failures.append({"check": "analysis_summary_rows_present", "analysis": label})
    dimensions = config.get("dimensionFilter", {})
    for column in ["cause", "location", "age", "sex"]:
        if not dimensions.get(column):
            failures.append({"check": "analysis_dimension_present", "analysis": label, "column": column})
    download = config.get("download")
    if download:
        if download.get("overwritePolicy") != "no-overwrite-without-force":
            failures.append({"check": "download_overwrite_policy", "analysis": label, "actual": download.get("overwritePolicy")})
        required_columns = set(download.get("requiredColumns", []))
        if source_rows:
            missing_columns = sorted(required_columns - set(source_rows[0].keys()))
            if missing_columns:
                failures.append({"check": "download_required_columns", "analysis": label, "missing": missing_columns})
            minimum_rows = int(download.get("expectedRowCountMinimum", 1))
            if len(source_rows) < minimum_rows:
                failures.append({"check": "download_row_count_minimum", "analysis": label, "actual": len(source_rows), "minimum": minimum_rows})
            endpoint = download.get("endpoint")
            downloaded_on = download.get("downloadedOn")
            source_note = download.get("sourceNote")
            for row in source_rows:
                if endpoint and row.get("source_endpoint") != endpoint:
                    failures.append({"check": "download_endpoint_matches", "analysis": label})
                    break
            for row in source_rows:
                if downloaded_on and row.get("downloaded_on") != downloaded_on:
                    failures.append({"check": "download_date_matches", "analysis": label})
                    break
            for row in source_rows:
                if source_note and row.get("source_note") != source_note:
                    failures.append({"check": "download_source_note_matches", "analysis": label})
                    break
    return source_rows, summary_rows


def validate(root: Path, demo: Path) -> dict:
    path = root / demo
    failures = []
    manifest_path = path / "project_manifest.json"
    analysis_manifest_path = path / "gbd_analysis_manifest.json"
    query_path = path / "gbd_query_manifest.csv"
    registry_path = path / "claim_registry.json"

    required_files = [manifest_path, analysis_manifest_path, query_path, registry_path]
    for required in required_files:
        if not required.exists():
            failures.append({"check": "file_exists", "path": str(required.relative_to(root))})
    if failures:
        return {"ok": False, "demo": str(demo), "failures": failures}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis_manifest = json.loads(analysis_manifest_path.read_text(encoding="utf-8"))
    analyses = analysis_manifest.get("analyses", {})
    fixture_config = analyses.get("fixture")
    real_config = analyses.get("realDefault")
    if not fixture_config:
        failures.append({"check": "analysis_manifest_fixture"})
    if not real_config and manifest.get("capabilityStatus") == "minimal-demo-plus-real-default-export":
        failures.append({"check": "analysis_manifest_real_default"})
    if manifest.get("capabilityStatus") not in {"minimal-demo", "minimal-demo-plus-real-default-export"}:
        failures.append({"check": "capability_status", "actual": manifest.get("capabilityStatus")})
    if manifest.get("analysisManifest") != str(analysis_manifest_path.relative_to(root)):
        failures.append({"check": "analysis_manifest_link", "actual": manifest.get("analysisManifest")})
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

    manuscript_parts = []
    if fixture_config:
        source_rows, summary_rows = validate_analysis_config(root, fixture_config, failures, "fixture")
        measures = {row.get("measure") for row in source_rows}
        if measures != {"Deaths", "DALYs"}:
            failures.append({"check": "source_measures", "expected": ["Deaths", "DALYs"], "actual": sorted(measures)})
        if any(row.get("metric") != "Number" for row in source_rows):
            failures.append({"check": "metric_number_only"})
        if not all(row.get("fixture_note") for row in source_rows):
            failures.append({"check": "fixture_note_present"})
        deaths = find_row(source_rows, fixture_config["dimensionFilter"], fixture_config["numberMeasures"]["deaths"])
        dalys = find_row(source_rows, fixture_config["dimensionFilter"], fixture_config["numberMeasures"]["dalys"])
        if not all([deaths, dalys]):
            failures.append({"check": "fixture_required_rows_present"})
        elif summary_rows:
            death_value = Decimal(deaths["val"])
            daly_value = Decimal(dalys["val"])
            expected_ratio = (daly_value / death_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            summary = summary_rows[0]
            if Decimal(summary["deaths_number"]) != death_value:
                failures.append({"check": "deaths_match_source"})
            if Decimal(summary["dalys_number"]) != daly_value:
                failures.append({"check": "dalys_match_source"})
            if Decimal(summary["dalys_per_death"]) != expected_ratio:
                failures.append({"check": "derived_ratio", "expected": str(expected_ratio), "actual": summary["dalys_per_death"]})
            if fixture_config["interpretationBoundary"] != summary.get("interpretation_boundary", ""):
                failures.append({"check": "summary_boundary"})
        if (root / fixture_config["outputMarkdown"]).exists():
            manuscript_parts.append((root / fixture_config["outputMarkdown"]).read_text(encoding="utf-8"))

    if manifest.get("capabilityStatus") == "minimal-demo-plus-real-default-export" and real_config:
        real_rows, real_summary_rows = validate_analysis_config(root, real_config, failures, "realDefault")
        if real_rows:
            for field in ["source_endpoint", "downloaded_on", "source_note"]:
                if not all(row.get(field) for row in real_rows):
                    failures.append({"check": "real_source_metadata", "field": field})
        if real_summary_rows:
            real_summary = real_summary_rows[0]
            deaths_2023 = find_row(real_rows, real_config["dimensionFilter"], real_config["numberMeasures"]["deaths"], real_config["numberYear"])
            dalys_2023 = find_row(real_rows, real_config["dimensionFilter"], real_config["numberMeasures"]["dalys"], real_config["numberYear"])
            rate_1990 = find_row(real_rows, real_config["dimensionFilter"], real_config["rateMeasure"], real_config["rateBaselineYear"])
            rate_2023 = find_row(real_rows, real_config["dimensionFilter"], real_config["rateMeasure"], real_config["rateComparisonYear"])
            if not all([deaths_2023, dalys_2023, rate_1990, rate_2023]):
                failures.append({"check": "real_required_rows_present"})
            else:
                if Decimal(real_summary["deaths_number"]) != Decimal(deaths_2023["val"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
                    failures.append({"check": "real_deaths_match_source"})
                if Decimal(real_summary["dalys_number"]) != Decimal(dalys_2023["val"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
                    failures.append({"check": "real_dalys_match_source"})
                if real_config["interpretationBoundary"] != real_summary.get("interpretation_boundary", ""):
                    failures.append({"check": "real_summary_boundary"})
        if (root / real_config["outputMarkdown"]).exists():
            manuscript_parts.append((root / real_config["outputMarkdown"]).read_text(encoding="utf-8"))

    manuscript = "\n".join(manuscript_parts)
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
