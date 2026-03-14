"""Load company dossier JSON files from data/processed/."""

import os
from pathlib import Path
from typing import Any

from src.utils.constants import DATA_PROCESSED
from src.utils.io_helpers import load_json

# Only JSON is used for dossiers in this workflow
SUPPORTED_EXTENSIONS = (".json",)


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
