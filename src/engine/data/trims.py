"""Data_Trims — trim x body x powertrain with MSRP/invoice.

First real data module (IC #1). It reads ``config/order_guide.json`` and emits one
row per fully-delivered *configuration* (trim x body-style x powertrain).

Row-shape contract for every Data_* module
-------------------------------------------
``load()`` returns a list of rows. **Each row is ``COLUMNS`` values followed by the
two provenance values** (``Source``, ``As_Of_Date``) as its last two elements — i.e.
a row is ``len(COLUMNS) + len(PROVENANCE_COLUMNS)`` wide, matching the full header
``write_data_table`` lays down (``COLUMNS + PROVENANCE_COLUMNS``). The renderer writes
rows verbatim; it does *not* append provenance for you, so the module must. Every
future data module (IC #2..#N) follows this shape: emit your declared columns, then
``source`` and ``as_of_date`` last. Provenance is per-row so a refresh that pulls
different values on different dates keeps each value's date honest.
"""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl.worksheet.worksheet import Worksheet

from engine.xlsx import write_data_table

TAB_NAME = "Data_Trims"
TABLE_NAME = "Trims"
COLUMNS = ["Trim", "Body", "Powertrain", "MSRP", "Invoice"]

# config/order_guide.json, resolved relative to this file (src/engine/data/trims.py
# -> repo root is three parents up from the package root).
_ORDER_GUIDE = Path(__file__).resolve().parents[3] / "config" / "order_guide.json"

# Short, human-readable powertrain labels keyed by the guide's QOP code prefix.
# 23 = 3.6L V6 + 6-speed manual, 22 = 2.0L turbo + 8-speed auto, 24 = V6 + 8-speed
# auto (4-door only). See config/order_guide_notes.md section 2. The guide also
# carries a verbose ``powertrain`` string per config; we relabel to the compact
# "engine + transmission" form the report uses everywhere.
_POWERTRAIN_LABELS = {
    "22": "2.0T 8AT",
    "23": "V6 6MT",
    "24": "V6 8AT",
}

# Compact body-style labels keyed by the JSON's body_styles key.
_BODY_LABELS = {
    "JL_2_door": "JL 2-door",
    "JLU_4_door": "JLU 4-door",
}


def load() -> list[list]:
    """Return one row per (trim x body-style x configuration) from the order guide.

    Each row is ``[Trim, Body, Powertrain, MSRP, Invoice, Source, As_Of_Date]`` —
    the ``COLUMNS`` values plus the two provenance values last (see module docstring).
    Invoice is ``None`` for every row: the guides publish FWP and MSRP only, never a
    dealer invoice (config/order_guide_notes.md section 6).
    """
    guide = json.loads(_ORDER_GUIDE.read_text(encoding="utf-8"))
    provenance = guide["provenance"]
    source = provenance["source"]
    as_of_date = provenance["as_of_date"]

    rows: list[list] = []
    for body_key, body in guide["body_styles"].items():
        body_label = _BODY_LABELS[body_key]
        for trim in body["trims"]:
            for config in trim["configurations"]:
                powertrain = _POWERTRAIN_LABELS[config["powertrain_prefix"]]
                rows.append(
                    [
                        trim["name"],
                        body_label,
                        powertrain,
                        config["msrp"],
                        config["invoice"],  # always None by design
                        source,
                        as_of_date,
                    ]
                )
    return rows


def render(ws: Worksheet) -> None:
    """Lay the Trims table onto ``ws`` (headers + rows, or a placeholder row)."""
    write_data_table(ws, TABLE_NAME, COLUMNS, load())
