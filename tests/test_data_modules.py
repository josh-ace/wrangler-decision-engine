"""Unit tests for the Data_* module plug-in pattern.

One test case per data module (parametrized) establishing the contract every
future IC fills in: declare the tab, return rows from ``load()``, lay a table via
``render()``.
"""

from __future__ import annotations

import pytest
from openpyxl import Workbook

from engine.data import DATA_MODULES

MODULE_IDS = [m.TAB_NAME for m in DATA_MODULES]


@pytest.mark.parametrize("module", DATA_MODULES, ids=MODULE_IDS)
def test_data_module_declares_tab_and_table(module):
    assert module.TAB_NAME.startswith("Data_")
    assert module.TABLE_NAME and " " not in module.TABLE_NAME
    assert isinstance(module.COLUMNS, list) and module.COLUMNS


@pytest.mark.parametrize("module", DATA_MODULES, ids=MODULE_IDS)
def test_data_module_load_returns_rows(module):
    rows = module.load()
    assert isinstance(rows, list)
    # Scaffold: no real data yet. When an IC lands, each row matches COLUMNS width.
    for row in rows:
        assert len(row) == len(module.COLUMNS)


@pytest.mark.parametrize("module", DATA_MODULES, ids=MODULE_IDS)
def test_data_module_render_builds_named_table(module):
    wb = Workbook()
    ws = wb.active
    module.render(ws)
    assert module.TABLE_NAME in ws.tables
