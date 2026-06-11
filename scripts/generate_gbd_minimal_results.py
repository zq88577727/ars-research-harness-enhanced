#!/usr/bin/env python3
"""Generate the committed GBD minimal-demo result artifacts."""

from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/gbd-burden-minimal-demo"
SOURCE = DEMO / "source_exports/gbd_results_minimal_fixture.csv"
OUT_CSV = DEMO / "results/gbd_minimal_summary.csv"
OUT_MD = DEMO / "results/gbd_minimal_summary.md"


def fmt_decimal(value: Decimal) -> str:
    return f"{value:,.2f}"


def main() -> int:
    rows = list(csv.DictReader(SOURCE.open("r", encoding="utf-8", newline="")))
    deaths = next(row for row in rows if row["measure"] == "Deaths")
    dalys = next(row for row in rows if row["measure"] == "DALYs")
    death_value = Decimal(deaths["val"])
    daly_value = Decimal(dalys["val"])
    ratio = (daly_value / death_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gbd_release",
                "cause",
                "location",
                "age",
                "sex",
                "year",
                "deaths_number",
                "dalys_number",
                "dalys_per_death",
                "interpretation_boundary",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "gbd_release": deaths["gbd_release"],
                "cause": deaths["cause"],
                "location": deaths["location"],
                "age": deaths["age"],
                "sex": deaths["sex"],
                "year": deaths["year"],
                "deaths_number": f"{death_value:.2f}",
                "dalys_number": f"{daly_value:.2f}",
                "dalys_per_death": f"{ratio:.2f}",
                "interpretation_boundary": "Teaching fixture for workflow traceability; not a publishable burden estimate until replaced with an approved GBD export and full citation.",
            }
        )

    OUT_MD.write_text(
        "\n".join(
            [
                "# GBD Minimal Result Summary",
                "",
                "In the minimal GBD Results-style teaching fixture, the global all-cause 2023",
                f"number rows contained {fmt_decimal(death_value)} deaths and {fmt_decimal(daly_value)} DALYs, yielding",
                f"{ratio:.2f} DALYs per death as a derived traceability check.",
                "",
                "This result is a workflow fixture, not a publishable disease-burden estimate.",
                "A real GBD manuscript must replace the fixture with an approved export, retain",
                "release version and query dimensions, cite IHME/GHDx appropriately, and",
                "interpret uncertainty intervals, metric type, age-standardization status, cause,",
                "location, age, sex, and year without mixing counts, rates, and percentages.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
