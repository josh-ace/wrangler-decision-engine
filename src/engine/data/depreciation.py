"""Data_Depreciation — JL-specific residual/depreciation curves.

Plug-in point for the depreciation IC. Implement ``load()`` to return rows
matching ``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Depreciation"
TABLE_NAME = "Depreciation"
COLUMNS = ["Config", "Age_Years", "Residual_Pct"]


def load() -> list[list]:
    """Return data rows for the Depreciation table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Depreciation table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
