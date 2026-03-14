"""Extract structured management guidance from company documents."""

from typing import Any

from pydantic import BaseModel, Field


class GuidanceAssumption(BaseModel):
    """A single structured assumption derived from management guidance."""

    metric: str = Field(description="e.g. revenue_growth, margin, capex")
    scenario: str = Field(description="bear | base | bull")
    value: float = Field(description="Numeric assumption")
    unit: str = Field(default="%", description="e.g. %, absolute")
    source_text: str | None = Field(default=None, description="Snippet from document")


class ExtractedGuidance(BaseModel):
    """Structured guidance extracted for one company."""

    company_id: str
    assumptions: list[GuidanceAssumption] = Field(default_factory=list)
    raw_quotes: list[str] = Field(default_factory=list, description="Key management quotes")


def extract_guidance(document: dict[str, Any]) -> ExtractedGuidance:
    """
    Extract management guidance and convert to structured assumptions.
    Placeholder: returns stub assumptions from document fields if present, else defaults.
    """
    company_id = document.get("company_id", "unknown")
    assumptions = []
    raw_quotes = document.get("raw_quotes") or document.get("quotes") or []

    # If document already has structured guidance, use it
    if "guidance" in document and isinstance(document["guidance"], list):
        for g in document["guidance"]:
            if isinstance(g, dict):
                assumptions.append(
                    GuidanceAssumption(
                        metric=g.get("metric", "revenue_growth"),
                        scenario=g.get("scenario", "base"),
                        value=float(g.get("value", 0)),
                        unit=g.get("unit", "%"),
                        source_text=g.get("source_text"),
                    )
                )
    if "assumptions" in document and isinstance(document["assumptions"], list):
        for a in document["assumptions"]:
            if isinstance(a, dict):
                assumptions.append(
                    GuidanceAssumption(
                        metric=a.get("metric", "revenue_growth"),
                        scenario=a.get("scenario", "base"),
                        value=float(a.get("value", 0)),
                        unit=a.get("unit", "%"),
                        source_text=a.get("source_text"),
                    )
                )

    # Stub: if no assumptions, add minimal placeholders
    if not assumptions:
        for scenario in ("bear", "base", "bull"):
            assumptions.append(
                GuidanceAssumption(
                    metric="revenue_growth",
                    scenario=scenario,
                    value={"bear": 3.0, "base": 6.0, "bull": 10.0}[scenario],
                    unit="%",
                    source_text=None,
                )
            )

    return ExtractedGuidance(company_id=company_id, assumptions=assumptions, raw_quotes=raw_quotes)
