"""Analysis_OngoingCosts — fuel/insurance/maintenance/tax per path over horizon N.

Plug-in point for the decomposition IC (#8). ``setup_formulas(ws)`` is where the
Excel formulas get written. Horizon N is a runtime input (a named range on Inputs),
not a build-time value. Scaffold: title only, no formulas yet.
"""

from __future__ import annotations

from openpyxl.worksheet.worksheet import Worksheet

TAB_NAME = "Analysis_OngoingCosts"
TITLE = "Ongoing costs over horizon N — by category, per path"


def setup_formulas(ws: Worksheet) -> None:
    """Write this tab's Excel formulas. Scaffold: title only, no formulas yet."""
    ws["A1"] = TITLE
