"""Minimal Streamlit dashboard for strategy comparison.

Run with:
    streamlit run dashboard/app.py

The app runs a small synthetic-demo workflow: generate prices, compute two factors,
rank assets, perform a walk-forward backtest and display NAV and simple metrics.
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# make sure local package is importable
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root / "src"))

import mfpc.data as data_mod
from mfpc.factors import calc_momentum, calc_volatility, calc_lowvol, calc_value, calc_quality, rank_factors
from mfpc.backtest import walk_forward, scores_to_weights


def max_drawdown(nav: pd.Series) -> float:
    roll_max = nav.cummax()
    drawdown = (nav - roll_max) / roll_max
    return drawdown.min()


st.title("Multi-factor Portfolio Construction — Demo")

with st.sidebar.expander("Data / Backtest parameters", expanded=True):
    data_source = st.selectbox("Data source", ["Synthetic", "Local CSVs"], index=0)
    if data_source == "Synthetic":
        n_assets = st.number_input("Number of assets", min_value=5, max_value=200, value=30, step=5)
        n_days = st.number_input("Historical days", min_value=252, max_value=5000, value=1000, step=252)
    else:
        csv_dir = st.text_input("Local prices directory", str(proj_root / "data" / "prices"))

    rebalance_days = st.number_input("Rebalance frequency (days)", min_value=1, max_value=252, value=21)
    top_n = st.number_input("Top N to hold (factor portfolio)", min_value=1, max_value=100, value=10)
    transaction_cost = st.number_input("Transaction cost per unit turnover", min_value=0.0, max_value=0.01, value=0.001, format="%.4f")

    available_factors = ["momentum", "value", "quality", "lowvol", "volatility"]
    sel_factors = st.multiselect("Factors to compute (combined)", available_factors, default=["momentum", "lowvol"])
    compare_factor = st.selectbox("Factor for portfolio comparison", sel_factors if sel_factors else available_factors)
    combine_eq = st.checkbox("Combine selected factors equally (composite)", value=True)
    weight_by_score = st.radio("Factor portfolio weighting", ["rank (equal among selected)", "score (proportional)"], index=0)


if st.button("Run demo"):
    st.info("Preparing prices and computing selected factors — this may take a few seconds.")
    if data_source == "Synthetic":
        prices = data_mod.load_synthetic_prices(n_assets=int(n_assets), n_days=int(n_days))
    else:
        prices = data_mod.load_prices_from_dir(csv_dir)

    # compute requested factors
    factor_map = {}
    if "momentum" in sel_factors:
        factor_map["momentum"] = calc_momentum(prices, lookback=63)
    if "volatility" in sel_factors:
        factor_map["volatility"] = calc_volatility(prices, lookback=63)
    if "lowvol" in sel_factors:
        factor_map["lowvol"] = calc_lowvol(prices, lookback=63)
    if "value" in sel_factors:
        factor_map["value"] = calc_value(prices, lookback=252)
    if "quality" in sel_factors:
        factor_map["quality"] = calc_quality(prices, lookback=252)

    st.write(f"Computed factors: {list(factor_map.keys())}")

    # composite scores (equal weight across selected factors)
    if combine_eq and factor_map:
        weights = {k: 1.0 / len(factor_map) for k in factor_map.keys()}
        composite_scores = rank_factors(factor_map, weights=weights)
    elif factor_map:
        # if not combining, just use the chosen compare factor as composite
        composite_scores = factor_map.get(compare_factor)
    else:
        st.error("No factors selected")
        st.stop()

    # prepare factor-only scores (the single chosen factor)
    factor_scores = factor_map.get(compare_factor, composite_scores)

    # prepare baseline equal-weight "scores" (ones) to generate equal weights across all assets
    ones = pd.DataFrame(1.0, index=prices.index, columns=prices.columns)

    scheme = "rank" if weight_by_score.startswith("rank") else "score"

    bt_eq, w_eq = walk_forward(prices, ones, rebalance_days=int(rebalance_days), top_n=None, scheme="rank", transaction_cost=float(transaction_cost))
    bt_fac, w_fac = walk_forward(prices, factor_scores, rebalance_days=int(rebalance_days), top_n=int(top_n), scheme=scheme.split()[0], transaction_cost=float(transaction_cost))

    st.subheader("NAV comparison")
    nav_eq = bt_eq["nav"].ffill().dropna()
    nav_fac = bt_fac["nav"].ffill().dropna()
    comp = pd.DataFrame({"EqualWeight": nav_eq, f"{compare_factor}": nav_fac}).dropna()
    st.line_chart(comp)

    # metrics
    st.write("Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("EqualWeight total return", f"{nav_eq.iloc[-1]-1.0:.2%}")
        st.metric("EqualWeight max drawdown", f"{max_drawdown(nav_eq):.2%}")
    with col2:
        st.metric("Factor total return", f"{nav_fac.iloc[-1]-1.0:.2%}")
        st.metric("Factor max drawdown", f"{max_drawdown(nav_fac):.2%}")

    # show ranking per selected compare factor (latest date)
    st.subheader(f"Latest ranking — {compare_factor}")
    latest = factor_scores.dropna(how="all").iloc[-1]
    rank_pct = latest.rank(pct=True, ascending=False)
    tbl = pd.DataFrame({"score": latest, "rank_pct": rank_pct}).sort_values("score", ascending=False)
    st.dataframe(tbl.head(50))

    st.subheader("Notes")
    st.write("This demo uses simple price-based proxies for value and quality. For production use, replace with fundamental data and add sector-neutralization and constrained optimizers.")

