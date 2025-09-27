"""Run the Dash application entrypoint."""

from __future__ import annotations

from . import create_app


def main() -> None:
    """Start the Dash development server."""
    app = create_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
