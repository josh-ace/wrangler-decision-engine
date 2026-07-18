"""Data_TaxRules — state x rate; federal credit status.

Plug-in point for the tax-rules IC. Implement ``load()`` to return rows matching
``COLUMNS``; the table, refresh, and tests already work. Note per finding #1:
federal EV credits (§30D/§25E/§45W) are dead for vehicles acquired after
2025-09-30, so ``Federal_Credit_Status`` will read as expired for all configs.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_TaxRules"
TABLE_NAME = "TaxRules"
COLUMNS = [
    "State",
    "Sales_Tax_Rate",
    "Doc_Fee",
    "Property_Tax_Rate",
    "Federal_Credit_Status",
]


def load() -> list[list]:
    """Return data rows for the TaxRules table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the TaxRules table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
