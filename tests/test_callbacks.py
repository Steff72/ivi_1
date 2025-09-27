"""Tests for Dash callbacks."""

from __future__ import annotations

from dash import Dash

from app.callbacks import register_callbacks


def test_register_callbacks_noop() -> None:
    """Register callbacks without raising errors."""
    app = Dash(__name__)
    register_callbacks(app)
