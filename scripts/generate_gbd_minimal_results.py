#!/usr/bin/env python3
"""Generate the committed GBD minimal-demo result artifacts."""

from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/gbd-burden-minimal-demo"
SOURCE = DEMO / "source_exports/gbd_results_minimal_fixture.csv"
REAL_SOURCE = DEMO / "source_exports/gbd_results_real_default_data.csv"
OUT_CSV = DEMO / "results/gbd_minimal_summary.csv"
OUT_MD = DEMO / "results/gbd_minimal_summary.md"
REAL_OUT_CSV = DEMO / "results/gbd_real_default_summary.csv"
REAL_OUT_MD = DEMO / "results/gbd_real_default_summary.md"


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
    if REAL_SOURCE.exists():
        real_rows = list(csv.DictReader(REAL_SOURCE.open("r", encoding="utf-8", newline="")))
        death_number = next(row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Number" and row["year"] == "2023")
        daly_number = next(row for row in real_rows if row["measure"] == "DALYs" and row["metric"] == "Number" and row["year"] == "2023")
        death_rate_1990 = next(row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Rate" and row["year"] == "1990")
        death_rate_2023 = next(row for row in real_rows if row["measure"] == "Deaths" and row["metric"] == "Rate" and row["year"] == "2023")
        d2023 = Decimal(death_number["val"])
        y2023 = Decimal(daly_number["val"])
        rate1990 = Decimal(death_rate_1990["val"])
        rate2023 = Decimal(death_rate_2023["val"])
        rate_change = ((rate2023 - rate1990) / rate1990 * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        real_ratio = (y2023 / d2023).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        with REAL_OUT_CSV.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "gbd_release",
                    "version_id",
                    "cause",
                    "location",
                    "age",
                    "sex",
                    "year",
                    "deaths_number",
                    "dalys_number",
                    "dalys_per_death",
                    "death_rate_1990",
                    "death_rate_2023",
                    "death_rate_percent_change_1990_2023",
                    "source_endpoint",
                    "interpretation_boundary",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "gbd_release": death_number["gbd_release"],
                    "version_id": death_number["version_id"],
                    "cause": death_number["cause"],
                    "location": death_number["location"],
                    "age": death_number["age"],
                    "sex": death_number["sex"],
                    "year": death_number["year"],
                    "deaths_number": f"{d2023:.2f}",
                    "dalys_number": f"{y2023:.2f}",
                    "dalys_per_death": f"{real_ratio:.2f}",
                    "death_rate_1990": f"{rate1990:.8f}",
                    "death_rate_2023": f"{rate2023:.8f}",
                    "death_rate_percent_change_1990_2023": f"{rate_change:.2f}",
                    "source_endpoint": death_number["source_endpoint"],
                    "interpretation_boundary": "Real GBD Results Tool default endpoint output for workflow demonstration; verify query dimensions, citation, and redistribution terms before manuscript use.",
                }
            )
        REAL_OUT_MD.write_text(
            "\n".join(
                [
                    "# GBD Real Default Data Summary",
                    "",
                    "Using the GBD Results Tool public default data endpoint for GBD 2023",
                    "(version_id 8352), the global all-cause all-age both-sexes 2023",
                    f"number rows contained {fmt_decimal(d2023)} deaths and {fmt_decimal(y2023)} DALYs, yielding",
                    f"{real_ratio:.2f} DALYs per death as a derived traceability check.",
                    "",
                    f"The global all-cause death rate in this endpoint changed from {rate1990:.8f} in 1990 to {rate2023:.8f} in 2023,",
                    f"a {rate_change:.2f}% relative change in the endpoint's rate scale.",
                    "",
                    "This is a real GBD Results Tool endpoint output used for workflow demonstration.",
                    "A submission-ready GBD manuscript still requires source citation, documented query",
                    "dimensions, uncertainty interpretation, and confirmation that downloaded data may",
                    "be reused under IHME/GHDx terms.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
