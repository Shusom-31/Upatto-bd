# Frontend setup

Requirements: Node.js 20 or later and npm.

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_URL` to the FastAPI base URL including `/api/v1` if it is not `http://localhost:8000/api/v1`. `npm run build` creates static assets in `dist/`; serve those behind HTTPS in deployment. The API CORS allowlist must include the frontend origin.
