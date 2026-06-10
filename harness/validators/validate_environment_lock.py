#!/usr/bin/env python3
"""Check that the project declares reproducible Python and R environments."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PIN_RE = re.compile(r"^[A-Za-z0-9_.-]+==[^=\s]+$")


def validate(root: Path) -> dict:
    failures: list[dict] = []
    checks: list[dict] = []

    requirements = root / "requirements.txt"
    if not requirements.exists():
        failures.append({"check": "requirements_exists"})
    else:
        lines = [
            line.strip()
            for line in requirements.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        unpinned = [line for line in lines if not PIN_RE.match(line)]
        checks.append({"check": "python_requirements_pinned", "count": len(lines), "ok": not unpinned})
        if unpinned:
            failures.append({"check": "python_requirements_pinned", "unpinned": unpinned})

    renv_lock = root / "renv.lock"
    if not renv_lock.exists():
        failures.append({"check": "renv_lock_exists"})
    else:
        data = json.loads(renv_lock.read_text(encoding="utf-8"))
        packages = data.get("Packages", {})
        required = {"haven", "dplyr", "readr", "survey", "ggplot2"}
        missing = sorted(required - set(packages))
        checks.append({"check": "renv_required_packages", "required": sorted(required), "ok": not missing})
        if missing:
            failures.append({"check": "renv_required_packages", "missing": missing})

    dockerfile = root / "Dockerfile"
    checks.append({"check": "dockerfile_exists", "ok": dockerfile.exists()})
    if not dockerfile.exists():
        failures.append({"check": "dockerfile_exists"})

    return {"ok": not failures, "checks": checks, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = validate(Path(args.root))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
