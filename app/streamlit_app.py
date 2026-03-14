"""
AnalystOS — AI-native sector analyst workflow.
Run from project root: streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.parsers.load_documents import (
    get_companies_for_sector,
    fetch_sector_dossiers,
    list_company_folders_in_raw,
    load_sector_mapping,
)
from src.pipeline.run_analysis import run_full_analysis, STEPS
from src.utils.constants import DATA_RAW, OUTPUTS_DIR
from src.utils.io_helpers import save_ranking_csv, ensure_dir
from src.utils.analyst_note import generate_analyst_note

st.set_page_config(page_title="AnalystOS", layout="wide")

# Session state
if "dossiers" not in st.session_state:
    st.session_state.dossiers = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "step_statuses" not in st.session_state:
    st.session_state.step_statuses = {s: "pending" for s in STEPS}
if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

# ---- A. PRODUCT HEADER ----
st.title("AnalystOS")
st.caption("**AI-native sector analyst workflow**")
st.markdown(
    "Select a sector. AnalystOS automatically fetches company documents, extracts forward guidance, "
    "builds model-ready assumptions, runs bull/base/bear scenarios, and ranks opportunities with full source traceability."
)
st.divider()

# ---- B. SIDEBAR ----
with st.sidebar:
    st.header("Sector & companies")
    mapping = load_sector_mapping()
    sector_options = list(mapping.keys()) if mapping else []
    if not sector_options:
        sector_options = ["power_equipment", "Technology", "Healthcare", "Consumer"]
    sector = st.selectbox("Sector", sector_options, key="sector")
    companies_raw = get_companies_for_sector(sector)
    st.caption(f"Companies in sector: {', '.join(companies_raw) or 'None'}")
    if st.button("Fetch Sector Documents", type="primary"):
        dossiers = fetch_sector_dossiers(sector)
        st.session_state.dossiers = dossiers
        st.session_state.analysis_result = None
        st.success(f"Fetched {len(dossiers)} companies")
    st.divider()
    if st.button("Run AnalystOS"):
        if not st.session_state.dossiers:
            st.warning("Click Fetch Sector Documents first.")
        else:
            st.session_state.step_statuses = {s: "pending" for s in STEPS}
            st.session_state.activity_log = []
            result = run_full_analysis(
                sector,
                run_extraction=True,
                on_step=lambda sid, status: st.session_state.step_statuses.update({sid: status}),
                on_activity=lambda msg: st.session_state.activity_log.append(msg),
            )
            st.session_state.analysis_result = result
            st.session_state.step_statuses = result.get("step_statuses", st.session_state.step_statuses)
            st.session_state.activity_log = result.get("activity_log", [])
            st.success("Analysis complete.")
    st.divider()
    company_options = [r["output"].company_name or r["output"].company_id for r in (st.session_state.analysis_result or {}).get("company_results", [])]
    selected_company = st.selectbox("Company deep dive", [""] + company_options, key="drilldown_company") if company_options else None

dossiers = st.session_state.dossiers
result = st.session_state.analysis_result
step_statuses = st.session_state.step_statuses
activity_log = st.session_state.activity_log

# ---- C. ANALYSIS PIPELINE ----
st.header("Analysis Pipeline")
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Step tracker")
    for sid in STEPS:
        status = step_statuses.get(sid, "pending")
        label = sid.replace("_", " ").title()
        if status == "completed":
            st.success(f"✓ {label}")
        elif status == "running":
            st.info(f"▶ {label}...")
        elif status == "failed":
            st.error(f"✗ {label}")
        else:
            st.caption(f"○ {label}")
with col2:
    st.subheader("Activity log")
    for line in activity_log[-20:]:
        st.caption(line)
    if not activity_log:
        st.caption("Run AnalystOS to see activity.")

st.divider()

# ---- D. SECTOR LEADERBOARD ----
st.header("Sector Opportunity Ranking")
if result and result.get("ranked"):
    ranked = result["ranked"]
    company_results = {r["output"].company_id: r for r in result["company_results"]}
    rows = []
    for i, o in enumerate(ranked):
        r = company_results.get(o.company_id, {})
        g = r.get("guidance")
        strength = r.get("guidance_strength", "")
        confidence = r.get("confidence", "")
        assumptions = g.assumptions if g else None
        rev_anchor = f"{assumptions.base_revenue_growth}%" if assumptions and assumptions.base_revenue_growth is not None else "—"
        margin_anchor = f"{assumptions.base_margin}%" if assumptions and assumptions.base_margin is not None else "—"
        quotes = getattr(g, "quotes", []) or []
        rev_src = next((q.get("source", "") for q in quotes if (q.get("metric") or "").lower() == "revenue_growth"), "")
        margin_src = next((q.get("source", "") for q in quotes if (q.get("metric") or "").lower() in ("ebitda_margin", "margin_floor", "margin")), "")
        rows.append({
            "Company": o.company_name or o.company_id,
            "Guidance Strength": strength,
            "Revenue Anchor": rev_anchor,
            "Margin Anchor": margin_anchor,
            "Base CAGR %": round(o.base_cagr_pct, 2) if o.base else None,
            "Bull CAGR %": round(o.bull.cagr_pct, 2) if o.bull else None,
            "Bear CAGR %": round(o.bear.cagr_pct, 2) if o.bear else None,
            "Verdict": o.verdict,
            "Confidence": confidence,
            "Revenue source doc": rev_src,
            "Margin source doc": margin_src,
        })
    rank_df = pd.DataFrame(rows)
    st.dataframe(rank_df, use_container_width=True, hide_index=True)
    ensure_dir(OUTPUTS_DIR)
    csv_path = save_ranking_csv(rank_df, "sector_ranking.csv")
    st.download_button("Download ranking (CSV)", data=rank_df.to_csv(index=False).encode("utf-8"), file_name="sector_ranking.csv", mime="text/csv")
else:
    st.info("Fetch sector documents and Run AnalystOS to see the ranking.")

st.divider()

# ---- E. COMPANY DEEP DIVE ----
st.header("Company Deep Dive")
if result and result.get("company_results"):
    company_results = result["company_results"]
    selected = st.selectbox(
        "Select company",
        [r["output"].company_name or r["output"].company_id for r in company_results],
        key="deep_dive_select",
    )
    if selected:
        cr = next((r for r in company_results if (r["output"].company_name or r["output"].company_id) == selected), None)
        if cr:
            guidance, output = cr["guidance"], cr["output"]
            dossier = cr.get("dossier", {})
            rank = next((i + 1 for i, o in enumerate(result["ranked"]) if o.company_id == output.company_id), 0)
            total = len(result["ranked"])
            tab1, tab2, tab3, tab4 = st.tabs(["Evidence", "Assumptions", "Valuation", "Analyst Note"])

            with tab1:
                st.subheader("Evidence")
                if guidance.quotes:
                    for q in guidance.quotes:
                        with st.expander(f"**View Source** — {q.get('metric', '')} ({q.get('category', '')})"):
                            st.caption(f"**Document:** {q.get('source', '')} | **Page:** {q.get('source_page', '—')} | **Confidence:** {q.get('confidence', '')} | **Method:** {q.get('extraction_method', '')}")
                            st.write(q.get("quote", ""))
                        st.caption(f"{q.get('metric')} | {q.get('type')} | {q.get('value_min')}–{q.get('value_max')} {q.get('unit') or ''} | {q.get('timeline') or ''}")
                if getattr(guidance, "conflicts", None):
                    st.subheader("Conflicts")
                    for c in guidance.conflicts:
                        st.caption(f"**{c.get('metric')}**: {c.get('source_a')} vs {c.get('source_b')} — {c.get('notes')}")
                        st.text(f"A: \"{c.get('quote_a', '')}\"")
                        st.text(f"B: \"{c.get('quote_b', '')}\"")

            with tab2:
                st.subheader("Assumptions")
                a = guidance.assumptions
                st.write(f"**Revenue growth %:** Bear {a.bear_revenue_growth} | Base {a.base_revenue_growth} | Bull {a.bull_revenue_growth}")
                st.write(f"**Margin %:** Bear {a.bear_margin} | Base {a.base_margin} | Bull {a.bull_margin}")
                st.caption(f"Target PE used: {output.target_pe} (from historical median)")
                st.caption("Supporting evidence: see Evidence tab for source quotes.")

            with tab3:
                st.subheader("Valuation")
                if output.bear and output.base and output.bull:
                    scenario_df = pd.DataFrame([
                        {"Scenario": "Bear", "Projected EPS": output.bear.projected_eps, "Projected revenue": output.bear.projected_revenue, "Projected margin %": output.bear.projected_margin, "Target price": output.bear.target_price, "CAGR %": output.bear.cagr_pct},
                        {"Scenario": "Base", "Projected EPS": output.base.projected_eps, "Projected revenue": output.base.projected_revenue, "Projected margin %": output.base.projected_margin, "Target price": output.base.target_price, "CAGR %": output.base.cagr_pct},
                        {"Scenario": "Bull", "Projected EPS": output.bull.projected_eps, "Projected revenue": output.bull.projected_revenue, "Projected margin %": output.bull.projected_margin, "Target price": output.bull.target_price, "CAGR %": output.bull.cagr_pct},
                    ])
                    st.dataframe(scenario_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Insufficient data for valuation.")

            with tab4:
                st.subheader("Analyst Note")
                key_evidence = [q.get("quote", "")[:100] + "..." for q in guidance.quotes[:2] if q.get("quote")]
                note = generate_analyst_note(
                    output.company_name or output.company_id,
                    rank, total, output.verdict, output.base_cagr_pct,
                    cr.get("guidance_strength", ""), cr.get("confidence", ""),
                    key_evidence, len(getattr(guidance, "conflicts", []) or []),
                )
                st.markdown(note)
else:
    st.info("Run AnalystOS to see company deep dive.")
