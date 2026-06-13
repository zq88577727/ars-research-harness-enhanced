#!/usr/bin/env python3
"""Validate repository artifact policy and reviewed exceptions."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "harness/artifact_policy.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def git_lines(*args: str) -> list[str]:
    run = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if run.returncode != 0:
        return []
    return [line.strip() for line in run.stdout.splitlines() if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def validate(policy_path: Path) -> dict:
    failures: list[dict] = []
    warnings: list[dict] = []
    checks: list[dict] = []

    policy = load_json(policy_path)
    tracked = set(git_lines("ls-files"))
    staged = set(git_lines("diff", "--cached", "--name-only"))
    tracked_or_staged = sorted(tracked | staged)

    forbidden_prefixes = policy.get("forbiddenTrackedPrefixes", [])
    forbidden_globs = policy.get("forbiddenTrackedGlobs", [])
    forbidden_hits = []
    for path in tracked_or_staged:
        if any(path.startswith(prefix.rstrip("*")) for prefix in forbidden_prefixes if "**" not in prefix):
            forbidden_hits.append(path)
        elif matches_any(path, forbidden_prefixes) or matches_any(path, forbidden_globs):
            forbidden_hits.append(path)
    if forbidden_hits:
        failures.append({"check": "forbidden_tracked_artifacts", "paths": sorted(set(forbidden_hits))})
    checks.append({"check": "forbiddenTrackedArtifacts", "count": len(set(forbidden_hits)), "ok": not forbidden_hits})

    reviewed_large = {item["path"]: item for item in policy.get("reviewedLargeArtifacts", [])}
    max_unreviewed = int(policy.get("maxUnreviewedFileBytes", 500000))
    unreviewed_large = []
    reviewed_large_present = []
    for path in tracked_or_staged:
        file_path = ROOT / path
        if not file_path.is_file():
            continue
        size = file_path.stat().st_size
        if size >= max_unreviewed:
            if path in reviewed_large:
                reviewed_large_present.append({"path": path, "size": size, "decision": reviewed_large[path].get("decision")})
            else:
                unreviewed_large.append({"path": path, "size": size})
    if unreviewed_large:
        failures.append({"check": "unreviewed_large_artifacts", "maxUnreviewedFileBytes": max_unreviewed, "files": unreviewed_large})
    checks.append({
        "check": "largeArtifactsReviewed",
        "reviewedCount": len(reviewed_large_present),
        "unreviewedCount": len(unreviewed_large),
        "ok": not unreviewed_large,
    })

    allowed_source_exports = {item["path"]: item for item in policy.get("allowedSourceExportCsvs", [])}
    source_export_csvs = [
        path for path in tracked_or_staged
        if "/source_exports/" in path and path.endswith(".csv")
    ]
    disallowed_source_exports = [path for path in source_export_csvs if path not in allowed_source_exports]
    if disallowed_source_exports:
        failures.append({"check": "disallowed_source_export_csvs", "paths": disallowed_source_exports})
    checks.append({
        "check": "sourceExportCsvsReviewed",
        "reviewedCount": len(source_export_csvs) - len(disallowed_source_exports),
        "unreviewedCount": len(disallowed_source_exports),
        "ok": not disallowed_source_exports,
    })

    for item in policy.get("allowedSourceExportCsvs", []):
        path = item["path"]
        if path not in tracked_or_staged:
            failures.append({"check": "allowed_source_export_exists", "path": path})
        else:
            warnings.append({
                "check": "reviewed_source_export_csv",
                "path": path,
                "decision": item.get("decision"),
                "rationale": item.get("rationale"),
            })

    for item in policy.get("reviewedDocxArtifacts", []):
        path = item["path"]
        if path not in tracked_or_staged:
            failures.append({"check": "reviewed_docx_exists", "path": path})
        elif not path.endswith(".docx"):
            failures.append({"check": "reviewed_docx_extension", "path": path})
    checks.append({
        "check": "reviewedDocxArtifactsPresent",
        "count": len(policy.get("reviewedDocxArtifacts", [])),
        "ok": not any(f["check"].startswith("reviewed_docx") for f in failures),
    })

    duplicate_groups = []
    for group in policy.get("reviewedDuplicateGroups", []):
        paths = group.get("paths", [])
        missing = [path for path in paths if path not in tracked_or_staged or not (ROOT / path).is_file()]
        hashes = {}
        if not missing:
            for path in paths:
                hashes[path] = sha256(ROOT / path)
        same_hash = len(set(hashes.values())) == 1 if hashes else False
        duplicate_groups.append({
            "id": group.get("id"),
            "paths": paths,
            "decision": group.get("decision"),
            "sameSha256": same_hash,
            "missing": missing,
        })
        if missing:
            failures.append({"check": "reviewed_duplicate_group_paths_exist", "id": group.get("id"), "missing": missing})
        elif not same_hash:
            failures.append({"check": "reviewed_duplicate_group_same_sha256", "id": group.get("id"), "hashes": hashes})
        else:
            warnings.append({
                "check": "reviewed_duplicate_group",
                "id": group.get("id"),
                "decision": group.get("decision"),
                "rationale": group.get("rationale"),
            })
    checks.append({
        "check": "reviewedDuplicateGroups",
        "count": len(duplicate_groups),
        "ok": not any(f["check"].startswith("reviewed_duplicate_group") for f in failures),
    })

    return {
        "ok": not failures,
        "policy": rel(policy_path),
        "trackedOrStagedCount": len(tracked_or_staged),
        "maxUnreviewedFileBytes": max_unreviewed,
        "checks": checks,
        "reviewedLargeArtifacts": reviewed_large_present,
        "sourceExportCsvs": source_export_csvs,
        "duplicateGroups": duplicate_groups,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default=rel(DEFAULT_POLICY))
    args = parser.parse_args()
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = ROOT / policy_path
    result = validate(policy_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
