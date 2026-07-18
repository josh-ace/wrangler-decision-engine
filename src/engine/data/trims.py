"""Data_Trims — trim x body x powertrain with MSRP/invoice.

Plug-in point for IC #1 (order-guide parse). To fill this tab with real data,
implement ``load()`` to read ``config/order_guide.json`` and return one list per
row matching ``COLUMNS`` (provenance columns are appended by the renderer). The
rest of the pipeline — the table, refresh, tests — already works.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Trims"
TABLE_NAME = "Trims"
COLUMNS = ["Trim", "Body", "Powertrain", "MSRP", "Invoice"]


def load() -> list[list]:
    """Return data rows for the Trims table. Empty until IC #1 lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Trims table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
