#!/usr/bin/env python3
"""Run all local validation gates for the research harness."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


COMMANDS = [
    ["python3", "harness/scripts/validate_checkpoint_workflow.py", "examples/nhanes-undiagnosed-diabetes/workflow-run.json"],
    ["python3", "harness/validators/validate_manuscript_numbers.py"],
    ["python3", "harness/validators/validate_references.py"],
    ["python3", "harness/validators/validate_external_literature.py"],
    ["python3", "harness/validators/validate_claims.py"],
    ["python3", "harness/validators/validate_candidate_claims.py"],
    ["python3", "harness/validators/validate_environment_lock.py"],
    ["python3", "harness/validators/validate_reporting_checklist.py"],
    ["python3", "harness/validators/validate_journal_profile.py"],
    ["python3", "harness/validators/validate_revision_trace.py"],
    ["python3", "harness/validators/validate_revision_diff_report.py"],
    ["python3", "harness/validators/validate_data_source_manifests.py"],
    ["python3", "harness/validators/validate_project_scaffold.py", "examples/charls-aging-template"],
    ["python3", "harness/validators/validate_project_scaffold.py", "examples/gbd-burden-template"],
    ["python3", "harness/validators/validate_project_scaffold.py", "examples/gbd-burden-minimal-demo"],
    ["python3", "harness/validators/validate_gbd_minimal_demo.py"],
    ["python3", "harness/scripts/generate_readiness_report.py"],
]


def main() -> int:
    results = []
    for command in COMMANDS:
        run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        try:
            payload = json.loads(run.stdout)
        except json.JSONDecodeError:
            payload = {"ok": False, "stdout": run.stdout, "stderr": run.stderr}
        results.append({"command": command, "returncode": run.returncode, "result": payload})

    ok = all(item["returncode"] == 0 and item["result"].get("ok") for item in results)
    print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
