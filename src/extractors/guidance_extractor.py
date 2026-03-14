"""Extract explicit management guidance into bear/base/bull assumptions; LLM-based extraction from PDF text."""

import json
import os
import re
from typing import Any

from pydantic import BaseModel, Field

# --- LLM extraction (OpenAI) ---

# Metrics supported for extraction (direct financial + operational + directional)
SUPPORTED_METRICS = frozenset({
    "revenue_growth", "ebitda_margin", "pat_margin", "eps",
    "capex", "order_book", "order_inflow_expected", "order_executable_horizon",
    "demand_outlook", "capacity_expansion", "facility_completion_timeline",
    "utilization_target", "revenue_capacity_potential", "margin_floor",
})

EXTRACT_SYSTEM_PROMPT = """You are a financial document extraction engine.

Your task is to extract only forward-looking management commentary from company documents such as earnings call transcripts and investor presentations.

Your goal is to extract any statement that can support future financial modeling.

There are three categories of extraction:

1. direct_financial
This includes explicit forward guidance on:
- revenue_growth
- ebitda_margin
- pat_margin
- eps

2. operational_modeling
This includes forward-looking operational statements that can support future modeling, such as:
- order_book
- order_inflow_expected
- order_executable_horizon
- capacity_expansion
- facility_completion_timeline
- utilization_target
- revenue_capacity_potential
- capex
- margin_floor

3. directional_context
This includes useful directional but non-numeric business outlook commentary, such as:
- demand_outlook

Rules:
- Extract only forward-looking statements made by management.
- Prefer explicit numerical guidance.
- If a statement contains a numerical target, range, floor, timing, or capacity-linked revenue potential, classify it carefully and preserve the numbers.
- If a statement is qualitative only, classify it as directional.
- Do not invent numbers.
- Do not estimate values that are not clearly stated.
- Do not convert operational commentary into revenue forecasts inside the extraction step.
- Keep the exact quote.
- Include the source document name for every extracted item.
- Return only valid JSON following the required schema.
- Do not add markdown fences.
- Do not add explanations."""

EXTRACTION_SCHEMA = """
Required JSON schema (return only this structure, no other keys at top level):
{
  "company": "Company Name",
  "guidance": [
    {
      "metric": "revenue_growth | ebitda_margin | pat_margin | eps | capex | order_book | order_inflow_expected | order_executable_horizon | demand_outlook | capacity_expansion | facility_completion_timeline | utilization_target | revenue_capacity_potential | margin_floor",
      "category": "direct_financial | operational_modeling | directional_context",
      "type": "explicit | directional",
      "value_min": 15,
      "value_max": 20,
      "unit": "percent | crore_rs | million_rs | years | months | x | null",
      "timeline": "next 2 years",
      "source_document": "latest_concall.pdf",
      "quote": "Exact quote from management",
      "notes": "Optional clarification if needed"
    }
  ]
}
- category must be one of: direct_financial, operational_modeling, directional_context.
- type must be one of: explicit, directional.
- For directional guidance use "type": "directional" and "value_min": null, "value_max": null.
- If only one number is given, set both value_min and value_max to that number.
"""


def build_user_prompt(company_name: str, file_name: str, text: str) -> str:
    """Build the user prompt for the LLM: company name, source document, and extracted text."""
    if not (text or "").strip():
        return ""
    return f"""Company name: {company_name}
Source document: {file_name}

Extract all forward-looking management guidance from the following document text.

Focus on:
- direct financial guidance
- operational guidance that can support modeling
- directional business outlook

Return only valid JSON.

Document text:
{text[:120000]}"""


def parse_llm_json_safely(raw: str) -> dict[str, Any] | None:
    """
    Parse LLM response as JSON. Strips markdown code fences if present. Returns None on failure.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    # Remove optional markdown code block
    for pattern in (r"^```(?:json)?\s*\n?", r"\n?```\s*$"):
        s = re.sub(pattern, "", s)
    s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def _normalize_guidance_item(g: dict[str, Any], file_name: str) -> dict[str, Any]:
    """Ensure each guidance item has category, type, source_document, notes."""
    g = dict(g)
    g.setdefault("category", "operational_modeling")
    g.setdefault("type", "directional")
    g["source_document"] = g.get("source_document") or file_name
    g.setdefault("notes", None)
    return g


def extract_guidance_from_text_via_llm(
    company_name: str,
    file_name: str,
    text: str,
    *,
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
) -> dict[str, Any] | None:
    """
    Send extracted PDF text to OpenAI and return structured guidance JSON for one document.
    Returns None on empty text, API error, or invalid JSON.
    """
    prompt = build_user_prompt(company_name, file_name, text)
    if not prompt:
        return None
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM_PROMPT + EXTRACTION_SCHEMA},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        raw = (response.choices[0].message.content or "").strip()
        if not raw:
            return None
        parsed = parse_llm_json_safely(raw)
        if not parsed or "guidance" not in parsed:
            return None
        parsed.setdefault("company", company_name)
        guidance = []
        for g in parsed.get("guidance") or []:
            if isinstance(g, dict):
                guidance.append(_normalize_guidance_item(g, file_name))
        parsed["guidance"] = guidance
        return parsed
    except Exception:
        return None


def extract_guidance_from_document(
    company_name: str,
    file_name: str,
    text: str,
    *,
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
) -> dict[str, Any] | None:
    """
    Pass 1: Extract guidance from a single document. Returns per-document JSON with guidance list.
    """
    return extract_guidance_from_text_via_llm(
        company_name, file_name, text, model=model, api_key=api_key
    )


def consolidate_company_guidance(
    company_name: str,
    extracted_document_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Pass 2: Combine per-document extractions into one company JSON.
    Deduplicates by quote (normalized); preserves materially different statements.
    Each item in extracted_document_results should have "file_name" and "guidance" (list).
    """
    documents_processed: list[str] = []
    all_guidance: list[dict[str, Any]] = []
    seen_quote_norm: set[str] = set()

    for doc_result in extracted_document_results:
        file_name = doc_result.get("file_name", "")
        if file_name and file_name not in documents_processed:
            documents_processed.append(file_name)
        for g in doc_result.get("guidance") or []:
            if not isinstance(g, dict):
                continue
            quote = (g.get("quote") or "").strip()
            quote_norm = quote.lower()[:200] if quote else ""
            if quote_norm and quote_norm in seen_quote_norm:
                continue
            if quote_norm:
                seen_quote_norm.add(quote_norm)
            all_guidance.append(dict(g))

    return {
        "company": company_name,
        "documents_processed": documents_processed,
        "guidance": all_guidance,
    }


