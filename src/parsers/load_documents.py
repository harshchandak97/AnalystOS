"""Load company dossier JSON files from data/processed/; PDF text extraction from raw folders."""

import os
from pathlib import Path
from typing import Any

from src.utils.constants import DATA_PROCESSED, DATA_RAW
from src.utils.io_helpers import load_json

# Only JSON is used for dossiers in this workflow
SUPPORTED_EXTENSIONS = (".json",)
PDF_EXT = ".pdf"


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


def extract_text_from_company_folder(company_folder_path: str) -> list[dict[str, str]]:
    """
    Extract text from all PDFs in a company folder.
    Returns a list of {"file_name": "x.pdf", "text": "..."}. Skips empty PDFs.
    """
    pdf_paths = list_pdf_files_in_folder(company_folder_path)
    out = []
    for path in pdf_paths:
        text = extract_text_from_pdf(path)
        file_name = os.path.basename(path)
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
