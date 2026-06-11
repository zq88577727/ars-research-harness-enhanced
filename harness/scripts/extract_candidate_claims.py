#!/usr/bin/env python3
"""Extract candidate numeric claims for human registry review."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NUMERIC_PATTERN = re.compile(
    r"(\d[\d,]*(?:\.\d+)?%?|95%\s*CI|\bOR\b|>=|<=|[<>]\s*\d)",
    re.IGNORECASE,
)
CORE_PATTERN = re.compile(
    r"(weighted prevalence|primary outcome|final analytic sample|odds|OR|95%\s*CI|DALYs?|deaths?|result|results)",
    re.IGNORECASE,
)
BACKGROUND_PATTERN = re.compile(
    r"(reported|prior|background|guideline|threshold|lists|emphasizes|Data Brief|Healthy People|ADA|NIDDK)",
    re.IGNORECASE,
)
BOUNDARY_PATTERN = re.compile(
    r"(not a publishable|not clinical|not clinically|not causal|associations rather than causal|fixture|diagnostic recommendations|single measurement)",
    re.IGNORECASE,
)


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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
        compact = compact_text(line)
        sentences.extend(sentence_parts(compact))
    return sentences


def classify(sentence: str) -> str:
    if BOUNDARY_PATTERN.search(sentence):
        return "core"
    if CORE_PATTERN.search(sentence):
        return "core"
    if BACKGROUND_PATTERN.search(sentence):
        return "background"
    return "supporting"


def evidence_type(sentence: str) -> str:
    if re.search(r"\bOR\b|95%\s*CI", sentence, re.IGNORECASE):
        return "model-estimate"
    if re.search(r"%", sentence):
        return "prevalence-or-percentage"
    if re.search(r"DALYs?|deaths?", sentence, re.IGNORECASE):
        return "burden-estimate"
    if re.search(r"participants?|sample", sentence, re.IGNORECASE):
        return "sample-size"
    if re.search(r">=|<=|mg/dL|mmHg|threshold", sentence, re.IGNORECASE):
        return "definition-or-threshold"
    return "numeric-claim"


def extract(manuscript: Path, registry: Path | None, prefix: str, limit: int | None) -> dict:
    text = manuscript.read_text(encoding="utf-8")
    registered_texts: list[str] = []
    if registry and registry.exists():
        data = json.loads(registry.read_text(encoding="utf-8"))
        registered_texts = [claim.get("expectedText", "") for claim in data.get("claims", [])]

    candidates = []
    for sentence in split_sentences(text):
        if sentence.startswith("#") or not NUMERIC_PATTERN.search(sentence):
            continue
        status = "already-registered" if any(expected and expected in sentence for expected in registered_texts) else "needs-human-review"
        candidates.append(
            {
                "id": f"{prefix}-candidate-{len(candidates) + 1:03d}",
                "status": status,
                "suggestedTier": classify(sentence),
                "type": evidence_type(sentence),
                "sentence": sentence,
                "interpretationBoundaryNeeded": not bool(BOUNDARY_PATTERN.search(sentence)),
            }
        )
        if limit and len(candidates) >= limit:
            break

    counts: dict[str, int] = {}
    for candidate in candidates:
        key = f"{candidate['status']}:{candidate['suggestedTier']}"
        counts[key] = counts.get(key, 0) + 1

    return {
        "ok": True,
        "manuscript": str(manuscript),
        "registry": str(registry) if registry else None,
        "candidateCount": len(candidates),
        "counts": counts,
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript")
    parser.add_argument("--registry")
    parser.add_argument("--prefix", default="claim")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = extract(
        manuscript=Path(args.manuscript),
        registry=Path(args.registry) if args.registry else None,
        prefix=args.prefix,
        limit=args.limit,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
