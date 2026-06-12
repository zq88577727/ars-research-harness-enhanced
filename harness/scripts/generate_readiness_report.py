#!/usr/bin/env python3
"""Generate a production-readiness gate report for the repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_POLICY_FILES = [
    "DATA_POLICY.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/README.md",
    "docs/11-study-design-support-matrix.md",
    "docs/12-artifact-governance.md",
    "examples/README.md",
]


def run_json(command: list[str]) -> dict:
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    try:
        result = json.loads(run.stdout)
    except json.JSONDecodeError:
        result = {"ok": False, "stdout": run.stdout, "stderr": run.stderr}
    return {"command": command, "returncode": run.returncode, "result": result}


def file_check() -> dict:
    missing = [path for path in REQUIRED_POLICY_FILES if not (ROOT / path).exists()]
    return {"ok": not missing, "missing": missing}


def raw_data_policy_check() -> dict:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ["data/charls/raw/", "data/gbd/raw/", "data/**/restricted/", "data/**/sensitive/"]
    missing = [item for item in required if item not in gitignore]
    return {"ok": not missing, "missing": missing}


def scaffold_boundary_check() -> dict:
    failures = []
    for rel in ["examples/charls-aging-template/project_manifest.json", "examples/gbd-burden-template/project_manifest.json"]:
        manifest = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        if manifest.get("capabilityStatus") != "scaffold-only":
            failures.append({"manifest": rel, "capabilityStatus": manifest.get("capabilityStatus")})
    return {"ok": not failures, "failures": failures}


def claim_tier_check() -> dict:
    registry = json.loads((ROOT / "harness/claims/nhanes_claim_registry.json").read_text(encoding="utf-8"))
    tiers = {"core": 0, "supporting": 0, "background": 0}
    failures = []
    for claim in registry.get("claims", []):
        tier = claim.get("tier")
        if tier not in tiers:
            failures.append({"claim": claim.get("id"), "tier": tier})
        else:
            tiers[tier] += 1
    if any(count == 0 for count in tiers.values()):
        failures.append({"check": "all_tiers_populated", "tiers": tiers})
    return {"ok": not failures, "tiers": tiers, "failures": failures}


def build_report() -> dict:
    validations = [
        run_json(["python3", "harness/scripts/validate_checkpoint_workflow.py", "examples/nhanes-undiagnosed-diabetes/workflow-run.json"]),
        run_json(["python3", "harness/validators/validate_claims.py"]),
        run_json(["python3", "harness/validators/validate_candidate_claims.py"]),
        run_json(["python3", "harness/validators/validate_reporting_checklist.py"]),
        run_json(["python3", "harness/validators/validate_data_source_manifests.py"]),
        run_json(["python3", "harness/validators/validate_project_scaffold.py", "examples/charls-aging-template"]),
        run_json(["python3", "harness/validators/validate_charls_design_gate.py"]),
        run_json(["python3", "harness/scripts/prepare_charls_design_gate_instance.py", "--dry-run"]),
        run_json(["python3", "harness/scripts/apply_charls_variable_mapping_decisions.py", "--dry-run"]),
        run_json(["python3", "harness/validators/validate_charls_local_dry_run.py"]),
        run_json(["python3", "harness/validators/validate_project_scaffold.py", "examples/gbd-burden-template"]),
        run_json(["python3", "harness/validators/validate_project_scaffold.py", "examples/gbd-burden-minimal-demo"]),
        run_json(["python3", "scripts/fetch_gbd_export.py", "--dry-run"]),
        run_json(["python3", "harness/validators/validate_gbd_minimal_demo.py"]),
    ]
    checks = {
        "policyFiles": file_check(),
        "rawDataPolicy": raw_data_policy_check(),
        "scaffoldBoundaries": scaffold_boundary_check(),
        "nhanesClaimTiers": claim_tier_check(),
    }
    validation_ok = all(item["returncode"] == 0 and item["result"].get("ok") for item in validations)
    check_ok = all(item.get("ok") for item in checks.values())
    warnings = []
    reporting = next(
        item["result"]
        for item in validations
        if item["command"] == ["python3", "harness/validators/validate_reporting_checklist.py"]
    )
    for item in reporting.get("authorDependentItems", []):
        warnings.append(f"Reporting checklist item {item} is author-dependent and must be completed before journal submission.")
    warnings.append("External literature validation is offline by default in CI; run the online mode before real submission when network access is available.")
    return {
        "ok": validation_ok and check_ok,
        "status": "ready-for-controlled-demo" if validation_ok and check_ok else "not-ready",
        "scope": "Production readiness gate for workflow governance, not a guarantee of journal acceptance.",
        "checks": checks,
        "validations": validations,
        "warnings": warnings,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Production Readiness Report",
        "",
        f"Status: `{report['status']}`",
        "",
        report["scope"],
        "",
        "## Checks",
        "",
    ]
    for name, payload in report["checks"].items():
        mark = "PASS" if payload.get("ok") else "FAIL"
        lines.append(f"- {mark}: `{name}`")
    lines.extend(["", "## Validation Gates", ""])
    for item in report["validations"]:
        mark = "PASS" if item["returncode"] == 0 and item["result"].get("ok") else "FAIL"
        lines.append(f"- {mark}: `{' '.join(item['command'])}`")
    lines.extend(["", "## Warnings", ""])
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    report = build_report()
    if args.format == "markdown":
        print(to_markdown(report))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
