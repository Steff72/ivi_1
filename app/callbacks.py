"""Register Dash callbacks for interactive behavior."""

from __future__ import annotations

from typing import Any, List

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output
from dash.exceptions import PreventUpdate

from core.loaders import load_coingecko_price_history, load_mempool_hash_rate


def register_callbacks(app: Dash) -> None:
    """Register Dash callbacks for fetching data and rendering charts."""

    @app.callback(
        Output("price-data-store", "data"),
        Output("hashrate-data-store", "data"),
        Input("price-refresh", "n_intervals"),
        prevent_initial_call=False,
    )
    def fetch_market_data(
        n_intervals: int | None,
    ) -> tuple[List[dict[str, Any]], List[dict[str, Any]]]:
        """Retrieve Bitcoin market data from external APIs."""

        if n_intervals is None:
            raise PreventUpdate
        frame = load_coingecko_price_history(days=365)
        iso_frame = frame.copy()
        iso_frame["date"] = iso_frame["date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        price_records = list(iso_frame.to_dict("records"))

        hashrate_frame = load_mempool_hash_rate(period="1y")
        iso_hashrate = hashrate_frame.copy()
        iso_hashrate["date"] = iso_hashrate["date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        hashrate_records = list(iso_hashrate.to_dict("records"))
        return price_records, hashrate_records

    @app.callback(
        Output("date-range-slider", "min"),
        Output("date-range-slider", "max"),
        Output("date-range-slider", "value"),
        Input("price-data-store", "data"),
    )
    def configure_range_slider(
        records: list[dict[str, Any]] | None,
    ) -> tuple[int, int, list[int]]:
        """Set the slider bounds based on the available price history."""

        if not records:
            return 0, 1, [0, 1]
        count = len(records)
        start_index = max(count - 90, 0)
        return 0, count - 1, [start_index, count - 1]

    @app.callback(
        Output("price-chart", "figure"),
        Input("price-data-store", "data"),
        Input("hashrate-data-store", "data"),
        Input("date-range-slider", "value"),
    )
    def render_price_chart(
        price_records: list[dict[str, Any]] | None,
        hashrate_records: list[dict[str, Any]] | None,
        selected_range: list[int] | None,
    ) -> go.Figure:
        """Render a line chart for the selected Bitcoin price history window."""

        figure = go.Figure()
        figure.update_layout(
            title="Bitcoin Price and Hash Rate",
            margin=dict(l=40, r=20, t=60, b=40),
            xaxis_title="Date",
            yaxis=dict(title="Price (USD)"),
            yaxis2=dict(
                title="Hash Rate (EH/s)", overlaying="y", side="right", showgrid=False
            ),
            template="plotly_dark",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        if not price_records:
            return figure

        frame = pd.DataFrame(price_records)
        frame["date"] = pd.to_datetime(frame["date"], utc=True)
        frame = frame.sort_values("date").reset_index(drop=True)

        if not selected_range or len(selected_range) != 2:
            start_idx, end_idx = 0, len(frame) - 1
        else:
            start_idx = max(selected_range[0], 0)
            end_idx = min(selected_range[1], len(frame) - 1)
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx

        filtered = frame.iloc[start_idx : end_idx + 1]
        filtered = filtered.reset_index(drop=True)
        start_date = filtered["date"].iloc[0]
        end_date = filtered["date"].iloc[-1]
        figure.add_trace(
            go.Scatter(
                x=filtered["date"],
                y=filtered["value"],
                name="Price (USD)",
                mode="lines",
            )
        )

        if hashrate_records:
            hashrate_frame = pd.DataFrame(hashrate_records)
            hashrate_frame["date"] = pd.to_datetime(hashrate_frame["date"], utc=True)
            hashrate_frame = hashrate_frame.sort_values("date").reset_index(drop=True)
            mask = (hashrate_frame["date"] >= start_date) & (
                hashrate_frame["date"] <= end_date
            )
            subset = hashrate_frame.loc[mask]
            if not subset.empty:
                figure.add_trace(
                    go.Scatter(
                        x=subset["date"],
                        y=subset["value"],
                        name="Hash Rate (EH/s)",
                        mode="lines",
                        line=dict(color="#FFA500"),
                        yaxis="y2",
                    )
                )
        return figure
