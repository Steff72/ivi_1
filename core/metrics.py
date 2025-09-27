"""Compute derived on-chain metrics."""

from __future__ import annotations

import pandas as pd

from .types import MetricFrame


def compute_rolling_average(frame: MetricFrame, window: int) -> MetricFrame:
    """Compute a rolling average for a tidy metric frame.

    Args:
        frame: Input metric frame sorted by date.
        window: Rolling window size in days.

    Returns:
        Metric frame with averaged values.
    """
    averaged = frame.copy()
    averaged["value"] = averaged["value"].rolling(window=window, min_periods=1).mean()
    return MetricFrame(averaged)
