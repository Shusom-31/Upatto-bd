# Backend setup

Requirements: Python 3.11 or later.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health check: `GET /health`; interactive API schema: `/docs`. Configure limits and CORS with `UPATTO_ALLOWED_ORIGINS`, `UPATTO_MAX_UPLOAD_MB`, `UPATTO_MAX_ROWS`, `UPATTO_MAX_COLUMNS`, `UPATTO_SESSION_TTL_MINUTES`, `UPATTO_CLEANUP_INTERVAL_SECONDS`, and `UPATTO_TEMPORARY_DIRECTORY`.

The supplied Dockerfile runs one Uvicorn process. Keep a single worker while the in-memory workspace registry is used. `.data` is for temporary export artifacts if later needed; current export responses stream directly.
