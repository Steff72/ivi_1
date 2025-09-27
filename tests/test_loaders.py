"""Tests for data loaders."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from core.loaders import load_metric_csv


def test_load_metric_csv_missing_file(tmp_path: Path) -> None:
    """Raise FileNotFoundError when CSV is absent."""
    with pytest.raises(FileNotFoundError):
        load_metric_csv(tmp_path / "missing.csv", metric="price_usd", source="Test")


def test_load_metric_csv_happy_path(tmp_path: Path) -> None:
    """Load and normalize CSV structure."""
    csv_path = tmp_path / "metric.csv"
    frame = pd.DataFrame({"date": ["2024-01-01"], "value": [1.0]})
    frame.to_csv(csv_path, index=False)
    result = load_metric_csv(csv_path, metric="price_usd", source="Test")
    assert list(result.columns) == ["date", "metric", "value", "source"]
    assert result.loc[0, "metric"] == "price_usd"
