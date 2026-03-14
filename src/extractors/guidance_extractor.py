"""Extract explicit management guidance into bear/base/bull assumptions."""

from typing import Any

from pydantic import BaseModel, Field


class GuidanceEntry(BaseModel):
    """One management guidance entry from a dossier (for typing/validation)."""
    metric: str
    type: str  # "explicit" | "directional"
    value_min: float | None = None
    value_max: float | None = None
    timeline: str | None = None
    source: str | None = None
    quote: str | None = None


class StructuredAssumptions(BaseModel):
    """
    Bear/base/bull assumptions derived from explicit guidance.
    Missing metrics are None (e.g. no margin guidance).
    """
    # Revenue growth (%)
    bear_revenue_growth: float | None = None
    base_revenue_growth: float | None = None
    bull_revenue_growth: float | None = None
    # Operating margin (%)
    bear_margin: float | None = None
    base_margin: float | None = None
    bull_margin: float | None = None


class ExtractedGuidance(BaseModel):
    """Full extraction result for one company."""
    company_id: str
    company_name: str = ""
    # Only explicit guidance used for modeling
    assumptions: StructuredAssumptions = Field(default_factory=StructuredAssumptions)
    # All guidance quotes for UI (explicit + directional)
    quotes: list[dict[str, Any]] = Field(default_factory=list)
    # True when no usable explicit revenue growth → mark "Insufficient Data"
    insufficient_guidance: bool = False


def _midpoint(min_val: float | None, max_val: float | None) -> float | None:
    if min_val is not None and max_val is not None:
        return (min_val + max_val) / 2.0
    return min_val if min_val is not None else max_val


def extract_guidance(dossier: dict[str, Any]) -> ExtractedGuidance:
    """
    Read company dossier and extract explicit guidance for revenue_growth and margin.
    Bear = value_min, Base = midpoint, Bull = value_max.
    Directional guidance is included in quotes but not used for numeric assumptions.
    """
    company_id = dossier.get("company_id", "unknown")
    company_name = dossier.get("company_name", company_id)
    raw = dossier.get("management_guidance") or []
    quotes: list[dict[str, Any]] = []
    rev_bear, rev_base, rev_bull = None, None, None
    margin_bear, margin_base, margin_bull = None, None, None

    for g in raw:
        if not isinstance(g, dict):
            continue
        metric = (g.get("metric") or "").strip().lower()
        gtype = (g.get("type") or "").strip().lower()
        q = g.get("quote") or ""
        # Store all quotes for UI
        quotes.append({
            "metric": metric,
            "type": gtype,
            "quote": q,
            "source": g.get("source"),
            "timeline": g.get("timeline"),
        })
        if gtype != "explicit":
            continue
        try:
            vmin = g.get("value_min")
            vmax = g.get("value_max")
            if vmin is not None:
                vmin = float(vmin)
            if vmax is not None:
                vmax = float(vmax)
        except (TypeError, ValueError):
            continue
        if metric == "revenue_growth":
            rev_bear = vmin
            rev_bull = vmax
            rev_base = _midpoint(vmin, vmax)
        elif metric == "margin":
            margin_bear = vmin
            margin_bull = vmax
            margin_base = _midpoint(vmin, vmax)

    # Require at least one explicit revenue growth range for modeling
    has_revenue_guidance = rev_bear is not None or rev_base is not None or rev_bull is not None
    insufficient_guidance = not has_revenue_guidance

    assumptions = StructuredAssumptions(
        bear_revenue_growth=rev_bear,
        base_revenue_growth=rev_base,
        bull_revenue_growth=rev_bull,
        bear_margin=margin_bear,
        base_margin=margin_base,
        bull_margin=margin_bull,
    )
    return ExtractedGuidance(
        company_id=company_id,
        company_name=company_name,
        assumptions=assumptions,
        quotes=quotes,
        insufficient_guidance=insufficient_guidance,
    )
