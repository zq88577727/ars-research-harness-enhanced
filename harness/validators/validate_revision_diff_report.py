#!/usr/bin/env python3
"""Validate that a generated revision diff report exists and is informative."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def validate(path: Path) -> dict:
    failures = []
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if not path.exists():
        failures.append({"check": "report_exists", "path": str(path)})
    for marker in ["# Revision Diff Report", "## Summary", "## Unified Diff", "## Machine Summary"]:
        if marker not in text:
            failures.append({"check": "marker_present", "marker": marker})
    added_match = re.search(r"Added lines: (\d+)", text)
    removed_match = re.search(r"Removed lines: (\d+)", text)
    if not added_match or int(added_match.group(1)) == 0:
        failures.append({"check": "added_lines_positive"})
    if not removed_match:
        failures.append({"check": "removed_lines_present"})
    return {"ok": not failures, "report": str(path), "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="examples/nhanes-undiagnosed-diabetes/submission_package/revision_diff_report.md")
    args = parser.parse_args()
    result = validate(Path(args.report))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
