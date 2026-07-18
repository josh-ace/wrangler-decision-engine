"""Refresh merge logic.

`engine refresh` opens an existing report and rewrites only the Python-owned
``Data_*`` tabs from fresh source data, leaving user tabs (Inputs, Notes),
Analysis tabs, and Ref tabs exactly as the user left them. In the scaffold every
``load()`` returns no rows, so a refresh is a structure-preserving no-op — but it
exercises the real code path: clear each data table, re-render it from its module.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from engine.data import DATA_MODULES
from engine.xlsx import clear_data_table


def refresh_workbook(path: str | Path) -> Path:
    """Rewrite the ``Data_*`` tabs of the workbook at ``path`` in place.

    Only data tabs are touched. Returns the path written. Raises
    ``FileNotFoundError`` if the workbook does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No workbook to refresh at {path}")

    wb = load_workbook(path)
    for module in DATA_MODULES:
        ws = wb[module.TAB_NAME]
        clear_data_table(ws, module.TABLE_NAME)
        module.render(ws)

    wb.save(path)
    return path
