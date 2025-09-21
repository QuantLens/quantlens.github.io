# ql-indicator (local dev)

Install (editable) so `ql_indicator` is importable and `python -m ql_indicator.run` works:

```powershell
cd tools/python_indicator_clone
pip install -e .
```

Or use the console script once installed:

```powershell
ql-indicator --source ccxt --exchange binance --symbol BTC/USDT --tf 1m --history 500
```

Run tests:

```powershell
pytest -q tools/python_indicator_clone/tests/test_fetch_ccxt.py
```

Dev check:

```powershell
python tools/python_indicator_clone/dev/check_df.py binance BTC/USDT 5m
```
# QuantLens Indicator (Python clone)

This is a Python clone of the TradingView Pine v6 indicator that emits compact, ML-friendly JSON payloads with multi-horizon context.

Features:

- Horizons: short (exec TF), optional medium/H4/long via resampling
- Technicals: ATR, ATR% (fallback to 0), HV(20), RSI, simple MA trends
- Optional enrichments: macro/correlations placeholders
- Lean/Balanced/Rich profiles with soft budgets and a hard byte cap
- Bars included; in Lean we only skip if the hard cap would be exceeded and flag `meta.budget_exceeded`
- Multi-exec snapshots (combined/separate)

## Quick start

1. Install

```bash
pip install -r requirements.txt
```

1. Run with sample data (yfinance):

```bash
python -m ql_indicator.run --symbol BTC-USD --tf 1h --profile balanced --emit combined --history 500
```

Outputs JSON to stdout. Use `--save` to write to a file.

## Notes

- This clone mirrors the JSON schema and policies (null handling, audit, clarity score) where practical in Python.
- Results may differ slightly from Pine due to indicator library differences and resampling edges.
