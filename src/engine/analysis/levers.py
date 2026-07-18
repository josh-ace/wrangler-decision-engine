"""Analysis_Levers — biggest levers sized in $ for the user.

Plug-in point for the decomposition IC (#8). Formulas are Excel-native; this
``setup_formulas(ws)`` is where the code writes them (structured references into
the ``Data_*`` tables + named-range inputs). Left empty in the scaffold beyond a
title cell — no real formulas yet, per scope.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

TAB_NAME = "Analysis_Levers"
TITLE = "Biggest levers for you (sized in $)"


def setup_formulas(ws: Worksheet) -> None:
    """Write this tab's Excel formulas. Scaffold: title only, no formulas yet."""
    ws["A1"] = TITLE
