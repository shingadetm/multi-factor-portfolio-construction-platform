"""Backtesting and walk-forward utilities."""
from typing import Optional
import pandas as pd


def scores_to_weights(scores: pd.DataFrame, top_n: Optional[int] = None, scheme: str = "rank") -> pd.DataFrame:
    """Convert cross-sectional scores at each date into portfolio weights.

    - If top_n is provided, only the top_n assets by score get positive weight.
    - scheme 'rank' gives equal weights to selected assets.
    - scheme 'score' allocates proportionally to the score (non-negative portion).
    Returns a DataFrame of weights with the same index and columns as scores.
    """
    weights = pd.DataFrame(0.0, index=scores.index, columns=scores.columns)

    for dt in scores.index:
        row = scores.loc[dt].dropna()
        if row.empty:
            continue
        if top_n is not None:
            sel = row.nlargest(top_n)
        else:
            sel = row

        if scheme == "rank":
            w = pd.Series(1.0 / len(sel), index=sel.index)
        else:
            # ensure non-negative allocation
            v = sel.clip(lower=0.0)
            if v.sum() == 0:
                w = pd.Series(1.0 / len(sel), index=sel.index)
            else:
                w = v / v.sum()

        weights.loc[dt, w.index] = w.values

    return weights


def rolling_backtest(prices: pd.DataFrame, weight_index: pd.DataFrame, transaction_cost: float = 0.001) -> pd.DataFrame:
    """Backtest given price series and discrete weights at rebalance dates.

    weight_index: DataFrame with weights at rebalance dates (subset of price dates). The function
    will assume weights hold until the next provided weight date.

    Returns a DataFrame with portfolio daily returns, cumulative returns, turnover, and NAV.
    """
    # daily returns
    daily_ret = prices.pct_change().fillna(0.0)

    # ensure weights are aligned: reindex to price index with forward fill
    w_daily = weight_index.reindex(prices.index).ffill().fillna(0.0)

    # compute portfolio returns = (weights at previous close) * daily returns
    # On rebalance day, we model transaction costs based on weight changes from previous day's weights
    prev_w = w_daily.shift(1).fillna(0.0)
    delta = (w_daily - prev_w).abs()
    turnover = delta.sum(axis=1)
    tc_cost = turnover * transaction_cost

    # daily portfolio returns before costs
    port_ret = (prev_w * daily_ret).sum(axis=1)
    # subtract transaction costs on the days trades executed (we assume cost applied same day)
    port_ret = port_ret - tc_cost

    nav = (1 + port_ret).cumprod()

    out = pd.DataFrame({
        "port_ret": port_ret,
        "nav": nav,
        "turnover": turnover,
        "tc_cost": tc_cost,
    }, index=prices.index)

    return out


def walk_forward(prices: pd.DataFrame, factor_scores: pd.DataFrame, lookback: int = 252, rebalance_days: int = 21, top_n: Optional[int] = 10, scheme: str = "rank", transaction_cost: float = 0.001):
    """Perform a rolling walk-forward: at each rebalance (every rebalance_days),
    compute weights from the most recent factor_scores (assumed already aligned with prices),
    then backtest out-of-sample until the next rebalance.

    Returns combined backtest DataFrame and the weights DataFrame used at each rebalance date.
    """
    dates = prices.index
    rebalance_dates = dates[::rebalance_days]
    weights = scores_to_weights(factor_scores.loc[rebalance_dates.intersection(factor_scores.index)], top_n=top_n, scheme=scheme)

    bt = rolling_backtest(prices, weights, transaction_cost=transaction_cost)
    return bt, weights


