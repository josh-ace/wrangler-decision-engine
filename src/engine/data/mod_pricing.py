"""Data_ModPricing — feature -> parts + install hours + as_of_date.

Plug-in point for the aftermarket mod-pricing IC. Implement ``load()`` to return
rows matching ``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_ModPricing"
TABLE_NAME = "ModPricing"
COLUMNS = ["Feature", "Parts_Cost", "Install_Hours"]


def load() -> list[list]:
    """Return data rows for the ModPricing table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the ModPricing table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
