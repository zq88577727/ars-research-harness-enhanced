#!/usr/bin/env python3
"""Validate structured reporting checklist files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {"addressed", "partial", "not-addressed", "not-applicable", "needs-author-completion"}


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    items = data.get("items", [])
    if not items:
        failures.append({"check": "items_present"})
    for item in items:
        for field in ["item", "domain", "requirement", "status", "manuscriptLocation"]:
            if field not in item:
                failures.append({"check": "required_field", "item": item.get("item"), "field": field})
        if item.get("status") not in ALLOWED_STATUSES:
            failures.append({"check": "allowed_status", "item": item.get("item"), "status": item.get("status")})
    unresolved = [item["item"] for item in items if item.get("status") in {"partial", "not-addressed", "needs-author-completion"}]
    return {
        "ok": not failures,
        "checklist": str(path),
        "itemCount": len(items),
        "unresolvedItems": unresolved,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checklist", default="harness/reporting_checklists/strobe.observational.json")
    args = parser.parse_args()
    result = validate(Path(args.checklist))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
