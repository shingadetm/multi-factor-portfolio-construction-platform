"""Run the platform on local Nifty50 CSV prices stored in data/prices.

Place the 50 CSV files (one per ticker) in `data/prices/` and run this script.
Each CSV must contain columns: Date,Open,High,Low,Close,Volume (Close is used).
"""
import sys
from pathlib import Path
import matplotlib.pyplot as plt

proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root / "src"))

from mfpc.data import load_prices_from_dir
from mfpc.factors import calc_momentum, calc_volatility, rank_factors
from mfpc.backtest import walk_forward


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "prices"
    print(f"Loading CSVs from {data_dir}")
    prices = load_prices_from_dir(str(data_dir), pattern="*.csv", price_col="Close")

    print("Computing factors")
    mom = calc_momentum(prices, lookback=63)
    vol = calc_volatility(prices, lookback=63)

    print("Ranking factors and running walk-forward backtest")
    scores = rank_factors({"momentum": mom, "vol": vol}, weights={"momentum": 0.7, "vol": 0.3})
    bt, weights = walk_forward(prices, scores, rebalance_days=21, top_n=10, scheme="rank", transaction_cost=0.001)

    print(bt.tail())

    plt.figure(figsize=(10, 5))
    plt.plot(bt.index, bt["nav"], label="Nifty50 strategy NAV")
    plt.title("Nifty50 demo NAV")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

