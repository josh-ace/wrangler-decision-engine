"""Wrangler decision engine — data loader + renderer for the report .xlsx.

Public API:
    render_workbook(output)   build a fresh report and save it
    refresh_workbook(path)    rewrite Data_* tabs of an existing report in place

Python's role stops at producing and updating the file. Once rendered, the .xlsx
is self-contained: Excel formulas drive every calculation.
"""

from __future__ import annotations

from pathlib import Path

from engine.refresh import refresh_workbook
from engine.workbook import build_workbook

__all__ = ["build_workbook", "render_workbook", "refresh_workbook"]


def render_workbook(output: str | Path) -> Path:
    """Build the report workbook and save it to ``output``. Returns the path."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb = build_workbook()
    wb.save(output)
    return output
