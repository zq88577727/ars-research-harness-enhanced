#!/usr/bin/env python3
"""Generate a manuscript revision diff report."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path


def summarize_diff(before: str, after: str) -> dict:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    diff = list(difflib.unified_diff(before_lines, after_lines, fromfile="before", tofile="after", lineterm=""))
    added = [line for line in diff if line.startswith("+") and not line.startswith("+++")]
    removed = [line for line in diff if line.startswith("-") and not line.startswith("---")]
    return {
        "addedLineCount": len(added),
        "removedLineCount": len(removed),
        "diffLineCount": len(diff),
        "addedHeadings": [line[1:] for line in added if line.startswith("+#")],
        "removedHeadings": [line[1:] for line in removed if line.startswith("-#")],
        "diff": diff,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", default="examples/nhanes-undiagnosed-diabetes/checkpoints/stage-S7b-citation-clean-draft.md")
    parser.add_argument("--after", default="examples/nhanes-undiagnosed-diabetes/checkpoints/stage-S8b-revised-manuscript.md")
    parser.add_argument("--output", default="examples/nhanes-undiagnosed-diabetes/submission_package/revision_diff_report.md")
    args = parser.parse_args()

    before_path = Path(args.before)
    after_path = Path(args.after)
    report = summarize_diff(before_path.read_text(encoding="utf-8"), after_path.read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# Revision Diff Report",
        "",
        f"Before: `{before_path}`",
        f"After: `{after_path}`",
        "",
        "## Summary",
        "",
        f"- Added lines: {report['addedLineCount']}",
        f"- Removed lines: {report['removedLineCount']}",
        f"- Diff lines: {report['diffLineCount']}",
        "",
        "## Added Headings",
        "",
    ]
    body.extend(f"- {heading}" for heading in report["addedHeadings"][:30])
    body.extend(["", "## Removed Headings", ""])
    body.extend(f"- {heading}" for heading in report["removedHeadings"][:30])
    body.extend(["", "## Unified Diff", "", "```diff"])
    body.extend(report["diff"][:1000])
    body.extend(["```", "", "## Machine Summary", "", "```json", json.dumps({k: v for k, v in report.items() if k != "diff"}, ensure_ascii=False, indent=2), "```", ""])
    output.write_text("\n".join(body), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output), "addedLineCount": report["addedLineCount"], "removedLineCount": report["removedLineCount"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
