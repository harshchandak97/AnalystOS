"""Shared constants and default paths for AnalystOS."""

import os

# Default paths (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
SECTOR_MAPPING_PATH = os.path.join(PROJECT_ROOT, "data", "sector_mapping.json")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
INTERMEDIATE_DIR = os.path.join(PROJECT_ROOT, "outputs", "intermediate")
SAMPLE_INPUT = os.path.join(PROJECT_ROOT, "sample_input")
SAMPLE_OUTPUT = os.path.join(PROJECT_ROOT, "sample_output")

# Supported file types for company documents
SUPPORTED_DOC_EXTENSIONS = (".json", ".csv", ".txt")

# Scenario labels
SCENARIOS = ("bear", "base", "bull")
