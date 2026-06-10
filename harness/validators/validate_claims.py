#!/usr/bin/env python3
"""Validate structured manuscript claims against a claim registry.

This is the first production-facing step beyond fixed number checks: claims are
explicit objects with source files, expected rendered text, and interpretation
boundaries. The validator also extracts candidate numeric sentences so reviewers
can see which claims are still outside the registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NUMERIC_PATTERN = re.compile(r"(\d[\d,]*(?:\.\d+)?%?|\bOR\b|95% CI)", re.IGNORECASE)


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text)
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", compact) if part.strip()]


def validate(root: Path, registry_path: Path) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    manuscript_path = root / registry["manuscript"]
    manuscript = manuscript_path.read_text(encoding="utf-8")
    manuscript_compact = re.sub(r"\s+", " ", manuscript)
    failures = []
    checks = []

    for claim in registry.get("claims", []):
        source = root / claim["sourceFile"]
        source_ok = source.exists()
        text_ok = claim["expectedText"] in manuscript_compact
        boundary_ok = bool(claim.get("interpretationBoundary"))
        checks.append(
            {
                "claim": claim["id"],
                "sourceExists": source_ok,
                "expectedTextPresent": text_ok,
                "interpretationBoundaryPresent": boundary_ok,
            }
        )
        if not source_ok:
            failures.append({"check": "source_exists", "claim": claim["id"], "source": claim["sourceFile"]})
        if not text_ok:
            failures.append({"check": "expected_text_present", "claim": claim["id"], "expected": claim["expectedText"]})
        if not boundary_ok:
            failures.append({"check": "interpretation_boundary", "claim": claim["id"]})

    registered_texts = [claim["expectedText"] for claim in registry.get("claims", [])]
    candidate_sentences = [
        sentence
        for sentence in split_sentences(manuscript)
        if NUMERIC_PATTERN.search(sentence)
        and not any(expected in sentence for expected in registered_texts)
        and not sentence.startswith("#")
    ]

    return {
        "ok": not failures,
        "registry": str(registry_path),
        "manuscript": str(manuscript_path),
        "registeredClaimCount": len(registry.get("claims", [])),
        "unregisteredNumericSentenceSample": candidate_sentences[:20],
        "checks": checks,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--registry", default="harness/claims/nhanes_claim_registry.json")
    args = parser.parse_args()
    result = validate(Path(args.root), Path(args.registry))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
