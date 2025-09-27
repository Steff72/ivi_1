CODEX_RULES.md — Rules for Implementing the Bitcoin On-Chain Visualization Project

1) Scope & Deliverables
	•	Build a Plotly Dash web app that visualizes 10 Bitcoin on-chain metrics with linked time-range exploration (overview → zoom/filter → details).
	•	Ship clean, reproducible code, tests, and a README.
	•	Data is publicly available (CSV snapshots in data/ by default; optional API adapters behind a flag).
	•	Include performance-aware interactions (snappy brushing/zooming; ≤ ~100k points rendered per chart at once).

2) Tech Stack (authoritative)
	•	Language: Python ≥ 3.11
	•	App: Plotly Dash
	•	Viz: Plotly (Graph Objects)
	•	Data wrangling: pandas, numpy
	•	Typing: typing, numpy.typing
	•	Lint/format/type: black, isort, flake8, mypy
	•	Tests: pytest
	•	Optional perf: plotly-resampler (behind feature flag)

3) Repository Layout (authoritative)

.
├── app/
│   ├── __init__.py
│   ├── main.py                  # Dash entrypoint
│   ├── layout.py                # Layout & components (no business logic)
│   ├── callbacks.py             # Dash callbacks only
│   ├── components/              # Reusable UI pieces (cards, legends, help)
│   └── styles/                  # CSS, themes
├── core/
│   ├── __init__.py
│   ├── spec.py                  # Metric & dataset schema, enums, constants
│   ├── types.py                 # Type aliases (NDArray, Frame schemas)
│   ├── loaders.py               # CSV/API loaders; caching
│   ├── transforms.py            # Resampling, smoothing, window ops
│   └── metrics.py               # Derived metrics (if computed locally)
├── data/                        # CSV snapshots; .gitignore large/raw files
├── tests/
│   ├── test_loaders.py
│   ├── test_transforms.py
│   ├── test_callbacks.py
│   └── test_contracts.py        # contract tests: shapes, columns, ranges
├── scripts/                     # one-off ETL, snapshotters
├── .pre-commit-config.yaml
├── pyproject.toml               # tool configs (black, isort, flake8, mypy)
├── README.md
└── CODEX_RULES.md               # this file

4) Data & Metric Contract (authoritative)
	•	Tidy time-series per metric: one row per day per metric.
	•	Required columns:
date: datetime64[ns, UTC], metric: str, value: float64, source: str
	•	Allowed metrics (exact ids):
price_usd, mvrv, nupl, sopr, puell_multiple, rhodl_ratio, exchange_netflow_btc, active_addresses, nvt, hash_rate_eh_s, coin_days_destroyed
	•	CSV rules: UTF-8, header row, ISO dates; no NA in date/value.
	•	Validation: load step must assert schema, monotonic dates, and non-negative where applicable (e.g., addresses, hash rate).

5) Coding Standards (strict)

5.1 PEP 8 + Tooling
	•	Format: black (line length 88) + isort (profile=black).
	•	Lint: flake8 (ban unused imports/vars; complexity ≤ 10).
	•	Type check: mypy --strict (no implicit Any; disallow untyped defs).
	•	No prints in library code. Use logging (INFO default; DEBUG guarded).
	•	Immutable config via @dataclass(frozen=True) where useful.

5.2 Typing & Aliases

In core/types.py:

from __future__ import annotations
from typing import Self, TypedDict, Literal
import numpy as np
import pandas as pd
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

MetricId = Literal[
    "price_usd", "mvrv", "nupl", "sopr", "puell_multiple", "rhodl_ratio",
    "exchange_netflow_btc", "active_addresses", "nvt", "hash_rate_eh_s",
    "coin_days_destroyed",
]

class MetricFrame(pd.DataFrame):  # for IDE help only, not enforced at runtime
    date: pd.Series  # datetime64[ns, UTC]
    metric: pd.Series  # str
    value: pd.Series  # float64
    source: pd.Series  # str

5.3 Docstrings (use this exact style)
	•	Module/class/function docstrings are triple-quoted, imperative voice.
	•	Sections order: Args:, Attributes>, Returns:, Raises: (if any).
	•	Shape annotations must be included where applicable (e.g., (n, p)).

