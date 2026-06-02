"""Portfolio construction methods."""
import numpy as np
import pandas as pd


def equal_weight_portfolio(assets: pd.Index) -> pd.Series:
    w = np.repeat(1.0 / len(assets), len(assets))
    return pd.Series(w, index=assets)


def inverse_vol_portfolio(prices: pd.DataFrame, lookback: int = 63) -> pd.Series:
    """Simple risk parity-ish weights: inverse of recent volatility.

    Returns weights (not normalized to leverage; normalized to sum to 1).
    """
    daily = prices.pct_change()
    vol = daily.rolling(window=lookback).std().iloc[-1]
    inv = 1.0 / vol.replace(0, np.nan)
    inv = inv.fillna(0.0)
    w = inv / inv.sum()
    return w


def mean_variance_weights(expected_returns: pd.Series, cov: pd.DataFrame, risk_aversion: float = 1.0) -> pd.Series:
    """Classic mean-variance closed form if unconstrained: w = (1/risk_aversion) * inv(C) * mu

    If cvxpy is available we could add constraints, but this function returns the unconstrained solution.
    """
    inv_cov = np.linalg.pinv(cov.values)
    w = (1.0 / risk_aversion) * inv_cov.dot(expected_returns.values)
    # normalize to sum 1 for long-only style (if all weights positive); caller can re-scale
    try:
        w_series = pd.Series(w, index=cov.index)
    except Exception:
        w_series = pd.Series(w)
    # if negatives exist, normalize in absolute terms
    if (w_series < 0).any():
        # fallback: shift to non-negative by setting negatives to zero then normalize
        w_series = w_series.clip(lower=0.0)
    if w_series.sum() == 0:
        # fallback to equal weight
        w_series = pd.Series(1.0 / len(w_series), index=w_series.index)
    else:
        w_series = w_series / w_series.sum()
    return w_series


