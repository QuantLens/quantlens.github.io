# QuantLens™ — Multi-Horizon Market Export Engine

README & Roadmap

> Build a Pine Script v6 indicator that emits a compact, LLM-friendly JSON report on every bar close, deliver it via TradingView alerts/webhooks, and process it downstream for research, backtesting, and signal generation.

## Vision

VisionDefinition: The payload’s vision is to provide a comprehensive, machine-readable dataset for LLM-driven trading decisions, delivering multi-timeframe technical analysis (TA), actionable signals, and market context for FETUSDT on a 5-minute chart (Bitget exchange). It should enable automated trading strategies, support both new and pro traders, and integrate seamlessly with tools like QuantLens™/StratoTrade Labs (per past discussions on TradingView indicator alerts).



## 1) Overview & Why

This project turns any TradingView chart into a structured, LLM-ready data source. A Pine v6 indicator collects multi-timeframe context (trend, momentum, volatility, volume, levels), packages it into a short-key JSON payload, and emits it via `alert()` to an alert log or webhook endpoint. A lightweight collector ingests, validates, and stores each payload so downstream jobs (LLMs, quant scripts, dashboards) can analyse a consistent schema.

Benefits in practice:

* **Consistent schema** → stable keys & types reduce parse errors and prompt overhead.
* **On-chart context** → short/medium/long horizons summarised; recent bars included.
* **Tunable payload** → switch profiles/knobs to balance richness vs reliability.

> Docs: [Settings Guide](./SETTINGS.md) · [What LLMs Extract](./MARKETING_LLMS.md)

## 2) Core features

* **Scans**: `Short`, `Medium`, `Deep` (tunes lengths, features, history, costs).
* **Execution timeframes**: 1, 2, 5, 15, 30 minutes (scalping→day trading).
* **Horizon aggregates**: short (exec TF), medium (60m), long (1D).
* **Metrics**: OHLCV, SMA/EMA, RSI, ATR & ATR%, HV (20/100), Bollinger position, volume-relative, breakout flags, swing counts, regime label.
* **Levels**: lightweight SR points + optional fib anchors.
* **Pair context**: correlation to a chosen symbol, optional spread z-score.
* **Bars array**: last N exec-TF bars `[t,o,h,l,c,v]` (cap via `barsExec`).
* **Profiles/knobs**: `payloadProfile`, `barsExec`, `precision`, `includeMedium/Long`, `includeFib`, `includeSignals`, `srMax*`.
* **Idempotency**: `uid = <symbol>-<tf>-<epoch>`; `schema/ver` headers.

## 3) Architecture

```text
TradingView (Pine v6 study)
  └─ emits JSON via alert() ──> Webhook (collector API) ──> Storage (S3/fs/db)
                                                    └─> Workers (LLM/analytics)
```

* **Pine indicator** (client): computes features per bar; builds JSON string safely.
* **Collector** (server): validates schema, dedupes by `uid`, stores `/symbol/tf/epoch.json`.
* **Workers**: summarise, score setups, produce backtests/forecasts, publish dashboards.

## 4) JSON schema v1 (short keys)

```json
{
  "schema":"v1",
  "ver":1,
  "uid":"<sym>-<tf>-<epoch>",
  "s":"<sym>",
  "tf":"<execTF>",
  "t":1700000000000,
  "horizons":{
    "short":{"tf":"5","n":100,
      "hdr":{"c":0.0,"ch1":0.0,"chN":0.0,"rng":0.0,"rngp":0.0},
      "feat":{"sma":0.0,"ema":0.0,"rsi":0.0,"atr":0.0,"atrp":0.0,
               "hv20":0.0,"hv100":0.0,"bbp":0.0,"vrel":1.0,
               "hh":0,"hl":0,"lh":0,"ll":0,"bkU":0,"bkD":0,"slope":0.0},
      "levels":{"sr":[[123.45,2.0],[120.10,1.0]],"fib":[118.00,126.00]}
    },
    "medium":{"…":"aggregates only"},
    "long":{"…":"aggregates only"}
  },
  "pair":{"sym":"BTCUSD","corr":0.12},
  "risk":{"atrp":0.006,"dd14":0.018},
  "regime":"uptrend_pullback",
  "context":{"tod":"ny-open","atrRank":0.62},
  "sig":{
    "long":{"trigger":0.821,"stop":0.805,"tp1":0.835,"tp2":0.845,"tpX":0.865,"rr":2.0,"context":"Breakout above fib 0.82, targeting daily EMA and extension."},
    "short":{"trigger":0.818,"stop":0.828,"tp1":0.801,"tp2":0.790,"tpX":0.757,"rr":2.1,"context":"Failed breakout at 0.82, fading back to SMA cluster / fib base."},
    "range":{"buy_zone":[0.800,0.801],"sell_zone":[0.820,0.822],"stop":0.796,"tp":0.818,"context":"Scalp range play if price oscillates between 0.80–0.82."}
  },
  "bars":[[1700000000000,1,1,1,1,1],…]
}
```

