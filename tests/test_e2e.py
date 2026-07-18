"""End-to-end tests exercising the whole pipeline through the CLI.

These are the tests future ICs extend: when a module fills in real data or
formulas, its assertions grow here alongside the smoke test.
"""

from __future__ import annotations

from click.testing import CliRunner
from openpyxl import load_workbook

from engine.analysis import ANALYSIS_MODULES
from engine.cli import main
from engine.data import DATA_MODULES
from engine.workbook import (
    INPUTS_TAB,
    NOTES_TAB,
    REF_LEGEND_TAB,
    REF_PROVENANCE_TAB,
)

# Authoritative expected tab set, derived from the same registries the renderer
# uses — add a module and this expectation updates itself.
EXPECTED_TABS = [
    INPUTS_TAB,
    NOTES_TAB,
    *[m.TAB_NAME for m in DATA_MODULES],
    *[m.TAB_NAME for m in ANALYSIS_MODULES],
    REF_PROVENANCE_TAB,
    REF_LEGEND_TAB,
]


def test_render_produces_all_tabs_tables_and_named_range(tmp_path):
    runner = CliRunner()
    out = tmp_path / "wrangler.xlsx"

    result = runner.invoke(main, ["render", "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()

    wb = load_workbook(out)

    # Every expected tab exists.
    assert wb.sheetnames == EXPECTED_TABS

    # Every Data_* tab has its Excel Table set up.
    for module in DATA_MODULES:
        ws = wb[module.TAB_NAME]
        assert module.TABLE_NAME in ws.tables, f"{module.TAB_NAME} missing its table"

    # At least one named range exists (and the table-referencing one is present).
    assert wb.defined_names
    assert "Trims_MSRP" in wb.defined_names


def test_refresh_preserves_user_edits(tmp_path):
    runner = CliRunner()
    out = tmp_path / "wrangler.xlsx"

    assert runner.invoke(main, ["render", "-o", str(out)]).exit_code == 0

    # User edits a cell on the Inputs tab (the HYSA-rate value cell).
    wb = load_workbook(out)
    wb[INPUTS_TAB]["B3"] = 4.75
    wb.save(out)

    # Refresh rewrites Data_* tabs only.
    result = runner.invoke(main, ["refresh", str(out)])
    assert result.exit_code == 0, result.output

    # The user's edit survives, and the data tables are still intact.
    wb2 = load_workbook(out)
    assert wb2[INPUTS_TAB]["B3"].value == 4.75
    for module in DATA_MODULES:
        assert module.TABLE_NAME in wb2[module.TAB_NAME].tables


def test_refresh_missing_file_errors_cleanly(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["refresh", str(tmp_path / "nope.xlsx")])
    assert result.exit_code != 0
    assert "No workbook to refresh" in result.output
