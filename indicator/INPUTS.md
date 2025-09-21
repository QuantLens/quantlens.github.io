# LLM JSON Export v6 — Input Guide and Cleanup Proposal

This guide lists all inputs available in the Pine v6 indicator, explains what each does, suggests sensible defaults, and proposes a cleaner, grouped layout for the TradingView settings panel. It also summarizes emission behavior and Multi‑Exec scan options.

## Quick start

- Execution timeframe: set to Chart (recommended) or a fixed TF like 5m or 1D.
- Payload profile: Balanced (good tradeoff). Use Lean for webhooks with tight limits; Rich when token budget allows.
- Multi‑Exec scan: leave off initially; enable later if you need multi‑timeframe snapshots.
- Macro, Correlations, On‑chain, Liquidity: optional context; defaults are off to keep payload compact.
- Alerts: use “Alert on Bar Close” for deterministic, one‑per‑bar payloads.

## Emission behavior (contract)

- Deterministic: Main payload emits on the execution TF’s bar close if “Alert on Bar Close” is enabled.
- Immediate emit: “Emit Once Immediately” (one‑time) and “Emit on Each Update (test)” are for testing only; they can also trigger alerts if “Alert on Immediate/Realtime Emits” is on.
- Multi‑Exec: When enabled, precomputed mini‑snapshots for selected TFs are emitted either combined in one payload or as separate messages (configurable).

---

## Inputs by section

### 1) Execution & Emission

- Scan Mode: `_scanMode` — Short / Medium / Deep
- Execution TF: `_execTF` — "Chart", "1", "2", "5", "15", "30", "240", "D", "W" (default: "5")
- Payload Profile: `_payloadProf` — Lean / Balanced / Rich
- Precision: `_precision` — number of decimals for numeric fields (default: 3)
- Bars (exec TF): `_barsExec` — number of bars to retain/analyze on exec TF (default: 100)
- Alert on Bar Close: `_alertOnClose` (default: true)
- Emit Once Immediately: `_emitOnceNow` (default: false)
- Emit on Each Update (test): `_emitRealtime` (default: false)
- Alert on Immediate/Realtime Emits: `_alertOnImmediate` (default: true)
- Show Payload Label (pane): `_showPayloadLabel` (default: false)
- Payload Wrap Width: `_wrapWidth` (default: 110)
- Debug Mode (dev only): `_debugMode` (default: false)
- Audit Max Errors: `_auditMaxErrors` (default: 10)

Recommended defaults:

- Execution TF: Chart
- Payload Profile: Balanced
- Alert on Bar Close: enabled


### 2) Horizons & Core Blocks

- Include Medium (60m): `_includeMedium` (default: true)
- Include 4H (240m): `_includeH4` (default: false)
- Include Long (1D): `_includeLong` (default: true)
- Include Fib Levels: `_includeFib` (default: true)
- Include Signals Block: `_includeSignals` (default: true)
- Legacy compatibility (emit legacy sig): `_legacyCompat` (default: false)
- Include Summary Block: `_includeSummary` (default: false)
- Rich On State Change Only: `_richStateOnly` (default: false)

Notes:

- Horizons gate medium/long context blocks; signals and fibs enrich the payload.
- “Rich on state change only” reduces chatter when using Rich profile.


### 3) Signals: Volume burst boost

- Enable Volume Burst Boost: `_volBoostEnabled` (default: true)
- Vol Burst Z Threshold (z20): `_volBurstZThresh` (default: 1.5)
- Rel Volume Threshold (x): `_volBurstRelThresh` (default: 1.5)

Use to increase signal confidence when volume regime is unusually strong.


### 4) Volume Profile (lite)

- Include VP (lite): `_includeVP` (default: true)
- VP Bins: `_vpBins` (default: 80)
- VP Value Area %: `_vpVaPct` (default: 0.70)
- VP Acceptance Window (bars): `_vpAcceptN` (default: 50)
- VP POC Drift Window: `_vpDriftW` (default: 20)
- VP Line Width: `_vpLineWidth` (default: 2)
- VP Transparency (0-100): `_vpTransp` (default: 0)
- Bring To Front: `_vpTop` — POC / VAL / VAH (default: POC)
- Show VP POC/VA overlay: `_vpOverlay` (default: false)


### 5) Macro context

