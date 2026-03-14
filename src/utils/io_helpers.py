"""I/O helpers for reading and writing JSON, CSV, and saving outputs."""

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.constants import OUTPUTS_DIR


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
