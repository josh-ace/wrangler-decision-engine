"""Analysis_Sensitivity — what input movements would flip which layer's answer.

Plug-in point for the decomposition IC (#8). ``setup_formulas(ws)`` is where the
Excel formulas get written. Scaffold: title only, no formulas yet.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

TAB_NAME = "Analysis_Sensitivity"
TITLE = "Sensitivity — what would change the picture"


def setup_formulas(ws: Worksheet) -> None:
    """Write this tab's Excel formulas. Scaffold: title only, no formulas yet."""
    ws["A1"] = TITLE
