"""Data ingestion utilities.

For demonstration we provide a synthetic price generator and a thin wrapper
for downloading price data via yfinance (optional dependency).
"""
from typing import List, Optional
import numpy as np
import pandas as pd


def load_synthetic_prices(n_assets: int = 10, n_days: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic price series for n_assets over n_days.

    Returns a DataFrame indexed by daily dates with columns Asset0..Asset{n-1}.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=n_days)
    # simulate log returns with asset-specific drift and volatility
    drifts = rng.normal(0.0002, 0.0005, size=n_assets)
    vols = rng.uniform(0.01, 0.03, size=n_assets)
    rets = rng.normal(loc=drifts, scale=vols, size=(n_days, n_assets))
    prices = 100 * np.exp(np.cumsum(rets, axis=0))
    cols = [f"Asset{i}" for i in range(n_assets)]
    return pd.DataFrame(prices, index=dates, columns=cols)


def load_prices_yf(tickers: List[str], start: str, end: Optional[str] = None) -> pd.DataFrame:
    """Download adjusted close prices using yfinance.

    yfinance is optional; raise ImportError with guidance if missing.
    Returns DataFrame with tickers as columns.
    """
    try:
        import yfinance as yf
    except Exception as e:
        raise ImportError("yfinance is required for download. Install via pip install yfinance") from e

    data = yf.download(tickers, start=start, end=end, progress=False)["Adj Close"]
    # ensure DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data = data.dropna(how="all")
    return data


def load_prices_from_dir(directory: str, pattern: str = "*.csv", price_col: str = "Close") -> pd.DataFrame:
    """Load price CSVs from a directory into a single DataFrame of close prices.

    Each CSV should have a 'Date' column and a `price_col` column (default 'Close').
    The column names in the resulting DataFrame are the filenames without extension.
    """
    import os
    import glob

    files = sorted(glob.glob(os.path.join(directory, pattern)))
    if not files:
        raise FileNotFoundError(f"No files found in {directory} matching {pattern}")

    series_list = []
    names = []
    for fp in files:
        df = pd.read_csv(fp)
        if "Date" not in df.columns:
            raise ValueError(f"CSV {fp} missing 'Date' column")
        if price_col not in df.columns:
            raise ValueError(f"CSV {fp} missing '{price_col}' column")
        s = pd.Series(df[price_col].values, index=pd.to_datetime(df["Date"]))
        # use filename (without extension) as column name
        name = os.path.splitext(os.path.basename(fp))[0]
        s.name = name
        series_list.append(s)
        names.append(name)

    prices = pd.concat(series_list, axis=1).sort_index()
    # forward/backfill small gaps conservatively
    prices = prices.sort_index().ffill().bfill()
    prices.columns = names
    return prices


