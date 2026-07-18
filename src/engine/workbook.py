"""Workbook assembly — the render orchestration.

``build_workbook()`` lays down the full tab structure from the module registries
(``DATA_MODULES`` / ``ANALYSIS_MODULES``) plus the user tabs, reference tabs, and
named ranges. This is the one place that knows the overall shape of the report;
individual tabs know only themselves.
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.worksheet import Worksheet

from engine.analysis import ANALYSIS_MODULES
from engine.data import DATA_MODULES

# User-owned tabs. Python renders them once and never writes them again — refresh
# leaves them untouched so user edits survive.
INPUTS_TAB = "Inputs"
NOTES_TAB = "Notes"

# Reference tabs.
REF_PROVENANCE_TAB = "Ref_Provenance"
REF_LEGEND_TAB = "Ref_Legend"

# Single-cell runtime inputs, laid out as (label, named-range name) down column A/B
# of the Inputs tab. Each value cell is exposed as a workbook-scope named range so
# Analysis formulas reference e.g. ``Input_Horizon`` instead of ``Inputs!$B$2``.
INPUT_ROWS: list[tuple[str, str | None]] = [
    ("Horizon (years)", "Input_Horizon"),
    ("HYSA rate (%)", "Input_HYSA_Rate"),
    ("Down payment ($)", "Input_Down_Payment"),
    ("Trade-in value ($)", "Input_Trade_In"),
    ("State", "Input_State"),
    ("ZIP", "Input_ZIP"),
    ("Home charging (Y/N)", "Input_Home_Charging"),
]


def _render_inputs(ws: Worksheet) -> None:
    ws["A1"] = "Input"
    ws["B1"] = "Value"
    for offset, (label, _name) in enumerate(INPUT_ROWS, start=2):
        ws.cell(row=offset, column=1, value=label)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 18


def _render_notes(ws: Worksheet) -> None:
    ws["A1"] = "Notes"
    ws["A2"] = "Free-form space for your own notes. Python never writes this tab."
    ws.column_dimensions["A"].width = 60


def _render_ref_provenance(ws: Worksheet) -> None:
    for col, name in enumerate(["Tab", "Column", "Value", "Source", "As_Of_Date"], start=1):
        ws.cell(row=1, column=col, value=name)
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["C"].width = 24


def _render_ref_legend(ws: Worksheet) -> None:
    lines = [
        ("How to read this workbook", ""),
        ("", ""),
        ("Ownership model", "Each tab is owned by exactly one party."),
        ("Inputs, Notes", "You own these. Edit freely. `engine refresh` never touches them."),
        ("Data_*", "Python owns these. `engine refresh` rewrites their rows from source data."),
        ("Analysis_*", "Excel formulas compute these from Data_* tables + your Inputs. No Python."),
        ("Ref_*", "Reference: Ref_Provenance lists every value's source; Ref_Legend is this tab."),
        ("", ""),
        ("Discipline", ""),
        ("Excel Tables", "Data lives in named Tables (e.g. Trims[MSRP]) so refresh never breaks formulas."),  # noqa: E501
        ("Named ranges", "Single-cell Inputs are named ranges (e.g. Input_Horizon) formulas reference."),  # noqa: E501
        ("Provenance", "Every Data_* row carries Source + As_Of_Date; Ref_Provenance consolidates them."),  # noqa: E501
    ]
    for offset, (left, right) in enumerate(lines, start=1):
        ws.cell(row=offset, column=1, value=left)
        ws.cell(row=offset, column=2, value=right)
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 90


def _add_named_ranges(wb: Workbook) -> None:
    # Single-cell input named ranges (the runtime-parameter pattern).
    for offset, (_label, name) in enumerate(INPUT_ROWS, start=2):
        if name is None:
            continue
        ref = f"{INPUTS_TAB}!$B${offset}"
        wb.defined_names[name] = DefinedName(name=name, attr_text=ref)

    # At least one named range referencing a Table, demonstrating the pattern that
    # Analysis formulas will use to pull structured columns out of Data_* tables.
    wb.defined_names["Trims_MSRP"] = DefinedName(name="Trims_MSRP", attr_text="Trims[MSRP]")


def build_workbook() -> Workbook:
    """Build and return the full report workbook (in memory; caller saves it)."""
    wb = Workbook()
    # Drop the default sheet; we create every tab explicitly and in order.
    wb.remove(wb.active)

    _render_inputs(wb.create_sheet(INPUTS_TAB))
    _render_notes(wb.create_sheet(NOTES_TAB))

    for module in DATA_MODULES:
        module.render(wb.create_sheet(module.TAB_NAME))

    for module in ANALYSIS_MODULES:
        module.setup_formulas(wb.create_sheet(module.TAB_NAME))

    _render_ref_provenance(wb.create_sheet(REF_PROVENANCE_TAB))
    _render_ref_legend(wb.create_sheet(REF_LEGEND_TAB))

    _add_named_ranges(wb)
    return wb
