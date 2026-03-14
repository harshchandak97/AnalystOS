#!/usr/bin/env python3
"""
Run the LLM-powered PDF extraction pipeline for a company.
Usage (from project root):
  python scripts/run_pdf_extraction.py <company_name> [folder_path]
  python -m scripts.run_pdf_extraction <company_name> [folder_path]

If folder_path is omitted, uses data/raw/<company_name>/.
Requires OPENAI_API_KEY in the environment.
"""
import sys
from pathlib import Path

# Project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.constants import DATA_RAW
from src.extractors.guidance_extractor import run_llm_extraction_pipeline


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_pdf_extraction.py <company_name> [folder_path]", file=sys.stderr)
        sys.exit(1)
    company_name = sys.argv[1].strip()
    folder_path = sys.argv[2].strip() if len(sys.argv) > 2 else None
    if not folder_path:
        folder_path = str(Path(DATA_RAW) / company_name)
    if not Path(folder_path).is_dir():
        print(f"Error: folder not found: {folder_path}", file=sys.stderr)
        sys.exit(1)
    result = run_llm_extraction_pipeline(company_name, folder_path)
    n = len(result.get("guidance", []))
    print(f"Extracted {n} guidance items for {result.get('company', company_name)}.")
    print(f"Saved to data/processed/{company_name}.json")


if __name__ == "__main__":
    main()
