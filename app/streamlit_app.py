"""
AnalystOS — Lightweight AI equity analyst workflow.
Run from project root: streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.parsers.load_documents import load_all_dossiers, load_dossiers_by_sector
from src.extractors.guidance_extractor import extract_guidance
from src.models.scenario_model import run_scenario_model, rank_companies
from src.utils.constants import DATA_PROCESSED, OUTPUTS_DIR
from src.utils.io_helpers import save_ranking_csv, ensure_dir

st.set_page_config(page_title="AnalystOS", layout="wide")

# Session state: loaded dossiers and run results
if "dossiers" not in st.session_state:
    st.session_state.dossiers = []
if "results" not in st.session_state:
    st.session_state.results = []  # list of (ExtractedGuidance, ScenarioOutput) per company

# ---- Title ----
st.title("AnalystOS")
st.caption("Guidance → assumptions → bull/base/bear valuation → ranking")

# ---- Sidebar ----
with st.sidebar:
    st.header("Data")
    sector = st.selectbox(
        "Sector",
        ["Technology", "Healthcare", "Consumer", "All"],
        key="sector",
    )
    if st.button("Load sample data", type="primary"):
        if sector == "All":
            dossiers = load_all_dossiers(DATA_PROCESSED)
        else:
            dossiers = load_dossiers_by_sector(sector, DATA_PROCESSED)
        st.session_state.dossiers = dossiers
        st.success(f"Loaded {len(dossiers)} companies")
        st.session_state.results = []
    st.divider()
    st.caption("Data from `data/processed/*.json`. Load then run AnalystOS below.")

# ---- Main: loaded companies table ----
st.header("Loaded companies")
dossiers = st.session_state.dossiers
if not dossiers:
    st.info("Click **Load sample data** in the sidebar to load company dossiers from `data/processed/`.")
else:
    table_data = []
    for d in dossiers:
        table_data.append({
            "Company": d.get("company_name") or d.get("company_id", ""),
            "Sector": d.get("sector", ""),
            "Current price": d.get("current_price", ""),
            "Current EPS": d.get("current_eps", ""),
            "Median PE": d.get("historical_median_pe", ""),
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

# ---- Run AnalystOS ----
st.header("Run AnalystOS")
if st.button("Run AnalystOS", type="primary"):
    if not dossiers:
        st.warning("Load sample data first.")
    else:
        results = []
        for d in dossiers:
            guidance = extract_guidance(d)
            target_pe = d.get("historical_median_pe") or 20.0
            current_price = float(d.get("current_price") or 0)
            current_eps = float(d.get("current_eps") or 0)
            # Pass assumptions as dict for consistent reading in scenario model
            assumptions_dict = guidance.assumptions.model_dump() if hasattr(guidance.assumptions, "model_dump") else guidance.assumptions
            output = run_scenario_model(
                company_id=d.get("company_id", ""),
                company_name=d.get("company_name", ""),
                current_price=current_price,
                current_eps=current_eps,
                target_pe=float(target_pe),
                assumptions=assumptions_dict,
                insufficient_guidance=guidance.insufficient_guidance,
            )
            results.append((guidance, output))
        st.session_state.results = results
        st.success("Done. See extracted guidance, scenario outputs, and ranking below.")

results = st.session_state.results

# ---- Per-company: guidance quotes, assumptions, scenario table ----
if results:
    st.header("Extracted guidance & scenario outputs")
    for guidance, output in results:
        with st.expander(f"**{output.company_name or output.company_id}** — {output.verdict}"):
            # Guidance table: metric, category, type, value_min/max, timeline, source, quote
            st.subheader("Guidance")
            if guidance.quotes:
                rows = []
                for q in guidance.quotes:
                    rows.append({
                        "Metric": q.get("metric", ""),
                        "Category": q.get("category", ""),
                        "Type": q.get("type", ""),
                        "Value min": q.get("value_min"),
                        "Value max": q.get("value_max"),
                        "Unit": q.get("unit", ""),
                        "Timeline": q.get("timeline", ""),
                        "Source": q.get("source", ""),
                        "Quote": (q.get("quote", ""))[:120] + ("..." if len(q.get("quote", "")) > 120 else ""),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No guidance quotes.")
            # Conflicts (if any)
            if getattr(guidance, "conflicts", None):
                st.subheader("Conflicts")
                for c in guidance.conflicts:
                    st.caption(f"**{c.get('metric', '')}**: {c.get('source_a', '')} vs {c.get('source_b', '')} — {c.get('notes', '')}")
                    st.text(f"A: \"{c.get('quote_a', '')}\"")
                    st.text(f"B: \"{c.get('quote_b', '')}\"")
            # Derived assumptions
            st.subheader("Derived assumptions (bear / base / bull)")
            a = guidance.assumptions
            rev = f"Revenue growth %: {a.bear_revenue_growth} / {a.base_revenue_growth} / {a.bull_revenue_growth}"
            margin = f"Margin %: {a.bear_margin} / {a.base_margin} / {a.bull_margin}"
            st.write(rev)
            st.write(margin)
            # Scenario valuation table
            st.subheader("Scenario valuation")
            if output.bear and output.base and output.bull:
                scenario_df = pd.DataFrame([
                    {
                        "Scenario": "Bear",
                        "Projected EPS": output.bear.projected_eps,
                        "Target price": output.bear.target_price,
                        "CAGR %": output.bear.cagr_pct,
                    },
                    {
                        "Scenario": "Base",
                        "Projected EPS": output.base.projected_eps,
                        "Target price": output.base.target_price,
                        "CAGR %": output.base.cagr_pct,
                    },
                    {
                        "Scenario": "Bull",
                        "Projected EPS": output.bull.projected_eps,
                        "Target price": output.bull.target_price,
                        "CAGR %": output.bull.cagr_pct,
                    },
                ])
                st.dataframe(scenario_df, use_container_width=True, hide_index=True)
            else:
                st.caption("Insufficient data for valuation.")

# ---- Final ranking ----
st.header("Final ranking")
if results:
    outputs = [r[1] for r in results]
    ranked = rank_companies(outputs)
    rows = []
    for i, o in enumerate(ranked):
        bear_cagr = o.bear.cagr_pct if o.bear else None
        base_cagr = o.base_cagr_pct
        bull_cagr = o.bull.cagr_pct if o.bull else None
        rows.append({
            "Rank": i + 1,
            "Company": o.company_name or o.company_id,
            "Base CAGR %": base_cagr,
            "Bull CAGR %": bull_cagr,
            "Bear CAGR %": bear_cagr,
            "Target price": o.base_target_price,
            "Verdict": o.verdict,
        })
    rank_df = pd.DataFrame(rows)
    st.dataframe(rank_df, use_container_width=True, hide_index=True)

    # Save to outputs and offer download
    ensure_dir(OUTPUTS_DIR)
    csv_path = save_ranking_csv(rank_df, "ranking_results.csv")
    st.download_button(
        "Download ranking (CSV)",
        data=rank_df.to_csv(index=False).encode("utf-8"),
        file_name="ranking_results.csv",
        mime="text/csv",
    )
    st.caption(f"Saved to `{csv_path}`")
else:
    st.write("Run AnalystOS to see the ranking.")