Function template (authoritative):

from typing import Self
import numpy as np

class ExampleModel:
    def fit(self, X: np.ndarray, y: np.ndarray) -> Self:
        """Fit the model coefficients.
        Args:
            X: input data (n, p)
            y: input labels (n, )

        Attributes>
            w_: model coefficients as 1d array, including bias weight w_0

        Returns:
            self
        """
        ...
        return self

Notes
	•	Return Self when method returns the instance.
	•	Learned attributes must end with trailing underscore (e.g., w_, df_).
	•	Public functions/classes require full docstrings; private helpers may be brief but typed.

5.4 Errors & Exceptions
	•	Validate all external inputs. Raise ValueError for invalid shapes/ranges, FileNotFoundError for missing CSV, RuntimeError for inconsistent state.
	•	Never swallow exceptions; attach context:

try:
    df = load_csv(path)
except FileNotFoundError as e:
    raise FileNotFoundError(f"Missing dataset at {path}") from e

5.5 Logging
	•	Use module-level logger = logging.getLogger(__name__).
	•	Emit one-line, actionable messages; no PII, no secrets.

6) Dash App Rules

6.1 Layout vs Logic Separation
	•	layout.py: components only (no data work).
	•	callbacks.py: read-only inputs → pure functions → figure/state outputs.
	•	loaders.py / transforms.py: all I/O, caching, resampling.

6.2 Performance & UX
	•	Keep each chart to ≤ ~100k points rendered. If more:
	•	downsample via transforms.resample_for_view(df, start, end, max_points=5000)
	•	or enable plotly-resampler behind env flag USE_RESAMPLER=1.
	•	Use shared time range across charts. Single source of truth for selection state.
	•	All callbacks idempotent and fast (< 150 ms typical). Heavy ops cached.
	•	No blocking I/O in callbacks; pre-load data at app start; memoize (functools.lru_cache).

6.3 Component IDs (naming contract)
	•	Graphs: graph-<metric-id> (e.g., graph-mvrv)
	•	Global controls: control-date-range, control-metric-toggle
	•	Store(s): store-selection, store-preferences

6.4 Figure Standards
	•	Title concise; axis labeled; units in y-axis titles (e.g., Hash Rate (EH/s)).
	•	Reference lines where meaningful (e.g., SOPR=1, MVRV=1 & 3).
	•	Tooltips show date, value, and a short definition on first hover (legend hovertext).

