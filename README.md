# Multi-factor Portfolio Construction Platform

This project is a demo platform for cross-sectional multi-factor portfolio construction. It includes:

- A modular Python package (`src/mfpc`) with data ingestion, factor calculation, portfolio construction, and backtesting utilities.
- An example demo script that generates synthetic data and runs a walk-forward backtest (`examples/run_demo.py`).
- A dashboard placeholder for Streamlit.
- A `requirements.txt` listing recommended dependencies.

Quick start
1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the demo to see a synthetic strategy backtest:

```powershell
python examples/run_demo.py
```

Project structure
- `src/mfpc/` - package modules: `data`, `factors`, `portfolio`, `backtest`.
- `examples/` - demo runner.
- `dashboard/` - Streamlit dashboard notes and future app.

