#!/usr/bin/env python3
"""Validate public-release safety for GBD and restricted-data artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "examples/gbd-cvd-china-global-instance"
REQUIRED_GITIGNORE_PATTERNS = {
    "data/gbd/raw/",
    "examples/gbd-cvd-china-global-instance/source_exports/*.csv",
    "data/charls/raw/",
    "data/charls/codebooks/",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def git_lines(*args: str) -> list[str]:
    run = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if run.returncode != 0:
        return []
    return [line.strip() for line in run.stdout.splitlines() if line.strip()]


def validate(project: Path) -> dict:
    project_dir = project if project.is_absolute() else ROOT / project
    failures: list[dict] = []
    warnings: list[dict] = []
    release_actions: list[dict] = []

    manifest_path = project_dir / "project_manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "project": rel(project_dir), "failures": [{"check": "project_manifest_exists"}]}
    manifest = load_json(manifest_path)

    profile = load_json(root_path(manifest["queryProfile"]))
    analysis = load_json(root_path(manifest["analysisManifest"]))["analyses"]["cvdChinaGlobal"]
    source_export = root_path(analysis["sourceFile"])
    source_citation = root_path(analysis["sourceCitationFile"])
    derived_summary = root_path(analysis["outputCsv"])
    citation_review = root_path(manifest["citationPolicyReview"])
    reuse_review = root_path(manifest["reuseReview"])
    public_release_audit = root_path(manifest["publicReleaseAudit"])
    release_commit_scope_audit = root_path(manifest["releaseCommitScopeAudit"])

    gitignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8") if (ROOT / ".gitignore").exists() else ""
    for pattern in sorted(REQUIRED_GITIGNORE_PATTERNS):
        if pattern not in gitignore_text:
            failures.append({"check": "gitignore_pattern", "pattern": pattern})

    tracked = set(git_lines("ls-files"))
    staged = set(git_lines("diff", "--cached", "--name-only"))
    tracked_or_staged = tracked | staged

    forbidden_tracked = []
    for path in tracked_or_staged:
        if path == rel(source_export):
            forbidden_tracked.append(path)
        if path.startswith("data/gbd/raw/") or path.startswith("data/charls/raw/") or path.startswith("data/charls/codebooks/"):
            forbidden_tracked.append(path)
    if forbidden_tracked:
        failures.append({"check": "restricted_or_raw_files_tracked", "paths": sorted(set(forbidden_tracked))})

    if source_export.exists():
        warnings.append({
            "check": "local_source_export_present",
            "path": rel(source_export),
            "action": "Keep local for strict reproduction; do not stage or package for public release until reuse is confirmed.",
        })
    else:
        warnings.append({
            "check": "local_source_export_absent",
            "path": rel(source_export),
            "action": "Public-release mode should rely on query manifests, provenance metadata, citation/reuse reviews, and derived summaries.",
        })

    if profile.get("reuseBoundary", {}).get("reviewStatus") != "reviewed-human-confirmation-required":
        failures.append({"check": "reuse_review_status", "actual": profile.get("reuseBoundary", {}).get("reviewStatus")})
    if profile.get("citationPolicy", {}).get("citationReviewStatus") != "reviewed-from-export-citation-human-confirmation-required":
        failures.append({"check": "citation_review_status", "actual": profile.get("citationPolicy", {}).get("citationReviewStatus")})

    for label, path in [
        ("source_citation", source_citation),
        ("derived_summary", derived_summary),
        ("citation_review", citation_review),
        ("reuse_review", reuse_review),
        ("public_release_audit", public_release_audit),
        ("release_commit_scope_audit", release_commit_scope_audit),
    ]:
        if not path.exists():
            failures.append({"check": f"{label}_exists", "path": rel(path)})

    release_actions.extend([
        {"path": rel(source_export), "classification": "local-only/raw-gbd-export", "recommendedAction": "do-not-commit"},
        {"path": rel(source_citation), "classification": "citation-evidence", "recommendedAction": "commit-with-review"},
        {"path": rel(derived_summary), "classification": "derived-aggregate", "recommendedAction": "commit-with-citation-reuse-review"},
        {"path": rel(citation_review), "classification": "compliance-review", "recommendedAction": "commit"},
        {"path": rel(reuse_review), "classification": "compliance-review", "recommendedAction": "commit"},
        {"path": rel(public_release_audit), "classification": "public-release-audit", "recommendedAction": "commit"},
        {"path": rel(release_commit_scope_audit), "classification": "release-commit-scope-audit", "recommendedAction": "commit"},
    ])

    return {
        "ok": not failures,
        "project": rel(project_dir),
        "sourceExport": rel(source_export),
        "sourceExportTracked": rel(source_export) in tracked_or_staged,
        "trackedForbiddenCount": len(forbidden_tracked),
        "releaseActions": release_actions,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=rel(DEFAULT_PROJECT))
    args = parser.parse_args()
    result = validate(Path(args.project))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
