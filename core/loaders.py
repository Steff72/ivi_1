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

    def get(self, url: str, *, timeout: float) -> SupportsJSONResponse:  # pragma: no cover
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
