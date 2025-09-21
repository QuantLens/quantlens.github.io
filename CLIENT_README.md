# QuantLens Client Quick Start

This document is meant to be copy/paste friendly for new (paying) users. Keep it to ONE screen.

## Base URLs

- Data API: `http://YOUR_HOST:8080`
- PTSM API: `http://YOUR_HOST:8081`

## Authentication

Send your API key in the **`x-api-key`** header on every request.

```http
x-api-key: YOUR_KEY
```

The legacy `?key=` query parameter is still accepted for backward compatibility, but is **deprecated**. New integrations must use the header.

Uniform auth errors use the JSON shape: `{ "ok": false, "code": 401, "error": "missing api key" }`.

## Rate Limits

Configured server-side via `QL_RPM` (requests per minute). Responses include headers so clients can back off gracefully:

| Header | Meaning |
|--------|---------|
| `X-RateLimit-Limit` | Allowed requests per rolling minute |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Epoch seconds when the window resets |
| (429 only) `Retry-After` | Seconds to wait before retrying |

Example 200 response headers:

```text
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1726921200
```

On 429 you also receive:

```text
Retry-After: 60
X-RateLimit-Reset: 1726921200
```

### Python SDK tip

The bundled Python client exposes convenience properties:

```python
from clients.python.quantlens_client import QuantLensClient
ql = QuantLensClient()
ql.fetch("AAPL","1d", limit=1, head_only=True)
print("remaining", ql.ratelimit_remaining, "limit", ql.ratelimit_limit, "resets_in_s", ql.ratelimit_seconds_to_reset)
```

## Endpoints (Essentials)

- `GET /v1/fetch?symbol=BTCUSD&tf=1h&limit=200` → OHLCV JSON list (chronological)
- `POST /v1/infer` body `{ "symbol": "BTCUSD", "tf": "1h", "limit": 200 }` → model output
- `POST /v1/train` body `{ "symbol": "BTCUSD", "tf": "1h" }` → training ack (async/future)
- `GET /metrics` → Prometheus text (counters)
- `GET /version` → `{ version, git_sha?, built_at?, provider_fallbacks }`
- `GET /healthz` → plain `ok`
- `GET /` → service metadata

## Timeframes (tf)

Examples: `1m,5m,15m,1h,4h,1d`. Normalized internally; invalid timeframe returns 400.

## Error Schema & Codes

All non-2xx responses return a uniform body:

```json
{ "ok": false, "code": 401, "error": "missing api key" }
```

Codes

- 400 Validation / provider failure
- 401 Missing or invalid key
- 404 Unknown path
- 429 Rate limit exceeded (check headers)
- 500 Internal (retry or contact support)

## Python Client (Bundled SDK)

A richer retrying & rate-limit aware client lives at `clients/python/quantlens_client.py`.

Minimal usage:

```python
from clients.python.quantlens_client import QuantLensClient
ql = QuantLensClient()
print(ql.version())
data = ql.fetch("AAPL","1d", limit=2, head_only=True)
print("rows=", data.get("rows"), "remaining=", ql.ratelimit_remaining)
```

## CORS

Set `QL_CORS_ORIGINS=https://yourapp.com` (comma separated for multiple) before starting service.

## Deployment Tips

- Dev: `QL_RELOAD=1 quantlens-api`
- Prod (single host): `quantlens-api --workers 4` (do NOT combine with `--reload`)
- Minute equities depth limited in yfinance; supply `POLYGON_API_KEY` for deeper intraday fallback.

## Version Metadata

Set before launch (optional):

```bash
set QL_VERSION=0.1.0
set GIT_SHA=<shortsha>
set BUILT_AT=2025-09-21T12:34:56Z
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 | Missing key | Add header `x-api-key` |
| 429 | Burst too fast | Back off; check `QL_RPM` |
| 422/400 timeframe | Invalid tf | Use supported values |
| uvicorn not found | Missing dep | `pip install uvicorn[standard]` |

## Metrics (examples)

Exposed at `/metrics` (gated by API key):

- `fetch_success_total` – successful fetches
- `fetch_error_total` – failed fetches
- `fallback_total` – provider fallbacks (yfinance -> polygon etc.)
- `infer_success_total`, `train_success_total` (PTSM service)

Happy building.
