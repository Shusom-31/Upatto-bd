import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.infrastructure.cleanup import cleanup_loop, stop_cleanup
from app.modules.sessions.router import router as sessions_router
from app.modules.datasets.router import router as datasets_router
from app.modules.cleaning.router import router as cleaning_router
from app.modules.charts.router import router as charts_router
from app.modules.exports.router import router as exports_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(cleanup_loop())
    yield
    await stop_cleanup(task)


app = FastAPI(title=settings.app_name, version="0.1.0", description="Temporary guest workspaces for tabular data preparation.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(sessions_router, prefix=settings.api_prefix)
app.include_router(datasets_router, prefix=settings.api_prefix)
app.include_router(cleaning_router, prefix=settings.api_prefix)
app.include_router(charts_router, prefix=settings.api_prefix)
app.include_router(exports_router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get(settings.api_prefix)
def api_root():
    return {"name": settings.app_name, "version": "v1", "docs": "/docs"}


@app.exception_handler(Exception)
async def unexpected_error(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})
