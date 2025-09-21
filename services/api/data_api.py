from fastapi import FastAPI, Depends, HTTPException, Query, Response, Request, Header
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os, time, logging, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock

# Ensure local package path (tools/python_indicator_clone/src) is importable when running tests
_root = Path(__file__).resolve().parents[2] / 'tools' / 'python_indicator_clone'
_src = _root / 'src'
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
# Add project root for 'services' package imports when tests executed from clone dir
_proj_root = Path(__file__).resolve().parents[2]
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

# Import the unified fetch orchestrator module (module import allows tests to monkeypatch run.fetch)
import ql_indicator.run as run_mod  # type: ignore

log = logging.getLogger("quantlens.data_api")
if not log.handlers:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(title="QuantLens Data API", version="0.1.0", description="Unified market data fetch API with provider fallback, strict semantics, and rate limiting.")

# CORS configuration via QL_CORS_ORIGINS (comma separated) or default allow localhost
_origins_env = os.getenv("QL_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QL_VERSION = os.getenv("QL_VERSION", app.version)
GIT_SHA = os.getenv("GIT_SHA", "dev")
BUILT_AT = os.getenv("BUILT_AT", "local")

# Metrics state (simple in-process counters; thread-safe via Lock)
_METRICS: Dict[str, int] = {
    "fetch_success_total": 0,
    "fetch_error_total": 0,
    "rate_limit_hits_total": 0,
    "fallback_total": 0,
}
_METRICS_LOCK = Lock()

def _inc(metric: str, n: int = 1) -> None:
    with _METRICS_LOCK:
        _METRICS[metric] = _METRICS.get(metric, 0) + n

class ErrorOut(BaseModel):
    ok: bool = False
    code: int
    error: str

def get_api_key(
    key: Optional[str] = Query(None, alias="key"),
    x_api_key: Optional[str] = Header(None, alias="x-api-key", convert_underscores=False),
) -> str:
    token = x_api_key or key
    if not token:
        raise HTTPException(status_code=401, detail="missing api key")
    allowed = {k.strip() for k in os.getenv("QL_API_KEYS", "").split(",") if k.strip()}
    if token in allowed:
        return token
    raise HTTPException(status_code=401, detail="invalid api key")

# Simple in-memory rate limiting bucket: key -> list[timestamps]
_BUCKET: Dict[str, List[float]] = {}

def rate_limit(key: str = Depends(get_api_key)) -> str:
    win = 60.0
    cap = int(os.getenv("QL_RPM", "60"))
    now = time.time()
    lst = _BUCKET.setdefault(key, [])
    # drop old entries
    while lst and now - lst[0] > win:
        lst.pop(0)
    if len(lst) >= cap:
        _inc("rate_limit_hits_total")
        # custom raise; handler will add headers
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    lst.append(now)
    return key

class Bar(BaseModel):
    t: str
    o: float
    h: float
    l: float
    c: float
    v: float

class FetchOut(BaseModel):
    symbol: str
    tf: str
    provider: Optional[str] = None
    exchange: Optional[str] = None
    rows: int
    first: Optional[str]
    last: Optional[str]
    duration_ms: int
    data: List[Bar]

class FetchOutExample(BaseModel):
    symbol: str = "AAPL"
    tf: str = "1d"
    provider: Optional[str] = "yf"
    exchange: Optional[str] = None
    rows: int = 5
    first: str = "2024-01-01T00:00:00Z"
    last: str = "2024-01-05T00:00:00Z"
    duration_ms: int = 42
    data: list = Field(
        default=[
            {"t":"2024-01-01T00:00:00Z","o":185.21,"h":186.40,"l":184.97,"c":186.12,"v":45678900},
            {"t":"2024-01-02T00:00:00Z","o":186.12,"h":187.00,"l":185.50,"c":186.75,"v":43210000}
        ],
        description="Example truncated to 2 bars"
    )

@app.get(
    "/v1/fetch",
    response_model=FetchOut,
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": FetchOutExample().dict()}}},
        400: {"model": ErrorOut, "description": "Provider/validation error", "content": {"application/json": {"example": {"ok": False, "code": 400, "error": "no data from yfinance/polygon for AAPL 15m"}}}},
        401: {"model": ErrorOut, "description": "Missing or invalid API key", "content": {"application/json": {"example": {"ok": False, "code": 401, "error": "missing api key"}}}},
        429: {"model": ErrorOut, "description": "Rate limit exceeded", "content": {"application/json": {"example": {"ok": False, "code": 429, "error": "rate limit exceeded"}}}},
        500: {"model": ErrorOut, "description": "Unexpected error"},
    },
)
def fetch_endpoint(
    symbol: str,
    tf: str,
    response: Response,  # injected Response must precede defaulted params
    limit: Optional[int] = None,
    provider: Optional[str] = None,
    exchange: str = "binance",
    head_only: bool = False,
    key: str = Depends(rate_limit),
):
    t0 = time.perf_counter()
    try:
        df = run_mod.fetch(symbol=symbol, tf=tf, limit=limit, provider=provider, exchange_id=exchange)
    except Exception:
        _inc("fetch_error_total")
        raise
    dur = int((time.perf_counter() - t0) * 1000)

    if provider is None and "/" not in symbol and df.attrs.get("provider") == "polygon":  # fallback occurred
        _inc("fallback_total")

    bars: List[Bar] = []
    if not head_only and len(df):
        for ts, r in df.iterrows():
            bars.append(Bar(
                t=ts.isoformat(),
                o=float(r["open"]), h=float(r["high"]),
                l=float(r["low"]),  c=float(r["close"]),
                v=float(r["volume"])
            ))

    out = FetchOut(
        symbol=symbol,
        tf=str(df.attrs.get("freq", tf)),
        provider=provider or ("ccxt" if "/" in symbol else df.attrs.get("provider", "yf")),
        exchange=exchange if (provider or "/" in symbol) else None,
        rows=int(len(df)),
        first=df.index[0].isoformat() if len(df) else None,
        last=df.index[-1].isoformat() if len(df) else None,
        duration_ms=dur,
        data=bars,
    )
    _inc("fetch_success_total")
    log.info("fetch symbol=%s tf=%s rows=%d ms=%d key=%s", symbol, out.tf, out.rows, dur, key[:6]+"***")
    # Rate limit headers (best-effort; response may be None if tests bypass injection)
    try:
        cap = int(os.getenv("QL_RPM", "60"))
        used = len(_BUCKET.get(key, []))
        remaining = max(0, cap - used)
        now_dt = datetime.now(timezone.utc)
        window_reset = (now_dt.replace(second=0, microsecond=0) + timedelta(minutes=1))
        response.headers["X-RateLimit-Limit"] = str(cap)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(window_reset.timestamp()))
    except Exception:
        pass
    return out