7) Data Loading & Caching
	•	Default path: data/*.csv. Require explicit mapping of metric→filename in spec.py.
	•	All loaders:
	•	parse dates as UTC
	•	enforce schema (raise on violation)
	•	attach metric and source
	•	cache final dataframes in-process
	•	Optional API adapters must be opt-in via env var and cache responses to disk (.cache/).

8) Metrics Implementation (if computed locally)
	•	Keep pure and deterministic. E.g., NVT = market_cap / onchain_volume.
	•	Validate denominators (> 0), align frequencies (daily), fill gaps with documented policy (forward-fill only when defensible; otherwise leave NA and mask in charts).

9) Testing & QA (authoritative)
	•	pytest with -q must pass.
	•	Minimum coverage 80% of core/ and app/callbacks.py.
	•	Tests:
	•	Schema tests: columns dtypes, monotonic dates.
	•	Transform tests: resampling preserves trend; max points respected.
	•	Callback tests: given inputs → outputs stable; no exceptions; figure contains expected traces/titles.
	•	Property tests (hypothesis) for selection window invariants (optional).
	•	Run pre-commit on all commits.

10) Accessibility & UX
	•	Color-blind friendly palette; do not encode meaning by color alone.
	•	Font sizes ≥ 12px, adequate contrast. Keyboard focus visible.
	•	Provide a Help popover explaining each metric (2 lines max + “Learn more” link placeholder).

11) Security & Privacy
	•	No secrets in code. Read API keys from env; project defaults to CSV (public data).
	•	Do not log file paths that may reveal local identity info.

12) Git & CI
	•	Conventional Commits (feat:, fix:, refactor:, chore: …).
	•	Small PRs with checklist (below). CI runs lint, type, tests.
	•	Tag releases as vMAJOR.MINOR.PATCH.

13) Acceptance Checklist (must pass before merge)
	•	Lint (black, isort, flake8) and type (mypy --strict) clean
	•	Tests pass; coverage ≥ 80%
	•	Data contract validated on sample CSVs
	•	Dash app starts; interactions responsive; shared range works
	•	Figures labeled, reference lines present where defined
	•	README updated (setup, run, data sources, known limits)

⸻

14) Snippets & Templates

14.1 Loader Template

"""CSV loaders for on-chain metrics."""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
from core.types import MetricId

logger = logging.getLogger(__name__)

def load_metric_csv(path: Path, metric: MetricId, source: str) -> pd.DataFrame:
    """Load a tidy time-series metric from CSV.
    Args:
        path: path to CSV file
        metric: metric identifier
        source: human-readable source name

    Returns:
        DataFrame with columns: date, metric, value, source
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    required = {"date", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns {missing} at {path}")

    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["metric"] = metric
    df["source"] = source
    df = df[["date", "metric", "value", "source"]].sort_values("date").reset_index(drop=True)

    if df["date"].isna().any() or df["value"].isna().any():
        raise ValueError(f"Nulls found in {path}")
    if not df["date"].is_monotonic_increasing:
        raise ValueError(f"Dates not monotonic in {path}")
    return df

14.2 Transform (Downsampling) Template

def resample_for_view(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, max_points: int = 5000) -> pd.DataFrame:
    """Downsample to at most `max_points` between start/end using time-based binning.
    Args:
        df: tidy metric frame
        start: inclusive start timestamp (UTC)
        end: inclusive end timestamp (UTC)
        max_points: hard cap for plotted samples

    Returns:
        Frame resampled to <= max_points while preserving trend
    """
    view = df[(df["date"] >= start) & (df["date"] <= end)]
    n = len(view)
    if n <= max_points:
        return view
    # Compute stride in days (ceil)
    stride = int(np.ceil(n / max_points))
    return view.iloc[::stride, :].copy()

14.3 Dash Callback Skeleton

from dash import Input, Output, State
import plotly.graph_objs as go

@APP.callback(
    Output("graph-mvrv", "figure"),
    Input("store-selection", "data"),   # holds current [start, end]
    State("graph-mvrv", "figure"),
)
def update_mvrv(selection, fig_state):
    """Update MVRV figure for selected range.
    Args:
        selection: dict with 'start'/'end' ISO strings
        fig_state: previous figure (for transitions)

    Returns:
        Updated Plotly figure
    """
    start = pd.to_datetime(selection["start"], utc=True)
    end = pd.to_datetime(selection["end"], utc=True)
    df = DATA["mvrv"]                                 # preloaded tidy frame
    view = resample_for_view(df, start, end, max_points=5000)
    fig = go.Figure()
    fig.add_scatter(x=view["date"], y=view["value"], mode="lines", name="MVRV")
    for y, color, dash in [(1.0, "gray", "dot"), (3.0, "red", "dot")]:
        fig.add_hline(y=y, line_color=color, line_dash=dash)
    fig.update_layout(title="MVRV (Market/Realized Cap)", yaxis_title="ratio")
    return fig

14.4 Function Style (authoritative example)

from typing import Self
import numpy as np

class LinearModel:
    def __init__(self) -> None:
        """Initialize an empty linear model.
        Attributes>
            w_: model coefficients as 1d array, including bias weight w_0
        """
        self.w_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> Self:
        """Fit the model coefficients.
        Args:
            X: input data (n, p)
            y: input labels (n, )

        Attributes>
            w_: model coefficients as 1d array, including bias weight w_0

        Returns:
            self
        """
        n, p = X.shape
        Xb = np.c_[np.ones((n, 1)), X]        # add bias
        self.w_ = np.linalg.pinv(Xb) @ y
        return self


⸻

15) Non-Functional Requirements (binding)
	•	Startup time: < 2s on a typical student laptop with cached CSVs.
	•	Interaction latency: brushed range → charts update in < 200 ms.
	•	Memory: steady-state < 500 MB for the app process with default datasets.

⸻

Adhering to these rules ensures the agent delivers a clean, performant, and maintainable Dash app aligned with the IVI module’s expectations and your stylistic preferences.