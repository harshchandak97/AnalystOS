"""Bull / base / bear scenario model: target price, CAGR, and verdict."""

from typing import Any

from pydantic import BaseModel, Field


class ScenarioResult(BaseModel):
    """Valuation result for one scenario."""

    scenario: str = Field(description="bear | base | bull")
    target_price: float = Field(description="Target price")
    cagr: float = Field(description="Expected CAGR %")
    assumptions_used: dict[str, float] = Field(default_factory=dict)


class CompanyVerdict(BaseModel):
    """Final output for one company: scenarios plus ranking fields."""

    company_id: str
    bear: ScenarioResult
    base: ScenarioResult
    bull: ScenarioResult
    expected_cagr: float = Field(description="e.g. base-case or weighted CAGR")
    target_price: float = Field(description="e.g. base-case target")
    verdict: str = Field(description="e.g. Buy / Hold / Sell or score")


def run_scenario_model(
    company_id: str,
    assumptions: list[dict[str, Any]],
) -> CompanyVerdict:
    """
    Run bull/base/bear valuation and return target price, CAGR, and verdict.
    Placeholder: uses assumptions to build stub ScenarioResults.
    """
    # Group by scenario
    by_scenario: dict[str, dict[str, float]] = {"bear": {}, "base": {}, "bull": {}}
    for a in assumptions:
        if isinstance(a, dict):
            sc = a.get("scenario", "base")
            if sc in by_scenario:
                by_scenario[sc][a.get("metric", "revenue_growth")] = float(a.get("value", 0))
        else:
            by_scenario["base"]["revenue_growth"] = 6.0

    # Stub target price and CAGR from revenue growth
    def make_result(scenario: str) -> ScenarioResult:
        growth = by_scenario.get(scenario, {}).get("revenue_growth", 5.0)
        # Placeholder formula: target = 100 * (1 + growth/100), cagr = growth
        target = 100.0 * (1.0 + growth / 100.0)
        return ScenarioResult(
            scenario=scenario,
            target_price=round(target, 2),
            cagr=round(growth, 2),
            assumptions_used=by_scenario.get(scenario, {}),
        )

    bear = make_result("bear")
    base = make_result("base")
    bull = make_result("bull")

    verdict = "Buy" if base.cagr >= 6 else "Hold" if base.cagr >= 3 else "Sell"

    return CompanyVerdict(
        company_id=company_id,
        bear=bear,
        base=base,
        bull=bull,
        expected_cagr=base.cagr,
        target_price=base.target_price,
        verdict=verdict,
    )


def rank_companies(verdicts: list[CompanyVerdict]) -> list[CompanyVerdict]:
    """Rank companies by expected CAGR (descending)."""
    return sorted(verdicts, key=lambda v: v.expected_cagr, reverse=True)