@app.get("/")
def index():
    return {
        "name": "QuantLens Data API",
        "version": QL_VERSION,
        "git_sha": GIT_SHA,
        "built_at": BUILT_AT,
        "endpoints": ["/healthz", "/version", "/metrics", "/docs", "/v1/fetch"],
    }

@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {
        "name": "QuantLens Data API",
        "version": QL_VERSION,
        "git_sha": GIT_SHA,
        "built_at": BUILT_AT,
    }

@app.get("/metrics")
def metrics(x_api_key: Optional[str] = Header(None, alias="x-api-key", convert_underscores=False)):
    allowed = {k.strip() for k in os.getenv("QL_API_KEYS", "").split(",") if k.strip()}
    if x_api_key not in allowed:
        raise HTTPException(status_code=401, detail="unauthorized metrics")
    out_lines = []
    for k, v in _METRICS.items():
        out_lines.append(f"# HELP {k} {k.replace('_', ' ')}")
        out_lines.append(f"# TYPE {k} counter")
        out_lines.append(f"{k} {v}")
    return "\n".join(out_lines)

@app.get("/favicon.ico")
def favicon():
    # Try to serve existing svg logo if present; otherwise return minimal inline svg
    logo_path = Path(__file__).resolve().parents[2] / 'site' / 'assets' / 'ql-logo.svg'
    if logo_path.exists():
        return Response(content=logo_path.read_text(encoding='utf-8'), media_type='image/svg+xml')
    inline_svg = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='45' fill='#111'/><text x='50' y='57' font-size='42' text-anchor='middle' fill='#00d8ff' font-family='Arial,Helvetica,sans-serif'>QL</text></svg>"""
    return Response(content=inline_svg, media_type='image/svg+xml')

# ---------------- Uniform error handling -----------------

def _error_payload(status: int, msg: str):
    return {"ok": False, "code": status, "error": msg}

@app.exception_handler(HTTPException)
async def http_exc_handler(_request: Request, exc: HTTPException):
    headers = {}
    if exc.status_code == 429:
        now_dt = datetime.now(timezone.utc)
        window_reset = (now_dt.replace(second=0, microsecond=0) + timedelta(minutes=1))
        headers["Retry-After"] = "60"
        headers["X-RateLimit-Reset"] = str(int(window_reset.timestamp()))
    return JSONResponse(status_code=exc.status_code, content=_error_payload(exc.status_code, exc.detail), headers=headers)

@app.exception_handler(Exception)
async def unhandled_exc_handler(_request: Request, exc: Exception):
    log.exception("unhandled error")
    return JSONResponse(status_code=500, content=_error_payload(500, "internal error"))

# -------- OpenAPI security augmentation (apply ApiKeyAuth to all /v1/* paths) ---------
def _secure_openapi():  # pragma: no cover
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=os.getenv("QL_VERSION", app.version),
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "x-api-key",
        "description": "Provide your QuantLens API key in the X-API-Key header.",
    }
    for path, methods in schema.get("paths", {}).items():
        if not path.startswith("/v1/"):
            continue
        for m in methods.values():
            if isinstance(m, dict):
                m.setdefault("security", []).append({"ApiKeyAuth": []})
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = _secure_openapi  # type: ignore