- Include Macro Context: `_includeMacro` (default: false)
- Macro TF: `_macroTF` — "60","240","D","W" (default: "D")
- DXY Symbol: `_dxySymbol` (default: TVC:DXY)
- VIX Symbol: `_vixSymbol` (default: CBOE:VIX)
- BTC Spot Symbol: `_btcSymbol` (default: BITSTAMP:BTCUSD)
- Macro Corr Short (bars): `_macroCorrShort` (default: 30)
- Macro Corr Short Fallback (bars): `_macroCorrShortFallback` (default: 14)
- Macro Corr Long (bars): `_macroCorrLong` (default: 90)
- Macro Corr Long Fallback 1 (bars): `_macroCorrLongFallback1` (default: 60)
- Macro Corr Long Fallback 2 (bars): `_macroCorrLongFallback2` (default: 30)
- DXY Slope Window: `_macroSlopeW` (default: 20)
- VIX Risk-On Max: `_vixOnMax` (default: 18.0)
- VIX Risk-Off Min: `_vixOffMin` (default: 24.0)

Notes:

- Macro correlations compute on a daily context with fallbacks to reduce nulls; “asof” fills with current time if needed.
- Only BTC/ETH are used for explicit crypto correlations (exchange defaults set to BITSTAMP).


### 6) Correlations (daily crypto)

- Include Correlations (daily): `_includeCorrelations` (default: false)
- Corr Lookback (days): `_corrLookbackDays` (default: 30)
- ETH Symbol: `_ethSymbol` (default: BITSTAMP:ETHUSD)

Notes:

- BTC symbol uses `_btcSymbol` from Macro context; ETH is configured here.


### 7) Pair correlation (advanced)

- Pair Symbol (corr): `_pairSymbol` (default: "")
- Pair Corr Window: `_pairCorrWinRaw` (default: 50)

Notes:

- Optional correlation to a second arbitrary symbol; leave empty to skip.


### 8) On‑chain (manual placeholder)

- Include On‑Chain Placeholder: `_includeOnChain` (default: false)
- Manual On‑Chain Inputs: `_onChainManual` (default: false)
- Active Addresses z (manual): `_onChainActiveZ` (default: 0.0)
- Transaction Count z (manual): `_onChainTxZ` (default: 0.0)
- Large Tx Flow (manual): `_onChainLargeFlow` (default: 0.0)

Notes:

- When manual is enabled, a simple `on_chain.health` scalar is emitted based on z‑scores and large flow.


### 9) Liquidity (manual placeholder)

- Include Liquidity Placeholder: `_includeLiquidity` (default: false)
- Manual Liquidity Inputs: `_liqManual` (default: false)
- Bid‑Ask Spread (manual): `_liqBidAsk` (default: 0.0)
- Order Book Imbalance (manual): `_liqImbalance` (default: 0.0)
- Depth Strength (manual): `_liqDepthStrength` (default: 0.0)

Notes:

- When manual is enabled, a simple `liquidity.health` scalar is emitted.


### 10) Multi‑Exec scan

- Enable Multi‑Exec Scan: `_multiExecEnabled` (default: false)
- Scan 1m: `_mx1` (default: false)
- Scan 2m: `_mx2` (default: false)
- Scan 3m: `_mx3` (default: false)
- Scan 5m: `_mx5` (default: true)
- Scan 15m: `_mx15` (default: true)
- Scan 30m: `_mx30` (default: true)
- Scan 60m (H1): `_mx60` (default: true)
- Scan 240m (H4): `_mx240` (default: true)
- Scan 1D: `_mxD` (default: true)
- Multi‑Exec Trigger: `_mxTrigger` — Each TF Close / Main Exec Close (default: Main Exec Close)
- Multi‑Exec Output: `_mxOutput` — combined / separate (default: combined)

Notes:

- Combined outputs all selected TF mini‑snapshots into one payload; Separate emits one payload per TF when triggered.


### 11) Bars export & S/R limits (advanced)

- Bars Page: `_barsPage` (default: 1)
- Bars Per Page: `_barsPerPage` (default: 100)
- Bars Compression: `_barsCompress` (default: 1)
- SR Max Short: `_srMaxShort` (default: 2)
- SR Max Medium: `_srMaxMed` (default: 2)
- SR Max Long: `_srMaxLong` (default: 2)


---

## Recommended defaults

