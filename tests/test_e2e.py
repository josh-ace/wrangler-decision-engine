"""End-to-end tests exercising the whole pipeline through the CLI.

These are the tests future ICs extend: when a module fills in real data or
formulas, its assertions grow here alongside the smoke test.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from openpyxl import load_workbook

from engine.analysis import ANALYSIS_MODULES
from engine.cli import main
from engine.data import DATA_MODULES, features, trims
from engine.workbook import (
    INPUTS_TAB,
    NOTES_TAB,
    REF_LEGEND_TAB,
    REF_PROVENANCE_TAB,
)

_FEATURES_JSON = Path(__file__).resolve().parents[1] / "data" / "features.json"

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


def _read_table_rows(ws, header):
    """Return the Data_* tab's rows (below the header) as a list of dict rows keyed
    by column name, reading straight from the worksheet cells."""
    names = [c.value for c in ws[1]]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(names, r)))
    assert names[: len(header)] == header
    return rows


def test_data_trims_has_real_rows_with_values_and_provenance(tmp_path):
    runner = CliRunner()
    out = tmp_path / "wrangler.xlsx"
    assert runner.invoke(main, ["render", "-o", str(out)]).exit_code == 0

    wb = load_workbook(out)
    ws = wb[trims.TAB_NAME]
    rows = _read_table_rows(ws, trims.COLUMNS)

    # One row per (trim x body x configuration) — 28 across both body styles.
    assert len(rows) == 28

    # Every row carries populated provenance.
    for row in rows:
        assert row["Source"] == "order_guide_2026"
        assert row["As_Of_Date"] == "2025-08-06"

    # Spot-check a known 2-door value: Sport V6 6MT MSRP = $33,785.
    sport_2dr = next(
        r for r in rows
        if r["Trim"] == "Sport" and r["Body"] == "JL 2-door" and r["Powertrain"] == "V6 6MT"
    )
    assert sport_2dr["MSRP"] == 33785
    assert sport_2dr["Invoice"] is None

    # Spot-check a known 4-door value: Rubicon V6 6MT MSRP = $49,270.
    rubicon_4dr = next(
        r for r in rows
        if r["Trim"] == "Rubicon" and r["Body"] == "JLU 4-door" and r["Powertrain"] == "V6 6MT"
    )
    assert rubicon_4dr["MSRP"] == 49270


def test_data_features_has_real_taxonomy_rows(tmp_path):
    runner = CliRunner()
    out = tmp_path / "wrangler.xlsx"
    assert runner.invoke(main, ["render", "-o", str(out)]).exit_code == 0

    taxonomy = json.loads(_FEATURES_JSON.read_text(encoding="utf-8"))

    wb = load_workbook(out)
    ws = wb[features.TAB_NAME]
    rows = _read_table_rows(ws, features.COLUMNS)

    # Row count matches the taxonomy exactly.
    assert len(rows) == len(taxonomy["features"])

    # Feature ids (slugs) are all unique — no duplicate features in the taxonomy.
    ids = [f["id"] for f in taxonomy["features"]]
    assert len(ids) == len(set(ids))

    # Every rendered row carries curator-attributed provenance and null prices.
    for row in rows:
        assert "curator" in row["Source"]
        assert row["As_Of_Date"] == "2026-07-18"
        assert row["Factory_Option_Price"] is None
        assert row["Aftermarket_Price"] is None

    by_feature = {row["Feature"]: row for row in rows}

    # Spot-check known off-road features and their standard-on availability.
    assert "Rubicon" in by_feature["Rear Locker"]["Standard_On"]
    rock_rails = by_feature["Rock Rails"]["Standard_On"]
    assert "Willys" in rock_rails and "Rubicon" in rock_rails


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
