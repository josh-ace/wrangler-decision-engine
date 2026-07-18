"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine import render_workbook


@pytest.fixture
def rendered_report(tmp_path: Path) -> Path:
    """Render a fresh report into a temp dir and return its path."""
    return render_workbook(tmp_path / "wrangler.xlsx")
