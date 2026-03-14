"""Bull/base/bear valuation: project EPS, target price, and CAGR."""

from typing import Any

from pydantic import BaseModel, Field

# Default horizon for CAGR (years)
HORIZON_YEARS = 3


class ScenarioResult(BaseModel):
    """Valuation result for one scenario (bear/base/bull)."""
    scenario: str
    projected_eps: float
    projected_revenue: float = 0.0
    projected_margin: float = 0.0
    target_price: float
    cagr_pct: float


class ScenarioOutput(BaseModel):
    """Full scenario output for one company."""
    company_id: str
    company_name: str = ""
    current_price: float = 0.0
    current_eps: float = 0.0
    target_pe: float = 0.0
    horizon_years: int = HORIZON_YEARS
    bear: ScenarioResult | None = None
    base: ScenarioResult | None = None
    bull: ScenarioResult | None = None
    # For ranking: base-case values
    base_cagr_pct: float = 0.0
    base_target_price: float = 0.0
    verdict: str = ""  # High Conviction | Watchlist | Avoid | Insufficient Data


def _project_eps(current_eps: float, growth_pct: float, years: int) -> float:
    """Project EPS using constant annual growth: EPS_y = current_eps * (1 + g/100)^years."""
    if years <= 0:
        return current_eps
    return current_eps * ((1.0 + growth_pct / 100.0) ** years)


def _cagr_pct(current_price: float, target_price: float, years: int) -> float:
    """CAGR from current to target over years, in percent."""
    if current_price <= 0 or years <= 0:
        return 0.0
    if target_price <= 0:
        return 0.0
    mult = target_price / current_price
    return (mult ** (1.0 / years) - 1.0) * 100.0


def run_scenario_model(
    company_id: str,
    company_name: str,
    current_price: float,
    current_eps: float,
    target_pe: float,
    assumptions: Any,  # StructuredAssumptions from guidance_extractor
    horizon_years: int = HORIZON_YEARS,
    insufficient_guidance: bool = False,
) -> ScenarioOutput:
    """
    Project EPS over horizon using scenario growth rates, then target price = projected_eps * target_pe.
    CAGR from current price to target price over horizon.
    Bear = lower bound growth, Base = midpoint, Bull = upper bound.
    """
    # Read growth rates from assumptions (dict or Pydantic model)
    g_bear = 0.0
    g_base = 0.0
    g_bull = 0.0
    if isinstance(assumptions, dict):
        g_bear = float(assumptions.get("bear_revenue_growth") or 0)
        g_base = float(assumptions.get("base_revenue_growth") or 0)
        g_bull = float(assumptions.get("bull_revenue_growth") or 0)
    else:
        ad = assumptions.model_dump() if hasattr(assumptions, "model_dump") else {}
        if ad:
            g_bear = float(ad.get("bear_revenue_growth") or 0)
            g_base = float(ad.get("base_revenue_growth") or 0)
            g_bull = float(ad.get("bull_revenue_growth") or 0)

    out = ScenarioOutput(
        company_id=company_id,
        company_name=company_name,
        current_price=current_price,
        current_eps=current_eps,
        target_pe=target_pe,
        horizon_years=horizon_years,
        verdict="Insufficient Data" if insufficient_guidance else "",
    )
    if insufficient_guidance or current_eps <= 0 or target_pe <= 0 or current_price <= 0:
        return out

    # Optional revenue/margin for display (current_revenue from dossier if available)
    current_revenue = getattr(assumptions, "current_revenue", None) if not isinstance(assumptions, dict) else assumptions.get("current_revenue")
    if isinstance(assumptions, dict):
        m_bear = float(assumptions.get("bear_margin") or 0)
        m_base = float(assumptions.get("base_margin") or 0)
        m_bull = float(assumptions.get("bull_margin") or 0)
    else:
        ad = assumptions.model_dump() if hasattr(assumptions, "model_dump") else {}
        m_bear = float(ad.get("bear_margin") or 0)
        m_base = float(ad.get("base_margin") or 0)
        m_bull = float(ad.get("bull_margin") or 0)
    current_revenue = float(current_revenue or 0)

    def make_result(scenario: str, growth: float, margin_pct: float) -> ScenarioResult:
        proj_eps = _project_eps(current_eps, growth, horizon_years)
        target_price = round(proj_eps * target_pe, 2)
        cagr = round(_cagr_pct(current_price, target_price, horizon_years), 2)
        proj_rev = current_revenue * ((1.0 + growth / 100.0) ** horizon_years) if current_revenue else 0.0
        return ScenarioResult(
            scenario=scenario,
            projected_eps=round(proj_eps, 4),
            projected_revenue=round(proj_rev, 2),
            projected_margin=round(margin_pct, 2),
            target_price=target_price,
            cagr_pct=cagr,
        )

    out.bear = make_result("bear", g_bear, m_bear)
    out.base = make_result("base", g_base, m_base)
    out.bull = make_result("bull", g_bull, m_bull)
    out.base_cagr_pct = out.base.cagr_pct
    out.base_target_price = out.base.target_price
    out.verdict = _verdict_from_base_cagr(out.base_cagr_pct)
    return out


def _verdict_from_base_cagr(base_cagr_pct: float) -> str:
    """High Conviction >20%, Watchlist 10–20%, Avoid <10%."""
    if base_cagr_pct > 20:
        return "High Conviction"
    if base_cagr_pct >= 10:
        return "Watchlist"
    return "Avoid"


def rank_companies(outputs: list[ScenarioOutput]) -> list[ScenarioOutput]:
    """Rank by base-case CAGR descending. Insufficient Data last."""
    def key(o: ScenarioOutput) -> tuple[int, float]:
        # Insufficient Data goes last
        if o.verdict == "Insufficient Data":
            return (1, -1e9)
        return (0, o.base_cagr_pct)
    return sorted(outputs, key=key, reverse=True)
