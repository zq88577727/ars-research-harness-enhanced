#!/usr/bin/env python3
"""Generate source-backed outputs for a targeted GBD scaffold."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def path_from_root(value: str) -> Path:
    return ROOT / value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decimal_text(value: Decimal, places: str = "0.01") -> str:
    return f"{value.quantize(Decimal(places), rounding=ROUND_HALF_UP):f}"


def display_number(value: Decimal) -> str:
    return f"{value:,.2f}"


def display_rate(value: Decimal) -> str:
    return f"{value:.2f}"


def normalized_measure(value: str) -> str:
    if value.startswith("DALYs"):
        return "DALYs"
    return value


MEASURE_BY_ID = {"1": "Deaths", "2": "DALYs"}
METRIC_BY_ID = {"1": "Number", "2": "Percent", "3": "Rate"}
LOCATION_BY_ID = {"1": "Global", "6": "China"}
AGE_BY_ID = {"22": "All ages", "27": "Age-standardized"}
SEX_BY_ID = {"3": "Both"}
CAUSE_BY_ID = {"491": "Cardiovascular diseases"}

ZH_VALUE_MAP = {
    "死亡": "Deaths",
    "伤残调整生命年": "DALYs",
    "數量": "Number",
    "数量": "Number",
    "率": "Rate",
    "百分比": "Percent",
    "全球": "Global",
    "中國": "China",
    "中国": "China",
    "全部": "All ages",
    "年龄标准化": "Age-standardized",
    "年齡標準化": "Age-standardized",
    "合计": "Both",
    "合計": "Both",
    "心血管疾病": "Cardiovascular diseases",
}


def pick(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def normalize_value(value: str, id_value: str = "", id_map: dict[str, str] | None = None) -> str:
    if value in ZH_VALUE_MAP:
        return ZH_VALUE_MAP[value]
    if id_map and id_value in id_map:
        return id_map[id_value]
    return value


def normalize_row(row: dict[str, str], defaults: dict[str, str]) -> dict[str, str]:
    updated = dict(row)
    updated["gbd_release"] = pick(row, "gbd_release") or defaults.get("gbd_release", "")
    updated["version_id"] = pick(row, "version_id") or defaults.get("version_id", "")
    updated["measure"] = normalized_measure(normalize_value(pick(row, "measure", "measure_name"), pick(row, "measure_id"), MEASURE_BY_ID))
    updated["metric"] = normalize_value(pick(row, "metric", "metric_name"), pick(row, "metric_id"), METRIC_BY_ID)
    updated["cause"] = normalize_value(pick(row, "cause", "cause_name"), pick(row, "cause_id"), CAUSE_BY_ID)
    updated["location"] = normalize_value(pick(row, "location", "location_name"), pick(row, "location_id"), LOCATION_BY_ID)
    updated["age"] = normalize_value(pick(row, "age", "age_name"), pick(row, "age_id"), AGE_BY_ID)
    updated["sex"] = normalize_value(pick(row, "sex", "sex_name"), pick(row, "sex_id"), SEX_BY_ID)
    updated["year"] = pick(row, "year", "year_id")
    return updated


def matches(row: dict[str, str], filters: dict[str, str]) -> bool:
    return all(str(row.get(key, "")) == str(value) for key, value in filters.items() if value)


def find_row(rows: list[dict[str, str]], **filters: str) -> dict[str, str]:
    for row in rows:
        if matches(row, filters):
            return row
    raise ValueError(f"GBD source row not found for filters: {filters}")


def percent_change(start: Decimal, end: Decimal) -> Decimal:
    return ((end - start) / start * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_source_rows(source_rows: list[dict[str, str]], query_rows: list[dict[str, str]], required_columns: list[str]) -> list[dict]:
    failures: list[dict] = []
    if not source_rows:
        failures.append({"check": "source_rows_present"})
        return failures
    missing_columns = sorted(set(required_columns) - set(source_rows[0]))
    if missing_columns:
        failures.append({"check": "source_required_columns", "missing": missing_columns})
        return failures
    for row in source_rows:
        for field in ["val", "lower", "upper"]:
            try:
                Decimal(row[field])
            except Exception:
                failures.append({"check": "source_numeric_field", "field": field, "row": row})
    for query in query_rows:
        filters = {
            "gbd_release": query["gbd_release"],
            "measure": normalized_measure(query["measure"]),
            "metric": query["metric"],
            "cause": query["cause"],
            "location": query["location"],
            "age": query["age"],
            "sex": query["sex"],
            "year": query["year"],
        }
        if not any(matches(row, filters) for row in source_rows):
            failures.append({"check": "query_row_matches_source", "filters": filters})
    return failures


def build_summary_rows(rows: list[dict[str, str]], config: dict) -> list[dict[str, str]]:
    out_rows = []
    base = config["dimensionFilter"]
    for location in config["locations"]:
        deaths_1990 = find_row(
            rows,
            **base,
            location=location,
            age=config["countAge"],
            measure="Deaths",
            metric="Number",
            year="1990",
        )
        deaths_2023 = find_row(
            rows,
            **base,
            location=location,
            age=config["countAge"],
            measure="Deaths",
            metric="Number",
            year="2023",
        )
        dalys_1990 = find_row(
            rows,
            **base,
            location=location,
            age=config["countAge"],
            measure="DALYs",
            metric="Number",
            year="1990",
        )
        dalys_2023 = find_row(
            rows,
            **base,
            location=location,
            age=config["countAge"],
            measure="DALYs",
            metric="Number",
            year="2023",
        )
        death_rate_1990 = find_row(
            rows,
            **base,
            location=location,
            age=config["rateAge"],
            measure="Deaths",
            metric="Rate",
            year="1990",
        )
        death_rate_2023 = find_row(
            rows,
            **base,
            location=location,
            age=config["rateAge"],
            measure="Deaths",
            metric="Rate",
            year="2023",
        )
        daly_rate_1990 = find_row(
            rows,
            **base,
            location=location,
            age=config["rateAge"],
            measure="DALYs",
            metric="Rate",
            year="1990",
        )
        daly_rate_2023 = find_row(
            rows,
            **base,
            location=location,
            age=config["rateAge"],
            measure="DALYs",
            metric="Rate",
            year="2023",
        )
        out_rows.append(
            {
                "gbd_release": deaths_2023["gbd_release"],
                "version_id": deaths_2023["version_id"],
                "cause": deaths_2023["cause"],
                "location": location,
                "sex": deaths_2023["sex"],
                "count_age": config["countAge"],
                "rate_age": config["rateAge"],
                "deaths_1990": decimal_text(Decimal(deaths_1990["val"])),
                "deaths_1990_lower": decimal_text(Decimal(deaths_1990["lower"])),
                "deaths_1990_upper": decimal_text(Decimal(deaths_1990["upper"])),
                "deaths_2023": decimal_text(Decimal(deaths_2023["val"])),
                "deaths_2023_lower": decimal_text(Decimal(deaths_2023["lower"])),
                "deaths_2023_upper": decimal_text(Decimal(deaths_2023["upper"])),
                "deaths_percent_change_1990_2023": decimal_text(percent_change(Decimal(deaths_1990["val"]), Decimal(deaths_2023["val"]))),
                "dalys_1990": decimal_text(Decimal(dalys_1990["val"])),
                "dalys_1990_lower": decimal_text(Decimal(dalys_1990["lower"])),
                "dalys_1990_upper": decimal_text(Decimal(dalys_1990["upper"])),
                "dalys_2023": decimal_text(Decimal(dalys_2023["val"])),
                "dalys_2023_lower": decimal_text(Decimal(dalys_2023["lower"])),
                "dalys_2023_upper": decimal_text(Decimal(dalys_2023["upper"])),
                "dalys_percent_change_1990_2023": decimal_text(percent_change(Decimal(dalys_1990["val"]), Decimal(dalys_2023["val"]))),
                "death_rate_1990": decimal_text(Decimal(death_rate_1990["val"])),
                "death_rate_1990_lower": decimal_text(Decimal(death_rate_1990["lower"])),
                "death_rate_1990_upper": decimal_text(Decimal(death_rate_1990["upper"])),
                "death_rate_2023": decimal_text(Decimal(death_rate_2023["val"])),
                "death_rate_2023_lower": decimal_text(Decimal(death_rate_2023["lower"])),
                "death_rate_2023_upper": decimal_text(Decimal(death_rate_2023["upper"])),
                "death_rate_percent_change_1990_2023": decimal_text(percent_change(Decimal(death_rate_1990["val"]), Decimal(death_rate_2023["val"]))),
                "daly_rate_1990": decimal_text(Decimal(daly_rate_1990["val"])),
                "daly_rate_1990_lower": decimal_text(Decimal(daly_rate_1990["lower"])),
                "daly_rate_1990_upper": decimal_text(Decimal(daly_rate_1990["upper"])),
                "daly_rate_2023": decimal_text(Decimal(daly_rate_2023["val"])),
                "daly_rate_2023_lower": decimal_text(Decimal(daly_rate_2023["lower"])),
                "daly_rate_2023_upper": decimal_text(Decimal(daly_rate_2023["upper"])),
                "daly_rate_percent_change_1990_2023": decimal_text(percent_change(Decimal(daly_rate_1990["val"]), Decimal(daly_rate_2023["val"]))),
                "interpretation_boundary": config["interpretationBoundary"],
            }
        )
    return out_rows


def write_summary_markdown(path: Path, summary_rows: list[dict[str, str]], config: dict) -> None:
    by_location = {row["location"]: row for row in summary_rows}
    china = by_location["China"]
    global_row = by_location["Global"]
    lines = [
        "# GBD CVD China-Global Summary",
        "",
        "Using the targeted GBD 2023 export, cardiovascular disease burden was summarized for China and the global population in 1990 and 2023.",
        "",
        f"In China, all-age CVD deaths changed from {display_number(Decimal(china['deaths_1990']))} (UI {display_number(Decimal(china['deaths_1990_lower']))}-{display_number(Decimal(china['deaths_1990_upper']))}) in 1990 to {display_number(Decimal(china['deaths_2023']))} (UI {display_number(Decimal(china['deaths_2023_lower']))}-{display_number(Decimal(china['deaths_2023_upper']))}) in 2023, while all-age CVD DALYs changed from {display_number(Decimal(china['dalys_1990']))} (UI {display_number(Decimal(china['dalys_1990_lower']))}-{display_number(Decimal(china['dalys_1990_upper']))}) to {display_number(Decimal(china['dalys_2023']))} (UI {display_number(Decimal(china['dalys_2023_lower']))}-{display_number(Decimal(china['dalys_2023_upper']))}).",
        f"The age-standardized CVD death rate in China changed from {display_rate(Decimal(china['death_rate_1990']))} (UI {display_rate(Decimal(china['death_rate_1990_lower']))}-{display_rate(Decimal(china['death_rate_1990_upper']))}) to {display_rate(Decimal(china['death_rate_2023']))} (UI {display_rate(Decimal(china['death_rate_2023_lower']))}-{display_rate(Decimal(china['death_rate_2023_upper']))}), and the age-standardized CVD DALY rate changed from {display_rate(Decimal(china['daly_rate_1990']))} (UI {display_rate(Decimal(china['daly_rate_1990_lower']))}-{display_rate(Decimal(china['daly_rate_1990_upper']))}) to {display_rate(Decimal(china['daly_rate_2023']))} (UI {display_rate(Decimal(china['daly_rate_2023_lower']))}-{display_rate(Decimal(china['daly_rate_2023_upper']))}).",
        "",
        f"Globally, all-age CVD deaths changed from {display_number(Decimal(global_row['deaths_1990']))} (UI {display_number(Decimal(global_row['deaths_1990_lower']))}-{display_number(Decimal(global_row['deaths_1990_upper']))}) in 1990 to {display_number(Decimal(global_row['deaths_2023']))} (UI {display_number(Decimal(global_row['deaths_2023_lower']))}-{display_number(Decimal(global_row['deaths_2023_upper']))}) in 2023, while all-age CVD DALYs changed from {display_number(Decimal(global_row['dalys_1990']))} (UI {display_number(Decimal(global_row['dalys_1990_lower']))}-{display_number(Decimal(global_row['dalys_1990_upper']))}) to {display_number(Decimal(global_row['dalys_2023']))} (UI {display_number(Decimal(global_row['dalys_2023_lower']))}-{display_number(Decimal(global_row['dalys_2023_upper']))}).",
        f"The global age-standardized CVD death rate changed from {display_rate(Decimal(global_row['death_rate_1990']))} (UI {display_rate(Decimal(global_row['death_rate_1990_lower']))}-{display_rate(Decimal(global_row['death_rate_1990_upper']))}) to {display_rate(Decimal(global_row['death_rate_2023']))} (UI {display_rate(Decimal(global_row['death_rate_2023_lower']))}-{display_rate(Decimal(global_row['death_rate_2023_upper']))}), and the global age-standardized CVD DALY rate changed from {display_rate(Decimal(global_row['daly_rate_1990']))} (UI {display_rate(Decimal(global_row['daly_rate_1990_lower']))}-{display_rate(Decimal(global_row['daly_rate_1990_upper']))}) to {display_rate(Decimal(global_row['daly_rate_2023']))} (UI {display_rate(Decimal(global_row['daly_rate_2023_lower']))}-{display_rate(Decimal(global_row['daly_rate_2023_upper']))}).",
        "",
        config["interpretationBoundary"],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_provenance(project: Path, manifest_path: Path, manifest: dict, config: dict, query_rows: list[dict[str, str]]) -> dict:
    source_path = path_from_root(config["sourceFile"])
    citation_path = path_from_root(config["sourceCitationFile"]) if config.get("sourceCitationFile") else None
    output_csv = path_from_root(config["outputCsv"])
    output_md = path_from_root(config["outputMarkdown"])
    claim_registry_output = path_from_root(config["claimRegistryOutput"])
    return {
        "schemaVersion": "gbd-provenance-v1",
        "project": str(project.relative_to(ROOT)),
        "analysisManifest": str(manifest_path.relative_to(ROOT)),
        "queryManifest": manifest["queryManifest"],
        "queryRowCount": len(query_rows),
        "analyses": {
            "cvdChinaGlobal": {
                "sourceFile": config["sourceFile"],
                "sourceSha256": sha256_file(source_path),
                "sourceRowCount": len(read_csv(source_path)),
                "sourceCitationFile": config.get("sourceCitationFile", ""),
                "sourceCitationSha256": sha256_file(citation_path) if citation_path and citation_path.exists() else "",
                "queryRowCount": len(query_rows),
                "queryDimensions": [
                    {
                        "measure": row["measure"],
                        "metric": row["metric"],
                        "cause": row["cause"],
                        "location": row["location"],
                        "age": row["age"],
                        "sex": row["sex"],
                        "year": row["year"],
                    }
                    for row in query_rows
                ],
                "outputCsv": config["outputCsv"],
                "outputCsvSha256": sha256_file(output_csv),
                "outputMarkdown": config["outputMarkdown"],
                "outputMarkdownSha256": sha256_file(output_md),
                "claimRegistryOutput": config["claimRegistryOutput"],
                "claimRegistryOutputSha256": sha256_file(claim_registry_output),
                "downloadSourceType": "manual-gbd-results-tool-export",
                "interpretationBoundary": config["interpretationBoundary"],
            }
        },
    }


def upgrade_claim_registry(project: Path, config: dict, summary_rows: list[dict[str, str]]) -> dict:
    registry_path = project / "claim_registry.json"
    registry = load_json(registry_path)
    by_location = {row["location"]: row for row in summary_rows}
    china = by_location["China"]
    global_row = by_location["Global"]
    replacements = {
        "gbd-cvd-deaths-count-change-china": (
            f"All-age CVD deaths in China changed from {display_number(Decimal(china['deaths_1990']))} "
            f"(UI {display_number(Decimal(china['deaths_1990_lower']))}-{display_number(Decimal(china['deaths_1990_upper']))}) in 1990 "
            f"to {display_number(Decimal(china['deaths_2023']))} in 2023 "
            f"(UI {display_number(Decimal(china['deaths_2023_lower']))}-{display_number(Decimal(china['deaths_2023_upper']))})."
        ),
        "gbd-cvd-dalys-count-change-china": (
            f"All-age CVD DALYs in China changed from {display_number(Decimal(china['dalys_1990']))} "
            f"(UI {display_number(Decimal(china['dalys_1990_lower']))}-{display_number(Decimal(china['dalys_1990_upper']))}) in 1990 "
            f"to {display_number(Decimal(china['dalys_2023']))} in 2023 "
            f"(UI {display_number(Decimal(china['dalys_2023_lower']))}-{display_number(Decimal(china['dalys_2023_upper']))})."
        ),
        "gbd-cvd-death-rate-comparison-china-global": (
            f"The age-standardized CVD death rate changed from {display_rate(Decimal(china['death_rate_1990']))} "
            f"(UI {display_rate(Decimal(china['death_rate_1990_lower']))}-{display_rate(Decimal(china['death_rate_1990_upper']))}) "
            f"to {display_rate(Decimal(china['death_rate_2023']))} "
            f"(UI {display_rate(Decimal(china['death_rate_2023_lower']))}-{display_rate(Decimal(china['death_rate_2023_upper']))}) in China and from "
            f"{display_rate(Decimal(global_row['death_rate_1990']))} "
            f"(UI {display_rate(Decimal(global_row['death_rate_1990_lower']))}-{display_rate(Decimal(global_row['death_rate_1990_upper']))}) "
            f"to {display_rate(Decimal(global_row['death_rate_2023']))} "
            f"(UI {display_rate(Decimal(global_row['death_rate_2023_lower']))}-{display_rate(Decimal(global_row['death_rate_2023_upper']))}) globally."
        ),
        "gbd-cvd-daly-rate-comparison-china-global": (
            f"The age-standardized CVD DALY rate changed from {display_rate(Decimal(china['daly_rate_1990']))} "
            f"(UI {display_rate(Decimal(china['daly_rate_1990_lower']))}-{display_rate(Decimal(china['daly_rate_1990_upper']))}) "
            f"to {display_rate(Decimal(china['daly_rate_2023']))} "
            f"(UI {display_rate(Decimal(china['daly_rate_2023_lower']))}-{display_rate(Decimal(china['daly_rate_2023_upper']))}) in China and from "
            f"{display_rate(Decimal(global_row['daly_rate_1990']))} "
            f"(UI {display_rate(Decimal(global_row['daly_rate_1990_lower']))}-{display_rate(Decimal(global_row['daly_rate_1990_upper']))}) "
            f"to {display_rate(Decimal(global_row['daly_rate_2023']))} "
            f"(UI {display_rate(Decimal(global_row['daly_rate_2023_lower']))}-{display_rate(Decimal(global_row['daly_rate_2023_upper']))}) globally."
        ),
    }
    for claim in registry.get("claims", []):
        if claim.get("id") in replacements:
            claim["submissionDisposition"] = "candidate-manuscript-claim"
            claim["claimRole"] = "source-backed-candidate-result"
            claim["expectedText"] = replacements[claim["id"]]
            claim["sourceFile"] = config["outputCsv"]
            claim["sourceFields"] = ["location", "measure", "metric", "count_age", "rate_age", "1990", "2023", "val", "lower", "upper"]
            claim["interpretationBoundary"] = "Source-backed descriptive GBD candidate claim; final citation, reuse, journal wording, and strict submission gate still required."
    return registry


def generate(project: Path, update_registry: bool, dry_run: bool) -> dict:
    manifest_path = project / "gbd_cvd_analysis_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "status": "missing-analysis-manifest", "failures": [{"check": "analysis_manifest_exists"}]}
    manifest = load_json(manifest_path)
    config = manifest["analyses"]["cvdChinaGlobal"]
    source_path = path_from_root(config["sourceFile"])
    query_path = path_from_root(manifest["queryManifest"])
    if not source_path.exists():
        return {
            "ok": True,
            "status": "awaiting-source-export",
            "sourceFile": config["sourceFile"],
            "message": "Place the matching GBD Results Tool CSV at sourceFile, then rerun without --dry-run.",
        }
    query_rows = read_csv(query_path)
    source_rows = [normalize_row(row, config["dimensionFilter"]) for row in read_csv(source_path)]
    failures = validate_source_rows(source_rows, query_rows, config["requiredColumns"])
    if failures:
        return {"ok": False, "status": "source-export-invalid", "sourceFile": config["sourceFile"], "failures": failures}
    summary_rows = build_summary_rows(source_rows, config)
    if dry_run:
        return {
            "ok": True,
            "status": "source-export-valid-dry-run",
            "sourceFile": config["sourceFile"],
            "queryRowCount": len(query_rows),
            "sourceRowCount": len(source_rows),
            "summaryRowCount": len(summary_rows),
        }

    output_csv = path_from_root(config["outputCsv"])
    output_md = path_from_root(config["outputMarkdown"])
    claim_registry_output = path_from_root(config["claimRegistryOutput"])
    write_csv(output_csv, summary_rows, list(summary_rows[0]))
    write_summary_markdown(output_md, summary_rows, config)
    upgraded_registry = upgrade_claim_registry(project, config, summary_rows)
    write_json(claim_registry_output, upgraded_registry)
    if update_registry:
        shutil.copyfile(claim_registry_output, project / "claim_registry.json")
    provenance = build_provenance(project, manifest_path, manifest, config, query_rows)
    provenance_path = path_from_root(manifest["provenanceFile"])
    write_json(provenance_path, provenance)
    return {
        "ok": True,
        "status": "source-backed-results-generated",
        "sourceFile": config["sourceFile"],
        "outputCsv": config["outputCsv"],
        "outputMarkdown": config["outputMarkdown"],
        "provenanceFile": manifest["provenanceFile"],
        "claimRegistryOutput": config["claimRegistryOutput"],
        "claimRegistryUpdated": update_registry,
        "queryRowCount": len(query_rows),
        "sourceRowCount": len(source_rows),
        "summaryRowCount": len(summary_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=str(DEFAULT_PROJECT.relative_to(ROOT)))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update-registry", action="store_true")
    args = parser.parse_args()
    result = generate(ROOT / args.project, args.update_registry, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
