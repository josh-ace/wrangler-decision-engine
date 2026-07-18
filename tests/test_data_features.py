"""Unit tests for Data_Features — the curated feature taxonomy (IC #2).

These assert the taxonomy JSON is well-formed and that ``load()`` honors the
row-shape contract, on top of the generic plug-in checks in
``tests/test_data_modules.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.data import features, trims
from engine.xlsx import PROVENANCE_COLUMNS

# The curated taxonomy file, resolved the same way the module resolves it.
_FEATURES_JSON = Path(__file__).resolve().parents[1] / "data" / "features.json"


def _taxonomy() -> dict:
    return json.loads(_FEATURES_JSON.read_text(encoding="utf-8"))


def test_features_json_is_well_formed_with_provenance_node():
    tax = _taxonomy()
    assert isinstance(tax["features"], list) and tax["features"]
    prov = tax["provenance"]
    # Curator step is cited because the taxonomy involves judgment.
    assert "curator" in prov["source"]
    assert prov["as_of_date"] == "2026-07-18"


def test_taxonomy_size_is_in_curated_range():
    # Scope guidance: ~30-60 features that differentiate trims and/or are mod targets.
    n = len(_taxonomy()["features"])
    assert 30 <= n <= 60, f"taxonomy has {n} features, expected 30-60"


def test_every_feature_has_id_name_and_category_in_closed_set():
    tax = _taxonomy()
    closed_categories = set(tax["categories"])
    for feature in tax["features"]:
        assert feature["id"] and isinstance(feature["id"], str)
        assert feature["name"] and isinstance(feature["name"], str)
        assert feature["category"] in closed_categories, feature["id"]


def test_feature_ids_are_unique_snake_case_slugs():
    ids = [f["id"] for f in _taxonomy()["features"]]
    assert len(ids) == len(set(ids)), "duplicate feature ids (slugs) in taxonomy"
    for fid in ids:
        assert fid == fid.lower()
        assert " " not in fid and "-" not in fid


def test_standard_on_references_known_trim_names():
    tax = _taxonomy()
    known = set(tax["trims"])
    for feature in tax["features"]:
        standard_on = feature["standard_on"]
        assert isinstance(standard_on, list)
        for trim in standard_on:
            assert trim in known, f"{feature['id']} lists unknown trim {trim!r}"


def test_declared_trims_are_real_trims_from_data_trims():
    # The taxonomy's trim vocabulary must match Data_Trims (minus fleet Sport RHD),
    # so standard_on can later join against the Trims table.
    trim_rows = trims.load()
    real_trims = {row[0] for row in trim_rows}  # row[0] == Trim name
    for trim in _taxonomy()["trims"]:
        assert trim in real_trims, f"taxonomy trim {trim!r} not in Data_Trims"


def test_load_returns_rows_matching_row_shape_contract():
    rows = features.load()
    assert len(rows) > 0
    assert len(rows) == len(_taxonomy()["features"])

    expected_width = len(features.COLUMNS) + len(PROVENANCE_COLUMNS)
    for row in rows:
        assert len(row) == expected_width
        # Placeholder price columns are null for IC #2.
        assert row[3] is None  # Factory_Option_Price
        assert row[4] is None  # Aftermarket_Price
        # Provenance is populated per-row from the taxonomy's provenance node.
        assert "curator" in row[-2]  # Source
        assert row[-1] == "2026-07-18"  # As_Of_Date


def test_standard_on_is_rendered_comma_separated():
    rows = features.load()
    by_feature = {row[0]: row for row in rows}
    # Rear Locker comes standard on Willys + Rubicon + Rubicon X.
    assert by_feature["Rear Locker"][2] == "Willys, Rubicon, Rubicon X"
    # Pure option / mod-target features render an empty Standard_On.
    assert by_feature["Steel Front & Rear Bumpers"][2] == ""
