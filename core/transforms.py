"""Provide time-series transformation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .types import MetricFrame


def resample_for_view(
    frame: MetricFrame, start: pd.Timestamp, end: pd.Timestamp, max_points: int = 5000
) -> MetricFrame:
    """Downsample a metric frame for visualization.

    Args:
        frame: Input metric frame sorted by date.
        start: Inclusive start timestamp (UTC).
        end: Inclusive end timestamp (UTC).
        max_points: Maximum number of rows to retain.

    Returns:
        Downsampled metric frame within the selected range.
    """
    view = frame[(frame["date"] >= start) & (frame["date"] <= end)]
    count = len(view)
    if count <= max_points:
        return MetricFrame(view.copy())
    stride = int(np.ceil(count / max_points))
    return MetricFrame(view.iloc[::stride, :].copy())
