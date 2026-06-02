# Multi-factor Portfolio Construction Platform

Lightweight demo platform for cross-sectional multi-factor portfolio construction and walk-forward backtesting. The project is designed to be a clear, recruiter-friendly showcase of systematic equity portfolio construction, factor engineering, and portfolio analytics.

What’s included
- `src/mfpc/` — modular Python package with:
  - `data` : synthetic price generator + CSV loader + yfinance helper
  - `factors` : momentum, volatility, low-vol, value, quality proxies and ranking utilities
  - `portfolio` : simple portfolio constructors / helpers
  - `backtest` : rolling backtest and walk-forward utilities (turnover & transaction-cost modeling)
- `examples/` : example runners
  - `run_demo.py` — synthetic demo
  - `run_nifty_real.py` — example that loads local CSVs from `data/prices` (Nifty50 style)
- `dashboard/` : Streamlit dashboard application (`dashboard/app.py`) — interactive demo where you can select factors, compare Equal-Weighted vs factor-driven strategies, and inspect rankings.
- `requirements.txt` — recommended dependencies

Quick start
1) Create and activate a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2) Run the synthetic demo (fast):

```powershell
python examples/run_demo.py
```

3) Run the Nifty / local-CSV example (place one CSV per ticker in `data/prices`, each with columns `Date` and `Close`):

```powershell
python examples/run_nifty_real.py
```

4) Start the Streamlit dashboard (interactive):

```powershell
streamlit run dashboard/app.py
```

Dashboard features
- Choose data source: Synthetic or Local CSVs (defaults to `data/prices`).
- Select factors to compute: momentum, value, quality, low-vol, volatility.
- Build a composite by combining selected factors (equal-weight by default) or select one factor to compare.
- Compare strategies: Equal-Weighted baseline vs selected factor-based portfolio (same rebalance schedule and transaction-cost model for apples-to-apples comparison).
- View latest cross-sectional ranking (raw score + percentile) and simple performance metrics (total return, max drawdown, turnover).

Logic notes (important)
- Ranking: cross-sectional percentile ranking is computed per rebalance date. Factor numbers are computed from historical lookbacks (e.g., momentum uses a 63-day return by default; value/quality use ~252-day lookbacks). The UI exposes factor selection; lookbacks are currently set in code but can be exposed as controls if desired.
- Equal-weight baseline: the baseline is constructed by giving every asset a constant score of 1.0 at each date and converting that into equal weights at each rebalance (i.e., equal-weight across the full investable universe unless you choose top-N). Turnover and transaction costs are modeled identically to the factor portfolio.
- Transaction costs & turnover: on each rebalance we compute absolute weight changes, sum them to produce turnover, and apply a linear transaction-cost model (turnover * unit_cost).

Project structure
- `src/mfpc/` — core package
- `examples/` — small runnable examples
- `dashboard/` — Streamlit app
- `data/prices/` — (not committed) place your local CSV price files here for real-data runs

Next steps:
- Add per-factor weight sliders in the dashboard for custom composites (easy to add).
- Add sector mappings and sector-neutralization (requires a sector map CSV).
- Replace simple price-based value/quality proxies with fundamental data if you have it (e.g., data from Quandl/Refinitiv/Compustat).
- Add constrained optimizers (cvxpy) for long-only/weight caps/turnover limits.

