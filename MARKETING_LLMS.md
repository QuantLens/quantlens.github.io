# QuantLens™ — What LLMs Extract From Your Payload

This guide showcases how an LLM can read a single QuantLens JSON payload and produce rich, actionable insights for traders and bots. Example below uses OPUSDT.P (Optimism/USDT Perpetuals) on a 5‑minute execution timeframe, with medium (60m) and long (1D) horizons enabled.

---

## 1) Metadata & Context

- Symbol: OPUSDT.P (Optimism/USDT Perpetual Futures)
- Timestamp: 1758199200 (Unix epoch) ≈ 2025‑09‑18 08:40:00 UTC
- Timeframe: Short=5m (exec), Medium=60m, Long=1D
- Profile: Rich (comprehensive dataset)
- Scan: Medium (balanced analysis depth)
- Precision: 3 decimals (precisionEff=3)
- Source: TradingView
- Anomaly: flag=false, vol_z=-0.466, rng_z=-0.927, sev=1
- Human Note: “Anomaly: vol low (‑0.4662σ), range tight (‑0.9266σ)”

Health

- Bars: 100 (last ~8.33 hours on 5m)
- Lag: −600000 ms (≈ −10 minutes)
- Calc: 1 (success)

Audit & Context

- Audit: No NaN; payload length ≈ 8,072 bytes
- ToD: eu (European session)
- ATR Rank: 0.308

Interpretation

- Robust, error‑free data. Low‑vol consolidation typical of EU session; the modest processing lag is negligible for most intraday systems.

---

## 2) Price Action (Header)

Short (5m)

- c=0.8161, ch1=0.0000, chN=−0.0020 (~−0.2% over ~8.3h)
- rng=0.022, rngp=0.027 (tight)

Medium (60m)

- c=0.8160, ch1=0.0000, chN=0.0450 (+4.5%)
- rng=0.105, rngp=0.128

Long (1D)

- c=0.8160, ch1=0.0040 (+0.4%), chN=−0.5090 (−50.9%)
- rng=2.318, rngp=2.84

Interpretation

- Short: flat and tight ⇒ consolidation.
- Medium: +4.5% suggests emerging uptrend; current bar flat ⇒ pause.
- Long: deeply bearish historically; slight daily gain hints at corrective bounce.

---

## 3) Technical Features

Short (5m)

- SMA=0.814, EMA=0.813 (price above both ⇒ mild bullish bias)
- RSI=52.26 (neutral), ATR=0.003 (low), atrp=0.003 (0.3%)
- HV: hv20=0.043, hv100=0.037 (low/consistent)
- BBP=0.84 (near upper band), VREL=0.338 (sub‑avg volume)
- vol_z=−0.466, rng_z=−0.927 (quiet & tight)
- Structure: hh=30, hl=32, lh=31, ll=33 (balanced)
- Breaks: bkU=0, bkD=0; Slope ≈ +1.9e‑4 (slightly up)
- Trend: ADX=28.88 (moderate), DI+=25.38 > DI−=12.26 (bullish tilt)
- VWAP≈0.816 (aligned), vwapd≈0, OBV slope≈+4,689 (buying bias)

Medium (60m)

- SMA=0.784, EMA=0.783 (price above ⇒ bullish), RSI=57.57
- ATR=0.009, atrp=0.011, hv20=0.154

Long (1D)

- SMA=0.719 (price above), EMA=0.845 (price below) ⇒ mixed long‑term bias
- RSI=52.92, ATR=0.070, atrp=0.085, hv20=0.493

---

## 4) Volume Profile (VP‑Lite)

- TF: 5m, method: close‑bin VAP
- POC=0.819, VAL=0.809, VAH=0.819, va_pct=0.70
- dist_to_poc_norm=−1.016 (slightly below POC), in_va=1 (accepted)
- acceptance_ratio=0.58 (moderate), regime=discovery, vp_quality=0.58
- poc_drift≈0 (stable), vp_lite=true

Interpretation

- POC=0.819 is a magnet/pivot; price=0.8161 sits within VA ⇒ acceptance.
- Moderate acceptance + discovery regime = exploratory behavior without strong anchoring.

---

## 5) Levels (Short)

- Fib: [0.805, 0.827] (support/resistance)
- Swings (sw): [0.805, 0.827]

Interpretation

- Support: 0.805 likely buyer interest.
- Resistance: 0.827 is the breakout pivot.

---

## 6) Regime & Trend

- Regime: range (score≈80.56)
- Per‑horizon: short=up, medium=up, long=up
- Consensus: up
- Z (100‑bar standardised): vol_z≈−1.281, rng_z≈−1.281

Interpretation

- Range‑bound with bullish tilt; high regime score supports consolidation.

---

## 7) Signals & Intent

Intent

- long=0, short=0
- t1=0.827, s1=0.805

Scenarios

- Bullish breakout: trigger close >0.828; invalid 0.825; stops/targets: 0.825/0.830/0.833/0.835; RR≈1:1
- Bearish rejection: wick rejection at 0.826; invalid 0.829; stops/targets: 0.829/0.824/0.814/0.818
- Range scalp: buy 0.805–0.806; sell 0.827; stop 0.803; tp 0.826

Interpretation

- Market is coiled; either breakout above 0.828 or rejection at 0.826 unlocks movement.

---

## 8) Risk Metrics

- atrp=0.003, atr=0.00318, dd14=0.004, ru=0.003
- suggested_stop≈0.811; r_multiple_unit=0.003; stop≈0.003

Interpretation

- Low volatility favors tight stops and modest targets; position sizing via ATR‑based RU.

---

## 9) Bars (OHLCV)

- 100× 5m bars embedded as [t,o,h,l,c,v]
- Recent drift from 0.8136 → 0.8161 on falling volume ⇒ consolidation

---

## 10) Strategy Summary (Marketing)

- Context: Tight‑range consolidation with bullish bias across horizons.
- Key Levels: 0.805 (support), 0.827 (resistance), 0.819 (POC pivot).
- Primary Play: Wait for a confirmed breakout above 0.828 with volume.
- Secondary Play: Range scalp within 0.805–0.827 with tight stops.
- Risk: Use RU=0.003 for sizing; watch for false breaks given sub‑avg volume.

---

### Why LLMs love QuantLens

- Clean, stable schema: consistent short‑keys and deterministic ordering.
- Multi‑horizon context: short/medium/long horizon summaries in one payload.
- Rich-yet-compact: tunable profiles to balance cost vs depth.
- Actionable scaffolding: signals, risk blocks, and levels are ready for prompt‑based agents.
