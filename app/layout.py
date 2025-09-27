"""Define Dash layout components."""

from __future__ import annotations

from dash import dcc, html


def create_layout() -> html.Div:
    """Create the root Dash layout container."""
    return html.Div(
        className="app-shell",
        children=[
            html.Header(html.H1("Bitcoin On-Chain Analytics")),
            html.Main(
                children=[
                    html.Section(
                        children=[
                            html.P(
                                "Interactive dashboard for Bitcoin on-chain metrics"
                            ),
                            dcc.Graph(id="price-chart"),
                            dcc.Graph(id="mvrv-chart"),
                            dcc.Graph(id="sopr-chart"),
                            dcc.Graph(id="active-chart"),
                            dcc.RangeSlider(id="date-range-slider", min=0, max=1, value=[0, 1]),
                        ]
                    ),
                ]
            ),
        ],
    )
