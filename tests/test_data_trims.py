"""Unit tests for the Data_Trims order-guide parser (IC #1).

Validates the row-shape contract every future data module follows: load() returns
real rows, each COLUMNS-wide plus provenance, with provenance populated.
"""

from __future__ import annotations

from engine.data import trims
from engine.xlsx import PROVENANCE_COLUMNS

EXPECTED_WIDTH = len(trims.COLUMNS) + len(PROVENANCE_COLUMNS)
# Column offsets within a row.
MSRP = trims.COLUMNS.index("MSRP")
INVOICE = trims.COLUMNS.index("Invoice")
SOURCE = len(trims.COLUMNS)  # first provenance column
AS_OF = len(trims.COLUMNS) + 1


def test_load_returns_rows():
    rows = trims.load()
    assert len(rows) > 0


def test_every_row_has_columns_plus_provenance_shape():
    for row in trims.load():
        assert len(row) == EXPECTED_WIDTH


def test_provenance_populated_on_every_row():
    for row in trims.load():
        assert row[SOURCE] == "order_guide_2026"
        assert row[AS_OF] == "2025-08-06"


def test_msrp_is_a_positive_number_invoice_is_none():
    for row in trims.load():
        assert isinstance(row[MSRP], (int, float)) and row[MSRP] > 0
        # Guides publish FWP + MSRP only; invoice is null by design (notes sec. 6).
        assert row[INVOICE] is None


def test_powertrain_labels_are_the_compact_form():
    labels = {row[trims.COLUMNS.index("Powertrain")] for row in trims.load()}
    assert labels == {"V6 6MT", "2.0T 8AT", "V6 8AT"}
