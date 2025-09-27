"""Tests for transform utilities."""

from __future__ import annotations

import pandas as pd

from core.transforms import resample_for_view


def test_resample_for_view_downsamples() -> None:
    """Downsample frames exceeding the maximum points."""
    dates = pd.date_range("2024-01-01", periods=10, tz="UTC")
    frame = pd.DataFrame(
        {
            "date": dates,
            "metric": "price_usd",
            "value": range(10),
            "source": "Test",
        }
    )
    result = resample_for_view(frame, dates[0], dates[-1], max_points=5)
    assert len(result) <= 5
