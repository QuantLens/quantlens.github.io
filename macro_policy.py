"""
Macro decision policy helper

Production-ready, typed constraints/gating for trade decisions using the JSON "macro" block
emitted by LLM_JSON_Export_v6.pine.

Drop-in usage:

    from macro_policy import apply_macro_rules, enforce_no_trade_clause, PolicyConfig

    payload = ...  # JSON from Pine
    reg = payload.get("reg", {})
    out = apply_macro_rules(
        macro=payload.get("macro", {}),
        mtf_trend=reg.get("consensus"),  # "up"|"down"|"mixed"|None
        portfolio={"open_risk_R": 2.4, "buckets": {"btc_beta": 1.1}}
    )

    if out.decision == "ok":
        candidate = {"invalidate": 0.8, "risk_R": 0.4, "tp": [1.0, 1.8], "direction": "long"}
        status, reason = enforce_no_trade_clause(out.constraints, candidate, payload.get("macro",{}).get("state","neutral"), reg.get("consensus"))
        final = {"decision": "proceed", "constraints": asdict(out.constraints)} if status == "ok" else {"decision": "no_trade", "reason": reason}
    else:
        final = {"decision": "no_trade", "reason": out.reason}
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Literal, Any

MacroState = Literal["risk_off", "caution", "neutral", "supportive"]
Trend = Literal["up", "down", "mixed", "neutral", None]
Dir = Literal["long", "short"]


@dataclass
class Macro:
    state: MacroState = "neutral"
    dxy_trend: Literal["bullish", "neutral", "bearish", None] = "neutral"
    risk_mode: Literal["off", "neutral", "on", None] = "neutral"
    corr: Optional[Dict[str, Optional[float]]] = None
    score: Optional[float] = None
    confidence: Literal["low", "med", "high"] = "med"


@dataclass
class Portfolio:
    open_risk_R: float = 0.0                     # sum of open R across all positions
    risk_cap_R: float = 3.0                      # global cap (informational)
    buckets: Dict[str, float] = field(default_factory=dict)  # e.g., {"btc_beta": 1.2}


@dataclass
class PolicyConfig:
    # Global caps
    cap_aggregate_risk_R: float = 3.0
    # Bucket caps by macro state
    bucket_caps_R: Dict[str, Dict[MacroState, float]] = field(default_factory=dict)
    # Initial risk caps by macro state
    initial_risk_cap_R: Dict[MacroState, float] = field(default_factory=dict)
    # Size multipliers by macro state
    size_multiplier: Dict[MacroState, float] = field(default_factory=dict)
    # Confidence degraders (applied multiplicatively if not supportive)
    confidence_multiplier: Dict[str, float] = field(default_factory=dict)
    # Corr guard
    corr30_bearish_threshold: float = -0.5

    def __post_init__(self):
        if not self.bucket_caps_R:
            self.bucket_caps_R = {
                "btc_beta": {
                    "risk_off": 1.0,
                    "caution": 1.5,
                    "neutral": 2.0,
                    "supportive": 2.5,
                }
            }
        if not self.initial_risk_cap_R:
            self.initial_risk_cap_R = {
                "risk_off": 0.5,
                "caution": 0.75,
                "neutral": 1.0,
                "supportive": 1.0,
            }
        if not self.size_multiplier:
            self.size_multiplier = {
                "risk_off": 0.5,   # ceiling; you can still cap lower via initial_risk
                "caution": 0.5,
                "neutral": 1.0,
                "supportive": 1.0,
            }
        if not self.confidence_multiplier:
            self.confidence_multiplier = {
                "low": 0.5,
                "med": 0.75,
                "high": 1.0,
            }


@dataclass
class Constraints:
    ban_new_counter_trend_longs: bool = False
    require_trend_alignment: bool = False
    require_location_confluence: bool = False
    tighten_stop: bool = False
    discount_longs: bool = False
    raise_confirmation_bar: bool = False
    normal_playbook: bool = False
    cap_initial_risk_R: Optional[float] = None
    cap_aggregate_risk_R: float = 3.0
    size_multiplier: float = 1.0   # final multiplier after confidence adjustments


@dataclass
class Decision:
    decision: Literal["no_trade", "ok"] = "ok"
    reason: Optional[str] = None
    constraints: Constraints = field(default_factory=Constraints)


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        xf = float(x)
        if xf != xf:  # NaN check
            return None
        return xf
    except Exception:
        return None


def is_counter_trend(direction: Dir, mtf_trend: Trend) -> bool:
    if mtf_trend in (None, "mixed", "neutral"):
        return False  # unclear regime; don't call it counter-trend
    if direction == "long" and mtf_trend == "down":
        return True
    if direction == "short" and mtf_trend == "up":
        return True
    return False


def apply_macro_rules(
    macro: Dict[str, Any],
    mtf_trend: Trend = None,
    portfolio: Optional[Dict[str, Any]] = None,
    cfg: Optional[PolicyConfig] = None,
) -> Decision:
    cfg = cfg or PolicyConfig()
    m = Macro(
        state=(macro or {}).get("state", "neutral") or "neutral",
        dxy_trend=(macro or {}).get("dxy_trend", "neutral") or "neutral",
        risk_mode=(macro or {}).get("risk_mode", "neutral") or "neutral",
        corr=(macro or {}).get("corr"),
        score=(macro or {}).get("score"),
        confidence=(macro or {}).get("confidence", "med") or "med",
    )
    p = Portfolio(**(portfolio or {}))

    c = Constraints()
    c.cap_aggregate_risk_R = cfg.cap_aggregate_risk_R

    # State-driven core rules
    if m.state == "risk_off":
        c.ban_new_counter_trend_longs = True
        c.require_trend_alignment = True
        c.tighten_stop = True
        c.cap_initial_risk_R = cfg.initial_risk_cap_R["risk_off"]
    elif m.state == "caution":
        c.require_location_confluence = True
        c.cap_initial_risk_R = cfg.initial_risk_cap_R["caution"]
    elif m.state == "supportive":
        c.normal_playbook = True
        c.cap_initial_risk_R = cfg.initial_risk_cap_R["supportive"]
    else:
        c.cap_initial_risk_R = cfg.initial_risk_cap_R["neutral"]

    # DXY/corr guard
    corr30 = _safe_float((m.corr or {}).get("btc_dxy_30"))
    if m.dxy_trend == "bullish" and corr30 is not None and corr30 < cfg.corr30_bearish_threshold:
        c.discount_longs = True
        c.raise_confirmation_bar = True

    # Size multipliers with confidence degradation (unless supportive)
    base_mult = cfg.size_multiplier[m.state]
    conf_mult = cfg.confidence_multiplier.get(m.confidence, 0.75)
    c.size_multiplier = base_mult if m.state == "supportive" else base_mult * conf_mult

    # Portfolio caps
    if p.open_risk_R > c.cap_aggregate_risk_R:
        return Decision("no_trade", f"portfolio open risk {p.open_risk_R:.2f}R exceeds cap {c.cap_aggregate_risk_R:.2f}R", c)

    # BTC-beta bucket enforcement under adverse macro
    btc_beta_cap = cfg.bucket_caps_R["btc_beta"][m.state]
    btc_beta_open = float(p.buckets.get("btc_beta", 0.0))
    if m.state in ("risk_off", "caution") and btc_beta_open > btc_beta_cap:
        return Decision("no_trade", f"BTC-beta bucket {btc_beta_open:.2f}R exceeds cap {btc_beta_cap:.2f}R under {m.state}", c)

    return Decision("ok", None, c)


def enforce_no_trade_clause(
    constraints: Constraints,
    candidate: Dict[str, Any],
    macro_state: MacroState,
    mtf_trend: Trend = None,
) -> Tuple[Literal["ok", "no_trade"], Optional[str]]:
    inval = candidate.get("invalidate")
    risk_R = candidate.get("risk_R")
    tps: List[float] = candidate.get("tp") or []
    direction: Dir = candidate.get("direction", "long")

    if inval is None or risk_R is None or len(tps) == 0:
        return "no_trade", "macro uncertainty: missing invalidate/R/TP"

    # Counter-trend ban (longs only) in risk_off if alignment is required but not met
    if constraints.ban_new_counter_trend_longs and direction == "long":
        if constraints.require_trend_alignment and is_counter_trend("long", mtf_trend):
            return "no_trade", "counter-trend long banned under risk_off"

    if constraints.cap_initial_risk_R is not None and float(risk_R) > float(constraints.cap_initial_risk_R):
        return "no_trade", f"initial risk {float(risk_R):.2f}R exceeds cap {float(constraints.cap_initial_risk_R):.2f}R under {macro_state}"

    return "ok", None


__all__ = [
    "MacroState",
    "Trend",
    "Dir",
    "Macro",
    "Portfolio",
    "PolicyConfig",
    "Constraints",
    "Decision",
    "apply_macro_rules",
    "enforce_no_trade_clause",
    "asdict",
]
