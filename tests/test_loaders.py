"""Tests for data loaders."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import requests

from core.loaders import load_coingecko_price_history, load_metric_csv


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


class _FakeResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict[str, object]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class _FakeSession:
    def __init__(self, payload: dict[str, object], status_code: int = 200) -> None:
        self._payload = payload
        self._status_code = status_code
        self.requested_urls: list[str] = []

    def get(self, url: str, *, timeout: float) -> _FakeResponse:
        self.requested_urls.append(url)
        return _FakeResponse(self._payload, status_code=self._status_code)


def test_load_coingecko_price_history_parses_payload() -> None:
    """Convert CoinGecko price payload into a MetricFrame."""

    payload = {
        "prices": [
            [1700000000000, 42000.0],
            [1700086400000, 43000.5],
        ]
    }
    session = _FakeSession(payload)
    frame = load_coingecko_price_history(days=30, session=session)

    assert len(frame) == 2
    assert frame.loc[0, "metric"] == "price_usd"
    assert any("days=30" in url for url in session.requested_urls)


def test_load_coingecko_price_history_rejects_missing_prices() -> None:
    """Raise ValueError when the API does not provide price data."""

    session = _FakeSession({}, status_code=200)
    with pytest.raises(ValueError):
        load_coingecko_price_history(session=session)
