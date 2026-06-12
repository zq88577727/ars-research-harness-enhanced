#!/usr/bin/env python3
"""Fetch a manifest-declared GBD Results Tool export into a controlled CSV."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "examples/gbd-burden-minimal-demo/gbd_analysis_manifest.json"

OUTPUT_COLUMNS = [
    "gbd_release",
    "version_id",
    "measure",
    "measure_id",
    "metric",
    "metric_id",
    "cause",
    "cause_id",
    "location",
    "location_id",
    "age",
    "age_id",
    "sex",
    "sex_id",
    "year",
    "val",
    "upper",
    "lower",
    "source_endpoint",
    "downloaded_on",
    "source_note",
]

VALUE_MAPS = {
    "measure": {1: "Deaths", 2: "DALYs"},
    "metric": {1: "Number", 2: "Percent", 3: "Rate"},
    "cause": {294: "All causes"},
    "location": {1: "Global"},
    "age": {22: "All ages"},
    "sex": {3: "Both"},
}


def path_from_root(value: str) -> Path:
    return ROOT / value


def load_analysis(manifest_path: Path, analysis: str) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analyses = manifest.get("analyses", {})
    if analysis not in analyses:
        raise KeyError(f"analysis not found in manifest: {analysis}")
    return analyses[analysis]


def id_to_name(field: str, value: object) -> str:
    try:
        key = int(value)
    except (TypeError, ValueError):
        return str(value)
    return VALUE_MAPS.get(field, {}).get(key, str(value))


def fetch_json_with_urllib(endpoint: str, timeout: int) -> dict:
    request = urllib.request.Request(endpoint, headers={"User-Agent": "ars-research-harness/gbd-fetcher"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_json_with_curl(endpoint: str, timeout: int) -> dict:
    completed = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", str(timeout), endpoint],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def fetch_json(endpoint: str, timeout: int, curl_fallback: bool) -> tuple[dict, str]:
    try:
        return fetch_json_with_urllib(endpoint, timeout), "urllib"
    except Exception:
        if not curl_fallback:
            raise
    return fetch_json_with_curl(endpoint, timeout), "curl"


def normalize_default_data(payload: dict, config: dict) -> list[dict[str, str]]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("GBD default-data payload did not contain a data array")
    cols = payload.get("cols")
    if cols is not None and not isinstance(cols, list):
        raise ValueError("GBD default-data payload cols must be a list when present")
    download = config["download"]
    endpoint = download["endpoint"]
    downloaded_on = download.get("downloadedOn") or date.today().isoformat()
    note = download.get("sourceNote", "")
    version_id = str(config.get("dimensionFilter", {}).get("version_id", ""))
    gbd_release = config.get("dimensionFilter", {}).get("gbd_release", "")
    normalized = []
    for row in rows:
        if isinstance(row, list):
            if not cols:
                raise ValueError("GBD row arrays require a cols list")
            row = dict(zip(cols, row))
        if not isinstance(row, dict):
            raise ValueError("GBD data rows must be objects or arrays with cols")
        measure_id = row.get("measure")
        metric_id = row.get("metric")
        cause_id = row.get("cause")
        location_id = row.get("location")
        age_id = row.get("age")
        sex_id = row.get("sex")
        normalized.append(
            {
                "gbd_release": gbd_release,
                "version_id": version_id,
                "measure": id_to_name("measure", measure_id),
                "measure_id": str(measure_id),
                "metric": id_to_name("metric", metric_id),
                "metric_id": str(metric_id),
                "cause": id_to_name("cause", cause_id),
                "cause_id": str(cause_id),
                "location": id_to_name("location", location_id),
                "location_id": str(location_id),
                "age": id_to_name("age", age_id),
                "age_id": str(age_id),
                "sex": id_to_name("sex", sex_id),
                "sex_id": str(sex_id),
                "year": str(row.get("year")),
                "val": str(row.get("val")),
                "upper": str(row.get("upper")),
                "lower": str(row.get("lower")),
                "source_endpoint": endpoint,
                "downloaded_on": downloaded_on,
                "source_note": note,
            }
        )
    return normalized


def write_csv_atomic(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=output_path.parent) as tmp:
        writer = csv.DictWriter(tmp, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        tmp_path = Path(tmp.name)
    tmp_path.replace(output_path)


def fetch_export(manifest_path: Path, analysis: str, output: Path | None, force: bool, dry_run: bool, timeout: int, curl_fallback: bool) -> dict:
    config = load_analysis(manifest_path, analysis)
    download = config.get("download")
    if not download:
        raise ValueError(f"analysis has no download block: {analysis}")
    if download.get("sourceType") != "gbd-default-data-json":
        raise ValueError(f"unsupported sourceType: {download.get('sourceType')}")
    output_path = output or path_from_root(config["sourceFile"])
    if output_path.exists() and not force and not dry_run:
        raise FileExistsError(f"output exists; use --force to overwrite: {output_path}")
    endpoint = download["endpoint"]
    if dry_run:
        return {
            "ok": True,
            "dryRun": True,
            "analysis": analysis,
            "endpoint": endpoint,
            "output": str(output_path),
            "wouldOverwrite": output_path.exists(),
            "overwritePolicy": download.get("overwritePolicy"),
        }
    payload, fetch_method = fetch_json(endpoint, timeout, curl_fallback)
    rows = normalize_default_data(payload, config)
    minimum = int(download.get("expectedRowCountMinimum", 1))
    if len(rows) < minimum:
        raise ValueError(f"download returned {len(rows)} rows; expected at least {minimum}")
    write_csv_atomic(rows, output_path)
    return {
        "ok": True,
        "dryRun": False,
        "analysis": analysis,
        "endpoint": endpoint,
        "output": str(output_path),
        "rowCount": len(rows),
        "downloadedOn": rows[0]["downloaded_on"] if rows else None,
        "fetchMethod": fetch_method,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--analysis", default="realDefault")
    parser.add_argument("--output")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-curl-fallback", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    try:
        result = fetch_export(
            manifest_path=Path(args.manifest),
            analysis=args.analysis,
            output=Path(args.output) if args.output else None,
            force=args.force,
            dry_run=args.dry_run,
            timeout=args.timeout,
            curl_fallback=not args.no_curl_fallback,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
