"""Multi-factor Portfolio Construction (mfpc) package.

Top-level package exports a few helper functions for quick demos.
"""
from .data import load_synthetic_prices
from .factors import calc_momentum, rank_factors
from .portfolio import equal_weight_portfolio, inverse_vol_portfolio
from .backtest import rolling_backtest

__all__ = [
    "load_synthetic_prices",
    "calc_momentum",
    "rank_factors",
    "equal_weight_portfolio",
    "inverse_vol_portfolio",
    "rolling_backtest",
]

