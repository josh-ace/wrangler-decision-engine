"""Data_ModPricing — aftermarket parts cost + install hours per mod-target feature.

Reads the **curated** ``data/mod_pricing.json`` (the ``features.py`` pattern from
IC #2): representative aftermarket prices can't be derived mechanically from a source
— retailers publish no API, prices are sale/coupon-driven, and choosing which
features have a *practical* aftermarket is judgment — so the data is version-
controlled and this module just renders it. Provenance carries
``aftermarket_retailers + curator`` to make the judgment step visible.

Join model (for the downstream Excel work in ``Analysis_TrimPath``)
------------------------------------------------------------------
Each pricing entry keys off a ``feature_id`` in ``data/features.json``. ``load()``
joins at render time, looking up the feature's display ``name`` so the emitted
``Feature`` column is the same name that appears in ``Data_Features`` — the two tabs
join by Feature name, and ``Analysis_TrimPath`` will VLOOKUP / INDEX-MATCH the
aftermarket price + install hours against the feature taxonomy. Only features with a
practical aftermarket are priced, so ``Data_ModPricing`` has fewer rows than
``Data_Features`` (that's expected; a feature with no row simply has no aftermarket
path).

**Labor is not stored here.** Retailers publish no install-labor dollar figure, so the
table emits ``Install_Hours`` only; ``Analysis_TrimPath`` multiplies it by a labor
rate that comes from the user's ``Inputs`` tab (a named range added when that analysis
lands). This keeps the one non-public number a single user-editable input instead of a
baked-in guess.

Row-shape contract (unchanged from IC #1): ``load()`` returns one row per pricing
entry as its ``COLUMNS`` values followed by the two provenance values (``Source``,
``As_Of_Date``) last — ``len(COLUMNS) + 2`` wide. Provenance is per-row, read from the
mod-pricing file's ``provenance`` node so a refresh dates each value honestly.
"""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_ModPricing"
TABLE_NAME = "ModPricing"
COLUMNS = ["Feature", "Parts_Cost", "Install_Hours"]

# Curated inputs, resolved relative to this file (src/engine/data/mod_pricing.py ->
# repo root is three parents up from the package root), matching trims.py/features.py.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_MOD_PRICING = _REPO_ROOT / "data" / "mod_pricing.json"
_FEATURES = _REPO_ROOT / "data" / "features.json"


def _feature_names_by_id() -> dict[str, str]:
    """Map every ``feature_id`` in the taxonomy to its display ``name``.

    The join key: mod-pricing entries reference features by id, but the rendered
    ``Feature`` column must be the display name so ``Data_ModPricing`` joins
    ``Data_Features`` by name downstream.
    """
    taxonomy = json.loads(_FEATURES.read_text(encoding="utf-8"))
    return {feature["id"]: feature["name"] for feature in taxonomy["features"]}


def load() -> list[list]:
    """Return one row per curated pricing entry, joined to the feature display name.

    Each row is ``[Feature, Parts_Cost, Install_Hours, Source, As_Of_Date]`` — the
    ``COLUMNS`` values plus the two provenance values last (see module docstring).
    ``Feature`` is the taxonomy's display name looked up from ``feature_id``; the
    optional ``parts_cost_range`` / ``retailer_sources`` / ``notes`` in the JSON are
    preserved in the file for provenance but not projected into the Excel table.
    """
    data = json.loads(_MOD_PRICING.read_text(encoding="utf-8"))
    provenance = data["provenance"]
    source = provenance["source"]
    as_of_date = provenance["as_of_date"]

    names_by_id = _feature_names_by_id()

    rows: list[list] = []
    for entry in data["pricing"]:
        feature_id = entry["feature_id"]
        # KeyError here is the honest failure mode: a pricing entry that references a
        # feature not in the taxonomy is a data bug (tests assert this can't happen).
        feature_name = names_by_id[feature_id]
        rows.append(
            [
                feature_name,
                entry["parts_cost"],
                entry["install_hours"],
                source,
                as_of_date,
            ]
        )
    return rows


def render(ws: Worksheet) -> None:
    """Lay the ModPricing table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