- Profile: Balanced
- Execution TF: Chart
- Horizons: Medium/Long on, 4H optional
- VP: on (lite), overlay off
- Macro/Correlations: off (enable when needed)
- On‑chain/Liquidity: off unless you have manual values
- Multi‑Exec: off (enable when you want a consolidated snapshot sweep)
- Alerts: Alert on Bar Close on; immediate/realtime off (for test only)


## Cleanup proposal (grouped settings)

Use TradingView input groups to make the panel cleaner and more discoverable:

- Group: Execution & Emission
  - `_scanMode`, `_execTF`, `_payloadProf`, `_precision`, `_barsExec`, `_alertOnClose`, `_emitOnceNow`, `_emitRealtime`, `_alertOnImmediate`, `_showPayloadLabel`, `_wrapWidth`, `_debugMode`, `_auditMaxErrors`, `_richStateOnly`

- Group: Horizons & Core
  - `_includeMedium`, `_includeH4`, `_includeLong`, `_includeFib`, `_includeSignals`, `_includeSummary`, `_legacyCompat`

- Group: Signals Boost
  - `_volBoostEnabled`, `_volBurstZThresh`, `_volBurstRelThresh`

- Group: Volume Profile (lite)
  - `_includeVP`, `_vpBins`, `_vpVaPct`, `_vpAcceptN`, `_vpDriftW`, `_vpLineWidth`, `_vpTransp`, `_vpTop`, `_vpOverlay`

- Group: Macro Context
  - `_includeMacro`, `_macroTF`, `_dxySymbol`, `_vixSymbol`, `_btcSymbol`, `_macroCorrShort`, `_macroCorrShortFallback`, `_macroCorrLong`, `_macroCorrLongFallback1`, `_macroCorrLongFallback2`, `_macroSlopeW`, `_vixOnMax`, `_vixOffMin`

- Group: Correlations (Crypto)
  - `_includeCorrelations`, `_corrLookbackDays`, `_ethSymbol`

- Group: Pair Correlation (Advanced)
  - `_pairSymbol`, `_pairCorrWinRaw`

- Group: On‑Chain (Manual)
  - `_includeOnChain`, `_onChainManual`, `_onChainActiveZ`, `_onChainTxZ`, `_onChainLargeFlow`

- Group: Liquidity (Manual)
  - `_includeLiquidity`, `_liqManual`, `_liqBidAsk`, `_liqImbalance`, `_liqDepthStrength`

- Group: Multi‑Exec Scan
  - `_multiExecEnabled`, `_mx1`, `_mx2`, `_mx3`, `_mx5`, `_mx15`, `_mx30`, `_mx60`, `_mx240`, `_mxD`, `_mxTrigger`, `_mxOutput`

- Group: Bars Export & S/R (Advanced)
  - `_barsPage`, `_barsPerPage`, `_barsCompress`, `_srMaxShort`, `_srMaxMed`, `_srMaxLong`

Additional UX improvements:

- Show “Manual” sub‑fields only when the parent include + manual toggles are enabled (already respected by code at runtime; reflect in input grouping via group names like "On‑Chain (Manual)" and descriptions).
- Keep Binance tickers out by default; defaults use BITSTAMP for BTC/ETH (already configured).
- Consider defaulting `_execTF` to "Chart" to reduce confusion for new users.

If you’d like, I can apply these input groups directly in the Pine file using the `group=` parameter of each `input.*` call.


## Notes on payload content

- Meta includes `features_ver` for schema/version tracking.
- Context includes `volatility_regime`.
- Macro correlations use daily series with multi‑stage fallbacks (30→14 and 90→60→30) and an `asof` fallback to `timenow` when needed.
- `liquidity.health` and `on_chain.health` are included when manual modes are enabled.
- Data‑quality warnings feed into `health.data_quality`.
- `signals_mtf` summarizes MTF confirmations; signals confidence receives boosts from MTF alignment and volume burst.
- Multi‑Exec emits precomputed mini‑snapshots for the selected TFs; output can be combined or separate.

---

## Want me to wire up the input groups now?

I can update `indicator/LLM_JSON_Export_v6.pine` to add `group=` labels exactly as proposed above so your settings panel is neatly organized. Let me know and I’ll apply the change in a single pass.

Note: The input groups described in this document are now wired into `indicator/LLM_JSON_Export_v6.pine`. If you change the grouping here later, we can sync the Pine inputs to match.
