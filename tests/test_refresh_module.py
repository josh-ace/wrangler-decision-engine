"""Unit tests for the refresh module plug-in point."""

from __future__ import annotations

import pytest

from engine.refresh import refresh_workbook


def test_refresh_is_callable():
    assert callable(refresh_workbook)


def test_refresh_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        refresh_workbook(tmp_path / "does_not_exist.xlsx")
