"""Define dataset and metric specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .types import MetricId


@dataclass(frozen=True)
class MetricSpec:
    """Describe a Bitcoin on-chain metric."""

    metric: MetricId
    name: str
    description: str
    source: str


METRIC_SPECS: Final[tuple[MetricSpec, ...]] = (
    MetricSpec(
        metric="price_usd",
        name="Price (USD)",
        description="Daily closing price for Bitcoin in USD.",
        source="Coin Metrics",
    ),
)
