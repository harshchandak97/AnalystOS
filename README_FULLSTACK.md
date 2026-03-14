# AnalystOS - AI-Native Sector Analyst Workflow

**Premium equity research product** — Automated sector analysis with full source traceability.

---

## 🎯 Product Overview

AnalystOS is a polished, demo-ready equity research platform that transforms raw company documents into actionable investment insights. The system automatically:

1. **Fetches** local company documents and financial data
2. **Extracts** management guidance using AI
3. **Builds** bear/base/bull scenario assumptions
4. **Values** companies using historical P/E multiples
5. **Ranks** opportunities by expected CAGR

Every insight is traceable back to its source document and page number.

---

## 🏗️ Architecture

### Full-Stack Application

- **Backend:** FastAPI (Python) — Wraps existing analysis pipeline
- **Frontend:** React + Tailwind CSS — Premium analyst dashboard
- **Data Layer:** Local JSON files (no database required)

### Tech Stack

**Backend:**
- FastAPI 0.104+
- Python 3.11+
- Pandas, OpenAI SDK, PyMuPDF, PDFPlumber

**Frontend:**
- React 18
- Tailwind CSS 3
- Recharts (data visualization)
- Axios (API client)

---

## 📁 Project Structure

```
/app/
├── backend/                    # FastAPI backend
│   ├── server.py              # API routes
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── HeroSection.js
│   │   │   ├── AnalysisPipeline.js
│   │   │   ├── SectorRanking.js
│   │   │   ├── CompanyDeepDive.js
│   │   │   ├── HistoricalFinancials.js
│   │   │   ├── Evidence.js
│   │   │   ├── Assumptions.js
│   │   │   ├── Valuation.js
│   │   │   └── AnalystNote.js
│   │   ├── App.js             # Main application
│   │   ├── index.js           # Entry point
│   │   └── index.css          # Global styles
│   ├── public/
│   ├── package.json
│   └── .env
│
├── src/                        # Core Python logic (unchanged)
│   ├── parsers/               # Document loading
│   ├── extractors/            # Guidance extraction
│   ├── models/                # Valuation models
│   ├── pipeline/              # Analysis pipeline
│   └── utils/                 # Helpers
│
├── data/                       # Data files (source of truth)
│   ├── raw/                   # Company PDFs
│   │   ├── QPOWER/
│   │   ├── TARIL/
│   │   └── SCHNEIDER/
│   ├── processed/             # Extracted guidance JSONs
│   ├── financials/            # Historical financial JSONs
│   └── sector_mapping.json    # Sector → company mapping
│
└── outputs/                   # Generated analysis outputs
```

---

## 🚀 Quick Start

### 1. Prerequisites

✅ Python 3.11+  
✅ Node.js 18+ & Yarn  
✅ Backend and frontend folders already set up

### 2. Install Dependencies

**Backend:**
```bash
cd /app/backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd /app/frontend
yarn install
```

### 3. Start Services

Both services are managed by Supervisor:

```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

You should see:
- `backend` running on port 8001
- `frontend` running on port 3000

### 4. Access the Application

🌐 **Frontend:** http://localhost:3000  
🔌 **Backend API:** http://localhost:8001  
📚 **API Docs:** http://localhost:8001/docs

---

## 🎨 UI Components

### 1. Hero Section
- **Top opportunity** card
- **Companies analyzed** count
- **Best base CAGR** metric

### 2. Analysis Pipeline
- **Step tracker** with live status
- **Activity log** showing recent actions

### 3. Sector Opportunity Ranking
Sortable table showing:
- Company name & rank
- Base/Bull/Bear CAGR
- Verdict (High Conviction / Watchlist / Avoid)
- Confidence level

### 4. Company Deep Dive (5 Tabs)

#### **Historical Financials**
- Current price, EPS, historical median P/E
- Revenue history (chart + table)
- Profitability history (PAT, PBT)
- Margin trend analysis

#### **Evidence**
- Management guidance quotes
- Source document & page number
- Confidence levels
- Conflict detection

#### **Assumptions**
- Bear/Base/Bull revenue growth
- Bear/Base/Bull margin assumptions
- Supporting evidence for each
- Target P/E multiple used

#### **Valuation**
- 3-scenario projections (revenue, EPS, margin)
- Target price for each scenario
- Expected CAGR comparison
- Visual charts

#### **Analyst Note**
- Investment summary
- Why this rank?
- Key upside driver
- Key risk factors
- What to monitor
- Final verdict

---

## 🔄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/sectors` | List available sectors |
| GET | `/api/sectors/{sector}/companies` | Get companies in sector |
| GET | `/api/sectors/{sector}/dossiers` | Fetch sector dossiers |
| POST | `/api/analysis/run` | Run full analysis pipeline |
| GET | `/api/companies/{id}/financials` | Get company financials |
| GET | `/api/companies/{id}/guidance` | Get extracted guidance |

