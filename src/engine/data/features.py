"""Data_Features — feature taxonomy, availability matrix, three-price data.

Plug-in point for the feature-value IC (three-price transparency). Implement
``load()`` to return rows matching ``COLUMNS``; the table, refresh, and tests
already work.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Features"
TABLE_NAME = "Features"
COLUMNS = [
    "Feature",
    "Category",
    "Standard_On",
    "Factory_Option_Price",
    "Aftermarket_Price",
]


def load() -> list[list]:
    """Return data rows for the Features table. Empty until its IC lands."""
    return []


def render(ws: Worksheet) -> None:
    """Lay the Features table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
