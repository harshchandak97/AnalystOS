"""I/O helpers for reading and writing JSON, CSV, and saving outputs."""

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.constants import OUTPUTS_DIR, DATA_PROCESSED, INTERMEDIATE_DIR


def load_json(path: str) -> dict[str, Any]:
    """Load a JSON file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict[str, Any], path: str) -> None:
    """Save a dict to a JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to CSV."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def ensure_dir(path: str) -> None:
    """Ensure a directory exists."""
    os.makedirs(path, exist_ok=True)


def save_ranking_csv(df: pd.DataFrame, filename: str = "ranking_results.csv") -> str:
    """
    Save a ranking DataFrame to outputs/<filename>.
    Returns the full path used.
    """
    ensure_dir(OUTPUTS_DIR)
    path = os.path.join(OUTPUTS_DIR, filename)
    save_csv(df, path)
    return path


def save_extracted_guidance_json(data: dict[str, Any], company_name: str) -> str:
    """
    Save extracted guidance JSON to data/processed/<company_name>.json.
    company_name can be a slug (e.g. acme_corp). Creates parent dir if needed.
    Returns the full path used.
    """
    ensure_dir(DATA_PROCESSED)
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in company_name).strip() or "company"
    path = os.path.join(DATA_PROCESSED, safe_name + ".json")
    save_json(data, path)
    return path


def load_extracted_guidance(company_name: str) -> dict[str, Any] | None:
    """Load extracted guidance JSON from data/processed/<company_name>.json. Returns None if not found."""
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in company_name).strip() or "company"
    path = os.path.join(DATA_PROCESSED, safe_name + ".json")
    if not os.path.isfile(path):
        return None
    try:
        return load_json(path)
    except Exception:
        return None


def save_intermediate_extraction(company_name: str, file_name: str, data: dict[str, Any]) -> str:
    """
    Save per-document extraction JSON to outputs/intermediate/<company_name>_<stem>.json for debugging.
    Returns the full path used.
    """
    ensure_dir(INTERMEDIATE_DIR)
    safe_company = "".join(c if c.isalnum() or c in "._-" else "_" for c in company_name).strip() or "company"
    stem = Path(file_name).stem if file_name else "doc"
    safe_stem = "".join(c if c.isalnum() or c in "._-" else "_" for c in stem).strip() or "doc"
    path = os.path.join(INTERMEDIATE_DIR, f"{safe_company}_{safe_stem}.json")
    save_json(data, path)
    return path
