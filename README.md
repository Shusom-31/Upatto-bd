# Tathyashala

Tathyashala is a guest workspace for exploring, cleaning and exporting tabular data. This repository contains a React/TypeScript client and a FastAPI service. The first implementation covers the core workspace, CSV/XLSX import, profiling, cleaning revisions, basic charts, and CSV/XLSX/PDF exports.

## Project structure

```text
Upatto-bd/
├── docs/
├── backend/
├── frontend/
├── .gitignore
└── README.md
```

## Run locally

**Backend** (Python 3.11+):

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Node 20+):

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open <http://localhost:5173>. The API docs are at <http://localhost:8000/docs>.

## What is implemented

- Named temporary workspaces, workspace credential checks and TTL cleanup.
- CSV and value-based XLSX import, worksheet choice, configurable CSV delimiter/encoding at the API, size/shape limits, duplicate/blank header normalization, profile summaries and paginated previews.
- Preview/apply for missing values, duplicates, text cleanup, type conversion and outlier review; revision checks, operation history, Undo and Reset.
- Basic category count, histogram, scatter and grouped charts.
- Value-based Excel, UTF-8 CSV and PDF summary exports.

ML preparation, reusable Excel templates, completed-file validation, Google Sheets, background jobs and multi-process shared storage are extension points, not finished features. See [the project overview](docs/PROJECT_OVERVIEW.md) and [API contract](docs/backend/API.md).

A small CSV fixture is available at [docs/samples/sample_employees.csv](docs/samples/sample_employees.csv).

The backend uses process-local temporary memory in this MVP. Run one worker only; data is lost when the API process restarts. It is not a production multi-user deployment without shared temporary storage, stronger session transport, monitoring and load/security review.
