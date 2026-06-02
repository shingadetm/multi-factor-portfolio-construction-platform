# Research notebook (outline)

This markdown file is a lightweight stand-in for a Jupyter research notebook. Convert it into a proper `.ipynb` when ready.

Sections:

1. Introduction and goal
2. Data ingestion
   - Synthetic demo and real data via `yfinance`
3. Factor construction
   - Momentum (12-month), Volatility, Quality (placeholder), Carry (placeholder)
   - Cross-sectional z-score ranking and combination
4. Portfolio construction
   - Equal weight, inverse-vol, mean-variance (unconstrained)
   - Constrained MV using `cvxpy` (notes)
5. Backtest and walk-forward validation
   - Transaction cost and turnover modeling
   - Rolling out-of-sample evaluation
6. Factor attribution and regime analysis
7. Results and dashboard snapshots
8. Lessons learned and overfitting considerations

Example code snippets

```python
from mfpc.data import load_synthetic_prices
from mfpc.factors import calc_momentum, calc_volatility, rank_factors
from mfpc.backtest import walk_forward

prices = load_synthetic_prices(n_assets=30, n_days=1200)
mom = calc_momentum(prices)
vol = calc_volatility(prices)
scores = rank_factors({"mom": mom, "vol": vol}, weights={"mom": 0.7, "vol": 0.3})
bt, w = walk_forward(prices, scores)

```

