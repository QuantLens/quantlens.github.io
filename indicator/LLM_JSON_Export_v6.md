# LLM JSON Export (v6) — Usage Guide

This indicator emits a compact, machine-friendly JSON payload on each confirmed bar. Use it to feed an LLM or downstream systems with consistent, schema-verified market snapshots.

## Quick start

- Add `LLM JSON Export (v6)` to your chart.
- Set Execution TF to your working timeframe (e.g., 5).
- For development: set Profile = Rich, turn Debug Mode ON, and turn on the blocks you want to inspect (Signals, VP, etc.).
- For production: set Profile = Balanced or Lean, turn Debug Mode OFF.
- Turn on "Alert on Bar Close" to emit the payload via `alert()` on confirmed bars.

### One‑minute setup (Lean production)

- Profile: Lean
- Debug Mode: OFF
- Alert on Bar Close: ON
- Include Medium (60m): ON if you need it; otherwise OFF
- Include Long (1D): ON if you need it; otherwise OFF
- Include Fib Levels: optional
- Include Signals Block: ON if your downstream uses signals
- Include Volume Profile (lite): OFF unless you need `vp.*`
- Include Human Summary: OFF
- Include Human Meta in JSON: OFF
- Include Vector Snapshot: OFF (turn ON only if you need `vec`/`vec_schema`)
- Rich On State Change Only: N/A (Lean ignores)

Result: smallest, machine‑friendly payload with `state`, `intent`, `signals` (if enabled), health, cfg, and `bars_header`.

### One‑minute setup (Debugging & validation)

- Profile: Rich
- Debug Mode: ON
- Include Signals Block: ON
- Include Volume Profile (lite): ON (overlay optional)
- Include Medium (60m) and Long (1D): ON
- Include Vector Snapshot: ON (optional)
- Include Human Summary / Human Meta: ON (optional)
- Rich On State Change Only: OFF (so you always see full details while testing)

Result: richer JSON + on‑chart payload label/overlays to verify everything quickly.

## Debug Mode

Turn this ON when validating the payload on-chart; turn it OFF for production alerts.

What it does when ON:

- Shows the latest JSON payload on the chart (small table). Optional label if "Show Payload Label (pane)" is enabled.
- Draws an "ANOM" badge on anomalous bars (based on canonical z-scores).
- Draws VP lines (VAL/VAH/POC) when Volume Profile is included (or when debugging).
- Emits richer JSON for inspection (when Profile is Rich):
  - Adds `meta.glossary` for niche metrics
  - Includes `vp.quality`
  - Includes the `bars` array for recent OHLCV

Trade-offs: bigger payloads and extra drawings; slightly higher CPU/bandwidth.

### Summary block: On or Off?

- Keep OFF for production ingestion to reduce size and avoid duplication with structured fields.
- Turn ON only when humans are reading alerts or during triage/debug.
- Toggles involved: "Include Human Summary" (adds `meta.human`), and optionally "Include Human Meta in JSON".

## Do I need to check everything for the next payload?

No. Only enable what you want included. The indicator’s Payload Profile gates which blocks are eligible, then each input toggle controls inclusion. Use the presets below.

## Recommended presets

- Validation / Debugging (see full JSON on chart)
  - Profile: Rich
  - Debug Mode: ON
  - Alert on Bar Close: ON
  - Include Signals Block: ON
  - Include Volume Profile (lite): ON (Overlay optional)
  - Include Medium (60m): ON
  - Include Long (1D): ON
  - Macro / Vector / Human: optional
  - Rich On State Change Only: OFF (so bars/vec/human always emit)

- Production / Smaller payloads
  - Profile: Balanced (or Lean for minimum)
  - Debug Mode: OFF
  - Alert on Bar Close: ON
  - Include Signals Block: ON if you want signals (not available in Lean)
  - Include Volume Profile (lite): as needed
  - Macro / Vector / Human: OFF unless required
  - Rich On State Change Only: ON if using Rich and you want fewer/lighter payloads
  - Include Medium/Long: ON only if you need those horizons

## Inputs cheat sheet

