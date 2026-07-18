"""Data_Lease — money factor / residual by term/config + as_of_date.

Plug-in point for the lease-program IC. Implement ``load()`` to return rows
matching ``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Lease"
TABLE_NAME = "Lease"
COLUMNS = ["Config", "Term", "Mileage", "Money_Factor", "Residual_Pct"]


def load() -> list[list]:
    """Return data rows for the Lease table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Lease table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
