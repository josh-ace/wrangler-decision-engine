"""Data_Options — option codes, prices, applies-to-trims.

Plug-in point for the order-guide / options IC. Implement ``load()`` to return
rows matching ``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Options"
TABLE_NAME = "Options"
COLUMNS = ["Option_Code", "Name", "Price", "Applies_To_Trims"]


def load() -> list[list]:
    """Return data rows for the Options table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Options table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
