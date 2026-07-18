"""Data_Features — curated feature taxonomy + availability matrix (IC #2).

Unlike ``trims.py`` (IC #1), which reads the parsed order guide directly, this
module reads a **curated** file, ``data/features.json``. Building the taxonomy is a
judgment step: which features to include (those that meaningfully differentiate
trims and/or are common Wrangler-buyer mod targets), what category each belongs to,
and how to reconcile the order guide's non-exhaustive "content" pages against its
separately-priced options. That curation can't be derived mechanically from the
source, so it is version-controlled as its own artifact and this module just renders
it. Provenance carries ``order_guide_2026 + curator`` to make the judgment step
visible. This establishes the pattern that later ICs read ``data/*.json`` curated
inputs where source parsing alone is not enough.

Scope of the taxonomy: ~drivetrain / suspension / wheels & tires / body armor /
lighting / tops / interior tech / ADAS / towing features that differentiate trims or
are common build targets — deliberately NOT every comfort/appearance options-page
line item. Aftermarket pricing is out of scope here (IC #17); ``Aftermarket_Price``
is left null. Per-trim factory option pricing lives in ``Data_Options`` and is joined
in ``Analysis_TrimPath``, so ``Factory_Option_Price`` is a null placeholder too (a
single scalar per feature cannot express per-trim option pricing).

Row-shape contract (unchanged from IC #1): ``load()`` returns one row per feature as
its ``COLUMNS`` values followed by the two provenance values (``Source``,
``As_Of_Date``) last — ``len(COLUMNS) + 2`` wide. Provenance is per-row, read from the
taxonomy's ``provenance`` node so a refresh dates each value honestly.
"""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Features"
TABLE_NAME = "Features"
COLUMNS = [
    "Feature",
    "Category",
    "Standard_On",
    "Factory_Option_Price",
    "Aftermarket_Price",
]

# data/features.json, resolved relative to this file (src/engine/data/features.py
# -> repo root is three parents up from the package root), matching trims.py.
_FEATURES = Path(__file__).resolve().parents[3] / "data" / "features.json"


def load() -> list[list]:
    """Return one row per feature from the curated taxonomy.

    Each row is ``[Feature, Category, Standard_On, Factory_Option_Price,
    Aftermarket_Price, Source, As_Of_Date]`` — the ``COLUMNS`` values plus the two
    provenance values last (see module docstring).

    - ``Standard_On`` is the comma-separated ``standard_on`` trim list (an informative
      denormalization; the structured per-trim list lives in ``data/features.json``
      for later formula work). It is empty for pure option / mod-target features.
    - ``Factory_Option_Price`` is always ``None`` (per-trim option pricing joins in
      from ``Data_Options`` in ``Analysis_TrimPath``).
    - ``Aftermarket_Price`` is always ``None`` (IC #17 fills it in).
    """
    taxonomy = json.loads(_FEATURES.read_text(encoding="utf-8"))
    provenance = taxonomy["provenance"]
    source = provenance["source"]
    as_of_date = provenance["as_of_date"]

    rows: list[list] = []
    for feature in taxonomy["features"]:
        rows.append(
            [
                feature["name"],
                feature["category"],
                ", ".join(feature["standard_on"]),
                None,  # Factory_Option_Price — joined from Data_Options downstream
                None,  # Aftermarket_Price — IC #17
                source,
                as_of_date,
            ]
        )
    return rows


def render(ws: Worksheet) -> None:
    """Lay the Features table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
