# Settings Guide — QuantLens™ (v6)

This indicator exports structured market context into JSON payloads at each bar close. It’s designed for LLM-based trading assistants and bots, so models can reason over clean, structured snapshots instead of raw charts.

This guide explains every setting, what it controls, and how to tune it for different use cases.

---

## 1) Core Settings

| Setting | Description | Usage Tips |
|---|---|---|
| Scan Mode | Chooses analysis depth via lookback windows. Options: Short, Medium, Deep. | Short = faster, shallow context; Deep = slower, longer context. Pick per strategy/time budget. |
| Execution TF (m) | Base timeframe for payload export, in minutes (e.g., 5 = 5‑minute bars). | Match to your strategy (scalping 1–5m; swing 60m+). |
| Payload Profile | Defines payload richness. Options: Lean, Balanced (default), Rich. | Lean trims fields; Rich adds extras (HV100, vectors, more meta). Use Balanced for most cases. |
| Precision | Decimal places for numbers in JSON. | 2–3 is typical. Higher can inflate payload size. |
| Bars (exec TF) | Bars exported at the execution TF in the `bars` array. | 50–150 balances history vs size. Capped automatically for ultra‑low TFs. |

---

## 2) Horizon Toggles

| Setting | Description | Usage Tips |
|---|---|---|
| Include Medium (60m) | Adds hourly context under `horizons.medium`. | Keep ON for intraday bias. |
| Include Long (1D) | Adds daily context under `horizons.long`. | Useful for swing trades and trend confirmation. |
| Include Fib Levels | Exports short‑horizon fib anchors when available. | Helpful when your AI uses fib confluence. |
| Include Signals Block | Adds compact scenario suggestions under `sig`. | Good for reasoning about state shifts. |
| Show Payload Label (pane) | Shows the JSON payload as a label in the pane. | Turn OFF if cluttered. |
| Include Human Summary | Adds a short human‑readable string alongside JSON. | Handy for debugging/oversight. |
| Include Human Meta in JSON | Embeds extra meta (exec TF, settings) into payload. | Keep ON for reproducibility. |
| Include Vector Snapshot | Adds a compact state vector (`vec`) for ML features. | Useful for feature engineering. |
| Rich On State Change Only | In Rich profile, emit full extras only on state change. | Saves tokens while keeping key updates. |
| Include Volume Profile (lite) | Adds VP‑lite block (POC/VAL/VAH, acceptance, drift). | Enable for balance/discovery context. |

---

## 3) Volume Profile Controls

| Setting | Description | Usage Tips |
|---|---|---|
| VP Bins | Number of price bins for VP‑lite. | 40–80 balanced; higher = more detail, larger JSON. |
| VP Value Area % | % of volume in Value Area (default 0.70). | Leave at 0.70 unless experimenting. |
| Show VP POC/VA overlay | Draws VAL/VAH/POC lines on chart. | Visual only. |
| VP Acceptance Window (bars) | Lookback for acceptance ratio smoothing. | 30–100 bars is common. |
| VP POC Drift Window | Window for POC drift linear regression. | Helps spot balance → discovery shifts. |
| VP Line Width | Overlay line thickness. | Cosmetic. |
| VP Transparency (0–100) | Overlay line transparency. | Cosmetic. |
| Bring To Front | Choose which VP line sits on top (POC/VAL/VAH). | Cosmetic. |

---

## 4) Macro Context

| Setting | Description | Usage Tips |
|---|---|---|
| Include Macro Context | Toggles macro data block (DXY, VIX, BTC). | Disable for lightweight payloads. |
| Macro TF | Timeframe for macro series (e.g., D). | D is standard for DXY/VIX. |
| DXY Symbol | Dollar index symbol. | Default: `TVC:DXY`. |
| VIX Symbol | Volatility index symbol. | Default: `CBOE:VIX`. |
| BTC Spot Symbol | BTC spot symbol. | Default: `BINANCE:BTCUSDT`. |
| Macro Corr Short (bars) | Short correlation lookback (BTC↔DXY). | 20–30 captures recent shifts. |
| Macro Corr Long (bars) | Long correlation lookback (BTC↔DXY). | 90+ captures broader relationships. |
| DXY Slope Window | Lookback for DXY short EMA slope. | Default 20 works well. |
| VIX Risk‑On Max | Below this VIX = risk‑on. | Default 18. |
| VIX Risk‑Off Min | Above this VIX = risk‑off. | Default 24. |

---

## 5) Pagination & Compression

| Setting | Description | Usage Tips |
|---|---|---|
| Bars Page | Page index when exporting history in chunks. | Use for large histories. |
| Bars Per Page | Count of bars per page. | 100 is a good default. |
| Bars Compression | Step between exported bars. | 1 = no compression; >1 thins history. |

---

## 6) Support & Resistance

| Setting | Description | Usage Tips |
|---|---|---|
| SR Max Short | Max SR levels for short horizon. | 2–3 keeps it clean. |
| SR Max Medium | Max SR levels for medium horizon. | 2–3 standard. |
| SR Max Long | Max SR levels for long horizon. | 2–3 standard. |

---

## 7) Pair Correlation

| Setting | Description | Usage Tips |
|---|---|---|
| Pair Symbol (corr) | Secondary symbol for correlation (e.g., ETH vs BTC). | Leave blank if unused. |
| Pair Corr Window | Window (bars) for correlation computation. | 30–50 works well. |

---

## 8) Alerts & Debugging

| Setting | Description | Usage Tips |
|---|---|---|
| Alert on Bar Close | Fires `alert()` with JSON each exec‑TF bar close. | Required for LLM/webhook integration. |
| Debug Mode (dev only) | Adds extra debug data/plots. | For testing only; increases payload. |
| Payload Wrap Width | Wrap width for on‑chart JSON label. | Formatting only. |
| Inputs in status line | Cosmetic indicator status line. | Not provided in v6 exporter. |

---

## ⚖️ Best Practices

- Balance richness vs size: Deep + Rich + Macro ON yields maximum context but larger payloads. Lean + Balanced trims to a lighter footprint.
- Match execution TF to strategy: scalpers use 1–5m; swing traders 60m+.
- Avoid overcrowding: too many SR levels, excessive VP bins, or all optional blocks at once can overwhelm both JSON size and AI context.
- Macro Context: Enable if trading assets sensitive to DXY/VIX (e.g., crypto); disable for pure price/volume focus.
- Debug Mode: Use during development; keep OFF in production.

---

### Profiles quick guide

- Lean: minimal fields, fewer optional blocks.
- Balanced (default): solid context without bloat.
- Rich: adds HV100, vectors, and more meta; optionally gated to state changes only.

---

If you extend the exporter, prefer additive fields to stay within schema `v1` and bump `ver` only for breaking changes.