- Payload Profile
  - Lean: Minimal payload (hides intent, signals, risk, human, vec; VP regime omitted; no `bars` array)
  - Balanced: Respects your toggles
  - Rich: Forces Medium/Long true and allows richer extras (bars, vec, glossary)
- Debug Mode: Adds on-chart payload + diagnostics; includes rich extras for inspection
- Include Signals Block: Adds legacy `sig` and streamlined `signals[]` with confidence (not in Lean)
- Include Volume Profile (lite): Adds `vp` with POC/VAL/VAH, normalized distance, `in_va` boolean, `acceptance`, `state`, and `vp_precision`
- Include Medium / Long: Adds those horizon sections under `horizons`
- Include Macro Context: Adds macro state, DXY trend, VIX mode, correlations
- Include Vector Snapshot: Adds `vec_schema` and `vec` (compact numeric vector)
- Include Human Summary / Include Human Meta: Short human strings for context (optional)
- Rich On State Change Only: When Rich, suppress heavy extras unless the market state changed
- Alert on Bar Close: Fires `alert(payload)` on confirmed bars
- Show Payload Label (pane): Shows a floating label with the payload

### Production defaults (recommended)

- Profile: Lean or Balanced
- Debug Mode: OFF
- Include Signals Block: ON (if you use signals), otherwise OFF
- Include Volume Profile (lite): OFF unless your downstream needs `vp.*`
- Include Human Summary: OFF
- Include Human Meta in JSON: OFF
- Include Vector Snapshot: OFF (turn ON only if you need vectors)
- Include Medium (60m) / Long (1D): ON only if needed
- Include Fib Levels: optional
- Rich On State Change Only: ON if using Rich and you want fewer/lighter payloads

## Payload highlights (v1 schema)

- `horizons.short|medium|long`: Per-horizon `hdr` and `feat` with key indicators (SMA, EMA, RSI, ATR, ADX, VWAP, etc.)
- Canonical z-scores: `vol_z` and `rng_z` live only in `short.feat`
- `state`: Authoritative market state with `consensus` and `vp_hint`
- `vp` (when enabled):
  - `method:"close_bins"`, `vp_precision` (e.g., "medium"), `va_pct`, `bins`
  - `poc`, `val`, `vah`, `dist_to_poc_norm` (ATR-normalized), `in_va` (boolean)
  - `acceptance`: `{ratio,count,denom}`
  - `state` always; `regime` included outside Lean
- `signals[]`: Condensed list with `type`, `trigger`, `stop`, `tp1`, `tp2`, `rr`, `confidence`, `condition`, `invalidation`, `context`
- `intent`: `long`, `short`, `t1`, `t2`, `s1`, `trade_recommended`, `priority_score`, `context`
- `meta`: `profile`, `scan`, `precision`, `tz`, `units`, `time_context`, `schema_ver`; `glossary` in Rich/debug
- `market_context` (non-Lean): compact high-level market view (trend, volatility, key level)
- `health`: `bars`, `lag_ms` (non-negative), `calc`, `data_completeness`, `source_reliability`
- `audit`: `nan`, `len`, `errors` (array)
- `bars_header` always; `bars` emitted in Rich or Debug Mode
- `vec_schema` and `vec` (when Vector enabled)

## Verify your next alert (checklist)

After you adjust settings, confirm the next alert contains the right fields:

- `meta.profile` is "Lean" or "Balanced" (as set)
- `horizons.long.tf` equals `1440` (number), not "D"
- `state` block exists; no root `regime`/`z` objects
- `bars_header` is present; `health.lag_ms` is non‑negative
- If VP is enabled: `vp.acceptance = {ratio,count,denom}`, `vp.in_va` is boolean, `vp.vp_precision` present
- If Summary is OFF: no `meta.human`
- If Vector is OFF: no `vec`/`vec_schema`

## Alerts

- Toggle "Alert on Bar Close" to emit `alert(payload)` each confirmed bar.
- You can also create a TradingView alert on the indicator and select:
  - Condition: this indicator
  - Option: "Any alert() function call" or the named condition

## Tips & troubleshooting

