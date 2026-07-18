"""Data_Incentives — manufacturer incentives + as_of_date.

Plug-in point for the incentives IC. Implement ``load()`` to return rows matching
``COLUMNS``; the table, refresh, and tests already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Incentives"
TABLE_NAME = "Incentives"
COLUMNS = ["Program", "Type", "Amount", "Config", "Expires"]


def load() -> list[list]:
    """Return data rows for the Incentives table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Incentives table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
