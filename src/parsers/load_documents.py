"""Load company dossier JSON files from data/processed/; PDF text extraction from raw folders; sector/company discovery."""

import os
from pathlib import Path
from typing import Any

from src.utils.constants import DATA_PROCESSED, DATA_RAW, SECTOR_MAPPING_PATH
from src.utils.io_helpers import load_json

# Only JSON is used for dossiers in this workflow
SUPPORTED_EXTENSIONS = (".json",)
PDF_EXT = ".pdf"


def load_sector_mapping(mapping_path: str | None = None) -> dict[str, list[str]]:
    """Load sector -> list of company folder names from data/sector_mapping.json. Returns {} on missing/invalid."""
    path = mapping_path or SECTOR_MAPPING_PATH
    if not os.path.isfile(path):
        return {}
    try:
        data = load_json(path)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def list_company_folders_in_raw(raw_dir: str | None = None) -> list[str]:
    """List company folder names under data/raw/ (subdirs with at least one file)."""
    raw_dir = raw_dir or DATA_RAW
    if not os.path.isdir(raw_dir):
        return []
    out = []
    for name in sorted(os.listdir(raw_dir)):
        if name.startswith("."):
            continue
        path = os.path.join(raw_dir, name)
        if os.path.isdir(path) and os.listdir(path):
            out.append(name)
    return out


def get_companies_for_sector(sector: str, raw_dir: str | None = None, mapping_path: str | None = None) -> list[str]:
    """
    Get company folder names for the selected sector.
    Uses sector_mapping.json if available; else falls back to all company folders in data/raw.
    """
    mapping = load_sector_mapping(mapping_path)
    sector_key = sector.strip().lower().replace(" ", "_")
    # Try exact key first
    companies = mapping.get(sector) or mapping.get(sector_key)
    if companies is not None and isinstance(companies, list):
        raw_dir = raw_dir or DATA_RAW
        return [c for c in companies if os.path.isdir(os.path.join(raw_dir, c))]
    # Fallback: all folders in raw
    return list_company_folders_in_raw(raw_dir)


def list_pdf_files_in_folder(folder_path: str) -> list[str]:
    """List full paths of all PDF files in the given folder. Returns empty list if not a dir."""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    out = []
    for name in sorted(os.listdir(folder_path)):
        if name.startswith(".") or Path(name).suffix.lower() != PDF_EXT:
            continue
        out.append(os.path.join(folder_path, name))
    return out


