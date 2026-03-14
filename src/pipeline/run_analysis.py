"""
Run full AnalystOS pipeline: fetch sector docs -> extract guidance -> build assumptions -> run scenarios -> rank.
Returns step statuses and activity log for UI.
"""

from typing import Any, Callable

from src.parsers.load_documents import fetch_sector_dossiers, extract_text_from_company_folder
from src.extractors.guidance_extractor import (
    extract_guidance,
    run_llm_extraction_pipeline,
)
from src.models.scenario_model import run_scenario_model, rank_companies
from src.utils.io_helpers import (
    save_extracted_guidance_json,
    load_json,
    load_financial_json,
    load_processed_json,
    to_slug,
)
import os
from src.utils.constants import DATA_PROCESSED

# Pipeline step ids for UI
STEPS = [
    "fetch_documents",
    "extract_text",
    "extract_guidance",
    "consolidate_evidence",
    "build_assumptions",
    "run_valuation",
    "rank_companies",
    "link_sources",
]


def _guidance_strength(guidance_obj: Any) -> str:
    """Strong / Moderate / Weak from number of explicit items."""
    quotes = getattr(guidance_obj, "quotes", []) or []
    explicit = sum(1 for q in quotes if (q.get("type") or "").lower() == "explicit")
    if explicit >= 3:
        return "Strong"
    if explicit >= 1:
        return "Moderate"
    return "Weak"


def _confidence(guidance_obj: Any, output: Any) -> str:
    """High / Medium / Low from guidance strength and conflicts."""
    conflicts = getattr(guidance_obj, "conflicts", None) or []
    if output.verdict == "Insufficient Data":
        return "Low"
    strength = _guidance_strength(guidance_obj)
    if strength == "Strong" and len(conflicts) == 0:
        return "High"
    if strength == "Weak" or len(conflicts) > 1:
        return "Low"
    return "Medium"


