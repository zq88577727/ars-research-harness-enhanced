#!/usr/bin/env python3
"""Import local CHARLS codebook metadata into the codebook extract schema.

The importer accepts narrow, variable-level codebook tables. It rejects likely
respondent-level wide data and never reads or writes restricted raw data files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_COLUMNS = [
    "source_wave",
    "file_label",
    "module",
    "source_variable",
    "variable_label",
    "construct_keywords",
    "measurement_domain",
    "measurement_type",
    "wave_role",
    "eligible_roles",
    "notes",
]
SYNONYMS = {
    "source_wave": ["source_wave", "wave", "waves", "year", "survey_wave", "charls_wave"],
    "file_label": ["file_label", "file", "dataset", "data_file", "table", "source_file"],
    "module": ["module", "section", "questionnaire_module", "instrument", "category"],
    "source_variable": ["source_variable", "variable", "variable_name", "varname", "var", "name", "item", "code"],
    "variable_label": ["variable_label", "label", "question", "question_text", "description", "desc", "title"],
    "construct_keywords": ["construct_keywords", "keywords", "construct", "concept", "topic"],
    "measurement_domain": ["measurement_domain", "domain", "measurement_area", "variable_domain"],
    "measurement_type": ["measurement_type", "type", "data_type", "value_type", "format"],
    "wave_role": ["wave_role", "time_role", "temporal_role"],
    "eligible_roles": ["eligible_roles", "role", "analysis_role", "roles"],
    "notes": ["notes", "note", "remarks", "comment", "comments"],
}
PLACEHOLDER = "TBD"
RAW_DATA_HEADER_PATTERNS = [
    r"^respondent[_-]?id$",
    r"^household[_-]?id$",
    r"^person[_-]?id$",
    r"^community[_-]?id$",
    r"^name$",
    r"^address$",
    r"^phone",
    r"^mobile",
    r"^email$",
    r"^latitude$",
    r"^longitude$",
    r"^gps",
]


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", (value or "").strip().lower()).strip("_")


def read_csv_like(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    suffix = path.suffix.lower()
    delimiter = "\t" if suffix == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = [{key: value for key, value in row.items()} for row in reader]
        return rows, reader.fieldnames or []


def read_xlsx(path: Path, sheet: str | None) -> tuple[list[dict[str, str]], list[str]]:
    try:
        import pandas as pd
    except Exception as exc:  # pragma: no cover - depends on local optional deps
        raise RuntimeError("XLSX import requires pandas with an Excel engine installed.") from exc
    frame = pd.read_excel(path, sheet_name=sheet or 0, dtype=str).fillna("")
    return frame.to_dict(orient="records"), [str(column) for column in frame.columns]


def read_table(path: Path, sheet: str | None) -> tuple[list[dict[str, str]], list[str]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        return read_csv_like(path)
    if suffix in {".xlsx", ".xls"}:
        return read_xlsx(path, sheet)
    raise ValueError(f"unsupported codebook input extension: {suffix}")


def project_path(value: str, project_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.exists() or value.startswith(("data/", "examples/", "harness/", "data_sources/")):
        return root_relative
    return project_dir / path


def load_column_map(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {key: value for key, value in data.items() if key in OUTPUT_COLUMNS}


def infer_column_map(headers: list[str], explicit: dict[str, str]) -> dict[str, str]:
    normalized = {normalize_header(header): header for header in headers}
    mapping: dict[str, str] = {}
    for target, explicit_source in explicit.items():
        if explicit_source in headers:
            mapping[target] = explicit_source
        elif normalize_header(explicit_source) in normalized:
            mapping[target] = normalized[normalize_header(explicit_source)]
    for target, names in SYNONYMS.items():
        if target in mapping:
            continue
        for name in names:
            if normalize_header(name) in normalized:
                mapping[target] = normalized[normalize_header(name)]
                break
    return mapping


def looks_like_raw_data(headers: list[str], mapping: dict[str, str]) -> bool:
    normalized = [normalize_header(header) for header in headers]
    direct_identifier_headers = [
        header
        for header in normalized
        if any(re.search(pattern, header) for pattern in RAW_DATA_HEADER_PATTERNS)
    ]
    has_codebook_core = "source_variable" in mapping and "variable_label" in mapping
    return bool(direct_identifier_headers) and not has_codebook_core


def infer_domain(text: str) -> str:
    value = text.lower()
    if any(term in value for term in ["id", "respondent", "person identifier"]):
        return "linkage"
    if any(term in value for term in ["age", "sex", "gender", "education", "marital", "residence"]):
        return "demographic"
    if any(term in value for term in ["weight", "sampling", "sample weight"]):
        return "design"
    if any(term in value for term in ["follow", "attrition", "interview status", "loss"]):
        return "missingness"
    if any(term in value for term in ["blood", "biomarker", "height", "weight", "waist", "grip"]):
        return "biomarker_or_exam"
    if any(term in value for term in ["disease", "diagnosis", "health", "function", "cognition", "depression"]):
        return "health"
    return PLACEHOLDER


def infer_measurement_type(text: str) -> str:
    value = text.lower()
    if any(term in value for term in ["id", "identifier"]):
        return "identifier"
    if any(term in value for term in ["weight", "sampling weight"]):
        return "weight"
    if any(term in value for term in ["yes/no", "binary", "status", "indicator"]):
        return "binary"
    if any(term in value for term in ["category", "categorical", "sex", "gender"]):
        return "categorical"
    if any(term in value for term in ["score", "scale", "index"]):
        return "score"
    if any(term in value for term in ["age", "year", "height", "weight", "waist", "blood", "value"]):
        return "continuous"
    return "mixed"


def infer_wave_role(source_wave: str, text: str, default_wave_role: str) -> str:
    value = f"{source_wave} {text}".lower()
    if "follow" in value or "wave2" in value or "2013" in value:
        return "followup"
    if "baseline" in value or "wave1" in value or "2011" in value:
        return "baseline"
    return default_wave_role


def infer_eligible_roles(domain: str, measurement_type: str, text: str) -> str:
    value = text.lower()
    if domain == "linkage":
        return "id"
    if domain == "design" or measurement_type == "weight":
        return "weight"
    if domain == "missingness":
        return "missingness"
    if any(term in value for term in ["outcome", "disease", "diagnosis", "function", "cognition", "depression"]):
        return "outcome;covariate"
    if any(term in value for term in ["exposure", "behavior", "smoking", "activity", "income", "education"]):
        return "exposure;covariate"
    return "covariate"


def keywords(source_variable: str, label: str, existing: str) -> str:
    if existing.strip():
        return existing.strip()
    tokens = [
        token
        for token in re.split(r"[^A-Za-z0-9_]+", f"{source_variable} {label}".lower())
        if len(token) >= 3 and token not in {"the", "and", "for", "with", "charls"}
    ]
    return ";".join(dict.fromkeys(tokens[:6])) or PLACEHOLDER


def transform_rows(rows: list[dict[str, str]], mapping: dict[str, str], defaults: dict[str, str]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        source_variable = (row.get(mapping.get("source_variable", ""), "") or "").strip()
        variable_label = (row.get(mapping.get("variable_label", ""), "") or "").strip()
        if not source_variable and not variable_label:
            continue
        source_wave = (row.get(mapping.get("source_wave", ""), "") or defaults["source_wave"]).strip()
        file_label = (row.get(mapping.get("file_label", ""), "") or defaults["file_label"]).strip()
        module = (row.get(mapping.get("module", ""), "") or defaults["module"]).strip()
        text = f"{source_variable} {variable_label} {module}"
        domain = (row.get(mapping.get("measurement_domain", ""), "") or infer_domain(text)).strip()
        measurement_type = (row.get(mapping.get("measurement_type", ""), "") or infer_measurement_type(text)).strip()
        wave_role = (row.get(mapping.get("wave_role", ""), "") or infer_wave_role(source_wave, text, defaults["wave_role"])).strip()
        eligible_roles = (row.get(mapping.get("eligible_roles", ""), "") or infer_eligible_roles(domain, measurement_type, text)).strip()
        output.append(
            {
                "source_wave": source_wave,
                "file_label": file_label,
                "module": module,
                "source_variable": source_variable or PLACEHOLDER,
                "variable_label": variable_label or PLACEHOLDER,
                "construct_keywords": keywords(source_variable, variable_label, row.get(mapping.get("construct_keywords", ""), "")),
                "measurement_domain": domain,
                "measurement_type": measurement_type,
                "wave_role": wave_role,
                "eligible_roles": eligible_roles,
                "notes": (row.get(mapping.get("notes", ""), "") or "Imported from local CHARLS codebook metadata; verify against official documentation before mapping.").strip(),
            }
        )
    return output


def write_extract(path: Path, rows: list[dict[str, str]], append: bool) -> int:
    existing: list[dict[str, str]] = []
    if append and path.exists():
        with path.open("r", encoding="utf-8", newline="") as f:
            existing = list(csv.DictReader(f))
    combined = existing + rows
    seen = set()
    deduped = []
    for row in combined:
        key = (row.get("source_variable"), row.get("source_wave"), row.get("file_label"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(deduped)
    return len(deduped)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--input", required=True)
    parser.add_argument("--sheet", default=None)
    parser.add_argument("--column-map", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--default-source-wave", default="wave1")
    parser.add_argument("--default-file-label", default="baseline_core")
    parser.add_argument("--default-module", default="TBD")
    parser.add_argument("--default-wave-role", default="baseline")
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        print(json.dumps({"ok": False, "error": f"missing project manifest: {manifest_path}"}, ensure_ascii=False, indent=2))
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = project_path(args.output or manifest.get("codebookExtract", "charls_codebook_extract.csv"), project_dir)
    input_path = Path(args.input)
    try:
        rows, headers = read_table(input_path, args.sheet)
        explicit = load_column_map(args.column_map)
        mapping = infer_column_map(headers, explicit)
        failures = []
        if "source_variable" not in mapping:
            failures.append({"check": "source_variable_column_detected", "headers": headers})
        if looks_like_raw_data(headers, mapping):
            failures.append({"check": "reject_likely_respondent_level_data", "headers": headers})
        transformed = [] if failures else transform_rows(
            rows,
            mapping,
            {
                "source_wave": args.default_source_wave,
                "file_label": args.default_file_label,
                "module": args.default_module,
                "wave_role": args.default_wave_role,
            },
        )
        if not transformed and not failures:
            failures.append({"check": "imported_rows_nonempty"})
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    result = {
        "ok": not failures,
        "input": str(input_path),
        "output": str(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output),
        "dryRun": args.dry_run,
        "append": args.append,
        "sourceRows": len(rows),
        "importableRows": len(transformed),
        "detectedColumns": mapping,
        "preview": transformed[:5],
        "failures": failures,
        "warnings": [],
    }
    if len(headers) > 20:
        result["warnings"].append({"check": "wide_codebook_table", "columnCount": len(headers)})
    if result["ok"] and not args.dry_run:
        result["writtenRows"] = write_extract(output, transformed, args.append)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
