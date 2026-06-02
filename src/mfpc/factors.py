"""Factor calculation and ranking utilities."""
from typing import Dict
import pandas as pd
import numpy as np


def calc_momentum(prices: pd.DataFrame, lookback: int = 63) -> pd.DataFrame:
    """Calculate simple total-return momentum over `lookback` days.

    Returns a DataFrame of momentum scores aligned to the price index (NaN for early rows).
    """
    returns = prices.pct_change(periods=lookback)
    return returns


def calc_volatility(prices: pd.DataFrame, lookback: int = 63) -> pd.DataFrame:
    """Calculate rolling annualized volatility using daily returns.
    """
    daily_ret = prices.pct_change()
    vol = daily_ret.rolling(window=lookback).std() * np.sqrt(252)
    return vol


def calc_lowvol(prices: pd.DataFrame, lookback: int = 63) -> pd.DataFrame:
    """Low-volatility signal: lower realized vol is better. We return inverse-vol proxy so
    that higher values indicate more desirable (lower volatility) assets.
    """
    vol = calc_volatility(prices, lookback=lookback)
    # avoid divide-by-zero
    inv = 1.0 / (vol.replace(0, np.nan))
    return inv.fillna(0.0)


def calc_value(prices: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """Simple price-based value proxy: ratio of long-term moving average to current price.

    If price is well below its long-term average, this proxy treats the asset as "cheap".
    """
    ma = prices.rolling(window=lookback).mean()
    val = ma / prices
    return val


def calc_quality(prices: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """Quality proxy: 1-year return divided by 1-year volatility (Sharpe-like).
    Higher values indicate better quality (higher risk-adjusted returns).
    """
    ret = prices.pct_change(periods=lookback)
    vol = prices.pct_change().rolling(window=lookback).std() * np.sqrt(252)
    q = ret / vol.replace(0, np.nan)
    return q.fillna(0.0)


def rank_factors(factors: Dict[str, pd.DataFrame], weights: Dict[str, float]) -> pd.DataFrame:
    """Combine multiple factor DataFrames into a single z-score rank.

    factors: mapping factor_name -> DataFrame (same shape)
    weights: factor_name -> weight (should sum to 1 but not required)

    Returns DataFrame of combined scores (higher = better).
    """
    # align all factors
    names = list(factors.keys())
    base = factors[names[0]].copy()
    score = pd.DataFrame(index=base.index, columns=base.columns, data=0.0)

    for name in names:
        f = factors[name]
        # z-score across columns (cross-section) at each date
        z = f.rank(axis=1, pct=True)
        w = weights.get(name, 1.0 / len(names))
        score = score.add(z * w, fill_value=0.0)

    return score

