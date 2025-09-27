# Bitcoin On-Chain Analytics Dashboard

This project hosts a Plotly Dash application for exploring key Bitcoin on-chain metrics. The
repository follows the layout defined in `project.md`, separating app code, data utilities, and
tests.

## Project Structure

- `app/`: Dash entrypoint, layout, callbacks, and reusable components.
- `core/`: Typed utilities for loading, transforming, and computing metrics.
- `data/`: Placeholder directory for CSV snapshots (tracked via `.gitkeep`).
- `scripts/`: Workspace for ETL helpers.
- `tests/`: Pytest suite covering loaders, transforms, callbacks, and contracts.
- `pyproject.toml`: Tooling configuration for formatting, linting, and tests.

## Getting Started

```bash
pip install -e .
python -m app.main
```

Run the automated tests with:

```bash
pytest
```
