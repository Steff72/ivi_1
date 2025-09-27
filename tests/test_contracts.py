"""Contract tests for dataset expectations."""

from __future__ import annotations

import pandas as pd

from core.types import MetricFrame


def test_metric_frame_columns() -> None:
    """Ensure metric frames expose required columns."""
    frame = MetricFrame(
        {
            "date": pd.to_datetime(["2024-01-01"], utc=True),
            "metric": ["price_usd"],
            "value": [1.0],
            "source": ["Test"],
        }
    )
    assert list(frame.columns) == ["date", "metric", "value", "source"]