### Notes

* **Short keys & stable order** help tokenisers and downstream parsers.
* Prefer **normalised values** (%, z-scores) to compare across symbols/TFs.
* The exporter omits optional metrics (`rev_prob`, HV, fib) when unavailable; emit `null` only when stability is required.

## 5) Profiles & knobs (inputs)

* `scanMode`: `Short` | `Medium` | `Deep`.
* `execTF`: `1|2|5|15|30`.
* `payloadProfile`: `Lean` | `Balanced` (default) | `Rich`.
* `precision`: decimals in JSON numbers (auto-trimmed).
* `barsExec`: cap for `bars` array (default 100; ≤150; auto-capped for ≤2m TFs).
* Toggles: `includeMedium`, `includeLong`, `includeSignals`, `includeFib`.
* Level caps: `srMaxShort`, `srMaxMed`, `srMaxLong`.
* Pairing: `pairSymbol`, `pairCorrWin`.
* **Profile interplay**: `Lean` forces Medium/Long/Signals off and trims bars; `Rich` enables extras (pair z-score, HV100) and honours longer histories.

## 6) Setup

1. **Indicator**: paste the Pine v6 study into TradingView → add to chart.
2. **Alert**: create an alert on this study → *Once per bar close* → choose **Webhook URL** (your collector).
3. **Collector**: run a small server (Node/Python) to accept POST JSON, validate `schema:"v1"`, dedupe by `uid`, write to storage.
4. **Workers**: consume stored JSON, generate analysis/forecasts, or stream to a dashboard.

### Minimal collector (Node/Express)

```js
app.post('/hook', express.json({limit:'1mb'}), (req,res)=>{
  const p=req.body; if(p.schema!=='v1') return res.status(400).end();
  const key=`${p.s}/${p.tf}/${p.t}.json`;
  // TODO: validate keys/types, enforce size caps
  fs.writeFileSync(path.join(DATA,key), JSON.stringify(p));
  res.sendStatus(200);
});
```

## 7) Usage patterns

* Start with **Balanced** profile, `barsExec=100`, `includeLong=true`, `includeMedium=true`.
* **Payload sizing**: target **15–20 KB** for Balanced; reduce `barsExec` (e.g., 80) on ultra-fast TFs or switch to **Lean**.
* For deep analytics, switch to **Rich** or paginate Deep scans (roadmap).
* NOTE: Current short horizon uses the chart timeframe; full decoupling via `_execTF` sourcing (`request.security`) is planned.

## 8) Limits & safety

* TradingView historical limits (~5–20k bars) vary by plan/symbol.
* Avoid heavy loops; cap arrays; prefer aggregates for higher TFs.
* Include `schema/ver` for backward compatibility.

## 9) Repository layout

```text
/indicator/         # Pine v6 study (JSON exporter)
/server/            # Collector (webhook) + schema validation
/workers/           # LLM/analytics jobs, prompts, notebooks
/examples/          # Sample payloads, test alerts, dashboards
/docs/              # README, ROADMAP, schema, prompts
```

---

## 10) Indicator Python Module (tools/python_indicator_clone)

This repository includes a lightweight Python package (`ql_indicator`) used for:

* Fetching market data from CCXT, Polygon, or yfinance (with unified fallback routing).
* Building enriched JSON payloads (macro correlations + technical feature emitter).
* Deterministic utility functions for resampling and gap detection.

### Key Utilities

* `fetch(symbol, tf, limit, provider=None)` – unified fetch; auto‑routes crypto vs equity.
* `normalize_tf(tf)` – canonical timeframe normalization (e.g. `15min` → `15m`).
* `resample_ohlcv(df, rule, drop_incomplete_tail=False)` – left‑closed, label‑left resample
  * Set `drop_incomplete_tail=True` to remove a partially formed final bar (useful for strict backtests).
* `detect_gaps(df, freq)` – returns list of missing timestamps.

### Deterministic Tests

Core tests live under `tools/python_indicator_clone/tests`:

| Test File | Purpose |
|-----------|---------|
| `test_resample_math.py` | Validates left‑closed OHLCV aggregation semantics |
| `test_resample_tail_option.py` | Verifies optional tail trimming behavior |
| `test_gap_detector.py` | Ensures gap detection returns expected missing bars |
| `test_fallback_polygon.py` | Confirms yfinance empty result triggers polygon fallback |
| `test_fallback_equity_router.py` | Confirms routing: `_safe_yf` then polygon when empty |
| `test_ccxt_stub.py` | Stubbed CCXT fetch path schema correctness |
| `test_fetch_yf.py` | Deterministic offline yfinance pathway (monkeypatched) |

### Network vs Deterministic

Tests marked with `@pytest.mark.network` are optional in CI and run only on lanes that keep the respective dependency (e.g. CCXT). Deterministic tests avoid live calls via monkeypatching to maintain reproducibility.

### CI Workflow

GitHub Actions workflow `indicator-tests.yml` runs:

1. Deterministic core tests on all matrix combos (Python 3.11 & 3.12, with/without CCXT).
2. Network tests only when `ccxt` is present.
3. Coverage (non-failing) artifact upload.

Add a coverage gate later by editing the workflow step:

```yaml
      - name: Coverage (fail under threshold)
        run: pytest --cov=ql_indicator --cov-report=term-missing --cov-fail-under=85
```

### Resample Semantics

* Bars are aggregated using left‑closed, label‑left windows; timestamp represents the bar start.
* Partial tail bar is kept by default for forward‑looking analytics; pass `drop_incomplete_tail=True` for strict backtests.
* Volume sums; high/low/last close semantics follow TradingView convention.

### Retry & Robustness

* yfinance fetch path wrapped in a Tenacity retry (`_safe_yf`) with exponential backoff.
* Fallback order for equities: yfinance → polygon.
* Macro correlations (optional) cached with TTL (`QL_MACRO_TTL_SEC`).

---

## ROADMAP

### Phase 0 — MVP (Exporter + Collector)

**Goals**: Compile Pine v6 exporter, emit JSON on bar close, store via webhook.

* ✓ Short-key schema `v1` with `uid`, `s`, `tf`, `t`.
* ✓ Horizons: short(exec), medium(60), long(1D) with `hdr/feat/levels`.
* ✓ Pair correlation; `risk` block (ATR%, DD14).
* ✓ Bars array (≤100). Alert once per bar close.
* ✓ Minimal collector with schema validation & dedupe.
  **Acceptance**: Valid JSON saved for BTCUSD/ETHUSD/AAPL over 24h; size â‰¤20 KB (Balanced).

### Phase 1 — Pagination & Deep Scans

**Goals**: Support `Deep` payload via pagination (`page/pages`), optional `barsDeep`.

* Add indicator toggle: `paginateDeep=true` â†’ emit multiple alerts per bar.
* Collector: assemble pages into one object; enforce total cap.
  **Acceptance**: Deep payload reconstructed with no data loss; alert rate manageable.
* Schema/version note: additive fields (`page`, `pages`, optional `barsDeep`) can stay in `schema:"v1"` with `ver` bumped to 1.1; reserve `ver:2` for breaking changes.

### Phase 2 — Pair Trading Enhancements

**Goals**: Spread modelling & z-score.

* Add `zspr` (spread z-score) and optional rolling beta.
* Input `pairModel`: `close-close` | `log-spread` | `beta-adjusted`.
  **Acceptance**: Sanity tests show stable z-scores; schema stays â‰¤ +1 KB.

### Phase 3 — Signals Plugin Layer

**Goals**: Extensible signals without bloating base payload.

* Add plugin interface: `sig_ext:{k:v}` behind `includeSignals`.
* Provide 2â€“3 sample signals (e.g., RSI divergence flag, HV squeeze, MTF alignment) with small integers/floats.
  **Acceptance**: Plugins toggle on/off without breaking `v1`.

### Phase 4 — Validation & Testing

**Goals**: CI + schema checks + sample fixtures.

* JSON Schema (Zod/TypeBox) & tests for fixtures.
* Golden samples for 3 symbols Ã— 3 TFs.
* Size regression guard (warn if >25 KB Balanced).
  **Acceptance**: CI green; invalid payloads rejected.

### Phase 5 — Dashboard & Docs

**Goals**: Basic web UI to browse payloads, quick charts, and an LLM prompt helper.

* Minimal SPA: select symbol/TF â†’ render horizons & bars; copy-ready prompts.
* Docs: how-to, FAQ, troubleshooting.
  **Acceptance**: Local dashboard renders data from `/data/<sym>/<tf>/`.

### Phase 6 — Packaging & Versioning

## Signals block (optional)

When the “Include Signals Block” toggle is enabled, the payload includes a compact `sig` object with three scenario suggestions:

* `long`: breakout above resistance/fib, with `trigger`, `stop`, `tp1`, `tp2`, `tpX`, `rr`, and a short `context` string.
* `short`: failed breakout/rejection, symmetric fields as above.
* `range`: scalp plan with `buy_zone` and `sell_zone` arrays, single `stop` and `tp`, plus `context`.

---

## VP‑Lite Patch Notes (v1.x)

This patch adds an optional, compact Volume Profile approximation to the exporter and wires it into the JSON payload and (optionally) on‑chart overlays.

What’s included:

* Compute: close‑bin Volume Profile over the short lookback on the execution TF, deriving `poc`, `val`, `vah`, `dist_to_poc_norm` (ATR‑normalized), `in_va` (0/1), `acceptance_ratio` (smoothed), `poc_drift` (linreg), `n_bins_eff` (debug), and a categorical `regime`.
* JSON: emits a `vp` block when enabled, plus `ext.vp_lite=true`.
* Profiles:
  * Lean: `vp` with core scalars + `regime` only.
  * Debug: adds `n_bins_eff`.
  * Rich: adds `acceptance_ratio_raw` = `{count, denom}`.
* Overlay: POC/VAL/VAH are plotted only when Debug is ON or the overlay toggle is ON; styling via line width, transparency, and a “bring‑to‑front” control. All plots are global‑scope safe.

Regime policy:

* balance if `acceptance_ratio ≥ 0.55` and `|dist_to_poc_norm| ≤ 1.0`; else discovery.

LLM wiring (drop‑in snippet):

Use `regime` to branch logic:

* balance → prioritize mean‑reversion toward `poc`; entries only if `in_va=1`, `acceptance_ratio ≥ 0.55`, and `|dist_to_poc_norm| ∈ [0.1, 1.0]`.
* discovery → prioritize continuation; require `in_va=0` and `sign(dist_to_poc_norm)=sign(poc_drift)`.

Down‑weight VP cues if `n_bins_eff < 24` (if provided). Treat `acceptance_ratio_raw` with low denominator as low confidence.

Validation checklist:

* Presence/absence: `_includeVP=false` → no `vp` block and no `ext.vp_lite`.
* Lean: `vp` present and `regime` present; no `n_bins_eff` and no `acceptance_ratio_raw`.
* Debug: adds `n_bins_eff`.
* Rich: adds `acceptance_ratio_raw`.
* Threshold sanity: balance vs discovery as above.
* Edge guards: finite `dist_to_poc_norm` on tiny ATR; `n_bins_eff` drops on sparse/tight tapes.

Optional polish:

* `vp_quality = clamp01((n_bins_eff/bins) * acceptance_ratio)` is emitted in Debug/Rich. If it proves useful, consider promoting it to live and de‑emphasising raw fields.

By default, these are derived from ATR (1× stop, 1×/2×/3× targets) and local structure (fib/SMA/EMA). Values are formatted with the same precision as the rest of the payload. If core inputs are unavailable on a bar, the `sig` block is omitted.

Notes:

* Stops ≈ 1 ATR from invalidation zones.
* Targets: conservative → EMA/fib → stretch.
* RR computed vs `tp1` and the stop.

Toggle: `Include Signals Block` (boolean). Emits only when enabled.

**Goals**: Version the schema and exporter cleanly.

* `schema:"v1"`, bump `ver` only for breaking changes; additive fields otherwise.
* Changelog; migration notes.
  **Acceptance**: Controlled releases; no downstream breakage on minor updates.

---

## Contributing

* Keep keys short and stable.
* Normalise values where useful (%, z-scores).
* Avoid adding heavy arrays to `horizons`; prefer aggregates.
* Propose changes via PR with sample payloads and size impact noted.

## License

Choose a permissive license (e.g., MIT/Apache-2.0) and include it in `/LICENSE`.

---

## Deploy

Ready to publish the marketing site? See `DEPLOYMENT.md` for step‑by‑step guides to GitHub Pages, Netlify, Vercel, and Cloudflare Pages. You can use a free subdomain now and attach a custom domain later.

