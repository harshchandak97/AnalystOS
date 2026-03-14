"""Load company documents from local files (JSON, CSV, or folder)."""

import os
from pathlib import Path
from typing import Any

from src.utils.constants import DATA_PROCESSED, DATA_RAW, SUPPORTED_DOC_EXTENSIONS
from src.utils.io_helpers import load_json, load_csv


def list_available_companies(data_dir: str | None = None) -> list[str]:
    """
    List company identifiers available in the data directory.
    Uses filenames (without extension) or subfolder names as company IDs.
    """
    data_dir = data_dir or DATA_PROCESSED
    if not os.path.isdir(data_dir):
        return []
    names = set()
    for name in os.listdir(data_dir):
        if name.startswith("."):
            continue
        path = os.path.join(data_dir, name)
        if os.path.isfile(path):
            stem = Path(name).stem
            if Path(name).suffix.lower() in SUPPORTED_DOC_EXTENSIONS:
                names.add(stem)
        elif os.path.isdir(path):
            names.add(name)
    return sorted(names)


def load_company_document(company_id: str, data_dir: str | None = None) -> dict[str, Any]:
    """
    Load a single company's document by ID.
    Looks for {company_id}.json, then {company_id}.csv, then {company_id}.txt.
    Returns a dict with at least 'company_id' and 'content' or structured fields.
    """
    data_dir = data_dir or DATA_PROCESSED
    base = os.path.join(data_dir, company_id)
    for ext in (".json", ".csv", ".txt"):
        path = base + ext
        if os.path.isfile(path):
            if ext == ".json":
                data = load_json(path)
                data.setdefault("company_id", company_id)
                return data
            if ext == ".csv":
                df = load_csv(path)
                return {"company_id": company_id, "content": df.to_dict(orient="records")}
            # .txt
            with open(path, "r", encoding="utf-8") as f:
                return {"company_id": company_id, "content": f.read()}
    return {"company_id": company_id, "content": ""}


def load_sector_documents(sector: str | None = None, data_dir: str | None = None) -> list[dict[str, Any]]:
    """
    Load all company documents for a sector (or all if sector is None).
    For now, sector is optional; we use a flat data dir and return all companies.
    """
    companies = list_available_companies(data_dir)
    if sector:
        # Placeholder: filter by sector if we add sector metadata later
        companies = [c for c in companies if _company_sector(c, data_dir) == sector]
    return [load_company_document(cid, data_dir) for cid in companies]


def _company_sector(company_id: str, data_dir: str) -> str | None:
    """Return sector for a company if available in its document; else None."""
    doc = load_company_document(company_id, data_dir)
    return doc.get("sector")
