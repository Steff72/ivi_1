"""Implement data loading helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .types import MetricFrame, MetricId


def load_metric_csv(path: Path, metric: MetricId, source: str) -> MetricFrame:
    """Load a tidy metric CSV file.

    Args:
        path: Path to the CSV file.
        metric: Metric identifier.
        source: Human-readable data source name.

    Returns:
        DataFrame with columns date, metric, value, and source.
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    frame = pd.read_csv(path)
    if "date" not in frame.columns or "value" not in frame.columns:
        missing = {"date", "value"} - set(frame.columns)
        raise ValueError(f"CSV missing columns {missing} at {path}")
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    frame["metric"] = metric
    frame["source"] = source
    ordered = frame[["date", "metric", "value", "source"]].sort_values("date")
    return MetricFrame(ordered.reset_index(drop=True))
