"""
AnalystOS — Lightweight AI equity analyst workflow.
Streamlit entrypoint: run from project root with
  streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# Ensure project root is on path when running from app/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.parsers.load_documents import list_available_companies, load_company_document
from src.extractors.guidance_extractor import extract_guidance
from src.models.scenario_model import run_scenario_model, rank_companies
from src.utils.constants import DATA_PROCESSED
from src.utils.io_helpers import save_json, ensure_dir
from src.utils.constants import OUTPUTS_DIR

st.set_page_config(page_title="AnalystOS", layout="wide")

# ---- Title ----
st.title("AnalystOS")
st.caption("Lightweight end-to-end AI equity analyst: guidance → assumptions → bull/base/bear valuation → ranking")

# ---- Sidebar: sector / company selector ----
with st.sidebar:
    st.header("Sector / Company")
    data_dir = DATA_PROCESSED
    companies = list_available_companies(data_dir)
    sector_placeholder = st.selectbox(
        "Sector (placeholder)",
        ["Technology", "Healthcare", "Consumer"],
        key="sector",
    )
    company_choice = st.selectbox(
        "Company",
        companies if companies else ["(No companies — add JSON to data/processed/)"],
        key="company",
    )

# ---- Main area ----
# 1. Upload / Load Documents
st.header("Upload / Load Documents")
if companies and company_choice and not company_choice.startswith("("):
    doc = load_company_document(company_choice, data_dir)
    st.success(f"Loaded **{company_choice}** from `data/processed/`")
    with st.expander("Raw document (preview)"):
        st.json(doc)
else:
    st.info("Add sample JSON files to `data/processed/` (e.g. `acme_corp.json`) to load a company.")
    doc = None

# 2. Extracted Guidance
st.header("Extracted Guidance")
if doc:
    guidance = extract_guidance(doc)
    st.write(f"**Company:** {guidance.company_id}")
    st.write("**Assumptions:**")
    for a in guidance.assumptions:
        st.write(f"- {a.scenario}: {a.metric} = {a.value} {a.unit}")
    if guidance.raw_quotes:
        st.write("**Quotes:**")
        for q in guidance.raw_quotes:
            st.caption(q)
else:
    st.write("Load a document above to see extracted guidance.")

# 3. Scenario Outputs
st.header("Scenario Outputs")
if doc:
    guidance = extract_guidance(doc)
    assumptions = [a.model_dump() for a in guidance.assumptions]
    verdict = run_scenario_model(doc["company_id"], assumptions)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bear — Target", verdict.bear.target_price)
        st.caption(f"CAGR: {verdict.bear.cagr}%")
    with col2:
        st.metric("Base — Target", verdict.base.target_price)
        st.caption(f"CAGR: {verdict.base.cagr}%")
    with col3:
        st.metric("Bull — Target", verdict.bull.target_price)
        st.caption(f"CAGR: {verdict.bull.cagr}%")
    st.write(f"**Verdict:** {verdict.verdict}")
else:
    st.write("Load a document to see scenario outputs.")

# 4. Final Ranking
st.header("Final Ranking")
if doc and companies and not company_choice.startswith("("):
    # Build verdicts for all loaded companies for ranking demo
    verdicts = []
    for cid in companies:
        d = load_company_document(cid, data_dir)
        g = extract_guidance(d)
        v = run_scenario_model(cid, [a.model_dump() for a in g.assumptions])
        verdicts.append(v)
    ranked = rank_companies(verdicts)
    rows = [
        {
            "Rank": i + 1,
            "Company": v.company_id,
            "Expected CAGR %": v.expected_cagr,
            "Target Price": v.target_price,
            "Verdict": v.verdict,
        }
        for i, v in enumerate(ranked)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    # Optional: save to outputs
    ensure_dir(OUTPUTS_DIR)
    out_path = Path(OUTPUTS_DIR) / "ranking_output.json"
    save_json(
        [{"company_id": v.company_id, "expected_cagr": v.expected_cagr, "target_price": v.target_price, "verdict": v.verdict} for v in ranked],
        str(out_path),
    )
    st.caption(f"Output saved to `{out_path}`")
else:
    st.write("Load at least one company to see the ranking table.")
