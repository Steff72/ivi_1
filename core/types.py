"""Declare shared typing aliases."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

MetricId = Literal[
    "price_usd",
    "mvrv",
    "nupl",
    "sopr",
    "puell_multiple",
    "rhodl_ratio",
    "exchange_netflow_btc",
    "active_addresses",
    "nvt",
    "hash_rate_eh_s",
    "coin_days_destroyed",
]


class MetricFrame(pd.DataFrame):
    """Typed DataFrame representing a tidy metric."""

    date: pd.Series
    metric: pd.Series
    value: pd.Series
    source: pd.Series
