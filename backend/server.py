"""FastAPI backend for AnalystOS - wraps existing Python logic."""

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.parsers.load_documents import (
    load_sector_mapping,
    get_companies_for_sector,
    fetch_sector_dossiers,
)
from src.pipeline.run_analysis import run_full_analysis
from src.utils.io_helpers import load_financial_json, load_processed_json, to_slug
from src.utils.constants import DATA_FINANCIALS, DATA_PROCESSED

app = FastAPI(title="AnalystOS API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for analysis results
analysis_cache: dict[str, Any] = {}


class RunAnalysisRequest(BaseModel):
    sector: str
    selected_companies: list[str] | None = None  # List of company IDs to analyze
    run_extraction: bool = False
    api_key: str | None = None


@app.get("/")
async def root():
    return {"message": "AnalystOS API", "status": "running"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/sectors")
async def get_sectors():
    """Get list of available sectors."""
    mapping = load_sector_mapping()
    sectors = list(mapping.keys()) if mapping else []
    if not sectors:
        sectors = ["power_equipment", "Technology", "Healthcare", "Consumer"]
    return {"sectors": sectors, "mapping": mapping}


@app.get("/api/sectors/{sector}/companies")
async def get_sector_companies(sector: str):
    """Get companies for a specific sector."""
    companies = get_companies_for_sector(sector)
    return {"sector": sector, "companies": companies}


@app.get("/api/sectors/{sector}/dossiers")
async def get_sector_dossiers(sector: str):
    """Fetch sector dossiers (company folders + metadata)."""
    dossiers = fetch_sector_dossiers(sector)
    # Convert to JSON-serializable format
    dossiers_json = []
    for d in dossiers:
        dossiers_json.append({
            "company_id": d.get("company_id"),
            "company_name": d.get("company_name"),
            "sector": d.get("sector"),
            "pdf_files": d.get("pdf_files", []),
            "has_guidance": bool(d.get("guidance") or d.get("management_guidance")),
        })
    return {"sector": sector, "count": len(dossiers_json), "dossiers": dossiers_json}


@app.post("/api/analysis/run")
async def run_analysis(request: RunAnalysisRequest):
    """Run full AnalystOS pipeline for a sector with optional company filtering."""
    sector = request.sector
    selected_companies = request.selected_companies
    
    # Create cache key including selected companies
    cache_key = f"{sector}_{','.join(sorted(selected_companies)) if selected_companies else 'all'}_{request.run_extraction}"
    if cache_key in analysis_cache:
        return analysis_cache[cache_key]
    
    try:
        result = run_full_analysis(
            sector,
            run_extraction=request.run_extraction,
            api_key=request.api_key,
            selected_companies=selected_companies,  # Pass selected companies to analysis
        )
        
        # Convert result to JSON-serializable format
        response = {
            "sector": sector,
            "step_statuses": result.get("step_statuses", {}),
            "activity_log": result.get("activity_log", []),
            "ranked": [],
            "company_results": [],
        }
        
        # Process ranked companies
        for output in result.get("ranked", []):
            ranked_item = {
                "company_id": output.company_id,
                "company_name": output.company_name,
                "verdict": output.verdict,
                "base_cagr_pct": output.base_cagr_pct,
                "bear": {
                    "cagr_pct": output.bear.cagr_pct,
                    "target_price": output.bear.target_price,
                } if output.bear else None,
                "base": {
                    "cagr_pct": output.base.cagr_pct,
                    "target_price": output.base.target_price,
                } if output.base else None,
                "bull": {
                    "cagr_pct": output.bull.cagr_pct,
                    "target_price": output.bull.target_price,
                } if output.bull else None,
            }
            response["ranked"].append(ranked_item)
        
        # Process company results
        for cr in result.get("company_results", []):
            output = cr["output"]
            guidance = cr["guidance"]
            merged = cr.get("merged", {})
            
            company_result = {
                "company_id": output.company_id,
                "company_name": output.company_name,
                "guidance_strength": cr.get("guidance_strength", ""),
                "confidence": cr.get("confidence", ""),
                "verdict": output.verdict,
                "current_price": output.current_price,
                "current_eps": output.current_eps,
                "target_pe": output.target_pe,
                "assumptions": {
                    "bear_revenue_growth": guidance.assumptions.bear_revenue_growth,
                    "base_revenue_growth": guidance.assumptions.base_revenue_growth,
                    "bull_revenue_growth": guidance.assumptions.bull_revenue_growth,
                    "bear_margin": guidance.assumptions.bear_margin,
                    "base_margin": guidance.assumptions.base_margin,
                    "bull_margin": guidance.assumptions.bull_margin,
                },
                "quotes": guidance.quotes,
                "conflicts": guidance.conflicts,
                "scenarios": {
                    "bear": {
                        "projected_eps": output.bear.projected_eps,
                        "projected_revenue": output.bear.projected_revenue,
                        "projected_margin": output.bear.projected_margin,
                        "target_price": output.bear.target_price,
                        "cagr_pct": output.bear.cagr_pct,
                    } if output.bear else None,
                    "base": {
                        "projected_eps": output.base.projected_eps,
                        "projected_revenue": output.base.projected_revenue,
                        "projected_margin": output.base.projected_margin,
                        "target_price": output.base.target_price,
                        "cagr_pct": output.base.cagr_pct,
                    } if output.base else None,
                    "bull": {
                        "projected_eps": output.bull.projected_eps,
                        "projected_revenue": output.bull.projected_revenue,
                        "projected_margin": output.bull.projected_margin,
                        "target_price": output.bull.target_price,
                        "cagr_pct": output.bull.cagr_pct,
                    } if output.bull else None,
                },
                "financials": merged.get("financials", {}),
                "has_financials": bool(merged.get("financials")),
            }
            response["company_results"].append(company_result)
        
        # Cache result
        analysis_cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{company_id}/financials")
async def get_company_financials(company_id: str):
    """Get historical financials for a company."""
    slug = to_slug(company_id)
    financials = load_financial_json(slug)
    
    if not financials:
        raise HTTPException(status_code=404, detail=f"Financials not found for {company_id}")
    
    return {"company_id": company_id, "slug": slug, "financials": financials}


@app.get("/api/companies/{company_id}/guidance")
async def get_company_guidance(company_id: str):
    """Get extracted guidance for a company."""
    slug = to_slug(company_id)
    processed = load_processed_json(slug)
    
    if not processed:
        raise HTTPException(status_code=404, detail=f"Guidance not found for {company_id}")
    
    return {"company_id": company_id, "slug": slug, "data": processed}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
