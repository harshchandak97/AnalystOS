# AnalystOS

**Lightweight end-to-end AI equity analyst workflow:** preprocessed company documents → management guidance → structured assumptions → bull/base/bear valuation → ranked outputs (CAGR, target price, verdict).

---

## Problem statement

Analysts spend hours reading earnings calls and filings to pull out management guidance, turn it into assumptions, and run scenarios. AnalystOS automates this pipeline for a small sector universe: load local documents, extract guidance into structured assumptions, run a simple bull/base/bear model, and display ranked results (expected CAGR, target price, verdict) — without overengineering, external APIs, or a database.

---

## How the workflow works

1. **Load documents** — Read preprocessed company data from local files (JSON/CSV) in `data/processed/` (or `data/raw/`).
2. **Extract guidance** — Parse management guidance from documents into structured assumptions (e.g. revenue growth by scenario).
3. **Run scenario model** — Apply bull/base/bear assumptions to a simple valuation model; compute target price and expected CAGR per scenario.
4. **Rank & output** — Rank companies by base-case CAGR; show target price and verdict; save CSV to `outputs/` and offer download.

**Verdicts (rule-based):** High Conviction (base CAGR >20%), Watchlist (10–20%), Avoid (<10%), Insufficient Data (no explicit revenue growth guidance).

---

## Folder structure

```
AnalystOS/
├── app/
│   └── streamlit_app.py      # Streamlit UI entrypoint
├── data/
│   ├── raw/                  # Raw inputs (optional)
│   └── processed/            # Preprocessed company JSON/CSV
├── outputs/                 # Generated rankings and exports
├── sample_input/            # Sample input files for demos
├── sample_output/           # Sample output examples
├── src/
│   ├── parsers/
│   │   └── load_documents.py # Load company docs from disk
│   ├── extractors/
│   │   └── guidance_extractor.py  # Guidance → structured assumptions
│   ├── models/
│   │   └── scenario_model.py # Bull/base/bear valuation & ranking
│   └── utils/
│       ├── constants.py      # Paths and constants
│       └── io_helpers.py    # JSON/CSV read/write
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Setup instructions

1. **Clone or open the repo** and go to the project root.

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional:** Add your own company JSON files under `data/processed/` (see sample files there for structure).

---

## How to run the app

From the **project root**:

```bash
# Create venv and install deps (first time)
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the app
streamlit run app/streamlit_app.py
```

The app opens in the browser. Click **Load sample data** in the sidebar (choose sector or All), then **Run AnalystOS**. The main area shows:

- **Loaded companies** — Table of dossiers from `data/processed/`.
- **Extracted guidance & scenario outputs** — Per company: guidance quotes, bear/base/bull assumptions, scenario valuation table.
- **Final ranking** — Companies ranked by base CAGR; download CSV to `outputs/ranking_results.csv`.

---

## Hackathon-friendly notes

- **Minimal stack:** Python backend, Streamlit frontend, local files only (JSON/CSV). No DB, no auth, no scraping.
- **Runnable from the start:** Placeholder logic in parsers, extractors, and the scenario model keeps the pipeline working so you can demo and iterate.
- **Easy to extend:** Swap in real guidance extraction (e.g. OpenAI) in `guidance_extractor.py` and a real DCF or multiples model in `scenario_model.py` without changing the UI.
- **Sample data included:** Three mock company JSONs in `data/processed/` let you test the full flow immediately.

---

## GitHub (optional)

To link this repo to GitHub: create a new repo on GitHub, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/AnalystOS.git
git branch -M main
git push -u origin main
```

Use `git@github.com:YOUR_USERNAME/AnalystOS.git` if you use SSH.
