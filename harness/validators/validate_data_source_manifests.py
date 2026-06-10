#!/usr/bin/env python3
"""Validate public database adapter manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = ["id", "name", "steward", "accessMode", "rawDataPolicy", "supportedStudyDesigns", "requiredHarnessStages"]


def validate(manifest_dir: Path) -> dict:
    failures = []
    checks = []
    for path in sorted(manifest_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        checks.append({"manifest": str(path), "missing": missing, "ok": not missing})
        if missing:
            failures.append({"check": "required_fields", "manifest": str(path), "missing": missing})
        if "raw" in data.get("rawDataPolicy", "").lower() and "commit" not in data.get("rawDataPolicy", "").lower():
            failures.append({"check": "raw_data_policy_explicit", "manifest": str(path)})
    return {"ok": not failures, "manifestCount": len(checks), "checks": checks, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", default="data_sources")
    args = parser.parse_args()
    result = validate(Path(args.manifest_dir))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