Org note: If you host under the QuantLens GitHub organization (<https://github.com/QuantLens>), your project Pages URL will look like `https://QuantLens.github.io/<repo>/`. For an organization root site, use a repo named `QuantLens.github.io`.

## Quick Start (Services)

### Local (no Docker)

```bash
# PowerShell
set QL_API_KEYS=dev123
uvicorn services.api.data_api:app --reload --port 8080
uvicorn services.ptsm.app:app --reload --port 8081
```

### Docker Compose

```bash
docker compose up --build -d
# Tail logs
docker compose logs -f api
```

Both services:

* Data API: <http://localhost:8080>
* PTSM API: <http://localhost:8081>

### Environment Variables

| Var | Purpose | Example |
|-----|---------|---------|
| QL_API_KEYS | Comma-separated API keys (simple static auth) | dev123,pro456 |
| QL_RPM | Per-key requests per minute window | 120 |
| POLYGON_API_KEY | Polygon.io key (optional, enables equity fallback) | (your key) |
| QL_MODEL_PATH | (PTSM) path for persisted models | /models/ptsm |

Copy `.env` and adjust for production.

## API Examples

Fetch bars (crypto auto-routes via CCXT stubbed/real):

```bash
curl "http://localhost:8080/v1/fetch?symbol=BTC/USDT&tf=15m&limit=100&key=dev123"
```

Fetch equity (yfinance→polygon fallback):

```bash
curl "http://localhost:8080/v1/fetch?symbol=AAPL&tf=5m&limit=120&key=dev123"
```

Infer with (placeholder) PTSM model:

```bash
curl -X POST "http://localhost:8081/v1/infer?key=dev123" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","tf":"1h","limit":200}'
```

## Pricing & Auth (Fast Path)

| Tier | RPM (QL_RPM) | Daily Cap | Notes |
|------|--------------|-----------|-------|
| Dev (Free) | 60 | 10k | Shared infra, basic SLAs |
| Pro | 120 | 250k | Higher burst & fallback priority |
| Enterprise | custom | custom | Dedicated containers / VLAN |

Implementation today: static key list in env. Upgrade path:

1. Move keys → SQLite table (key, plan, rpm, daily_cap, created_at, last_used_at).
2. Introduce rotating prefix keys and revocation list.
3. Stripe webhook populates/updates subscription → plan → env or DB row.

## CI & Coverage

Workflow `.github/workflows/ci.yml` runs matrix (OS × Python) with ruff, mypy (non-blocking), and targeted coverage gate (>=50). Raise `--cov-fail-under` gradually (e.g., +10% weekly) until 85–90% for core deterministic modules.

## Operational Next Steps

Planned hardening (next sprint):

* /metrics (Prometheus) with counters: fetch_success_total, fallback_total, rate_limit_hits_total.
* Stripe billing + DB-backed API keys (SQLite→Postgres migration path).
* Coverage ratchet: 50 → 60 → 70 → 80+.
* Qwen-3 Orchestrator (external) selects (symbol, tf, features) then POST /v1/train.

Future optional:

* Structured logging (JSON) + log retention policy.
* Canary lane for new provider integrations.
* Circuit breaker around external market data providers.

## Docker Images

Build manually:

```bash
docker build -t ql-api -f services/api/Dockerfile .
docker build -t ql-ptsm -f services/ptsm/Dockerfile .
```

Run:

```bash
docker run --rm -p 8080:8080 -e QL_API_KEYS=dev123 ql-api
```

## Qwen Orchestrator Hook

Place orchestrator code under `src/LLM/` (outside service containers) to decide fetch/training configs. Optionally self-host a quant LLM; warm it at PTSM startup for lower latency if memory budget allows.

### Service Endpoints

| Endpoint | Service | Purpose |
|----------|---------|---------|
| `/healthz` | both | Liveness probe (always `{ok:true}` if process healthy) |
| `/version` | both | Returns `{version: <QL_VERSION or app.version>}` |
| `/metrics` | both | Prometheus counters (plain text) |
| `/v1/fetch` | Data API | Fetch OHLCV bars (strict fail-fast) |
| `/v1/infer` | PTSM | Run model inference (stub) |
| `/v1/train` | PTSM | Trigger training stub |

### Metrics (excerpt)

```text
# HELP fetch_success_total fetch success total
# TYPE fetch_success_total counter
fetch_success_total 10
# HELP fetch_error_total fetch error total
# TYPE fetch_error_total counter
fetch_error_total 0
```

### Errors & Rate Limits

| Code | Meaning | Typical Cause | Action |
|------|---------|---------------|--------|
| 400 | Bad Request | Missing/invalid params | Fix query/body |
| 401 | Invalid API key | Key absent or not in `QL_API_KEYS` | Provide correct key |
| 429 | Rate limited | Exceeded `QL_RPM` in 60s window | Backoff / upgrade plan |
| 500 | Internal error | Provider failure or uncaught edge | Retry (exponential) |

`QL_RPM` is enforced per key in-memory; for multi-instance deploys use a shared store (Redis) with a sliding window or token bucket.

### Versioning

Set `QL_VERSION` in `.env` (e.g., `QL_VERSION=0.1.0`) to have `/version` reflect release tags. Bump alongside schema-impacting changes.
