#!/usr/bin/env python3
"""Optionally validate journal references against Crossref and PubMed.

Default mode is offline and verifies that references with DOIs are eligible for
external checks. Use `--online` in a network-enabled environment for live checks.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def fetch_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ars-literature-validator/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def crossref_check(doi: str, must_contain: list[str]) -> dict:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    try:
        payload = fetch_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"doi": doi, "service": "crossref", "ok": False, "error": str(exc)}
    message = payload.get("message", {})
    title = " ".join(message.get("title", []))
    container = " ".join(message.get("container-title", []))
    year_parts = message.get("published-print") or message.get("published-online") or {}
    year = str((year_parts.get("date-parts") or [[""]])[0][0])
    haystack = " ".join([title, container, year]).lower()
    return {
        "doi": doi,
        "title": title,
        "container": container,
        "year": year,
        "ok": any(value.lower() in haystack for value in must_contain),
    }


def pubmed_check(doi: str) -> dict:
    query = urllib.parse.quote(f"{doi}[doi]")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={query}"
    try:
        payload = fetch_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"doi": doi, "service": "pubmed", "ok": False, "error": str(exc)}
    ids = payload.get("esearchresult", {}).get("idlist", [])
    return {"doi": doi, "pubmedIds": ids, "ok": bool(ids)}


def validate(registry_path: Path, online: bool) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    failures = []
    checks = []
    doi_refs = [item for item in registry.get("references", []) if item.get("doi")]
    for item in doi_refs:
        doi = item["doi"]
        if not online:
            checks.append({"number": item["number"], "doi": doi, "eligibleForExternalCheck": True, "ok": True})
            continue
        crossref = crossref_check(doi, item.get("must_contain", []))
        pubmed = pubmed_check(doi)
        checks.append({"number": item["number"], "crossref": crossref, "pubmed": pubmed, "ok": crossref["ok"] and pubmed["ok"]})
        if not crossref["ok"]:
            failures.append({"check": "crossref", "number": item["number"], "doi": doi})
        if not pubmed["ok"]:
            failures.append({"check": "pubmed", "number": item["number"], "doi": doi})
    return {"ok": not failures, "online": online, "checkedDoiReferences": len(doi_refs), "checks": checks, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="harness/reference_registry/nhanes_undiagnosed_diabetes.references.json")
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    result = validate(Path(args.registry), args.online)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
