"""Unit tests for the Analysis_* module plug-in pattern.

One test case per analysis module (parametrized). The contract: declare the tab
and expose ``setup_formulas(ws)`` where a future IC writes Excel formulas.
"""

from __future__ import annotations

import pytest
from openpyxl import Workbook

from engine.analysis import ANALYSIS_MODULES

MODULE_IDS = [m.TAB_NAME for m in ANALYSIS_MODULES]


@pytest.mark.parametrize("module", ANALYSIS_MODULES, ids=MODULE_IDS)
def test_analysis_module_declares_tab(module):
    assert module.TAB_NAME.startswith("Analysis_")
    assert module.TITLE


@pytest.mark.parametrize("module", ANALYSIS_MODULES, ids=MODULE_IDS)
def test_analysis_module_setup_formulas_runs(module):
    wb = Workbook()
    ws = wb.active
    module.setup_formulas(ws)  # stub: writes a title, no formulas yet
    assert ws["A1"].value == module.TITLE
