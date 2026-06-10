#!/usr/bin/env python3
"""Validate that reviewer-response trace items point to real files and anchors."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate(root: Path, trace_path: Path) -> dict:
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    manuscript_path = root / trace["revisedManuscript"]
    manuscript = manuscript_path.read_text(encoding="utf-8") if manuscript_path.exists() else ""
    failures = []
    for idx, item in enumerate(trace.get("items", []), start=1):
        for file_name in item.get("evidenceFiles", []):
            if not (root / file_name).exists():
                failures.append({"check": "evidence_file_exists", "item": idx, "file": file_name})
        for anchor in item.get("manuscriptAnchors", []):
            if anchor not in manuscript:
                failures.append({"check": "manuscript_anchor_present", "item": idx, "anchor": anchor})
        if item.get("status") not in {"implemented", "partially-implemented", "rejected", "deferred"}:
            failures.append({"check": "status_allowed", "item": idx, "status": item.get("status")})
    return {
        "ok": not failures,
        "trace": str(trace_path),
        "itemCount": len(trace.get("items", [])),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--trace", default="harness/revision_traces/nhanes_s8_major_revision_trace.json")
    args = parser.parse_args()
    result = validate(Path(args.root), Path(args.trace))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