---

## 📊 Data Files

### Required Files

1. **`/app/data/sector_mapping.json`**
   Maps sectors to company folder names

2. **`/app/data/raw/{COMPANY}/`**
   Company PDF documents (earnings calls, presentations)

3. **`/app/data/financials/{company}.json`**
   Historical financial statements (annual + quarterly)

4. **`/app/data/processed/{company}.json`**
   Extracted management guidance (auto-generated or manual)

### Example: QPOWER

- PDFs: `/app/data/raw/QPOWER/`
- Financials: `/app/data/financials/QPOWER.json`
- Guidance: `/app/data/processed/QPOWER.json`

---

## 🧪 Testing the Application

### 1. Test Backend API
```bash
curl http://localhost:8001/api/sectors
curl http://localhost:8001/api/sectors/power_equipment/companies
```

### 2. Run Analysis (Backend)
```bash
curl -X POST http://localhost:8001/api/analysis/run \
  -H "Content-Type: application/json" \
  -d '{"sector": "power_equipment", "run_extraction": false}'
```

### 3. Test Frontend
1. Open browser: http://localhost:3000
2. Select "POWER_EQUIPMENT" sector
3. Click "Run Analysis"
4. View results across all sections

---

## 🎯 Design Goals (Achieved)

✅ **Clean** — Minimal, professional interface  
✅ **Premium** — High-quality typography, spacing, colors  
✅ **Serious** — Equity research product, not a toy  
✅ **Demo-ready** — Polished enough for stakeholder demos  
✅ **Not a chatbot** — Task-focused analyst workflow  
✅ **Not an admin dashboard** — Investment-focused UI  

---

## 🔧 Configuration

### Backend Environment (`.env`)
```bash
# Optional: OpenAI API key for guidance extraction
# OPENAI_API_KEY=your_key_here
```

### Frontend Environment (`.env`)
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🐛 Troubleshooting

### Backend not starting
```bash
tail -50 /var/log/supervisor/backend.err.log
cd /app/backend && python server.py
```

### Frontend not compiling
```bash
tail -50 /var/log/supervisor/frontend.err.log
cd /app/frontend && yarn start
```

### CORS errors
Check that backend allows frontend origin in CORS middleware

### No data showing
1. Verify data files exist in `/app/data/`
2. Check sector_mapping.json
3. Ensure company folders match mapping

---

## 📝 Usage Workflow

1. **Select Sector** → Choose from dropdown (e.g., power_equipment)
2. **Run Analysis** → Click button to start pipeline
3. **View Hero Metrics** → Top opportunity, count, best CAGR
4. **Check Pipeline** → Monitor workflow steps + activity log
5. **Review Ranking** → Sort by CAGR, verdict, confidence
6. **Deep Dive** → Click any company to see 5-tab analysis
7. **Inspect Sources** → Click "View Source" on any evidence

---

## 🚢 Production Deployment

### Environment Variables
- `REACT_APP_BACKEND_URL` → Point to production backend
- `OPENAI_API_KEY` → If running live extraction

### Build Frontend
```bash
cd /app/frontend
yarn build
```

### Serve Static Build
Use nginx or any static file server to serve `/app/frontend/build/`

### Backend
Run with gunicorn + uvicorn workers:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001
```

---

## 📖 Original Python Logic

All existing Python modules in `/app/src/` are **preserved and unchanged**:

- ✅ `src/parsers/load_documents.py` — Document loading
- ✅ `src/extractors/guidance_extractor.py` — LLM extraction
- ✅ `src/models/scenario_model.py` — Valuation logic
- ✅ `src/pipeline/run_analysis.py` — Full pipeline
- ✅ `src/utils/` — Constants, I/O helpers, analyst note

The FastAPI backend **wraps** this logic without modification.

---

## 🎓 Key Features

1. **Source Traceability** — Every metric links to source doc + page
2. **Historical Financials** — Charts + tables for revenue, PAT, margins
3. **Active Workflow** — Visible pipeline steps, not just final output
4. **3-Scenario Valuation** — Bear/Base/Bull with full transparency
5. **Conflict Detection** — Flags contradictory guidance
6. **Analyst Note** — PM-style investment memo per company

---

## 📚 Additional Resources

- **Backend API Docs:** http://localhost:8001/docs (Swagger UI)
- **Original Streamlit App:** `/app/app/streamlit_app.py` (archived)
- **Sample Data:** `/app/sample_input/`, `/app/sample_output/`

---

## 🏆 Credits

Built on the **AnalystOS** Python codebase with a modern full-stack upgrade:

- Original logic: Python-based guidance extraction & valuation
- UI upgrade: React + Tailwind premium interface
- Architecture: FastAPI backend + React frontend
- Design philosophy: Clean, serious, demo-ready equity research product

---

**Ready to analyze sectors? Start the app and select a sector!** 🚀