def detect_conflicts(guidance_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Detect conflicts: same metric, different explicit values or timelines across sources.
    Simple heuristic: group by metric; if 2+ items have different value_min/value_max or timeline, add conflict.
    """
    from collections import defaultdict
    by_metric: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for g in guidance_items:
        if not isinstance(g, dict):
            continue
        m = (g.get("metric") or "").strip().lower()
        if m:
            by_metric[m].append(g)

    conflicts: list[dict[str, Any]] = []
    for metric, items in by_metric.items():
        if len(items) < 2:
            continue
        explicit = [x for x in items if x.get("value_min") is not None or x.get("value_max") is not None]
        if len(explicit) < 2:
            continue
        for i in range(len(explicit)):
            for j in range(i + 1, len(explicit)):
                a, b = explicit[i], explicit[j]
                v_a = (a.get("value_min"), a.get("value_max"), (a.get("timeline") or "").strip())
                v_b = (b.get("value_min"), b.get("value_max"), (b.get("timeline") or "").strip())
                if v_a != v_b:
                    conflicts.append({
                        "metric": metric,
                        "source_a": a.get("source_document", ""),
                        "quote_a": a.get("quote", ""),
                        "source_b": b.get("source_document", ""),
                        "quote_b": b.get("quote", ""),
                        "notes": "Potential inconsistency across sources",
                    })
                    break
            else:
                continue
            break
    return conflicts


def run_llm_extraction_pipeline(
    company_name: str,
    company_folder_path: str,
    *,
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
    save_path: str | None = None,
    save_intermediate: bool = True,
) -> dict[str, Any]:
    """
    Two-pass extraction: Pass 1 per-document LLM extraction; Pass 2 consolidate + conflict detection.
    Saves final JSON to data/processed/<company_name>.json; optionally saves per-doc JSON to outputs/intermediate/.
    """
    from src.parsers.load_documents import extract_text_from_company_folder
    from src.utils.io_helpers import save_extracted_guidance_json, save_intermediate_extraction

    documents = extract_text_from_company_folder(company_folder_path)
    if not documents:
        print(f"[extract] No PDFs found in {company_folder_path}")
        out = {"company": company_name, "documents_processed": [], "guidance": [], "conflicts": []}
        save_extracted_guidance_json(out, company_name)
        return out

    print(f"[extract] Processing {len(documents)} PDF(s) for {company_name}")
    extracted_document_results: list[dict[str, Any]] = []

    for doc in documents:
        file_name = doc.get("file_name", "")
        text = (doc.get("text") or "").strip()
        if not text:
            print(f"[extract]   Skip {file_name}: empty text")
            continue
        result = extract_guidance_from_document(
            company_name, file_name, text, model=model, api_key=api_key
        )
        if not result:
            print(f"[extract]   Skip {file_name}: no result or invalid JSON")
            continue
        guidance = result.get("guidance") or []
        print(f"[extract]   {file_name}: {len(guidance)} guidance item(s)")
        extracted_document_results.append({"file_name": file_name, "guidance": guidance})
        if save_intermediate:
            save_intermediate_extraction(company_name, file_name, result)

    consolidated = consolidate_company_guidance(company_name, extracted_document_results)
    guidance_list = consolidated.get("guidance", [])
    conflicts = detect_conflicts(guidance_list)
    consolidated["conflicts"] = conflicts

    total = len(guidance_list)
    print(f"[extract] Consolidated: {total} guidance item(s), {len(conflicts)} conflict(s)")

    if save_path is None:
        save_extracted_guidance_json(consolidated, company_name)
    else:
        from pathlib import Path
        from src.utils.io_helpers import save_json
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        save_json(consolidated, save_path)
    return consolidated


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
    # Conflicts across documents (from two-pass extraction)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
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
    Accepts both management_guidance and LLM-output guidance (with source_document).
    """
    company_id = dossier.get("company_id", dossier.get("company", "unknown"))
    company_name = dossier.get("company_name", dossier.get("company", company_id))
    raw = dossier.get("management_guidance") or dossier.get("guidance") or []
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
            "category": g.get("category"),
            "type": gtype,
            "value_min": g.get("value_min"),
            "value_max": g.get("value_max"),
            "unit": g.get("unit"),
            "timeline": g.get("timeline"),
            "quote": q,
            "source": g.get("source") or g.get("source_document"),
            "notes": g.get("notes"),
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
        elif metric in ("margin", "ebitda_margin", "pat_margin", "margin_floor"):
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
    conflicts = dossier.get("conflicts") if isinstance(dossier.get("conflicts"), list) else []
    return ExtractedGuidance(
        company_id=company_id,
        company_name=company_name,
        assumptions=assumptions,
        quotes=quotes,
        conflicts=conflicts,
        insufficient_guidance=insufficient_guidance,
    )