def _extract_text_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF (fitz)."""
    import fitz
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text())
    doc.close()
    return "\n".join(parts).strip()


def extract_pages_from_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """Extract text per page. Returns [{"page": 1, "text": "..."}, ...]. Page numbers 1-based."""
    if not os.path.isfile(pdf_path) or Path(pdf_path).suffix.lower() != PDF_EXT:
        return []
    try:
        import fitz
        doc = fitz.open(pdf_path)
        out = []
        for i, page in enumerate(doc):
            out.append({"page": i + 1, "text": page.get_text().strip()})
        doc.close()
        return out
    except Exception:
        try:
            import pdfplumber
            out = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    out.append({"page": i + 1, "text": (t or "").strip()})
            return out
        except Exception:
            return []


def _extract_text_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber."""
    import pdfplumber
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
    return "\n".join(parts).strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a single PDF. Uses PyMuPDF (fitz) if available, else pdfplumber.
    Returns empty string on error or empty PDF.
    """
    if not os.path.isfile(pdf_path) or Path(pdf_path).suffix.lower() != PDF_EXT:
        return ""
    try:
        return _extract_text_pymupdf(pdf_path)
    except Exception:
        try:
            return _extract_text_pdfplumber(pdf_path)
        except Exception:
            return ""


def extract_text_from_company_folder(company_folder_path: str, with_pages: bool = False) -> list[dict[str, Any]]:
    """
    Extract text from all PDFs in a company folder.
    If with_pages=False: returns [{"file_name": "x.pdf", "text": "..."}].
    If with_pages=True: also adds "pages": [{"page": 1, "text": "..."}] and "text" has "--- Page N ---" markers for LLM source_page.
    """
    pdf_paths = list_pdf_files_in_folder(company_folder_path)
    out = []
    for path in pdf_paths:
        file_name = os.path.basename(path)
        if with_pages:
            pages = extract_pages_from_pdf(path)
            if not pages:
                continue
            parts = [f"--- Page {p['page']} ---\n{p['text']}" for p in pages]
            text = "\n\n".join(parts)
            out.append({"file_name": file_name, "text": text, "pages": pages})
        else:
            text = extract_text_from_pdf(path)
            out.append({"file_name": file_name, "text": text})
    return out


def load_all_dossiers(data_dir: str | None = None) -> list[dict[str, Any]]:
    """
    Load all company dossier JSON files from data/processed/.
    Returns a list of dicts (one per company). Each dict has company_id, company_name,
    sector, current_price, current_eps, historical_median_pe, management_guidance, etc.
    """
    data_dir = data_dir or DATA_PROCESSED
    if not os.path.isdir(data_dir):
        return []
    out: list[dict[str, Any]] = []
    for name in sorted(os.listdir(data_dir)):
        if name.startswith(".") or not name.lower().endswith(".json"):
            continue
        path = os.path.join(data_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            data = load_json(path)
            data.setdefault("company_id", Path(name).stem)
            out.append(data)
        except Exception:
            continue
    return out


def load_dossiers_by_sector(sector: str, data_dir: str | None = None) -> list[dict[str, Any]]:
    """Load all dossiers and filter by sector."""
    all_dossiers = load_all_dossiers(data_dir)
    return [d for d in all_dossiers if (d.get("sector") or "").strip() == sector.strip()]


def list_available_companies(data_dir: str | None = None) -> list[str]:
    """List company identifiers (JSON stems) in the data directory."""
    data_dir = data_dir or DATA_PROCESSED
    if not os.path.isdir(data_dir):
        return []
    names = set()
    for name in os.listdir(data_dir):
        if name.startswith("."):
            continue
        if Path(name).suffix.lower() in SUPPORTED_EXTENSIONS:
            names.add(Path(name).stem)
    return sorted(names)


def load_company_document(company_id: str, data_dir: str | None = None) -> dict[str, Any] | None:
    """Load a single company dossier by company_id. Returns None if not found."""
    data_dir = data_dir or DATA_PROCESSED
    path = os.path.join(data_dir, company_id + ".json")
    if not os.path.isfile(path):
        return None
    data = load_json(path)
    data.setdefault("company_id", company_id)
    return data


def fetch_sector_dossiers(
    sector: str,
    raw_dir: str | None = None,
    processed_dir: str | None = None,
    mapping_path: str | None = None,
) -> list[dict[str, Any]]:
    """
    For the given sector, discover companies and build a list of dossiers.
    Each dossier has: company_id, company_name, sector, folder_path, pdf_files, and any keys from data/processed/<id>.json (current_price, current_eps, guidance, etc.).
    Companies without processed JSON still appear with folder_path and pdf_files so the app can run extraction.
    """
    raw_dir = raw_dir or DATA_RAW
    processed_dir = processed_dir or DATA_PROCESSED
    companies = get_companies_for_sector(sector, raw_dir=raw_dir, mapping_path=mapping_path)
    out = []
    for cid in companies:
        folder_path = os.path.join(raw_dir, cid)
        pdfs = list_pdf_files_in_folder(folder_path)
        pdf_files = [os.path.basename(p) for p in pdfs]
        dossier = load_company_document(cid, processed_dir) or {}
        dossier.setdefault("company_id", cid)
        dossier.setdefault("company_name", cid.replace("_", " ").title())
        dossier.setdefault("sector", sector)
        dossier["folder_path"] = folder_path
        dossier["pdf_files"] = pdf_files
        out.append(dossier)
    return out
