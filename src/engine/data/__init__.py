"""Python-owned ``Data_*`` tabs.

Each submodule declares one tab (``TAB_NAME``, ``TABLE_NAME``, ``COLUMNS``) and
exposes ``load()`` + ``render(ws)``. ``DATA_MODULES`` is the registry the renderer
and the refresh walk over — adding a new data tab means writing one module and
appending it here; nothing else in the pipeline changes.
"""

from __future__ import annotations

from types import ModuleType

from . import (
    depreciation,
    features,
    incentives,
    lease,
    mod_pricing,
    options,
    tax_rules,
    trims,
    used,
)

# Order here is the tab order in the workbook.
DATA_MODULES: list[ModuleType] = [
    trims,
    options,
    features,
    incentives,
    lease,
    mod_pricing,
    used,
    tax_rules,
    depreciation,
]

__all__ = ["DATA_MODULES"]
