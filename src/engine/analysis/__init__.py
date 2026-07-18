"""Excel-computed ``Analysis_*`` tabs.

Each submodule declares one tab (``TAB_NAME``, ``TITLE``) and exposes
``setup_formulas(ws)``. Calculations live as Excel formulas in the workbook; this
code only *writes* them. ``ANALYSIS_MODULES`` is the registry the renderer walks —
adding an analysis tab means writing one module and appending it here.
"""

from __future__ import annotations

from types import ModuleType

from . import (
    financing,
    levers,
    ongoing_costs,
    sensitivity,
    sourcing,
    timing,
    trim_path,
)

# Order here is the tab order in the workbook. Levers first — it is the summary
# the user reads before the per-layer transparency sections.
ANALYSIS_MODULES: list[ModuleType] = [
    levers,
    trim_path,
    sourcing,
    financing,
    timing,
    ongoing_costs,
    sensitivity,
]

__all__ = ["ANALYSIS_MODULES"]
