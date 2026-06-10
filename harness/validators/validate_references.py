#!/usr/bin/env python3
"""Validate final manuscript references against a structured registry.

Offline mode checks numbering, expected metadata, DOI/URL syntax, and
claim-to-reference coverage. Optional online mode can verify DOI and PubMed URLs
when network access is available.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_references(manuscript: str) -> dict[int, str]:
    refs: dict[int, str] = {}
    in_refs = False
    for line in manuscript.splitlines():
        if line.strip() == "# References":
            in_refs = True
            continue
        if not in_refs:
            continue
        match = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if match:
            refs[int(match.group(1))] = normalize(match.group(2))
    return refs


def url_ok(url: str, timeout: int = 10) -> bool:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ars-reference-validator/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 400
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return False


def validate(manuscript_path: Path, registry_path: Path, online: bool = False) -> dict:
    manuscript = manuscript_path.read_text(encoding="utf-8")
    refs = parse_references(manuscript)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    expected = registry["references"]
    failures: list[dict] = []
    checks: list[dict] = []

    if len(refs) != len(expected):
        failures.append({"check": "reference_count", "expected": len(expected), "actual": len(refs)})

    for item in expected:
        number = int(item["number"])
        ref_text = refs.get(number, "")
        if not ref_text:
            failures.append({"check": "missing_reference", "number": number})
            continue

        for field in item.get("must_contain", []):
            ok = field.lower() in ref_text.lower()
            checks.append({"check": "must_contain", "number": number, "value": field, "ok": ok})
            if not ok:
                failures.append({"check": "must_contain", "number": number, "value": field})

        doi = item.get("doi")
        if doi:
            ok = bool(DOI_RE.match(doi)) and f"doi:{doi}".lower() in ref_text.lower()
            checks.append({"check": "doi_syntax_and_presence", "number": number, "doi": doi, "ok": ok})
            if not ok:
                failures.append({"check": "doi_syntax_and_presence", "number": number, "doi": doi})
            if online:
                doi_url = f"https://doi.org/{doi}"
                reachable = url_ok(doi_url)
                checks.append({"check": "doi_online", "number": number, "url": doi_url, "ok": reachable})
                if not reachable:
                    failures.append({"check": "doi_online", "number": number, "url": doi_url})

        url = item.get("url")
        if url:
            ok = bool(URL_RE.match(url)) and url in ref_text
            checks.append({"check": "url_syntax_and_presence", "number": number, "url": url, "ok": ok})
            if not ok:
                failures.append({"check": "url_syntax_and_presence", "number": number, "url": url})
            if online:
                reachable = url_ok(url)
                checks.append({"check": "url_online", "number": number, "url": url, "ok": reachable})
                if not reachable:
                    failures.append({"check": "url_online", "number": number, "url": url})

    cited_numbers: set[int] = set()
    for citation in re.findall(r"\[([0-9,\-\s]+)\]", manuscript):
        for part in citation.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = [int(value) for value in part.split("-", 1)]
                cited_numbers.update(range(start, end + 1))
            else:
                cited_numbers.add(int(part))
    for item in expected:
        number = int(item["number"])
        ok = number in cited_numbers
        checks.append({"check": "in_text_citation_present", "number": number, "ok": ok})
        if not ok:
            failures.append({"check": "in_text_citation_present", "number": number})

    for claim in registry.get("claim_map", []):
        missing = [ref for ref in claim["references"] if ref not in refs]
        ok = not missing
        checks.append({"check": "claim_map", "claim": claim["claim"], "references": claim["references"], "ok": ok})
        if not ok:
            failures.append({"check": "claim_map", "claim": claim["claim"], "missing": missing})

    return {
        "ok": not failures,
        "manuscript": str(manuscript_path),
        "registry": str(registry_path),
        "referenceCount": len(refs),
        "checks": checks,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manuscript",
        default="examples/nhanes-undiagnosed-diabetes/submission_package/manuscript_final_generic_sci.md",
    )
    parser.add_argument(
        "--registry",
        default="harness/reference_registry/nhanes_undiagnosed_diabetes.references.json",
    )
    parser.add_argument("--online", action="store_true", help="Verify DOI/URL reachability.")
    args = parser.parse_args()
    result = validate(Path(args.manuscript), Path(args.registry), args.online)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
