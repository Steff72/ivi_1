"""Define Dash layout components."""

from __future__ import annotations

from dash import dcc, html


def create_layout() -> html.Div:
    """Create the root Dash layout container."""
    return html.Div(
        className="app-shell",
        children=[
            dcc.Store(id="price-data-store"),
            dcc.Interval(id="price-refresh", interval=24 * 60 * 60 * 1000, n_intervals=0),
            html.Header(html.H1("Bitcoin On-Chain Analytics")),
            html.Main(
                children=[
                    html.Section(
                        children=[
                            html.P(
                                "Interactive dashboard loading Bitcoin metrics from the CoinGecko API"
                            ),
                            dcc.Graph(id="price-chart"),
                            dcc.RangeSlider(
                                id="date-range-slider",
                                min=0,
                                max=1,
                                value=[0, 1],
                                allowCross=False,
                            ),
                        ]
                    ),
                ]
            ),
        ],
    )
