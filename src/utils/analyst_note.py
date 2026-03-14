"""Template-based analyst note for company deep dive."""

from typing import Any


def generate_analyst_note(
    company_name: str,
    rank: int,
    total: int,
    verdict: str,
    base_cagr: float,
    guidance_strength: str,
    confidence: str,
    key_evidence: list[str],
    conflicts_count: int,
) -> str:
    """
    Generate a concise PM-style analyst note.
    """
    lines = []
    lines.append(f"**Why this rank:** {company_name} ranks #{rank} of {total} in the sector based on base-case expected CAGR of {base_cagr:.1f}% and {verdict} verdict.")
    lines.append("")
    if key_evidence:
        lines.append(f"**Key upside driver:** {key_evidence[0]}")
    else:
        lines.append("**Key upside driver:** Management guidance supports revenue/margin trajectory; see Evidence tab for details.")
    lines.append("")
    if confidence == "Low" or conflicts_count > 0:
        lines.append("**Key risk:** Limited explicit guidance or conflicting statements across documents; treat scenario as indicative.")
    else:
        lines.append("**Key risk:** Execution and macro dependence; monitor next earnings for guidance reiteration.")
    lines.append("")
    lines.append("**What to monitor:** Next earnings call for updated guidance; order book and utilization for operational names.")
    lines.append("")
    lines.append(f"**Verdict:** {verdict}. Guidance strength: {guidance_strength}. Confidence: {confidence}.")
    return "\n".join(lines)
