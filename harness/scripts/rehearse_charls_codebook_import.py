#!/usr/bin/env python3
"""Rehearse local CHARLS codebook import and candidate generation.

This script is intentionally project-read-only by default. It discovers or
accepts local variable-level codebook files, runs the import transformation in
memory, and feeds the resulting temporary extract into the S1/S2 candidate
generator. It does not read restricted respondent-level data and does not update
the project codebook extract unless an explicit output path is provided.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import tempfile
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
CODEBOOK_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls"}


def load_script_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IMPORTER = load_script_module("charls_codebook_importer", SCRIPT_DIR / "import_charls_codebook_extract.py")
INSTANTIATOR = load_script_module("charls_design_gate_instantiator", SCRIPT_DIR / "prepare_charls_design_gate_instance.py")


def project_path(value: str, project_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.exists() or value.startswith(("data/", "examples/", "harness/", "data_sources/")):
        return root_relative
    return project_dir / path


def rel(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def discover_inputs(search_dirs: list[str], project_dir: Path) -> list[Path]:
    discovered: list[Path] = []
    seen = set()
    for value in search_dirs:
        directory = project_path(value, project_dir)
        if not directory.exists() or not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in CODEBOOK_EXTENSIONS:
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    discovered.append(resolved)
    return discovered


def explicit_inputs(inputs: list[str], project_dir: Path) -> list[Path]:
    paths: list[Path] = []
    seen = set()
    for value in inputs:
        path = project_path(value, project_dir).resolve()
        if path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def rehearse_one(path: Path, args: argparse.Namespace) -> tuple[dict, list[dict[str, str]]]:
    failures = []
    warnings = []
    transformed: list[dict[str, str]] = []
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    mapping: dict[str, str] = {}
    try:
        if not path.exists():
            failures.append({"check": "input_exists", "path": str(path)})
        else:
            rows, headers = IMPORTER.read_table(path, args.sheet)
            explicit = IMPORTER.load_column_map(args.column_map)
            mapping = IMPORTER.infer_column_map(headers, explicit)
            if "source_variable" not in mapping:
                failures.append({"check": "source_variable_column_detected", "headers": headers})
            if IMPORTER.looks_like_raw_data(headers, mapping):
                failures.append({"check": "reject_likely_respondent_level_data", "headers": headers})
            if not failures:
                transformed = IMPORTER.transform_rows(
                    rows,
                    mapping,
                    {
                        "source_wave": args.default_source_wave,
                        "file_label": args.default_file_label,
                        "module": args.default_module,
                        "wave_role": args.default_wave_role,
                    },
                )
                if not transformed:
                    failures.append({"check": "imported_rows_nonempty"})
    except Exception as exc:
        failures.append({"check": "read_or_transform_codebook", "error": str(exc)})

    if len(headers) > 20:
        warnings.append({"check": "wide_codebook_table", "columnCount": len(headers)})
    return (
        {
            "ok": not failures,
            "input": rel(path),
            "sourceRows": len(rows),
            "importableRows": len(transformed),
            "detectedColumns": mapping,
            "preview": transformed[: args.preview_rows],
            "failures": failures,
            "warnings": warnings,
        },
        transformed,
    )


def write_extract(path: Path, rows: list[dict[str, str]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    return IMPORTER.write_extract(path, rows, append=False)


def temporary_extract(rows: list[dict[str, str]]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
    with temp:
        writer = csv.DictWriter(temp, fieldnames=IMPORTER.OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(temp.name)


def render_report(result: dict) -> str:
    lines = [
        "# CHARLS Local Codebook Import Rehearsal",
        "",
        f"Project: `{result['project']}`",
        f"Status: `{result['status']}`",
        "",
        "This rehearsal is a local metadata audit. It does not approve real CHARLS analysis, does not commit official codebooks, and does not replace human review against the official documentation.",
        "",
        "## Inputs",
        "",
    ]
    if result["inputs"]:
        for item in result["inputs"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- No local codebook files were found or provided.")
    lines.extend(["", "## Import Results", ""])
    for item in result["importResults"]:
        mark = "PASS" if item["ok"] else "FAIL"
        lines.append(f"- {mark}: `{item['input']}` -> {item['importableRows']} importable rows")
        for failure in item["failures"]:
            lines.append(f"  - Failure: `{failure.get('check')}`")
    lines.extend(
        [
            "",
            "## Candidate Summary",
            "",
            f"- Imported variable-level rows: {result['combinedImportableRows']}",
            f"- Minimum displayed candidate score: {result['minCandidateScore']}",
            f"- Target variables reviewed: {result.get('targetVariableCount', 0)}",
            f"- Candidate suggestions: {result.get('candidateSuggestionCount', 0)}",
            f"- Variables still requiring human mapping: {result.get('needsHumanMappingCount', 0)}",
            "",
            "## Candidate Review",
            "",
            "| canonical variable | role | wave role | candidate suggestions |",
            "|---|---|---|---|",
        ]
    )
    for target in result.get("targets", []):
        suggestions = []
        for candidate in target.get("candidates", []):
            row = candidate["candidate"]
            suggestions.append(f"`{row.get('source_variable')}` ({row.get('source_wave')}/{row.get('file_label')}, score {candidate['score']})")
        if not suggestions:
            suggestions = ["No candidate from current local codebook rehearsal"]
        lines.append(
            "| {name} | {role} | {wave} | {suggestions} |".format(
                name=target.get("canonicalName", ""),
                role=target.get("role", ""),
                wave=target.get("waveRole", ""),
                suggestions="<br>".join(suggestions),
            )
        )
    lines.extend(["", "## Next Human Actions", ""])
    if result["status"] == "awaiting-local-codebook":
        lines.append("- Place official local CHARLS codebook/questionnaire exports under `data/charls/codebooks/` and rerun the rehearsal.")
    else:
        lines.extend(
            [
                "- Confirm that every imported row is variable-level metadata, not respondent-level data.",
                "- Review candidate source variables against official CHARLS documentation.",
                "- Record accepted mappings in `charls_variable_mapping_decisions.json` before updating `variable_map.csv`.",
                "- Keep `charls_design_gate.json` pending until exposure, outcome, attrition, and weight decisions are resolved.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict:
    project_dir = Path(args.project).resolve()
    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing project manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataSource") != "charls":
        raise ValueError("project manifest must declare dataSource=charls")

    inputs = explicit_inputs(args.input, project_dir)
    if not inputs:
        inputs = discover_inputs(args.search_dir, project_dir)

    import_results = []
    combined_rows: list[dict[str, str]] = []
    for path in inputs:
        result, rows = rehearse_one(path, args)
        import_results.append(result)
        if result["ok"]:
            combined_rows.extend(rows)

    if not inputs:
        status = "awaiting-local-codebook"
    elif any(not item["ok"] for item in import_results):
        status = "import-rehearsal-failed"
    elif not combined_rows:
        status = "no-importable-codebook-rows"
    else:
        status = "candidate-review-ready"

    result = {
        "ok": status in {"awaiting-local-codebook", "candidate-review-ready"},
        "status": status,
        "project": rel(project_dir),
        "inputs": [rel(path) for path in inputs],
        "searchDirs": args.search_dir,
        "minCandidateScore": args.min_candidate_score,
        "importResults": import_results,
        "combinedImportableRows": len(combined_rows),
        "outputExtract": None,
        "outputReport": None,
        "readinessBlockers": [],
        "targets": [],
    }

    if args.require_input and not inputs:
        result["ok"] = False
        result["readinessBlockers"].append("No local CHARLS codebook files were found or provided.")

    if combined_rows:
        extract_path = project_path(args.output_extract, project_dir) if args.output_extract else temporary_extract(combined_rows)
        written_rows = write_extract(extract_path, combined_rows)
        result["outputExtract"] = rel(extract_path)
        result["outputExtractRows"] = written_rows
        candidate_result = INSTANTIATOR.build(project_dir, str(extract_path), args.candidate_limit)
        for key in [
            "targetVariableCount",
            "codebookRowCount",
            "usableCodebookRowCount",
            "needsHumanMappingCount",
            "readinessBlockers",
            "targets",
        ]:
            result[key] = candidate_result.get(key)
        for target in result["targets"]:
            target["candidates"] = [
                candidate
                for candidate in target.get("candidates", [])
                if candidate.get("score", 0) >= args.min_candidate_score
            ]
        result["candidateSuggestionCount"] = sum(len(target.get("candidates", [])) for target in result["targets"])

    report = render_report(result)
    if args.write_report:
        report_path = project_path(args.output_report, project_dir)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        result["outputReport"] = rel(report_path)
    result["reportMarkdown"] = report
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="examples/charls-aging-template")
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--search-dir", action="append", default=["data/charls/codebooks"])
    parser.add_argument("--sheet", default=None)
    parser.add_argument("--column-map", default=None)
    parser.add_argument("--output-extract", default=None)
    parser.add_argument("--output-report", default="examples/charls-aging-template/charls_codebook_import_rehearsal.md")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--min-candidate-score", type=int, default=12)
    parser.add_argument("--preview-rows", type=int, default=5)
    parser.add_argument("--default-source-wave", default="wave1")
    parser.add_argument("--default-file-label", default="baseline_core")
    parser.add_argument("--default-module", default="TBD")
    parser.add_argument("--default-wave-role", default="baseline")
    parser.add_argument("--require-input", action="store_true")
    args = parser.parse_args()

    try:
        result = build(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = {key: value for key, value in result.items() if key != "reportMarkdown"}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
