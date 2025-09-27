"""Implement data loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import pandas as pd
import requests

from .types import MetricFrame, MetricId


class SupportsJSONResponse(Protocol):
    """Protocol describing the subset of a ``requests`` response we rely on."""

    status_code: int

    def json(self) -> Any:  # pragma: no cover - protocol definition only
        """Return the JSON payload from the HTTP response."""

    def raise_for_status(self) -> None:  # pragma: no cover - protocol definition only
        """Raise an HTTP error if the response indicates failure."""


class SupportsGet(Protocol):
    """Protocol for objects supporting the ``requests.Session.get`` API."""

    def get(
        self, url: str, *, timeout: float
    ) -> SupportsJSONResponse:  # pragma: no cover
        """Perform an HTTP GET request and return a JSON-capable response."""


def load_metric_csv(path: Path, metric: MetricId, source: str) -> MetricFrame:
    """Load a tidy metric CSV file."""
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


COINGECKO_MARKET_CHART_URL = (
    "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
)


MEMPOOL_HASHRATE_URL = "https://mempool.space/api/v1/mining/hashrate"


def load_coingecko_price_history(
    *,
    days: int = 365,
    vs_currency: str = "usd",
    session: SupportsGet | None = None,
) -> MetricFrame:
    """Fetch daily Bitcoin prices from the CoinGecko market chart API."""

    if days <= 0:
        raise ValueError("`days` must be a positive integer")

    http = session or requests.Session()
    url = (
        f"{COINGECKO_MARKET_CHART_URL}?vs_currency={vs_currency}&days={days}"
        "&interval=daily"
    )
    response = http.get(url, timeout=10)
    response.raise_for_status()
    payload = response.json()
    prices = payload.get("prices") if isinstance(payload, dict) else None
    if not prices:
        raise ValueError("CoinGecko response missing daily price data")
    frame = pd.DataFrame(prices, columns=["timestamp_ms", "value"])
    frame["date"] = pd.to_datetime(frame["timestamp_ms"], unit="ms", utc=True)
    frame["metric"] = "price_usd"
    frame["source"] = "CoinGecko API"
    tidy = frame[["date", "metric", "value", "source"]]
    ordered = tidy.sort_values("date").reset_index(drop=True)
    return MetricFrame(ordered)


def load_mempool_hash_rate(
    *, period: str = "1y", session: SupportsGet | None = None
) -> MetricFrame:
    """Fetch Bitcoin hash rate history from the mempool.space API."""

    if not period:
        raise ValueError("`period` must be a non-empty string")

    http = session or requests.Session()
    url = f"{MEMPOOL_HASHRATE_URL}/{period}"
    response = http.get(url, timeout=10)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list) or not payload:
        raise ValueError("mempool.space response missing hash rate data")

    frame = pd.DataFrame(payload)
    if frame.empty:
        raise ValueError("mempool.space response empty")

    value_column = next(
        (
            column
            for column in ("avgHashrate", "hashrate", "value")
            if column in frame.columns
        ),
        None,
    )
    if value_column is None:
        raise ValueError("mempool.space payload missing hash rate values")

    time_column = next(
        (column for column in ("time", "timestamp", "date") if column in frame.columns),
        None,
    )
    if time_column is None:
        raise ValueError("mempool.space payload missing timestamps")

    raw_times = frame[time_column]
    if pd.api.types.is_numeric_dtype(raw_times):
        max_time = float(raw_times.max()) if not raw_times.empty else 0.0
        unit = "ms" if max_time > 10**12 else "s"
        dates = pd.to_datetime(raw_times, unit=unit, utc=True)
    else:
        dates = pd.to_datetime(raw_times, utc=True, errors="raise")

    values = pd.to_numeric(frame[value_column], errors="coerce")
    if values.isna().any():
        raise ValueError("mempool.space payload contained invalid hash rate values")

    tidy = pd.DataFrame(
        {
            "date": dates,
            "metric": "hash_rate_eh_s",
            "value": values.astype("float64"),
            "source": "mempool.space API",
        }
    )

    ordered = tidy.sort_values("date").reset_index(drop=True)
    return MetricFrame(ordered)