- Payload too large? Turn Debug Mode OFF, disable `bars`, `vec`, and `human`, use Balanced or Lean, or enable "Rich On State Change Only".
- VP looks flat? Ensure "Include Volume Profile (lite)" is ON, adjust `VP Bins`, and note it’s OHLCV-based (vp_precision: "medium").
- Signals missing? Ensure Profile is not Lean and "Include Signals Block" is ON.
- Where are z-scores? Only in `short.feat` (`vol_z`, `rng_z`) by design.

### Seeing old fields (legacy schema)?

If an alert still shows old keys (e.g., `tf` as strings, `meta.anomaly`, root `z`, `acceptance_ratio`):

1) Remove the indicator instance from the chart
2) Add the updated script to the chart again (from Pine Editor)
3) Delete and recreate the TradingView alert targeting the new instance
4) Trigger one more bar close and re‑check the checklist above

## FAQ

- Do I need to enable everything to get the next payload?
  - No. Turn on only the blocks you want. Profiles gate what’s eligible; toggles control inclusion.
- Which profile is minimal?
  - Lean (Clarity-first). Useful for production if you want small, consistent payloads.
- Why is `acceptance` an object?
  - To make the ratio traceable: `{ratio,count,denom}`.
- What does `vp_precision` mean?
  - A qualitative label of the VP method’s fidelity (e.g., close-binning → "medium").

## 10/10 clarity checklist ✅

Target this set for a perfectly clean, machine‑friendly payload:

- Redundancy
  - No `hv100` in `horizons.short.feat` (keep `hv20` only for short horizon)
  - No `meta.anomaly` block (canonical anomaly stays only in `short.feat` via `vol_z`, `rng_z`, and flags)
- VP
  - `vp.vp_precision` present (e.g., "medium") when `vp` is enabled
  - `vp.acceptance` uses object form: `{"ratio":<0-1>,"count":<int>,"denom":<int>}`
- Signals
  - Either drop legacy `sig` or gate it with `meta.legacy_compat:false` (prefer `signals[]` only)
- Audit
  - `audit.errors: []` exists and `audit.max_errors` is included (e.g., 10)
- Size & profile
  - `meta.profile` is "Lean" or "Balanced" for production; vector and bars omitted unless needed
- Time context
  - `meta.time_context` includes `session`, `expected_volatility`, `typical_range`, and `impact`

Use the “Verify your next alert (checklist)” above to spot‑check the next payload.

## Pine changes to reach 10/10 (guide)

Make these small edits in your Pine script (v6). They’re safe, incremental, and schema‑aligned:

### Step 1 — Remove redundant fields in short.feat

- Drop `hv100` from `horizons.short.feat` (keep `hv20`).
- Keep canonical z only in short: `vol_z`, `rng_z`; do not emit `meta.anomaly`.

### Step 2 — Add audit.max_errors

- Add a constant or input for the cap (e.g., `10`) and include it alongside `errors`:
  - `audit = { nan, len, errors: [], max_errors: 10 }`

### Step 3 — Add vp.vp_precision

- When `vp` is enabled (close‑binning method), add `vp_precision: "medium"`.
- Keep acceptance in object form: `acceptance: { ratio, count, denom }`.

### Step 4 — Gate legacy `sig`

- Introduce `meta.legacy_compat` (boolean). When `false`, omit the legacy `sig` block and rely on `signals[]`.

### Step 5 — Default to Lean profile (optional but recommended)

- Set default payload profile to Lean. Balanced/Rich can still be chosen.
- In Lean, omit `bars`, `vec`, human summary/meta by default.

### Step 6 — Complete time_context

- Add `expected_volatility` (e.g., low/medium/high) and `typical_range` (e.g., ATR or % range) to `meta.time_context`.

After changes: save, add the indicator to chart again, and recreate the alert so TradingView uses the updated instance.

## Payload size safety (avoid truncation)

Aim for < 3800 characters to stay well under TradingView’s ~4096 limit:

- Use Profile = Lean or Balanced in production
- Turn OFF: Human Summary, Human Meta, Vector Snapshot, Volume Profile (unless needed)
- Turn OFF bars array (Lean does this automatically); keep only `bars_header`
- Reduce horizons (disable Long/Medium if not required)
- Keep precision at 3 and avoid verbose descriptors inside values

If an alert still runs long, disable VP or the Signals block temporarily and check the next payload size.
