#!/usr/bin/env python3
"""Validate structured manuscript claims against a claim registry.

This is the first production-facing step beyond fixed number checks: claims are
explicit objects with source files, expected rendered text, interpretation
boundaries, and review priority tiers. The validator also extracts candidate
numeric sentences so reviewers can see which claims are still outside the
registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NUMERIC_PATTERN = re.compile(r"(\d[\d,]*(?:\.\d+)?%?|\bOR\b|95% CI)", re.IGNORECASE)
ALLOWED_TIERS = {"core", "supporting", "background"}


def sentence_parts(text: str) -> list[str]:
    protected = text.replace("U.S.", "US_ABBREV")
    return [part.replace("US_ABBREV", "U.S.").strip() for part in re.split(r"(?<=[.!?])\s+", protected) if part.strip()]


def split_sentences(text: str) -> list[str]:
    sentences = []
    metadata_prefixes = (
        "Article type:",
        "Running title:",
        "Authors:",
        "Affiliations:",
        "Corresponding author:",
        "Funding:",
        "Conflicts of interest:",
        "Author contributions:",
        "Acknowledgements:",
        "Word count:",
        "**Keywords:**",
    )
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        if any(line.startswith(prefix) for prefix in metadata_prefixes):
            continue
        compact = re.sub(r"\s+", " ", line)
        sentences.extend(sentence_parts(compact))
    return sentences


def validate(root: Path, registry_path: Path) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    manuscript_path = root / registry["manuscript"]
    manuscript = manuscript_path.read_text(encoding="utf-8")
    manuscript_compact = re.sub(r"\s+", " ", manuscript)
    failures = []
    checks = []
    tier_counts = {tier: 0 for tier in sorted(ALLOWED_TIERS)}

    for claim in registry.get("claims", []):
        source = root / claim["sourceFile"]
        source_ok = source.exists()
        text_ok = claim["expectedText"] in manuscript_compact
        boundary_ok = bool(claim.get("interpretationBoundary"))
        tier = claim.get("tier")
        tier_ok = tier in ALLOWED_TIERS
        if tier_ok:
            tier_counts[tier] += 1
        checks.append(
            {
                "claim": claim["id"],
                "tier": tier,
                "sourceExists": source_ok,
                "expectedTextPresent": text_ok,
                "interpretationBoundaryPresent": boundary_ok,
                "tierValid": tier_ok,
            }
        )
        if not source_ok:
            failures.append({"check": "source_exists", "claim": claim["id"], "source": claim["sourceFile"]})
        if not text_ok:
            failures.append({"check": "expected_text_present", "claim": claim["id"], "expected": claim["expectedText"]})
        if not boundary_ok:
            failures.append({"check": "interpretation_boundary", "claim": claim["id"]})
        if not tier_ok:
            failures.append({"check": "allowed_tier", "claim": claim["id"], "tier": tier})

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
        "registeredClaimTiers": tier_counts,
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
