"""Application package for the Bitcoin on-chain dashboard."""

from __future__ import annotations

from dash import Dash

from .callbacks import register_callbacks
from .layout import create_layout

__all__ = ["create_app"]


def create_app() -> Dash:
    """Create the Dash application instance.

    Returns:
        Dash application configured with layout and callbacks.
    """
    app = Dash(__name__)
    app.title = "Bitcoin On-Chain Analytics"
    app.layout = create_layout()
    register_callbacks(app)
    return app
