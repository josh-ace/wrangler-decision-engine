"""Unit tests for Data_ModPricing — curated aftermarket mod pricing (IC #3).

These assert the mod-pricing JSON is well-formed, that every entry keys off a real
feature id in ``data/features.json``, and that ``load()`` honors the row-shape
contract while joining feature_id -> display name — on top of the generic plug-in
checks in ``tests/test_data_modules.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.data import features, mod_pricing
from engine.xlsx import PROVENANCE_COLUMNS

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_MOD_PRICING_JSON = _DATA_DIR / "mod_pricing.json"
_FEATURES_JSON = _DATA_DIR / "features.json"


def _pricing() -> dict:
    return json.loads(_MOD_PRICING_JSON.read_text(encoding="utf-8"))


def _feature_ids() -> set[str]:
    tax = json.loads(_FEATURES_JSON.read_text(encoding="utf-8"))
    return {f["id"] for f in tax["features"]}


def test_mod_pricing_json_is_well_formed_with_provenance_node():
    data = _pricing()
    assert isinstance(data["pricing"], list) and data["pricing"]
    prov = data["provenance"]
    # Curator step is cited because feature selection + typical-price choice is judgment.
    assert "curator" in prov["source"]
    assert prov["as_of_date"] == "2026-07-18"


def test_coverage_is_in_curated_range():
    # Scope guidance: ~15-25 practical aftermarket mod-target features.
    n = len(_pricing()["pricing"])
    assert 15 <= n <= 25, f"mod pricing has {n} entries, expected 15-25"


def test_every_feature_id_exists_in_features_json():
    known = _feature_ids()
    for entry in _pricing()["pricing"]:
        assert entry["feature_id"] in known, (
            f"pricing entry references unknown feature_id {entry['feature_id']!r}"
        )


def test_feature_ids_are_unique():
    ids = [e["feature_id"] for e in _pricing()["pricing"]]
    assert len(ids) == len(set(ids)), "duplicate feature_id in mod pricing"


def test_parts_cost_positive_and_install_hours_non_negative():
    for entry in _pricing()["pricing"]:
        fid = entry["feature_id"]
        assert isinstance(entry["parts_cost"], int), f"{fid}: parts_cost must be int USD"
        assert entry["parts_cost"] > 0, f"{fid}: parts_cost must be > 0"
        hours = entry["install_hours"]
        assert isinstance(hours, (int, float)), f"{fid}: install_hours must be a number"
        assert hours >= 0, f"{fid}: install_hours must be >= 0"


def test_parts_cost_range_is_coherent_when_present():
    for entry in _pricing()["pricing"]:
        rng = entry.get("parts_cost_range")
        if rng is None:
            continue
        assert rng["low"] <= entry["parts_cost"] <= rng["high"], (
            f"{entry['feature_id']}: parts_cost outside its [low, high] range"
        )


def test_every_entry_has_non_empty_retailer_sources_with_real_urls():
    for entry in _pricing()["pricing"]:
        sources = entry["retailer_sources"]
        assert isinstance(sources, list) and sources, (
            f"{entry['feature_id']}: retailer_sources must be non-empty"
        )
        for src in sources:
            assert src["retailer"] and isinstance(src["retailer"], str)
            assert src["product"] and isinstance(src["product"], str)
            assert src["url"].startswith("https://"), (
                f"{entry['feature_id']}: retailer source url must be a real https URL"
            )


def test_retailer_sources_reference_documented_retailers():
    documented = set(_pricing()["retailers"])
    for entry in _pricing()["pricing"]:
        for src in entry["retailer_sources"]:
            assert src["retailer"] in documented, (
                f"{entry['feature_id']}: retailer {src['retailer']!r} not in retailers map"
            )


def test_retailers_map_documents_url_and_reliability_tier():
    for name, meta in _pricing()["retailers"].items():
        assert meta["url"].startswith("https://"), f"{name}: retailer url must be real"
        assert meta["reliability_tier"] in {"HIGH", "MEDIUM", "LOW"}, name


def test_load_returns_rows_matching_row_shape_contract():
    rows = mod_pricing.load()
    assert len(rows) > 0
    assert len(rows) == len(_pricing()["pricing"])

    expected_width = len(mod_pricing.COLUMNS) + len(PROVENANCE_COLUMNS)
    for row in rows:
        assert len(row) == expected_width
        # [Feature, Parts_Cost, Install_Hours, Source, As_Of_Date]
        assert isinstance(row[0], str) and row[0]  # Feature (display name)
        assert row[1] > 0  # Parts_Cost
        assert row[2] >= 0  # Install_Hours
        # Provenance is populated per-row from the pricing file's provenance node.
        assert "curator" in row[-2]  # Source
        assert row[-1] == "2026-07-18"  # As_Of_Date


def test_load_joins_feature_id_to_display_name_from_taxonomy():
    # The rendered Feature column must be the taxonomy display name (join key with
    # Data_Features), not the raw feature_id slug.
    feature_rows = features.load()
    feature_names = {row[0] for row in feature_rows}  # row[0] == Feature name

    for row in mod_pricing.load():
        assert row[0] in feature_names, (
            f"mod-pricing Feature {row[0]!r} is not a Data_Features name"
        )

    # Spot-check a couple of known joins: the rear locker and the Currie/Antirock
    # equivalent of the electronic sway-bar disconnect both render by display name.
    by_feature = {row[0]: row for row in mod_pricing.load()}
    assert "Rear Locker" in by_feature
    assert "Electronic Front Sway Bar Disconnect" in by_feature
