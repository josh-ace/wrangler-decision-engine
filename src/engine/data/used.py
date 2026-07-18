"""Data_Used — Edmunds TMV/TCO for canonical used entries + as_of_date.

Plug-in point for IC #9 (used entries). Implement ``load()`` to return rows
matching ``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Used"
TABLE_NAME = "Used"
COLUMNS = ["Entry", "Year", "Trim", "Powertrain", "Mileage", "TMV", "TCO"]


def load() -> list[list]:
    """Return data rows for the Used table. Empty until IC #9 lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Used table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
