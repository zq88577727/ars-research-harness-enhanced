#!/usr/bin/env python3
"""Generate the committed GBD minimal-demo result artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/gbd-burden-minimal-demo"
ANALYSIS_MANIFEST = DEMO / "gbd_analysis_manifest.json"
QUERY_MANIFEST = DEMO / "gbd_query_manifest.csv"


def fmt_decimal(value: Decimal) -> str:
    return f"{value:,.2f}"


def display_dimension(value: str) -> str:
    replacements = {
        "All causes": "all-cause",
        "All ages": "all-age",
        "Both": "both-sexes",
        "Global": "global",
    }
    return replacements.get(value, value.lower())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def path_from_root(value: str) -> Path:
    return ROOT / value


def matches(row: dict[str, str], dimensions: dict[str, str]) -> bool:
    return all(row.get(key) == value for key, value in dimensions.items() if value)


def find_row(rows: list[dict[str, str]], dimensions: dict[str, str], measure: dict[str, str], year: str | None = None) -> dict[str, str]:
    filters = dict(dimensions)
    filters.update(measure)
    if year:
        filters["year"] = year
    for row in rows:
        if matches(row, filters):
            return row
    raise ValueError(f"GBD source row not found for filters: {filters}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_matching_rows(rows: list[dict[str, str]], dimensions: dict[str, str]) -> int:
    return sum(1 for row in rows if matches(row, dimensions))


def query_rows_for_source(query_rows: list[dict[str, str]], source_file: str) -> list[dict[str, str]]:
    return [row for row in query_rows if row.get("export_file") == source_file]


def write_provenance(manifest: dict) -> None:
    query_rows = read_csv(QUERY_MANIFEST)
    provenance = {
        "schemaVersion": "gbd-provenance-v1",
        "analysisManifest": str(ANALYSIS_MANIFEST.relative_to(ROOT)),
        "queryManifest": str(QUERY_MANIFEST.relative_to(ROOT)),
        "queryRowCount": len(query_rows),
        "analyses": {},
    }
    for label, config in manifest["analyses"].items():
        source_path = path_from_root(config["sourceFile"])
        output_csv = path_from_root(config["outputCsv"])
        output_md = path_from_root(config["outputMarkdown"])
        source_rows = read_csv(source_path)
        matching_queries = query_rows_for_source(query_rows, config["sourceFile"])
        provenance["analyses"][label] = {
            "sourceFile": config["sourceFile"],
            "sourceSha256": sha256_file(source_path),
            "sourceRowCount": len(source_rows),
            "matchingSourceRows": count_matching_rows(source_rows, config.get("dimensionFilter", {})),
            "queryRowCount": len(matching_queries),
            "queryDimensions": [
                {
                    "measure": row.get("measure", ""),
                    "metric": row.get("metric", ""),
                    "cause": row.get("cause", ""),
                    "location": row.get("location", ""),
                    "age": row.get("age", ""),
                    "sex": row.get("sex", ""),
                    "year": row.get("year", ""),
                }
                for row in matching_queries
            ],
            "outputCsv": config["outputCsv"],
            "outputCsvSha256": sha256_file(output_csv),
            "outputMarkdown": config["outputMarkdown"],
            "outputMarkdownSha256": sha256_file(output_md),
            "downloadSourceType": config.get("download", {}).get("sourceType", "local-fixture"),
            "sourceEndpoint": config.get("download", {}).get("endpoint", ""),
            "downloadedOn": config.get("download", {}).get("downloadedOn", ""),
            "interpretationBoundary": config["interpretationBoundary"],
        }
    output = path_from_root(manifest["provenanceFile"])
    output.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_fixture_summary(config: dict) -> None:
    rows = read_csv(path_from_root(config["sourceFile"]))
    dimensions = config["dimensionFilter"]
    measures = config["numberMeasures"]
    deaths = find_row(rows, dimensions, measures["deaths"])
    dalys = find_row(rows, dimensions, measures["dalys"])
    death_value = Decimal(deaths["val"])
    daly_value = Decimal(dalys["val"])
    ratio = (daly_value / death_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    out_csv = path_from_root(config["outputCsv"])
    out_md = path_from_root(config["outputMarkdown"])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gbd_release",
                "cause",
                "location",
                "age",
                "sex",
                "year",
                "deaths_number",
                "dalys_number",
                "dalys_per_death",
                "interpretation_boundary",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "gbd_release": deaths["gbd_release"],
                "cause": deaths["cause"],
                "location": deaths["location"],
                "age": deaths["age"],
                "sex": deaths["sex"],
                "year": deaths["year"],
                "deaths_number": f"{death_value:.2f}",
                "dalys_number": f"{daly_value:.2f}",
                "dalys_per_death": f"{ratio:.2f}",
                "interpretation_boundary": config["interpretationBoundary"],
            }
        )

    out_md.write_text(
        "\n".join(
            [
                "# GBD Minimal Result Summary",
                "",
                f"In the minimal GBD Results-style teaching fixture, the {display_dimension(deaths['location'])} {display_dimension(deaths['cause'])} {deaths['year']}",
                f"number rows contained {fmt_decimal(death_value)} deaths and {fmt_decimal(daly_value)} DALYs, yielding",
                f"{ratio:.2f} DALYs per death as a derived traceability check.",
                "",
                "This result is a workflow fixture, not a publishable disease-burden estimate.",
                "A real GBD manuscript must replace the fixture with an approved export, retain",
                "release version and query dimensions, cite IHME/GHDx appropriately, and",
                "interpret uncertainty intervals, metric type, age-standardization status, cause,",
                "location, age, sex, and year without mixing counts, rates, and percentages.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_real_default_summary(config: dict) -> None:
    source_path = path_from_root(config["sourceFile"])
    if not source_path.exists():
        return
    real_rows = read_csv(source_path)
    dimensions = config["dimensionFilter"]
    measures = config["numberMeasures"]
    death_number = find_row(real_rows, dimensions, measures["deaths"], config["numberYear"])
    daly_number = find_row(real_rows, dimensions, measures["dalys"], config["numberYear"])
    death_rate_1990 = find_row(real_rows, dimensions, config["rateMeasure"], config["rateBaselineYear"])
    death_rate_2023 = find_row(real_rows, dimensions, config["rateMeasure"], config["rateComparisonYear"])
    d2023 = Decimal(death_number["val"])
    y2023 = Decimal(daly_number["val"])
    rate1990 = Decimal(death_rate_1990["val"])
    rate2023 = Decimal(death_rate_2023["val"])
    rate_change = ((rate2023 - rate1990) / rate1990 * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    real_ratio = (y2023 / d2023).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    out_csv = path_from_root(config["outputCsv"])
    out_md = path_from_root(config["outputMarkdown"])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gbd_release",
                "version_id",
                "cause",
                "location",
                "age",
                "sex",
                "year",
                "deaths_number",
                "deaths_lower",
                "deaths_upper",
                "dalys_number",
                "dalys_lower",
                "dalys_upper",
                "dalys_per_death",
                "death_rate_1990",
                "death_rate_1990_lower",
                "death_rate_1990_upper",
                "death_rate_2023",
                "death_rate_2023_lower",
                "death_rate_2023_upper",
                "death_rate_percent_change_1990_2023",
                "source_endpoint",
                "interpretation_boundary",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "gbd_release": death_number["gbd_release"],
                "version_id": death_number["version_id"],
                "cause": death_number["cause"],
                "location": death_number["location"],
                "age": death_number["age"],
                "sex": death_number["sex"],
                "year": death_number["year"],
                "deaths_number": f"{d2023:.2f}",
                "deaths_lower": f"{Decimal(death_number['lower']):.2f}",
                "deaths_upper": f"{Decimal(death_number['upper']):.2f}",
                "dalys_number": f"{y2023:.2f}",
                "dalys_lower": f"{Decimal(daly_number['lower']):.2f}",
                "dalys_upper": f"{Decimal(daly_number['upper']):.2f}",
                "dalys_per_death": f"{real_ratio:.2f}",
                "death_rate_1990": f"{rate1990:.8f}",
                "death_rate_1990_lower": f"{Decimal(death_rate_1990['lower']):.8f}",
                "death_rate_1990_upper": f"{Decimal(death_rate_1990['upper']):.8f}",
                "death_rate_2023": f"{rate2023:.8f}",
                "death_rate_2023_lower": f"{Decimal(death_rate_2023['lower']):.8f}",
                "death_rate_2023_upper": f"{Decimal(death_rate_2023['upper']):.8f}",
                "death_rate_percent_change_1990_2023": f"{rate_change:.2f}",
                "source_endpoint": death_number["source_endpoint"],
                "interpretation_boundary": config["interpretationBoundary"],
            }
        )
    out_md.write_text(
        "\n".join(
            [
                "# GBD Real Default Data Summary",
                "",
                "Using the GBD Results Tool public default data endpoint for GBD 2023",
                f"(version_id {death_number['version_id']}), the {display_dimension(death_number['location'])} {display_dimension(death_number['cause'])}",
                f"{display_dimension(death_number['age'])} {display_dimension(death_number['sex'])} {death_number['year']} number rows contained",
                f"{fmt_decimal(d2023)} deaths (UI {fmt_decimal(Decimal(death_number['lower']))}-{fmt_decimal(Decimal(death_number['upper']))})",
                f"and {fmt_decimal(y2023)} DALYs (UI {fmt_decimal(Decimal(daly_number['lower']))}-{fmt_decimal(Decimal(daly_number['upper']))}), yielding",
                f"{real_ratio:.2f} DALYs per death as a derived traceability check.",
                "",
                f"The {display_dimension(death_rate_2023['location'])} {display_dimension(death_rate_2023['cause'])} death rate in this endpoint changed from",
                f"{rate1990:.8f} (UI {Decimal(death_rate_1990['lower']):.8f}-{Decimal(death_rate_1990['upper']):.8f}) in {config['rateBaselineYear']} to",
                f"{rate2023:.8f} (UI {Decimal(death_rate_2023['lower']):.8f}-{Decimal(death_rate_2023['upper']):.8f}) in {config['rateComparisonYear']},",
                f"a {rate_change:.2f}% relative change in the endpoint's rate scale.",
                "",
                "This is a real GBD Results Tool endpoint output used for workflow demonstration.",
                "A submission-ready GBD manuscript still requires source citation, documented query",
                "dimensions, uncertainty interpretation, and confirmation that downloaded data may",
                "be reused under IHME/GHDx terms.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    manifest = json.loads(ANALYSIS_MANIFEST.read_text(encoding="utf-8"))
    analyses = manifest["analyses"]
    write_fixture_summary(analyses["fixture"])
    write_real_default_summary(analyses["realDefault"])
    write_provenance(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
