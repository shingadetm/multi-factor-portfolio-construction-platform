"""Demo runner that creates synthetic data, computes factors, builds portfolios and backtests."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt

# ensure package import from local src
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root / "src"))

from mfpc.data import load_synthetic_prices
from mfpc.factors import calc_momentum, calc_volatility, rank_factors
from mfpc.backtest import walk_forward
from mfpc.portfolio import inverse_vol_portfolio

def main():
    prices = load_synthetic_prices(n_assets=20, n_days=1000)

    mom = calc_momentum(prices, lookback=63)
    vol = calc_volatility(prices, lookback=63)

    scores = rank_factors({"momentum": mom, "vol": vol}, weights={"momentum": 0.7, "vol": 0.3})

    bt, weights = walk_forward(prices, scores, lookback=252, rebalance_days=21, top_n=5, scheme="rank", transaction_cost=0.001)

    print(bt.tail())

    plt.figure(figsize=(10, 5))
    plt.plot(bt.index, bt["nav"], label="Strategy NAV")
    plt.title("Demo strategy NAV (synthetic)")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