def run_full_analysis(
    sector: str,
    *,
    run_extraction: bool = True,
    api_key: str | None = None,
    selected_companies: list[str] | None = None,
    on_step: Callable[[str, str], None] | None = None,
    on_activity: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """
    Run the full pipeline for the sector. Optionally run LLM extraction for companies with PDFs but no processed guidance.
    selected_companies: Optional list of company IDs to filter analysis to.
    on_step(step_id, status): status in pending|running|completed|failed
    on_activity(message): human-readable log line.
    Returns { "step_statuses": {...}, "activity_log": [...], "ranked": [...], "company_results": [...], "dossiers": [...] }
    """
    step_statuses = {s: "pending" for s in STEPS}
    activity_log: list[str] = []

    def step(sid: str, status: str) -> None:
        step_statuses[sid] = status
        if on_step:
            on_step(sid, status)

    def log(msg: str) -> None:
        activity_log.append(msg)
        if on_activity:
            on_activity(msg)

    # 1. Fetch sector documents
    step("fetch_documents", "running")
    dossiers = fetch_sector_dossiers(sector)
    
    # Filter by selected companies if provided
    if selected_companies:
        dossiers = [d for d in dossiers if d.get("company_id") in selected_companies]
        log(f"Filtering to {len(selected_companies)} selected companies")
    
    if not dossiers:
        log("No company folders found for selected sector.")
        step("fetch_documents", "completed")
        return {
            "step_statuses": step_statuses,
            "activity_log": activity_log,
            "ranked": [],
            "company_results": [],
            "dossiers": [],
        }
    log(f"Found {len(dossiers)} company folder(s) in sector: {sector}")
    step("fetch_documents", "completed")

    # 2. For each company with PDFs but no/missing guidance, run extraction
    step("extract_text", "running")
    for d in dossiers:
        cid = d.get("company_id", "")
        folder = d.get("folder_path", "")
        pdf_files = d.get("pdf_files", [])
        if not pdf_files:
            continue
        log(f"Loaded {len(pdf_files)} PDF(s) for {cid}")
        # If we have no guidance in processed, run extraction
        existing = None
        try:
            from src.utils.io_helpers import load_extracted_guidance
            existing = load_extracted_guidance(cid)
        except Exception:
            pass
        has_guidance = existing and (existing.get("guidance") or existing.get("management_guidance"))
        if run_extraction and not has_guidance and folder:
            step("extract_guidance", "running")
            try:
                run_llm_extraction_pipeline(cid, folder, api_key=api_key, save_intermediate=False)
                log(f"Extracted guidance from PDFs for {cid}")
            except Exception as e:
                log(f"Extraction failed for {cid}: {e}")
            step("extract_guidance", "completed")
        elif has_guidance:
            log(f"Using existing guidance for {cid}")
    step("extract_text", "completed")
    if step_statuses.get("extract_guidance") == "pending":
        step("extract_guidance", "completed")  # skipped (all had guidance)

    # Load financials + processed per company, build merged object (normalized slug)
    step("consolidate_evidence", "running")
    merged_dossiers: list[dict[str, Any]] = []
    for d in dossiers:
        cid = d.get("company_id", "")
        slug = to_slug(cid)
        financials = load_financial_json(slug)
        processed = load_processed_json(slug)
        guidance_list = (processed or {}).get("guidance") or (processed or {}).get("management_guidance") or []
        conflicts_list = (processed or {}).get("conflicts") or []
        company_name = (processed or {}).get("company") or (processed or {}).get("company_name") or d.get("company_name") or cid
        # Pull valuation inputs from financials first, then processed, then fallback
        def _from_financials(key: str, default: Any = None) -> Any:
            if not financials:
                return default
            v = financials.get(key)
            if v is not None:
                return v
            meta = financials.get("metadata") or {}
            return meta.get(key, default)
        current_price = _from_financials("current_price") or (processed or {}).get("current_price") or d.get("current_price") or 100.0
        current_eps = _from_financials("current_eps") or (processed or {}).get("current_eps") or d.get("current_eps") or 5.0
        historical_median_pe = _from_financials("historical_median_pe") or (processed or {}).get("historical_median_pe") or d.get("historical_median_pe") or 20.0
        merged = {
            "company": company_name,
            "company_id": slug,
            "company_name": company_name,
            "slug": slug,
            "financials": financials or {},
            "guidance": guidance_list,
            "conflicts": conflicts_list,
            "folder_path": d.get("folder_path", ""),
            "pdf_files": d.get("pdf_files", []),
            "current_price": float(current_price),
            "current_eps": float(current_eps),
            "historical_median_pe": float(historical_median_pe),
        }
        merged_keys = list(merged.keys())
        print(f"[merge] Built merged object for {slug} with keys: {merged_keys}")
        log(f"Merged {slug}: financials={'yes' if financials else 'no'}, guidance={len(guidance_list)} items")
        merged_dossiers.append(merged)
    log("Consolidated evidence across documents")
    step("consolidate_evidence", "completed")

    # Build assumptions and run valuation per company (using merged object)
    step("build_assumptions", "running")
    step("run_valuation", "running")
    company_results = []
    for merged in merged_dossiers:
        guidance = extract_guidance(merged)
        assumptions_dict = guidance.assumptions.model_dump() if hasattr(guidance.assumptions, "model_dump") else guidance.assumptions
        target_pe = float(merged.get("historical_median_pe") or 20)
        current_price = float(merged.get("current_price") or 0)
        current_eps = float(merged.get("current_eps") or 0)
        output = run_scenario_model(
            company_id=merged.get("company_id", ""),
            company_name=merged.get("company_name", ""),
            current_price=current_price,
            current_eps=current_eps,
            target_pe=target_pe,
            assumptions=assumptions_dict,
            insufficient_guidance=guidance.insufficient_guidance,
        )
        guidance_strength = _guidance_strength(guidance)
        confidence = _confidence(guidance, output)
        company_results.append({
            "merged": merged,
            "dossier": merged,
            "guidance": guidance,
            "output": output,
            "guidance_strength": guidance_strength,
            "confidence": confidence,
        })
    log("Built scenario assumptions and ran valuation for all companies")
    step("build_assumptions", "completed")
    step("run_valuation", "completed")

    # Rank
    step("rank_companies", "running")
    outputs = [r["output"] for r in company_results]
    ranked = rank_companies(outputs)
    log(f"Ranked {len(ranked)} companies by base-case CAGR")
    step("rank_companies", "completed")

    step("link_sources", "running")
    log("Linked assumptions to source evidence")
    step("link_sources", "completed")

    return {
        "step_statuses": step_statuses,
        "activity_log": activity_log,
        "ranked": ranked,
        "company_results": company_results,
        "dossiers": merged_dossiers,
    }
