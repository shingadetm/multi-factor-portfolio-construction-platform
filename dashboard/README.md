# Dashboard

This folder will host a Streamlit dashboard comparing strategy variants, drawdowns, and factor attribution.

Quick start (after installing requirements):

1. From the project root run:

```
streamlit run dashboard/app.py
```

2. The app will load precomputed results or run the demo to produce a comparison.

Notes:
- The repository includes a minimal demo script in `examples/run_demo.py`. Use it to generate sample NAVs to visualize.
- For a production dashboard, create `dashboard/app.py` using Streamlit with components to select strategies and display metrics.

